import json
import types
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

class TestReciprocalRankFusion:

    def _make_result(self, chunk_id: str, score: float = 1.0) -> dict:
        return {"chunk_id": chunk_id, "text": "text", "score": score}

    def test_rrf_top_result_is_consistent_winner(self):
        from retrieval.hybrid_search import HybridSearcher

        # chunk_id "A" appears at rank 0 in both lists — should win
        semantic = [self._make_result("A"), self._make_result("B"), self._make_result("C")]
        bm25     = [self._make_result("A"), self._make_result("D"), self._make_result("E")]

        fused = HybridSearcher._reciprocal_rank_fusion([semantic, bm25])
        assert fused[0]["chunk_id"] == "A"

    def test_rrf_returns_union_of_results(self):
        from retrieval.hybrid_search import HybridSearcher

        semantic = [{"chunk_id": "X", "text": "t"}, {"chunk_id": "Y", "text": "t"}]
        bm25     = [{"chunk_id": "Y", "text": "t"}, {"chunk_id": "Z", "text": "t"}]

        fused = HybridSearcher._reciprocal_rank_fusion([semantic, bm25])
        ids = {r["chunk_id"] for r in fused}
        assert ids == {"X", "Y", "Z"}

    def test_rrf_empty_lists_return_empty(self):
        from retrieval.hybrid_search import HybridSearcher

        assert HybridSearcher._reciprocal_rank_fusion([[], []]) == []

    def test_rrf_single_list_preserves_order(self):
        from retrieval.hybrid_search import HybridSearcher

        ranked = [
            {"chunk_id": "first",  "text": "t"},
            {"chunk_id": "second", "text": "t"},
            {"chunk_id": "third",  "text": "t"},
        ]
        fused = HybridSearcher._reciprocal_rank_fusion([ranked])
        assert [r["chunk_id"] for r in fused] == ["first", "second", "third"]

    def test_rrf_score_decreases_with_rank(self):
        from retrieval.hybrid_search import HybridSearcher

        ranked = [{"chunk_id": f"id{i}", "text": "t"} for i in range(5)]
        fused = HybridSearcher._reciprocal_rank_fusion([ranked])
        scores = [r.get("score", 0) for r in fused]
        assert scores == sorted(scores, reverse=True), "RRF scores should be descending"

    def test_rrf_k_parameter_effect(self):
        from retrieval.hybrid_search import HybridSearcher

        ranked = [{"chunk_id": "top", "text": "t"}, {"chunk_id": "bottom", "text": "t"}]
        fused_low  = HybridSearcher._reciprocal_rank_fusion([ranked], k=1)
        fused_high = HybridSearcher._reciprocal_rank_fusion([ranked], k=1000)

        score_diff_low  = fused_low[0].get("score", 0)  - fused_low[1].get("score", 0)
        score_diff_high = fused_high[0].get("score", 0) - fused_high[1].get("score", 0)

        assert score_diff_low > score_diff_high, "Lower k should create larger score gaps"


class TestBM25Integration:

    def _make_chunk(self, chunk_id: str, text: str) -> dict:
        return {
            "chunk_id": chunk_id,
            "text": text,
            "score": 1.0,
            "source": "pubmed",
            "doc_type": "abstract",
            "agency": "OTHER",
            "country": "EU",
            "date": "2024-01-01",
        }

    def _build_searcher_with_corpus(self, corpus: list[dict]):
        from retrieval.hybrid_search import HybridSearcher

        mock_store = MagicMock()
        mock_store.scroll_all.return_value = corpus
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.0] * 768

        searcher = HybridSearcher.__new__(HybridSearcher)
        searcher.store = mock_store
        searcher.embedder = mock_embedder
        searcher._bm25_index = None
        searcher._bm25_corpus = None
        return searcher

    def test_bm25_ranks_relevant_doc_first(self):
        from retrieval.hybrid_search import HybridSearcher

        corpus = [
            self._make_chunk("doc_a", "G-BA requires comparative clinical data for oncology"),
            self._make_chunk("doc_b", "Weather forecast for Berlin in summer"),
            self._make_chunk("doc_c", "NICE appraisal process for cancer drugs"),
        ]
        searcher = self._build_searcher_with_corpus(corpus)
        searcher._ensure_bm25_index()

        results = searcher._bm25_search("G-BA oncology evidence requirement")
        if results:
            assert results[0]["chunk_id"] == "doc_a"

    def test_bm25_index_built_once(self):
        from retrieval.hybrid_search import HybridSearcher

        corpus = [self._make_chunk("x", "some text")]
        searcher = self._build_searcher_with_corpus(corpus)
        searcher._ensure_bm25_index()
        first_index = id(searcher._bm25_index)
        searcher._ensure_bm25_index()  # Second call
        assert id(searcher._bm25_index) == first_index, "BM25 index should not be rebuilt"

    def test_bm25_empty_corpus_returns_empty(self):
        from retrieval.hybrid_search import HybridSearcher

        searcher = self._build_searcher_with_corpus([])
        searcher._ensure_bm25_index()
        results = searcher._bm25_search("anything")
        assert results == []



