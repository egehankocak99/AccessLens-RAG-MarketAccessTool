from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request

from api.models import QueryFilters, QueryRequest, QueryResponse, SourceDocument, UsageStats
from generation.generator import AnswerGenerator
from ingestion.clinicaltrials_fetcher import ClinicalTrialsFetcher
from ingestion.pubmed_fetcher import PubMedFetcher

logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])

_live_executor = ThreadPoolExecutor(max_workers=4)


@router.post("/query", response_model=QueryResponse, summary="Execute EU Market Access RAG query")
async def query_endpoint(body: QueryRequest, request: Request) -> QueryResponse:
    start_time = time.monotonic()

    state = request.app.state
    rewriter = getattr(state, "query_rewriter", None)
    searcher = getattr(state, "hybrid_searcher", None)
    reranker = getattr(state, "reranker", None)
    chunker = getattr(state, "chunker", None)

    if any(c is None for c in [rewriter, searcher, reranker, chunker]):
        raise HTTPException(
            status_code=503,
            detail="AccessLens pipeline components are not fully initialised. Check server logs.",
        )

    # Use caller-supplied API key or fall back to server .env key
    generator = AnswerGenerator(api_key=body.anthropic_api_key or None)

    try:
        return await _run_pipeline(
            body=body,
            rewriter=rewriter,
            searcher=searcher,
            reranker=reranker,
            generator=generator,
            chunker=chunker,
            start_time=start_time,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error in /query pipeline: %s", exc)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}") from exc


async def _run_pipeline(
    body: QueryRequest,
    rewriter: Any,
    searcher: Any,
    reranker: Any,
    generator: Any,
    chunker: Any,
    start_time: float,
) -> QueryResponse:
    logger.info("[pipeline] Rewriting query: '%s'", body.question[:80])
    try:
        query_variants = rewriter.rewrite(body.question)
    except Exception as exc:
        logger.warning("Query rewriting failed, using original: %s", exc)
        query_variants = [body.question]

    logger.info("[pipeline] Query variants: %s", query_variants)

    # Live ingest: fetch fresh documents from PubMed + ClinicalTrials in parallel
    logger.info("[pipeline] Live ingesting fresh documents for query...")
    await _live_ingest(query_variants, searcher, chunker)

    filters = _build_filters(body.filters)
    logger.info("[pipeline] Running hybrid search (top_k=%d)", body.top_k * 4)
    try:
        search_results = searcher.search(
            queries=query_variants,
            top_k=body.top_k * 4,
            filters=filters if filters else None,
        )
    except Exception as exc:
        logger.error("Hybrid search failed: %s", exc)
        search_results = []

    if not search_results:
        logger.warning("No search results found — returning empty answer")
        return QueryResponse(
            answer=(
                "No relevant documents were found for your query. "
                "The live fetch from PubMed and ClinicalTrials.gov returned no matching results. "
                "Try rephrasing your question with different terms."
            ),
            sources=[],
            faithfulness_score=0.0,
            latency_ms=int((time.monotonic() - start_time) * 1000),
            model_used="",
            query_variants=query_variants,
        )

    logger.info("[pipeline] Reranking %d candidates → top %d", len(search_results), body.top_k)
    try:
        reranked = reranker.rerank(
            query=body.question,
            candidates=search_results,
            top_n=body.top_k,
        )
    except Exception as exc:
        logger.warning("Reranking failed, using unranked results: %s", exc)
        reranked = search_results[: body.top_k]

    logger.info("[pipeline] Generating answer with %d context chunks", len(reranked))
    generation_result = generator.generate(
        question=body.question,
        chunks=reranked,
    )

    total_latency_ms = int((time.monotonic() - start_time) * 1000)
    sources = _build_source_documents(reranked, generation_result.get("citations", []))
    faithfulness = _estimate_faithfulness(
        answer=generation_result["answer"],
        chunks=reranked,
    )

    usage = generation_result.get("token_usage", {})
    return QueryResponse(
        answer=generation_result["answer"],
        sources=sources,
        faithfulness_score=faithfulness,
        latency_ms=total_latency_ms,
        model_used=generation_result.get("model_used", ""),
        token_usage=UsageStats(
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
        ),
        query_variants=query_variants,
    )


