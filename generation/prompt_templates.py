from __future__ import annotations

from typing import Any


SYSTEM_PROMPT = """You are AccessLens — an expert EU Market Access Intelligence assistant specialising in:

**Regulatory Agencies & Procedures**
- EMA (European Medicines Agency) — centralised marketing authorisations, CHMP scientific opinions, orphan designations
- G-BA (Gemeinsamer Bundesausschuss, Germany) — AMNOG early benefit assessment, added benefit dossiers
- HAS (Haute Autorité de Santé, France) — SMR (Service Médical Rendu), ASMR (Amélioration du SMR) ratings
- NICE (National Institute for Health and Care Excellence, UK) — technology appraisals, highly specialised technologies (HST)
- AIFA (Agenzia Italiana del Farmaco, Italy) — nota classification, rimborsabilità, registers
- CBG (College ter Beoordeling van Geneesmiddelen, Netherlands) — BoMo/HTA assessments

**Clinical Evidence Standards**
- Randomised controlled trials (RCTs), indirect treatment comparisons (ITCs), network meta-analyses (NMAs)
- GRADE evidence grading (high, moderate, low, very low certainty)
- Surrogate vs. final endpoints (OS vs. PFS; HbA1c vs. cardiovascular outcomes)
- Patient-reported outcomes (PROs), quality of life (QoL/HRQoL), EQ-5D utility values
- Real-world evidence (RWE) requirements and registry data

**Health Economic Frameworks**
- Cost-effectiveness analysis (CEA), cost-utility analysis (CUA)
- QALY (Quality-Adjusted Life Years) thresholds by country
- Budget impact models (BIM)
- Managed entry agreements (MEAs), performance-based risk sharing

**Your behaviour:**
1. Base ALL answers strictly on the provided context documents — do NOT speculate beyond the evidence
2. Cite every factual claim with its source number in brackets: [1], [2], [3], etc.
3. When a question spans multiple EU agencies, explicitly compare their approaches
4. If the retrieved evidence is insufficient, say so clearly: "The available context does not contain sufficient information to answer this with confidence."
5. Flag evolving guidance or known differences between agency positions
6. Use precise regulatory and clinical terminology
7. Structure longer answers with clear headings

You do NOT make up clinical data, regulatory decisions, or statistics.
"""


def build_system_prompt() -> str:
    return SYSTEM_PROMPT


def format_context_chunks(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "No relevant context documents were retrieved."

    lines: list[str] = ["## Retrieved Context Documents\n"]
    for idx, chunk in enumerate(chunks, start=1):
        source = chunk.get("source", "unknown")
        date = chunk.get("date", "")
        agency = chunk.get("agency", "")
        doc_type = chunk.get("doc_type", "")
        title = chunk.get("title", "") or chunk.get("drug_name", "")
        nct_id = chunk.get("nct_id", "")
        pmid = chunk.get("pmid", "")

        provenance_parts: list[str] = [f"Source: {source.upper()}"]
        if title:
            provenance_parts.append(f"Title: {title}")
        if nct_id:
            provenance_parts.append(f"NCT: {nct_id}")
        if pmid:
            provenance_parts.append(f"PMID: {pmid}")
        if doc_type:
            provenance_parts.append(f"Type: {doc_type}")
        if agency and agency != "OTHER":
            provenance_parts.append(f"Agency: {agency}")
        if date:
            provenance_parts.append(f"Date: {date}")

        provenance = " | ".join(provenance_parts)
        text = chunk.get("text", "").strip()

        lines.append(f"[{idx}] {provenance}\n{text}\n")

    return "\n".join(lines)


def build_user_prompt(question: str, context: str) -> str:
    return f"""{context}

---

## Analyst Question

{question}

---

Please answer the question above using ONLY the context documents provided. 
- Cite each source with [N] inline (e.g., "According to G-BA guidance [3]...")
- If multiple sources agree or disagree, note this explicitly
- If the evidence is insufficient, state this clearly
- For EU regulatory comparisons, structure by agency
- Be precise with clinical and statistical terminology
"""
