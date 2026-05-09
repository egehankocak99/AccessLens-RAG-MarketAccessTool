from __future__ import annotations

import logging
import time
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


LABEL_URL = "https://api.fda.gov/drug/label.json"
ADVERSE_URL = "https://api.fda.gov/drug/event.json"
LABEL_LIMIT = 10
ADVERSE_LIMIT = 10


class OpenFDAFetcher:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AccessLens/1.0"})

    def fetch_labels(self, drug_name: str) -> list[dict[str, Any]]:
        params = self._build_params(
            search=f'openfda.generic_name:"{quote(drug_name)}" openfda.brand_name:"{quote(drug_name)}"',
            limit=LABEL_LIMIT,
        )
        try:
            response = self._get_with_backoff(LABEL_URL, params)
        except requests.HTTPError as exc:
            logger.warning("OpenFDA label fetch failed for '%s': %s", drug_name, exc)
            return []

        data = response.json()
        return [self._parse_label(result, drug_name) for result in data.get("results", [])]

    def fetch_adverse_events(self, drug_name: str) -> list[dict[str, Any]]:
        params = self._build_params(
            search=f'patient.drug.medicinalproduct:"{quote(drug_name)}"',
            limit=ADVERSE_LIMIT,
        )
        try:
            response = self._get_with_backoff(ADVERSE_URL, params)
        except requests.HTTPError as exc:
            logger.warning("OpenFDA AE fetch failed for '%s': %s", drug_name, exc)
            return []

        data = response.json()
        return [self._parse_adverse_event(result, drug_name) for result in data.get("results", [])]

    def fetch_all(self, drug_name: str) -> list[dict[str, Any]]:
        labels = self.fetch_labels(drug_name)
        time.sleep(0.3)
        adverse = self.fetch_adverse_events(drug_name)
        return labels + adverse

    def _build_params(self, search: str, limit: int) -> dict[str, Any]:
        params: dict[str, Any] = {"search": search, "limit": limit}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def _parse_label(self, result: dict[str, Any], drug_name: str) -> dict[str, Any]:
        openfda = result.get("openfda", {})
        brand_names: list[str] = openfda.get("brand_name", [])
        generic_names: list[str] = openfda.get("generic_name", [])
        display_name = brand_names[0] if brand_names else (generic_names[0] if generic_names else drug_name)

        indications = " ".join(result.get("indications_and_usage", []))
        warnings = " ".join(result.get("warnings", []))
        adverse = " ".join(result.get("adverse_reactions", []))
        mechanism = " ".join(result.get("mechanism_of_action", []))

        content_parts: list[str] = []
        if indications:
            content_parts.append(f"INDICATIONS AND USAGE: {indications}")
        if mechanism:
            content_parts.append(f"MECHANISM OF ACTION: {mechanism}")
        if warnings:
            content_parts.append(f"WARNINGS: {warnings}")
        if adverse:
            content_parts.append(f"ADVERSE REACTIONS: {adverse}")

        return {
            "drug_name": display_name,
            "content": "\n\n".join(content_parts),
            "doc_type": "drug_label",
            "source": "openfda",
        }

    def _parse_adverse_event(self, result: dict[str, Any], drug_name: str) -> dict[str, Any]:
        reactions: list[str] = [
            r.get("reactionmeddrapt", "")
            for r in result.get("patient", {}).get("reaction", [])
            if r.get("reactionmeddrapt")
        ]
        serious: str = "Serious" if result.get("serious") == "1" else "Non-serious"
        report_date: str = result.get("receiptdate", "")
        country: str = result.get("occurcountry", "")

        content = (
            f"ADVERSE EVENT REPORT\n"
            f"Drug: {drug_name}\n"
            f"Reactions: {', '.join(reactions)}\n"
            f"Outcome: {serious}\n"
            f"Receipt date: {report_date}\n"
            f"Country: {country}"
        )

        return {
            "drug_name": drug_name,
            "content": content,
            "doc_type": "drug_label",
            "source": "openfda",
        }

    def _get_with_backoff(
        self, url: str, params: dict[str, Any], max_retries: int = 4, base_delay: float = 1.0
    ) -> requests.Response:
        delay = base_delay
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=30)
                if response.status_code == 404:
                    response.raise_for_status()
                if response.status_code == 429 or response.status_code >= 500:
                    raise requests.HTTPError(response=response)
                response.raise_for_status()
                return response
            except requests.HTTPError as exc:
                if attempt == max_retries:
                    raise
                logger.warning(
                    "OpenFDA HTTP error (attempt %d/%d): %s — retrying in %.1fs",
                    attempt + 1,
                    max_retries,
                    exc,
                    delay,
                )
                time.sleep(delay)
                delay *= 2
            except requests.RequestException as exc:
                if attempt == max_retries:
                    raise
                logger.warning("OpenFDA request error: %s — retrying", exc)
                time.sleep(delay)
                delay *= 2

        raise requests.HTTPError("Exhausted retries for OpenFDA request")


def _ingest_default_drugs() -> list[dict[str, Any]]:
    drugs = [
        "pembrolizumab",
        "semaglutide",
        "ibrutinib",
        "venetoclax",
        "nivolumab",
    ]
    fetcher = OpenFDAFetcher()
    results: list[dict[str, Any]] = []

    for drug in drugs:
        logger.info("Fetching OpenFDA: %s", drug)
        docs = fetcher.fetch_all(drug)
        results.extend(docs)
        time.sleep(0.5)

    logger.info("OpenFDA ingestion complete — %d documents", len(results))
    return results


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    docs = _ingest_default_drugs()
    print(json.dumps(docs[:2], indent=2, default=str))
    print(f"\nTotal fetched: {len(docs)}")
