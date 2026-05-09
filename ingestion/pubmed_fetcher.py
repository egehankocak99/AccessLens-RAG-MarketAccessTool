from __future__ import annotations

import logging
import os
import time
import xml.etree.ElementTree as ET
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
RETMAX = 20
EU_FILTER = '(European[tiab] OR EMA[tiab] OR CHMP[tiab] OR "European Medicines Agency"[tiab])'
NCBI_EMAIL = os.getenv("NCBI_EMAIL", "accesslens@example.com")


class PubMedFetcher:
    def __init__(self, email: str | None = None, retmax: int = RETMAX) -> None:
        self.email = email or NCBI_EMAIL
        self.retmax = retmax
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AccessLens/1.0 (contact: {})".format(self.email)})

    def fetch(self, query: str) -> list[dict[str, Any]]:
        eu_query = f"({query}) AND {EU_FILTER}"
        pmids = self._search(eu_query)
        if not pmids:
            logger.warning("PubMed: no results for query '%s'", query)
            return []
        return self._fetch_details(pmids)

    def _search(self, query: str) -> list[str]:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": self.retmax,
            "retmode": "json",
            "email": self.email,
        }
        response = self._get_with_backoff(ESEARCH_URL, params)
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])

    def _fetch_details(self, pmids: list[str]) -> list[dict[str, Any]]:
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "rettype": "abstract",
            "retmode": "xml",
            "email": self.email,
        }
        response = self._get_with_backoff(EFETCH_URL, params)
        return self._parse_xml(response.text)

    def _parse_xml(self, xml_text: str) -> list[dict[str, Any]]:
        articles: list[dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            logger.error("PubMed XML parse error: %s", exc)
            return articles

        for article in root.findall(".//PubmedArticle"):
            try:
                parsed = self._parse_article(article)
                if parsed["title"] or parsed["abstract"]:
                    articles.append(parsed)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping malformed article: %s", exc)

        return articles

    def _parse_article(self, article: ET.Element) -> dict[str, Any]:
        medline = article.find("MedlineCitation")
        if medline is None:
            return {}

        pmid_el = medline.find("PMID")
        pmid = pmid_el.text if pmid_el is not None else ""
        art = medline.find("Article")
        title_el = art.find("ArticleTitle") if art is not None else None
        title = "".join(title_el.itertext()) if title_el is not None else ""
        abstract_sections: list[str] = []
        abstract_el = art.find("Abstract") if art is not None else None
        if abstract_el is not None:
            for text_el in abstract_el.findall("AbstractText"):
                label = text_el.get("Label", "")
                content = "".join(text_el.itertext())
                if label:
                    abstract_sections.append(f"{label}: {content}")
                else:
                    abstract_sections.append(content)
        abstract = " ".join(abstract_sections)

        authors: list[str] = []
        author_list = art.find("AuthorList") if art is not None else None
        if author_list is not None:
            for author in author_list.findall("Author"):
                last = author.findtext("LastName", "")
                fore = author.findtext("ForeName", "")
                if last:
                    authors.append(f"{last} {fore}".strip())

        pub_date = ""
        journal = art.find("Journal") if art is not None else None
        if journal is not None:
            pub_info = journal.find("JournalIssue/PubDate")
            if pub_info is not None:
                year = pub_info.findtext("Year", "")
                month = pub_info.findtext("Month", "")
                pub_date = f"{year}-{month}" if month else year

        return {
            "title": title.strip(),
            "abstract": abstract.strip(),
            "authors": authors,
            "pub_date": pub_date,
            "pmid": pmid,
            "source": "pubmed",
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
                    "PubMed HTTP error (attempt %d/%d): %s — retrying in %.1fs",
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
                logger.warning("PubMed request error: %s — retrying", exc)
                time.sleep(delay)
                delay *= 2

        raise requests.HTTPError("Exhausted retries for PubMed request")


def _ingest_default_queries() -> list[dict[str, Any]]:
    queries = [
        "HTA reimbursement oncology Europe",
        "AMNOG added benefit assessment Germany",
        "NICE technology appraisal rare disease",
        "GLP-1 agonist safety EU regulatory",
        "NASH treatment clinical trial Europe",
    ]
    fetcher = PubMedFetcher()
    results: list[dict[str, Any]] = []
    seen_pmids: set[str] = set()

    for q in queries:
        logger.info("Fetching PubMed: %s", q)
        articles = fetcher.fetch(q)
        for art in articles:
            if art.get("pmid") and art["pmid"] not in seen_pmids:
                seen_pmids.add(art["pmid"])
                results.append(art)
        time.sleep(0.4)

    logger.info("PubMed ingestion complete — %d unique articles", len(results))
    return results


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    docs = _ingest_default_queries()
    print(json.dumps(docs[:2], indent=2))
    print(f"\nTotal fetched: {len(docs)}")
