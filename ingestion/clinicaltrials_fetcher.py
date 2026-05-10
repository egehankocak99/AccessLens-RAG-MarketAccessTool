from __future__ import annotations

import logging
import time
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


CT_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
PAGE_SIZE = 20
RELEVANT_STATUSES = ["COMPLETED", "ACTIVE_NOT_RECRUITING", "RECRUITING"]


class ClinicalTrialsFetcher:
    def __init__(self, page_size: int = PAGE_SIZE) -> None:
        self.page_size = page_size
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AccessLens/1.0"})

    def fetch(self, query: str) -> list[dict[str, Any]]:
        params = self._build_params(query)
        raw_studies = self._paginate(params)
        parsed = [self._parse_study(s) for s in raw_studies]
        # Drop records missing both title and conditions
        return [p for p in parsed if p.get("title") or p.get("conditions")]

    def _build_params(self, query: str) -> dict[str, Any]:
        # ClinicalTrials API rejects very long query strings with 400; truncate to safe length
        safe_query = query[:200]
        return {
            "query.term": safe_query,
            "filter.geo": "distance(51.5,10,3000km)",
            "filter.overallStatus": "|".join(RELEVANT_STATUSES),
            "pageSize": self.page_size,
            "format": "json",
            "fields": (
                "NCTId,BriefTitle,OfficialTitle,Condition,InterventionName,"
                "Phase,StartDate,LeadSponsorName,OverallStatus,"
                "BriefSummary,PrimaryOutcomeMeasure"
            ),
        }

    def _paginate(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        studies: list[dict[str, Any]] = []
        next_token: str | None = None

        while True:
            if next_token:
                params["pageToken"] = next_token

            response = self._get_with_backoff(CT_BASE_URL, params)
            data = response.json()
            studies.extend(data.get("studies", []))
            next_token = data.get("nextPageToken")

            if not next_token or len(studies) >= self.page_size:
                break

            time.sleep(0.5)

        return studies[: self.page_size]

    def _parse_study(self, study: dict[str, Any]) -> dict[str, Any]:
        proto = study.get("protocolSection", {})
        id_mod = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        conditions_mod = proto.get("conditionsModule", {})
        arms_mod = proto.get("armsInterventionsModule", {})
        design_mod = proto.get("designModule", {})
        desc_mod = proto.get("descriptionModule", {})
        sponsor_mod = proto.get("sponsorCollaboratorsModule", {})

        nct_id: str = id_mod.get("nctId", "")
        title: str = id_mod.get("briefTitle", "") or id_mod.get("officialTitle", "")
        conditions: list[str] = conditions_mod.get("conditions", [])

        interventions: list[str] = [
            iv.get("name", "")
            for iv in arms_mod.get("interventions", [])
            if iv.get("name")
        ]

        phases: list[str] = design_mod.get("phases", [])
        phase: str = ", ".join(phases) if phases else ""

        start_date_struct = status_mod.get("startDateStruct", {})
        start_date: str = start_date_struct.get("date", "")

        sponsor: str = sponsor_mod.get("leadSponsor", {}).get("name", "")
        status: str = status_mod.get("overallStatus", "")
        brief_summary: str = desc_mod.get("briefSummary", "")

        return {
            "nct_id": nct_id,
            "title": title,
            "conditions": conditions,
            "interventions": interventions,
            "phase": phase,
            "start_date": start_date,
            "sponsor": sponsor,
            "status": status,
            "brief_summary": brief_summary,
            "source": "clinicaltrials",
        }

    def _get_with_backoff(
        self,
        url: str,
        params: dict[str, Any],
        max_retries: int = 4,
        base_delay: float = 1.0,
    ) -> requests.Response:
        delay = base_delay
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=30)
                if response.status_code == 429 or response.status_code >= 500:
                    raise requests.HTTPError(response=response)
                response.raise_for_status()
                return response
            except requests.HTTPError as exc:
                if attempt == max_retries:
                    raise
                logger.warning(
                    "ClinicalTrials HTTP error (attempt %d/%d): %s — retrying in %.1fs",
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
                logger.warning("ClinicalTrials request error: %s — retrying", exc)
                time.sleep(delay)
                delay *= 2

        raise requests.HTTPError("Exhausted retries for ClinicalTrials request")


def _ingest_default_queries() -> list[dict[str, Any]]:
    queries = [
        "oncology immunotherapy Europe",
        "NASH non-alcoholic steatohepatitis treatment",
        "GLP-1 receptor agonist obesity",
        "rare disease orphan drug EU",
        "cardiovascular outcomes Europe randomized",
    ]
    fetcher = ClinicalTrialsFetcher()
    results: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for q in queries:
        logger.info("Fetching ClinicalTrials: %s", q)
        studies = fetcher.fetch(q)
        for study in studies:
            nct = study.get("nct_id", "")
            if nct and nct not in seen_ids:
                seen_ids.add(nct)
                results.append(study)
        time.sleep(0.5)

    logger.info("ClinicalTrials ingestion complete — %d unique studies", len(results))
    return results


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    docs = _ingest_default_queries()
    print(json.dumps(docs[:2], indent=2))
    print(f"\nTotal fetched: {len(docs)}")
