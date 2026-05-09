from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class QueryFilters(BaseModel):
    agency: Optional[str] = None
    country: Optional[str] = None
    doc_type: Optional[str] = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    filters: Optional[QueryFilters] = None
    anthropic_api_key: Optional[str] = None

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("question must not be blank")
        return stripped


class SourceDocument(BaseModel):
    citation_number: int
    text: str = ""
    title: Optional[str] = None
    source: str = "unknown"
    doc_type: str = ""
    agency: str = "OTHER"
    date: str = ""
    url: Optional[str] = None
    pmid: Optional[str] = None
    nct_id: Optional[str] = None
    relevance_score: float = 0.0


class UsageStats(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceDocument] = Field(default_factory=list)
    faithfulness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    latency_ms: int = 0
    model_used: str = ""
    token_usage: UsageStats = Field(default_factory=UsageStats)
    query_variants: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    qdrant_points: int = 0
    version: str = "1.0.0"
