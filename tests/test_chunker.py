import hashlib
import pytest
from ingestion.chunker import DocumentChunker


@pytest.fixture()
def chunker():
    return DocumentChunker(chunk_size=256, chunk_overlap=32)


def _abstract_doc(text: str, pmid: str = "12345678") -> dict:
    return {
        "pmid": pmid,
        "title": "Test Study",
        "abstract": text,
        "date": "2024-01-01",
        "source": "pubmed",
        "doc_type": "abstract",
        "agency": "OTHER",
        "country": "EU",
    }


def _trial_doc(text: str, nct_id: str = "NCT00000001") -> dict:
    return {
        "nct_id": nct_id,
        "title": "Test Trial",
        "brief_summary": text,
        "date": "2024-01-01",
        "source": "clinicaltrials",
        "doc_type": "trial",
        "agency": "EMA",
        "country": "EU",
    }



def test_chunks_respect_max_size(chunker):
    long_text = "word " * 600  # ~3 000 chars
    doc = _abstract_doc(long_text)
    chunks = chunker.chunk(doc)
    for c in chunks:
        assert len(c["text"]) <= chunker.chunk_size * 6, (
            f"Chunk exceeded expected max length: {len(c['text'])}"
        )


def test_no_empty_chunks(chunker):
    doc = _abstract_doc("This is a short sentence.")
    chunks = chunker.chunk(doc)
    assert all(c["text"].strip() for c in chunks), "Found an empty chunk"



def test_pmid_propagated(chunker):
    doc = _abstract_doc("Some text about an HTA submission. " * 30, pmid="99887766")
    chunks = chunker.chunk(doc)
    assert chunks, "No chunks produced"
    for c in chunks:
        assert c.get("pmid") == "99887766"


def test_nct_id_propagated(chunker):
    doc = _trial_doc("Phase III trial evaluating drug efficacy. " * 30)
    chunks = chunker.chunk(doc)
    assert chunks, "No chunks produced"
    for c in chunks:
        assert c.get("nct_id") == "NCT00000001"


def test_source_field_set(chunker):
    doc = _abstract_doc("Market access evidence requirements differ across EU agencies. " * 20)
    chunks = chunker.chunk(doc)
    for c in chunks:
        assert c.get("source") == "pubmed"


def test_doc_type_preserved(chunker):
    doc = _trial_doc("Randomised controlled trial in oncology patients. " * 20)
    chunks = chunker.chunk(doc)
    for c in chunks:
        assert c.get("doc_type") == "trial"


def test_chunk_index_sequential(chunker):
    doc = _abstract_doc("sentence about HTA. " * 100)
    chunks = chunker.chunk(doc)
    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks))), "Chunk indices are not sequential"



def test_doc_id_uses_pmid(chunker):
    doc = _abstract_doc("Some text.", pmid="11111111")
    chunks = chunker.chunk(doc)
    assert chunks[0]["doc_id"] == "pubmed_11111111"


def test_doc_id_uses_nct_id(chunker):
    doc = _trial_doc("Some text.")
    chunks = chunker.chunk(doc)
    assert chunks[0]["doc_id"] == "ct_NCT00000001"


def test_doc_id_fallback_sha1(chunker):
    doc = {
        "title": "No ID Document",
        "text": "Fallback content.",
        "date": "2024-01-01",
        "source": "openfda",
        "doc_type": "drug_label",
        "agency": "EMA",
        "country": "EU",
    }
    chunks = chunker.chunk(doc)
    for c in chunks:
        assert c["doc_id"].startswith("doc_") or len(c["doc_id"]) > 4, (
            f"Unexpected doc_id format: {c['doc_id']}"
        )



def test_section_headers_split(chunker):
    doc = _abstract_doc(
        "Background: " + "context word " * 60 +
        " Methods: " + "methodology word " * 60 +
        " Results: " + "results word " * 60 +
        " Conclusion: " + "conclusion word " * 60
    )
    chunks = chunker.chunk(doc)
    assert len(chunks) >= 2, "Expected multiple chunks from a multi-section document"



def test_empty_text_returns_empty(chunker):
    doc = _abstract_doc("")
    chunks = chunker.chunk(doc)
    assert chunks == [], "Expected empty list for empty text"


def test_whitespace_only_returns_empty(chunker):
    doc = _abstract_doc("   \n\n\t  ")
    chunks = chunker.chunk(doc)
    assert chunks == [], "Expected empty list for whitespace-only text"


def test_single_sentence(chunker):
    doc = _abstract_doc("One sentence.")
    chunks = chunker.chunk(doc)
    assert len(chunks) == 1
    assert "One sentence." in chunks[0]["text"]



def test_chunk_ids_unique(chunker):
    doc = _abstract_doc("Repeated text. " * 200)
    chunks = chunker.chunk(doc)
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids)), "Duplicate chunk_ids found"