class TestQueryRewriter:

    def _make_rewriter(self, llm_response: str | None, raises: bool = False):
        from retrieval.query_rewriter import QueryRewriter, MODEL, MAX_TOKENS

        mock_client = MagicMock()
        if raises:
            mock_client.messages.create.side_effect = Exception("API error")
        else:
            mock_msg = MagicMock()
            mock_msg.content = [MagicMock(text=llm_response)]
            mock_client.messages.create.return_value = mock_msg

        rewriter = QueryRewriter.__new__(QueryRewriter)
        rewriter.client = mock_client
        rewriter.model = MODEL
        rewriter.max_tokens = MAX_TOKENS
        return rewriter

    def test_rewrite_returns_three_variants(self):
        payload = json.dumps([
            "What evidence does G-BA require for oncology benefit assessment?",
            "G-BA AMNOG oncology added benefit clinical evidence requirements",
            "European HTA evidence standards oncology drugs Germany",
        ])
        rewriter = self._make_rewriter(payload)
        variants = rewriter.rewrite("G-BA oncology evidence")
        assert len(variants) == 3

    def test_rewrite_strips_markdown_fences(self):
        payload = "```json\n[\"var1\", \"var2\", \"var3\"]\n```"
        rewriter = self._make_rewriter(payload)
        variants = rewriter.rewrite("test query")
        assert variants == ["var1", "var2", "var3"]

    def test_rewrite_falls_back_on_api_error(self):
        rewriter = self._make_rewriter(llm_response=None, raises=True)
        variants = rewriter.rewrite("HTA submission requirements")
        assert len(variants) >= 1
        assert all(isinstance(v, str) and v.strip() for v in variants)

    def test_fallback_includes_original_query(self):
        rewriter = self._make_rewriter(llm_response=None, raises=True)
        query = "NICE cost-effectiveness threshold"
        variants = rewriter.rewrite(query)
        assert any(query.lower() in v.lower() for v in variants), (
            "Fallback should include the original query"
        )

    def test_parse_json_list_handles_plain_array(self):
        from retrieval.query_rewriter import QueryRewriter

        rewriter = QueryRewriter.__new__(QueryRewriter)
        result = rewriter._parse_json_list('["a", "b", "c"]')
        assert result == ["a", "b", "c"]

    def test_parse_json_list_handles_fenced_json(self):
        from retrieval.query_rewriter import QueryRewriter

        rewriter = QueryRewriter.__new__(QueryRewriter)
        result = rewriter._parse_json_list("```json\n[\"x\", \"y\"]\n```")
        assert result == ["x", "y"]

    def test_parse_json_list_returns_empty_on_junk(self):
        from retrieval.query_rewriter import QueryRewriter

        rewriter = QueryRewriter.__new__(QueryRewriter)
        result = rewriter._parse_json_list("this is not json")
        assert result == []



class TestCrossEncoderReranker:

    def _make_candidates(self, n: int) -> list[dict]:
        return [
            {"chunk_id": f"c{i}", "text": f"Document {i} about HTA submission", "score": 0.5}
            for i in range(n)
        ]

    def _mock_reranker(self, scores: list[float]):
        from retrieval.reranker import CrossEncoderReranker

        mock_model = MagicMock()
        mock_model.predict.return_value = scores

        reranker = CrossEncoderReranker.__new__(CrossEncoderReranker)
        reranker._model = mock_model
        return reranker

    def test_rerank_returns_top_n(self):
        candidates = self._make_candidates(10)
        scores = list(range(10))  # ascending — last one is best
        reranker = self._mock_reranker(scores)

        result = reranker.rerank("HTA evidence requirements", candidates, top_n=3)
        assert len(result) == 3

    def test_rerank_orders_by_score_descending(self):
        import random
        candidates = self._make_candidates(5)
        scores = [0.2, 0.9, 0.1, 0.8, 0.5]
        reranker = self._mock_reranker(scores)

        result = reranker.rerank("query", candidates, top_n=5)
        rerank_scores = [r["rerank_score"] for r in result]
        assert rerank_scores == sorted(rerank_scores, reverse=True)

    def test_rerank_adds_rerank_score_field(self):
        candidates = self._make_candidates(3)
        reranker = self._mock_reranker([0.4, 0.7, 0.2])

        result = reranker.rerank("query", candidates, top_n=3)
        for r in result:
            assert "rerank_score" in r

    def test_rerank_top_n_capped_at_candidates(self):
        candidates = self._make_candidates(2)
        reranker = self._mock_reranker([0.5, 0.8])

        result = reranker.rerank("query", candidates, top_n=100)
        assert len(result) == 2

    def test_rerank_empty_candidates_returns_empty(self):
        from retrieval.reranker import CrossEncoderReranker

        mock_model = MagicMock()
        mock_model.predict.return_value = []

        reranker = CrossEncoderReranker.__new__(CrossEncoderReranker)
        reranker._model = mock_model

        result = reranker.rerank("query", [], top_n=5)
        assert result == []
