from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(
    level=os.getenv("ACCESSLENS_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def _configure_langsmith() -> None:
    if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
        api_key = os.getenv("LANGCHAIN_API_KEY")
        if api_key:
            os.environ.setdefault("LANGCHAIN_PROJECT", "accesslens")
            logger.info("LangSmith tracing enabled (project: %s)", os.environ["LANGCHAIN_PROJECT"])
        else:
            logger.warning("LANGCHAIN_TRACING_V2=true but LANGCHAIN_API_KEY is not set — tracing disabled")


_configure_langsmith()

from ingestion.chunker import DocumentChunker
from ingestion.embedder import DocumentEmbedder
from generation.generator import AnswerGenerator
from retrieval.query_rewriter import QueryRewriter
from retrieval.hybrid_search import HybridSearcher
from retrieval.reranker import CrossEncoderReranker
from vectorstore.qdrant_store import QdrantStore

from api.routes import health as health_router
from api.routes import query as query_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("AccessLens API starting up...")

    qdrant_path = os.getenv("QDRANT_PATH", "./qdrant_data")
    logger.info("Initialising Qdrant store at: %s", qdrant_path)
    store = QdrantStore(path=qdrant_path)
    app.state.qdrant_store = store

    chunker = DocumentChunker()
    app.state.chunker = chunker

    vector_count = store.get_count()
    logger.info("Qdrant collection '%s': %d vectors indexed", store.collection_name, vector_count)

    if vector_count == 0:
        logger.warning(
            "Qdrant collection is empty. Run the ingestion pipeline to populate it:\n"
            "  python -m ingestion.pubmed_fetcher\n"
            "  python -m ingestion.clinicaltrials_fetcher\n"
            "  python -m ingestion.openfda_fetcher"
        )

    logger.info("Loading document embedder (BAAI/bge-base-en-v1.5)...")
    embedder = DocumentEmbedder()
    app.state.embedder = embedder

    searcher = HybridSearcher(store=store, embedder=embedder)
    app.state.hybrid_searcher = searcher

    reranker = CrossEncoderReranker()
    app.state.reranker = reranker

    rewriter = QueryRewriter()
    app.state.query_rewriter = rewriter

    generator = AnswerGenerator()
    app.state.generator = generator

    logger.info("AccessLens API ready — serving on http://0.0.0.0:8000")

    yield

    logger.info("AccessLens API shutting down...")



app = FastAPI(
    title="AccessLens API",
    description=(
        "EU Market Access Intelligence — production-grade RAG API for pharmaceutical "
        "and biotech Market Access teams. Retrieves and synthesises evidence from PubMed, "
        "ClinicalTrials.gov, and OpenFDA, grounded in EU agency (EMA, G-BA, HAS, NICE, AIFA, CBG) context."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


_cors_origins_raw = os.getenv(
    "ACCESSLENS_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500",
)
cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(health_router.router)
app.include_router(query_router.router)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "message": "AccessLens API v1.0.0 — visit /docs for the interactive API reference.",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
    }


def run() -> None:
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run()
