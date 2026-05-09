from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from api.models import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check(request: Request) -> HealthResponse:
    qdrant_points = 0
    try:
        store = request.app.state.qdrant_store
        if store is not None:
            qdrant_points = store.get_count()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Health check: Qdrant count failed: %s", exc)

    return HealthResponse(
        status="ok",
        qdrant_points=qdrant_points,
        version="1.0.0",
    )