async def _live_ingest(query_variants: list[str], searcher: Any, chunker: Any) -> None:
    loop = asyncio.get_event_loop()

    # Use the first two query variants as search terms (most specific)
    search_terms = query_variants[:2]

    def _fetch_and_upsert() -> int:
        pubmed = PubMedFetcher()
        ct = ClinicalTrialsFetcher()
        docs: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for term in search_terms:
            try:
                for article in pubmed.fetch(term):
                    pid = article.get("pmid", "")
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        docs.append(article)
            except Exception as exc:
                logger.warning("Live PubMed fetch failed for '%s': %s", term[:50], exc)

            try:
                for study in ct.fetch(term):
                    nct = study.get("nct_id", "")
                    if nct and nct not in seen_ids:
                        seen_ids.add(nct)
                        docs.append(study)
            except Exception as exc:
                logger.warning("Live ClinicalTrials fetch failed for '%s': %s", term[:50], exc)

        if not docs:
            return 0

        chunks = chunker.chunk_documents(docs)
        embedded = searcher.embedder.embed_chunks(chunks)
        upserted = searcher.store.upsert_chunks(embedded)

        # Reset BM25 index so it rebuilds with new docs included
        searcher._bm25_index = None
        searcher._bm25_corpus = []

        logger.info("[live_ingest] Fetched %d docs → %d chunks → %d upserted", len(docs), len(chunks), upserted)
        return upserted

    try:
        upserted = await loop.run_in_executor(_live_executor, _fetch_and_upsert)
        logger.info("[live_ingest] Complete — %d new/updated vectors", upserted)
    except Exception as exc:
        logger.warning("[live_ingest] Failed (continuing with existing index): %s", exc)


def _build_filters(filters: Optional[QueryFilters]) -> dict[str, Any]:
    if filters is None:
        return {}
    result: dict[str, Any] = {}
    if filters.agency:
        result["agency"] = filters.agency
    if filters.country:
        result["country"] = filters.country
    if filters.doc_type:
        result["doc_type"] = filters.doc_type
    return result


def _build_source_documents(chunks: list[dict[str, Any]], citations: list[dict[str, Any]]) -> list[SourceDocument]:
    citation_map: dict[int, dict[str, Any]] = {c["citation_number"]: c for c in citations}

    sources: list[SourceDocument] = []
    for idx, chunk in enumerate(chunks, start=1):
        cit = citation_map.get(idx, {})
        sources.append(
            SourceDocument(
                citation_number=idx,
                text=chunk.get("text", "")[:500],
                title=chunk.get("title") or chunk.get("drug_name") or cit.get("title"),
                source=chunk.get("source", "unknown"),
                doc_type=chunk.get("doc_type", ""),
                agency=chunk.get("agency", "OTHER"),
                date=chunk.get("date", ""),
                url=cit.get("url"),
                pmid=chunk.get("pmid"),
                nct_id=chunk.get("nct_id"),
                relevance_score=chunk.get("rerank_score") or chunk.get("score") or 0.0,
            )
        )

    return sources


def _estimate_faithfulness(answer: str, chunks: list[dict[str, Any]]) -> float:
    import re

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
    if not sentences:
        return 0.0

    cited = sum(1 for s in sentences if re.search(r"\[\d+\]", s))
    return round(cited / len(sentences), 4)


router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse, summary="Execute EU Market Access RAG query")
async def query_endpoint(body: QueryRequest, request: Request) -> QueryResponse:
    start_time = time.monotonic()


    state = request.app.state
    rewriter = getattr(state, "query_rewriter", None)
    searcher = getattr(state, "hybrid_searcher", None)
    reranker = getattr(state, "reranker", None)
    generator = getattr(state, "generator", None)

    if any(c is None for c in [rewriter, searcher, reranker, generator]):
        raise HTTPException(
            status_code=503,
            detail="AccessLens pipeline components are not fully initialised. Check server logs.",
        )

    try:
        return await _run_pipeline(
            body=body,
            rewriter=rewriter,
            searcher=searcher,
            reranker=reranker,
            generator=generator,
            start_time=start_time,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled error in /query pipeline: %s", exc)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}") from exc

