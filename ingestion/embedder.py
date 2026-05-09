from __future__ import annotations

import logging
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-base-en-v1.5"
BATCH_SIZE = 32
EMBEDDING_DIM = 768


class DocumentEmbedder:
    def __init__(self, model_name: str = MODEL_NAME, batch_size: int = BATCH_SIZE) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_chunks(self, chunks: list[dict[str, Any]]) -> list[tuple[dict[str, Any], list[float]]]:
        if not chunks:
            return []

        texts = [c["text"] for c in chunks]
        embeddings = self._batch_encode(texts)

        return [(chunk, emb.tolist()) for chunk, emb in zip(chunks, embeddings)]

    def embed_query(self, query: str) -> list[float]:
        instruction = "Represent this sentence for searching relevant passages: "
        embedding = self.model.encode(
            instruction + query,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self._batch_encode(texts)
        return [e.tolist() for e in embeddings]

    def _batch_encode(self, texts: list[str]) -> np.ndarray:
        all_embeddings: list[np.ndarray] = []
        total = len(texts)
        for start in range(0, total, self.batch_size):
            batch = texts[start : start + self.batch_size]
            batch_embeddings = self.model.encode(
                batch,
                batch_size=len(batch),
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            all_embeddings.append(batch_embeddings)
            logger.debug("Embedded batch %d–%d / %d", start + 1, min(start + self.batch_size, total), total)
        return np.vstack(all_embeddings) if all_embeddings else np.empty((0, EMBEDDING_DIM))
