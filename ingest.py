from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("ACCESSLENS_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

from ingestion.pubmed_fetcher import PubMedFetcher
from ingestion.clinicaltrials_fetcher import ClinicalTrialsFetcher
from ingestion.openfda_fetcher import OpenFDAFetcher
from ingestion.chunker import DocumentChunker
from ingestion.embedder import DocumentEmbedder
from vectorstore.qdrant_store import QdrantStore


def run() -> None:
    qdrant_path = os.getenv("QDRANT_PATH", "./qdrant_data")
    store = QdrantStore(path=qdrant_path)
    chunker = DocumentChunker()
    embedder = DocumentEmbedder()

    sources = [
        ("PubMed",         _fetch_pubmed),
        ("ClinicalTrials", _fetch_clinicaltrials),
        ("OpenFDA",        _fetch_openfda),
    ]

    total_upserted = 0
    for name, fetch_fn in sources:
        logger.info("=== Ingesting %s ===", name)
        docs = fetch_fn()
        logger.info("%s: fetched %d documents", name, len(docs))

        chunks = chunker.chunk_documents(docs)
        logger.info("%s: produced %d chunks", name, len(chunks))

        embedded = embedder.embed_chunks(chunks)
        logger.info("%s: embedded %d chunks", name, len(embedded))

        upserted = store.upsert_chunks(embedded)
        logger.info("%s: upserted %d vectors into Qdrant", name, upserted)
        total_upserted += upserted

    logger.info("Ingestion complete. Total vectors in store: %d", store.get_count())


def _fetch_pubmed() -> list[dict]:
    import time
    queries = [
        "HTA reimbursement oncology Europe",
        "AMNOG added benefit assessment Germany",
        "NICE technology appraisal rare disease",
        "GLP-1 agonist safety EU regulatory",
        "NASH treatment clinical trial Europe",
    ]
    fetcher = PubMedFetcher()
    results: list[dict] = []
    seen: set[str] = set()
    for q in queries:
        logger.info("PubMed query: %s", q)
        for art in fetcher.fetch(q):
            pmid = art.get("pmid", "")
            if pmid and pmid not in seen:
                seen.add(pmid)
                results.append(art)
        time.sleep(0.4)
    return results


def _fetch_clinicaltrials() -> list[dict]:
    import time
    queries = [
        "oncology immunotherapy Europe",
        "NASH non-alcoholic steatohepatitis treatment",
        "GLP-1 receptor agonist obesity",
        "rare disease orphan drug EU",
        "cardiovascular outcomes Europe randomized",
    ]
    fetcher = ClinicalTrialsFetcher()
    results: list[dict] = []
    seen: set[str] = set()
    for q in queries:
        logger.info("ClinicalTrials query: %s", q)
        for study in fetcher.fetch(q):
            nct = study.get("nct_id", "")
            if nct and nct not in seen:
                seen.add(nct)
                results.append(study)
        time.sleep(0.5)
    return results


def _fetch_openfda() -> list[dict]:
    drugs = ["pembrolizumab", "semaglutide", "ibrutinib", "nivolumab", "dupilumab"]
    fetcher = OpenFDAFetcher()
    results: list[dict] = []
    seen: set[str] = set()
    for drug in drugs:
        logger.info("OpenFDA drug: %s", drug)
        for label in fetcher.fetch(drug):
            name = label.get("drug_name", drug)
            if name not in seen:
                seen.add(name)
                results.append(label)
    return results


if __name__ == "__main__":
    run()
