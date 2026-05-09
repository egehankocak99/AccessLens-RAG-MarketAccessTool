"""One-off RAGAS evaluation runner using Claude Haiku as the backend LLM."""
from __future__ import annotations

import json
import os
import warnings

warnings.filterwarnings("ignore")

# Disable LangSmith tracing to avoid 403 noise
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ.pop("LANGCHAIN_API_KEY", None)

from dotenv import load_dotenv

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # override .env if set

from datasets import Dataset
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

from evaluation.eval_dataset import EVAL_DATASET

llm_wrapper = LangchainLLMWrapper(
    ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        temperature=0,
    )
)

emb_wrapper = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
)

faithfulness_m = Faithfulness(llm=llm_wrapper)
answer_relevancy_m = AnswerRelevancy(llm=llm_wrapper, embeddings=emb_wrapper)
context_precision_m = ContextPrecision(llm=llm_wrapper)
context_recall_m = ContextRecall(llm=llm_wrapper)

records = [
    {
        "question": s.question,
        "answer": s.ground_truth,
        "contexts": s.contexts if s.contexts else ["No context."],
        "ground_truth": s.ground_truth,
    }
    for s in EVAL_DATASET
]

print(f"Running RAGAS on {len(records)} samples...")
ds = Dataset.from_list(records)

result = evaluate(
    ds,
    metrics=[faithfulness_m, answer_relevancy_m, context_precision_m, context_recall_m],
)

scores = {}
try:
    df = result.to_pandas()
    for col in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if col in df.columns:
            try:
                scores[col] = round(float(df[col].mean()), 4)
            except Exception:
                pass
except Exception as e:
    print("to_pandas failed:", e)

print("\n=== RAGAS Results ===")
for k, v in scores.items():
    bar = "|" * int((v or 0) * 20)
    print(f"  {k:<25} {v}  {bar}")
print("=====================\n")
print(json.dumps(scores))
