from __future__ import annotations

import logging
import os
import uuid
from typing import Any, Optional

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from vectorstore.schema import ChunkMetadata

load_dotenv()

logger = logging.getLogger(__name__)

COLLECTION_NAME = "accesslens"
VECTOR_SIZE = 768
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")


class QdrantStore:
    def __init__(self, path: str = QDRANT_PATH, collection_name: str = COLLECTION_NAME) -> None:
        self.path = path
        self.collection_name = collection_name
        self.client = QdrantClient(path=path)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        existing = {c.name for c in self.client.get_collections().collections}
        if self.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection '%s'", self.collection_name)
        else:
            logger.debug("Using existing Qdrant collection '%s'", self.collection_name)

    def delete_collection(self) -> None:
        self.client.delete_collection(self.collection_name)
        logger.warning("Deleted Qdrant collection '%s'", self.collection_name)
        self._ensure_collection()

    def get_count(self) -> int:
        info = self.client.get_collection(self.collection_name)
        return info.points_count or 0

    def upsert_chunks(self, embedded_chunks: list[tuple[dict[str, Any], list[float]]]) -> int:
        if not embedded_chunks:
            return 0

        points: list[qdrant_models.PointStruct] = []
        for chunk_dict, embedding in embedded_chunks:
            payload = self._build_payload(chunk_dict)
            point_id = self._chunk_id_to_uuid(chunk_dict.get("chunk_id", ""))
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        batch_size = 100
        upserted = 0
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
                wait=True,
            )
            upserted += len(batch)
            logger.debug("Upserted %d/%d points", upserted, len(points))

        logger.info("Upserted %d chunks into '%s'", upserted, self.collection_name)
        return upserted

    def search(self, query_vector: list[float], top_k: int = 20, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        qdrant_filter = self._build_filter(filters) if filters else None

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
            with_vectors=False,
        )

        results: list[dict[str, Any]] = []
        for hit in response.points:
            payload = hit.payload or {}
            results.append(
                {
                    **payload,
                    "score": hit.score,
                    "point_id": str(hit.id),
                }
            )

        return results

    def scroll_all(self, batch_size: int = 256) -> list[dict[str, Any]]:
        all_payloads: list[dict[str, Any]] = []
        offset = None

        while True:
            records, offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            for record in records:
                if record.payload:
                    all_payloads.append({**record.payload, "point_id": str(record.id)})
            if offset is None:
                break

        return all_payloads

    @staticmethod
    def _build_payload(chunk_dict: dict[str, Any]) -> dict[str, Any]:
        try:
            meta = ChunkMetadata(**chunk_dict)
            return meta.model_dump()
        except Exception as exc:  # noqa: BLE001
            logger.debug("ChunkMetadata validation warning: %s — using raw dict", exc)
            return {k: v for k, v in chunk_dict.items() if isinstance(v, (str, int, float, bool, list)) or v is None}

    @staticmethod
    def _chunk_id_to_uuid(chunk_id: str) -> str:
        if not chunk_id:
            return str(uuid.uuid4())
        return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))

    @staticmethod
    def _build_filter(filters: dict[str, Any]) -> qdrant_models.Filter:
        conditions: list[qdrant_models.FieldCondition] = []
        for key, value in filters.items():
            if value is not None:
                conditions.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchValue(value=value),
                    )
                )
        return qdrant_models.Filter(must=conditions)
