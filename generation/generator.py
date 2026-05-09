from __future__ import annotations

import logging
import os
import re
import time
from typing import Any

import anthropic
from dotenv import load_dotenv

from generation.prompt_templates import (
    build_system_prompt,
    build_user_prompt,
    format_context_chunks,
)

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048
TEMPERATURE = 0.1


class AnswerGenerator:
    def __init__(self, api_key: str | None = None, model: str = MODEL, max_tokens: int = MAX_TOKENS, temperature: float = TEMPERATURE) -> None:
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, question: str, chunks: list[dict[str, Any]]) -> dict[str, Any]:
        start_time = time.monotonic()

        context = format_context_chunks(chunks)
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(question, context)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            answer_text = message.content[0].text if message.content else ""
            token_usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }

        except anthropic.APIError as exc:
            logger.error("Claude API error during generation: %s", exc)
            raise

        latency_ms = int((time.monotonic() - start_time) * 1000)
        citations = self._extract_citations(answer_text, chunks)

        logger.info(
            "Generated answer: %d chars, %d citations, %d ms, %d output tokens",
            len(answer_text),
            len(citations),
            latency_ms,
            token_usage["output_tokens"],
        )

        return {
            "answer": answer_text,
            "citations": citations,
            "model_used": self.model,
            "token_usage": token_usage,
            "latency_ms": latency_ms,
        }

    @staticmethod
    def _extract_citations(answer: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cited_indices: set[int] = set()
        for match in re.finditer(r"\[(\d+)\]", answer):
            idx = int(match.group(1))
            if 1 <= idx <= len(chunks):
                cited_indices.add(idx)

        citations: list[dict[str, Any]] = []
        for idx in sorted(cited_indices):
            chunk = chunks[idx - 1]
            citation = {
                "citation_number": idx,
                "source": chunk.get("source", "unknown"),
                "doc_type": chunk.get("doc_type", ""),
                "title": chunk.get("title") or chunk.get("drug_name") or "",
                "date": chunk.get("date", ""),
                "agency": chunk.get("agency", ""),
                "pmid": chunk.get("pmid"),
                "nct_id": chunk.get("nct_id"),
                "url": _build_source_url(chunk),
                "text_excerpt": chunk.get("text", "")[:200] + "...",
            }
            citations.append(citation)

        return citations


def _build_source_url(chunk: dict[str, Any]) -> str | None:
    if chunk.get("pmid"):
        return f"https://pubmed.ncbi.nlm.nih.gov/{chunk['pmid']}/"
    if chunk.get("nct_id"):
        return f"https://clinicaltrials.gov/study/{chunk['nct_id']}"
    if chunk.get("source") == "openfda" and chunk.get("drug_name"):
        from urllib.parse import quote
        return f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{quote(chunk['drug_name'])}&limit=1"
    return None
