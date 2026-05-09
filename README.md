```
 █████╗  ██████╗ ██████╗███████╗███████╗███████╗██╗     ███████╗███╗   ██╗███████╗
██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝██║     ██╔════╝████╗  ██║██╔════╝
███████║██║     ██║     █████╗  ███████╗███████╗██║     █████╗  ██╔██╗ ██║███████╗
██╔══██║██║     ██║     ██╔══╝  ╚════██║╚════██║██║     ██╔══╝  ██║╚██╗██║╚════██║
██║  ██║╚██████╗╚██████╗███████╗███████║███████║███████╗███████╗██║ ╚████║███████║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝
```

# AccessLens — EU Market Access Intelligence

> **Production-grade RAG system for pharmaceutical and biotech Market Access professionals**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com)
[![Claude claude-sonnet-4-20250514](https://img.shields.io/badge/Claude-claude--sonnet--4--20250514-orange.svg)](https://anthropic.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-local-red.svg)](https://qdrant.tech)
[![LangSmith](https://img.shields.io/badge/LangSmith-traced-green.svg)](https://smith.langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Why AccessLens?

Market Access teams at pharma and biotech companies face a critical intelligence gap: regulatory guidance, HTA dossiers, clinical trial results, and drug safety signals are scattered across dozens of EU agency portals, PubMed, and ClinicalTrials.gov — and they change constantly.

**AccessLens solves this** by combining live data retrieval from authoritative scientific sources with a state-of-the-art RAG pipeline powered by Claude claude-sonnet-4-20250514. Analysts get grounded, cited answers to complex reimbursement and evidence strategy questions — in seconds, not hours.

---

## EU Agencies Covered

| Agency | Country | Scope |
|--------|---------|-------|
| **EMA** | EU-wide | Centralised marketing authorisations, CHMP opinions |
| **G-BA** | Germany | AMNOG added-benefit assessments |
| **HAS** | France | SMR/ASMR clinical benefit ratings |
| **NICE** | UK (reference) | Technology appraisals, HST decisions |
| **AIFA** | Italy | Nota classification, rimborsabilità |
| **CBG** | Netherlands | Beoordeling medicijnen |

---

## Architecture

```
                        ┌─────────────────────────────┐
                        │        User Question         │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │      Query Rewriter          │
                        │  (Claude: 3 expanded queries)│
                        └─────────────┬───────────────┘
                                      │
              ┌───────────────────────┼─────────────────────────┐
              │                       │                         │
    ┌─────────▼──────┐     ┌──────────▼──────────┐   ┌─────────▼──────┐
    │  PubMed API    │     │ ClinicalTrials.gov   │   │   OpenFDA API  │
    │  (Entrez)      │     │ (v2 REST API)        │   │  (drug labels) │
    └─────────┬──────┘     └──────────┬──────────┘   └─────────┬──────┘
              │                       │                         │
              └───────────────────────┼─────────────────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │    Chunker + Embedder        │
                        │  BGE-base-en-v1.5 (768-dim) │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │     Qdrant (local mode)      │
                        │   Vector Store + Metadata    │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │      Hybrid Search           │
                        │  Semantic + BM25 → RRF       │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │  Cross-Encoder Reranker      │
                        │  ms-marco-MiniLM-L-6-v2     │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │   Claude claude-sonnet-4-20250514 Generator │
                        │ Grounded answer + citations  │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │   RAGAS Faithfulness Score   │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │     FastAPI Response         │
                        │  answer + sources + scores   │
                        └─────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- An Anthropic API key ([get one here](https://console.anthropic.com))
- A LangSmith API key ([get one here](https://smith.langchain.com)) — optional but recommended

### Step 1 — Clone and set up environment

```bash
cd accesslens
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure environment variables

```bash
cp .env.example .env
# Edit .env with your API keys and email
```

### Step 4 — Ingest data (first run)

```bash
# Ingest PubMed documents
python -m ingestion.pubmed_fetcher

# Ingest ClinicalTrials.gov studies
python -m ingestion.clinicaltrials_fetcher

# Ingest OpenFDA drug labels
python -m ingestion.openfda_fetcher
```

### Step 5 — Start the API server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6 — Open the frontend

Open `frontend/index.html` in your browser (double-click or serve with Live Server in VS Code).

---

## Usage Examples

### Via the Web UI

Navigate to `frontend/index.html`, select agency filters, and type your question.

### Via the REST API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the reimbursement evidence standard for oncology drugs at G-BA?",
    "top_k": 5,
    "filters": {"agency": "G-BA"}
  }'
```

### Sample Queries

```
"What evidence does G-BA require for added benefit assessment of oncology drugs?"

"Find clinical trials for NASH treatments submitted in Europe after 2022"

"What safety signals exist for GLP-1 agonists in European regulatory filings?"

"What is the NICE technology appraisal process for rare disease drugs?"

"How does HAS evaluate the clinical benefit (SMR) for cardiovascular drugs?"

"What are the reimbursement conditions for CAR-T therapies in Germany?"
```

---

## RAG Pipeline Explained

| Stage | Component | Description |
|-------|-----------|-------------|
| 1. Query Expansion | `query_rewriter.py` | Claude generates 3 HTA-optimised query variants |
| 2. Live Data Fetch | `pubmed_fetcher.py`, `clinicaltrials_fetcher.py`, `openfda_fetcher.py` | Real-time retrieval from authoritative APIs |
| 3. Chunking | `chunker.py` | Recursive + section-aware splitting (512 tokens, 64 overlap) |
| 4. Embedding | `embedder.py` | BAAI/bge-base-en-v1.5 (768-dim, SOTA for biomedical) |
| 5. Indexing | `qdrant_store.py` | Local Qdrant with rich metadata payload |
| 6. Hybrid Search | `hybrid_search.py` | Semantic + BM25 fused via Reciprocal Rank Fusion |
| 7. Reranking | `reranker.py` | Cross-encoder rescores top 20 → returns top 5 |
| 8. Generation | `generator.py` | Claude claude-sonnet-4-20250514 with grounded, cited answers |
| 9. Evaluation | `ragas_eval.py` | Faithfulness, relevancy, precision, recall scores |
| 10. Tracing | LangSmith | Full pipeline observability and debugging |

---

## Evaluation Results

*Run `python -m evaluation.ragas_eval` to populate this table with your results.*

| Metric | Score | Threshold |
|--------|-------|-----------|
| Faithfulness | — | ≥ 0.80 |
| Answer Relevancy | — | ≥ 0.75 |
| Context Precision | — | ≥ 0.70 |
| Context Recall | — | ≥ 0.70 |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Anthropic Claude claude-sonnet-4-20250514 |
| **Embeddings** | BAAI/bge-base-en-v1.5 (sentence-transformers) |
| **Vector Store** | Qdrant (local mode) |
| **Reranker** | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| **BM25** | rank-bm25 |
| **API Framework** | FastAPI + Uvicorn |
| **Observability** | LangSmith |
| **Evaluation** | RAGAS |
| **Data Sources** | PubMed (NCBI Entrez), ClinicalTrials.gov v2, OpenFDA |
| **Frontend** | Vanilla HTML/CSS/JS |

---

## Project Structure

```
accesslens/
├── ingestion/          # Live data fetchers + chunking + embedding
├── vectorstore/        # Qdrant integration + metadata schema
├── retrieval/          # Query rewriting, hybrid search, reranking
├── generation/         # Claude prompt templates + answer generation
├── evaluation/         # RAGAS evaluation + curated QA dataset
├── api/                # FastAPI application + routes + models
├── frontend/           # Single-file web UI
└── tests/              # Unit + integration tests
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
