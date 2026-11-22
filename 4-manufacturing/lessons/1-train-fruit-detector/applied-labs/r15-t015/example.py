"""
Classification Evaluation — Offline Service Adapter (R15-T015)

Lesson reference: 4-manufacturing/lessons/1-train-fruit-detector/README.md
Concept: Training a fruit quality detector requires evaluating classification performance
using confusion matrices, precision, and recall. In production and edge testing environments,
evaluations must be resilient to zero denominators and isolated behind callable adapters.

Policy & Contract:
1. Binary classification with labels 1 (ripe/pass) and 0 (unripe/fail).
2. Confusion matrix computation: TP, FN, FP, TN.
3. Explicit Zero-Denominator Policy:
   - If (TP + FP) == 0: precision is explicitly 0.0 (no positive predictions).
   - If (TP + FN) == 0: recall is explicitly 0.0 (no actual positive ground-truth).
4. External service abstraction: Put prediction and evaluation behind an adapter interface.
"""

from typing import Dict, List, NamedTuple, Protocol, Tuple


class ConfusionMatrix(NamedTuple):
    tp: int
    fn: int
    fp: int
    tn: int
    precision: float
    recall: float


class ClassificationService(Protocol):
    """Callable interface abstracting vision services."""
    def predict(self, samples: List[Dict]) -> List[int]:
        ...


class OfflineFruitDetectorAdapter:
    """
    Deterministic offline adapter providing fixed mock predictions
    without network calls, GPUs, or cloud credentials.
    """
    def __init__(self, canned_predictions: List[int]):
        self._canned_predictions = list(canned_predictions)

    def predict(self, samples: List[Dict]) -> List[int]:
        if len(samples) != len(self._canned_predictions):
            raise ValueError(f"Sample count {len(samples)} mismatch with canned predictions {len(self._canned_predictions)}")
        return list(self._canned_predictions)


def compute_metrics(y_true: List[int], y_pred: List[int]) -> ConfusionMatrix:
    """
    Computes confusion matrix, precision, and recall with explicit zero-denominator handling.
    """
    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: len(y_true)={len(y_true)}, len(y_pred)={len(y_pred)}")

    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)

    # Explicit Zero-Denominator Policy
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0

    return ConfusionMatrix(tp=tp, fn=fn, fp=fp, tn=tn, precision=precision, recall=recall)


def run_demo() -> ConfusionMatrix:
    y_true = [1, 1, 0, 0]
    y_pred = [1, 0, 1, 0]
    metrics = compute_metrics(y_true, y_pred)
    print(f"y_true: {y_true}, y_pred: {y_pred}")
    print(f"TP={metrics.tp}, FN={metrics.fn}, FP={metrics.fp}, TN={metrics.tn}")
    print(f"Precision={metrics.precision}, Recall={metrics.recall}")
    return metrics


if __name__ == "__main__":
    run_demo()
