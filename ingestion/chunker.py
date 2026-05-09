from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

SECTION_HEADERS = re.compile(
    r"(?m)^(Abstract|Introduction|Background|Methods?|Materials?\s+and\s+Methods?|"
    r"Results?|Discussion|Conclusion|References?|Acknowledgements?|"
    r"Summary|Objectives?|Endpoints?|Safety|Efficacy|Pharmacology|"
    r"Clinical\s+Evidence|Benefit.Risk|Regulatory\s+Context|"
    r"Primary\s+Outcome|Secondary\s+Outcomes?)\s*[:.]?\s*$",
    re.IGNORECASE,
)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


class DocumentChunker:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_document(self, document: dict[str, Any]) -> list[dict[str, Any]]:
        text = self._extract_text(document)
        if not text:
            logger.debug("Document has no text to chunk: %s", document.get("pmid") or document.get("nct_id", "unknown"))
            return []

        sections = self._split_on_headers(text)
        raw_chunks: list[str] = []
        for section in sections:
            raw_chunks.extend(self.splitter.split_text(section))

        chunks: list[dict[str, Any]] = []
        base_meta = self._extract_metadata(document)
        doc_id = self._make_doc_id(document)

        for idx, chunk_text in enumerate(raw_chunks):
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue
            chunk_id = self._make_chunk_id(doc_id, idx)
            chunks.append(
                {
                    **base_meta,
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "chunk_index": idx,
                    "text": chunk_text,
                }
            )

        logger.debug("Document '%s' → %d chunks", doc_id, len(chunks))
        return chunks

    chunk = chunk_document

    def chunk_documents(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        all_chunks: list[dict[str, Any]] = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        logger.info("Chunked %d documents into %d chunks", len(documents), len(all_chunks))
        return all_chunks

    def _extract_text(self, document: dict[str, Any]) -> str:
        for field in ("abstract", "content", "brief_summary", "text"):
            value = document.get(field, "")
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _extract_metadata(self, document: dict[str, Any]) -> dict[str, Any]:
        source = document.get("source", "unknown")
        meta = {
            "source": source,
            "doc_type": document.get("doc_type", self._infer_doc_type(source)),
            "date": document.get("pub_date") or document.get("start_date", ""),
            "agency": document.get("agency", "OTHER"),
            "country": document.get("country", ""),
        }
        if "pmid" in document:
            meta["pmid"] = document["pmid"]
            meta["title"] = document.get("title", "")
        if "nct_id" in document:
            meta["nct_id"] = document["nct_id"]
            meta["title"] = document.get("title", "")
        if "drug_name" in document:
            meta["drug_name"] = document["drug_name"]
        return meta

    def _infer_doc_type(self, source: str) -> str:
        mapping = {
            "pubmed": "abstract",
            "clinicaltrials": "trial",
            "openfda": "drug_label",
        }
        return mapping.get(source, "dossier")

    def _split_on_headers(self, text: str) -> list[str]:
        parts = SECTION_HEADERS.split(text)
        if len(parts) == 1:
            return [text]

        sections: list[str] = []
        if parts[0].strip():
            sections.append(parts[0].strip())
        for i in range(1, len(parts), 2):
            header = parts[i] if i < len(parts) else ""
            body = parts[i + 1] if i + 1 < len(parts) else ""
            combined = f"{header}\n{body}".strip()
            if combined:
                sections.append(combined)

        return sections or [text]

    @staticmethod
    def _make_doc_id(document: dict[str, Any]) -> str:
        if document.get("pmid"):
            return f"pubmed_{document['pmid']}"
        if document.get("nct_id"):
            return f"ct_{document['nct_id']}"
        fingerprint = (document.get("title", "") + document.get("source", "")).encode()
        return "doc_" + hashlib.sha1(fingerprint).hexdigest()[:12]

    @staticmethod
    def _make_chunk_id(doc_id: str, chunk_index: int) -> str:
        return f"{doc_id}_chunk_{chunk_index}"
