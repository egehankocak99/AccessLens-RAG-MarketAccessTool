from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class RAGASEvaluator:
    def __init__(self, output_path: str = "eval_results.json") -> None:
        self.output_path = output_path

    def evaluate(self, eval_samples: list[Any], answerer_fn: Any | None = None) -> dict[str, float]:
        try:
            from datasets import Dataset
            from ragas import evaluate
            from ragas.metrics import (
                answer_relevancy,
                context_precision,
                context_recall,
                faithfulness,
            )
        except ImportError as exc:
            logger.error("RAGAS or datasets package not installed: %s", exc)
            raise

        records = self._build_ragas_records(eval_samples, answerer_fn)
        if not records:
            logger.error("No evaluation records to process")
            return {}

        dataset = Dataset.from_list(records)

        logger.info("Running RAGAS evaluation on %d samples...", len(records))
        start = time.monotonic()

        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )

        elapsed = time.monotonic() - start
        logger.info("RAGAS evaluation complete in %.1f seconds", elapsed)

        scores = self._extract_scores(result)
        self._save_results(scores, records)

        return scores

    def evaluate_from_json(self, json_path: str) -> dict[str, float]:
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )

        dataset = Dataset.from_list(records)
        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        return self._extract_scores(result)

    def _build_ragas_records(self, eval_samples: list[Any], answerer_fn: Any | None) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []

        for sample in eval_samples:
            answer = sample.ground_truth
            contexts = sample.contexts

            if answerer_fn is not None:
                try:
                    pipeline_result = answerer_fn(sample.question)
                    answer = pipeline_result.get("answer", sample.ground_truth)
                    sources = pipeline_result.get("sources", [])
                    if sources:
                        contexts = [s.get("text", "") for s in sources if s.get("text")]
                except Exception as exc:  # noqa: BLE001
                    logger.warning("answerer_fn failed for '%s': %s", sample.question[:50], exc)

            records.append(
                {
                    "question": sample.question,
                    "answer": answer,
                    "contexts": contexts if contexts else ["No context available."],
                    "ground_truth": sample.ground_truth,
                }
            )

        return records

    @staticmethod
    def _extract_scores(result: Any) -> dict[str, float]:
        scores: dict[str, float] = {}
        try:
            for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
                try:
                    val = result[metric_name]
                    scores[metric_name] = round(float(val), 4)
                except (KeyError, TypeError):
                    pass
        except Exception as exc:  # noqa: BLE001
            logger.warning("Score extraction error: %s", exc)

        return scores

    def _save_results(self, scores: dict[str, float], records: list[dict[str, Any]]) -> None:
        output = {
            "scores": scores,
            "num_samples": len(records),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            logger.info("Evaluation results saved to %s", self.output_path)
        except OSError as exc:
            logger.error("Failed to save eval results: %s", exc)



if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    from evaluation.eval_dataset import EVAL_DATASET

    evaluator = RAGASEvaluator(output_path="eval_results.json")

    try:
        scores = evaluator.evaluate(EVAL_DATASET, answerer_fn=None)
        print("\n=== RAGAS Evaluation Results ===")
        for metric, score in scores.items():
            bar = "█" * int(score * 20)
            print(f"  {metric:<25} {score:.4f}  {bar}")
        print("=================================\n")
        print(f"Results saved to eval_results.json")
    except Exception as exc:
        logger.error("Evaluation failed: %s", exc)
        sys.exit(1)
