from __future__ import annotations

import logging
from typing import Any

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_TOP_N = 5
MAX_LENGTH = 512


class CrossEncoderReranker:
    def __init__(self, model_name: str = CROSS_ENCODER_MODEL, top_n: int = DEFAULT_TOP_N) -> None:
        self.model_name = model_name
        self.top_n = top_n
        self._model: CrossEncoder | None = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            logger.info("Loading cross-encoder reranker: %s", self.model_name)
            self._model = CrossEncoder(self.model_name, max_length=MAX_LENGTH)
        return self._model

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        top_n: int | None = None,
    ) -> list[dict[str, Any]]:
        n = top_n if top_n is not None else self.top_n
        if not candidates:
            return []

        pairs = [(query, c.get("text", "")) for c in candidates]
        try:
            scores = self.model.predict(pairs, show_progress_bar=False)
        except Exception as exc:
            logger.error("Cross-encoder scoring failed: %s", exc)
            return candidates[:n]

        scored = sorted(zip(scores, candidates), key=lambda x: float(x[0]), reverse=True)

        results = []
        for score, chunk in scored[:n]:
            enriched = dict(chunk)
            enriched["rerank_score"] = float(score)
            results.append(enriched)

        logger.info(
            "Reranked %d candidates → top %d (best score: %.4f)",
            len(candidates),
            len(results),
            results[0]["rerank_score"] if results else 0.0,
        )
        return results
