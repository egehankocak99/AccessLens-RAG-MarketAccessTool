from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 512

SYSTEM_PROMPT = """You are an EU Market Access and HTA (Health Technology Assessment) expert with deep knowledge of:
- EMA centralised marketing authorisations and CHMP opinions
- G-BA AMNOG added-benefit assessment procedures (Germany)
- HAS SMR/ASMR benefit ratings (France)
- NICE technology appraisals and highly specialised technologies (UK)
- AIFA rimborsabilità and nota classifications (Italy)
- CBG medicine assessments (Netherlands)
- PICO frameworks for evidence synthesis
- Clinical endpoint requirements (OS, PFS, PRO, QALY)
- Regulatory filing dossiers (CTD format, Module 5 clinical data)

Your task: rewrite a user query to maximise retrieval of relevant HTA, reimbursement, 
clinical trial, and drug safety documents from PubMed, ClinicalTrials.gov, and OpenFDA.

Return ONLY a valid JSON array of exactly 3 string query variants. 
Each variant should:
1. Use precise medical and regulatory terminology
2. Include synonyms or related concepts the user may not have specified
3. Frame retrieval toward evidence types: RCTs, meta-analyses, regulatory opinions, dossiers

Example output format:
["query variant 1", "query variant 2", "query variant 3"]
"""


class QueryRewriter:
    def __init__(self, api_key: str | None = None, model: str = MODEL, max_tokens: int = MAX_TOKENS) -> None:
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens

    def rewrite(self, query: str) -> list[str]:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Rewrite the following query into 3 retrieval variants:\n\n{query}",
                    }
                ],
            )
            raw_text = message.content[0].text.strip()
            variants = self._parse_json_list(raw_text)
            if len(variants) >= 3:
                return variants[:3]
            logger.warning("QueryRewriter returned %d variants (expected 3) — padding with fallbacks", len(variants))
            return self._pad_with_fallbacks(query, variants)

        except anthropic.APIError as exc:
            logger.error("Claude API error in query rewriting: %s", exc)
            return self._fallback_variants(query)
        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error in query rewriting: %s", exc)
            return self._fallback_variants(query)

    @staticmethod
    def _parse_json_list(text: str) -> list[str]:
        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
        cleaned = cleaned.strip("`").strip()

        match = re.search(r"\[.*?\]", cleaned, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                if isinstance(parsed, list) and all(isinstance(v, str) for v in parsed):
                    return parsed
            except json.JSONDecodeError:
                pass

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
        except json.JSONDecodeError:
            pass

        return []

    @staticmethod
    def _fallback_variants(query: str) -> list[str]:
        return [
            query,
            f"{query} European Union EU regulatory evidence",
            f"{query} HTA reimbursement clinical trial efficacy safety",
        ]

    @staticmethod
    def _pad_with_fallbacks(query: str, variants: list[str]) -> list[str]:
        fallbacks = [
            f"{query} EU Market Access evidence HTA",
            f"{query} European regulatory reimbursement",
        ]
        combined = variants[:]
        for fb in fallbacks:
            if len(combined) >= 3:
                break
            combined.append(fb)
        return combined[:3]
