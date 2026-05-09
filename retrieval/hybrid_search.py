from __future__ import annotations

import logging
from typing import Any, Optional

from rank_bm25 import BM25Okapi

from ingestion.embedder import DocumentEmbedder
from vectorstore.qdrant_store import QdrantStore

logger = logging.getLogger(__name__)

TOP_K_SEMANTIC = 20
TOP_K_BM25 = 20
TOP_K_FUSED = 10
RRF_K = 60


class HybridSearcher:
    def __init__(self, store: QdrantStore, embedder: DocumentEmbedder) -> None:
        self.store = store
        self.embedder = embedder
        self._bm25_index: Optional[BM25Okapi] = None
        self._bm25_corpus: list[dict[str, Any]] = []

    def search(self, queries: list[str], top_k: int = TOP_K_FUSED, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        if not queries:
            return []

        self._ensure_bm25_index()

        all_semantic_lists: list[list[dict[str, Any]]] = []
        all_bm25_lists: list[list[dict[str, Any]]] = []

        for query in queries:
            sem_results = self._semantic_search(query, top_k=TOP_K_SEMANTIC, filters=filters)
            bm25_results = self._bm25_search(query, top_k=TOP_K_BM25)
            all_semantic_lists.append(sem_results)
            all_bm25_lists.append(bm25_results)
            logger.debug("Query '%s...' → semantic: %d, BM25: %d", query[:40], len(sem_results), len(bm25_results))

        fused = self._reciprocal_rank_fusion(all_semantic_lists + all_bm25_lists, top_k=top_k)
        logger.info("Hybrid search: %d query variants → %d fused results", len(queries), len(fused))
        return fused

    def _semantic_search(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        query_vector = self.embedder.embed_query(query)
        results = self.store.search(query_vector, top_k=top_k, filters=filters)
        for r in results:
            r["retrieval_method"] = "semantic"
        return results

    def _ensure_bm25_index(self) -> None:
        if self._bm25_index is not None:
            return

        logger.info("Building BM25 index from Qdrant collection...")
        all_chunks = self.store.scroll_all()

        if not all_chunks:
            logger.warning("BM25: Qdrant collection is empty — BM25 will return no results")
            self._bm25_corpus = []
            return

        self._bm25_corpus = all_chunks
        tokenised = [self._tokenize(c.get("text", "")) for c in all_chunks]
        self._bm25_index = BM25Okapi(tokenised)
        logger.info("BM25 index built over %d documents", len(all_chunks))

    def _bm25_search(self, query: str, top_k: int = TOP_K_BM25) -> list[dict[str, Any]]:
        if not self._bm25_corpus or self._bm25_index is None:
            return []

        tokenised_query = self._tokenize(query)
        scores = self._bm25_index.get_scores(tokenised_query)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results: list[dict[str, Any]] = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            chunk = dict(self._bm25_corpus[idx])
            chunk["score"] = float(scores[idx])
            chunk["retrieval_method"] = "bm25"
            results.append(chunk)

        return results

    @staticmethod
    def _reciprocal_rank_fusion(ranked_lists: list[list[dict[str, Any]]], top_k: int = TOP_K_FUSED, k: int = RRF_K) -> list[dict[str, Any]]:
        rrf_scores: dict[str, float] = {}
        chunk_map: dict[str, dict[str, Any]] = {}

        for ranked_list in ranked_lists:
            for rank, result in enumerate(ranked_list, start=1):
                doc_key = result.get("chunk_id") or result.get("point_id") or result.get("text", "")[:64]
                rrf_scores[doc_key] = rrf_scores.get(doc_key, 0.0) + 1.0 / (k + rank)
                if doc_key not in chunk_map:
                    chunk_map[doc_key] = result

        sorted_keys = sorted(rrf_scores, key=lambda k: rrf_scores[k], reverse=True)
        fused: list[dict[str, Any]] = []
        for key in sorted_keys[:top_k]:
            chunk = dict(chunk_map[key])
            chunk["score"] = rrf_scores[key]
            chunk["retrieval_method"] = "hybrid_rrf"
            fused.append(chunk)

        return fused

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return text.lower().split() if text else [""]
