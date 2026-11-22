# Applied Lab: Classification Evaluation — Offline Service Adapter (R15-T015)

This lab extends the [Train a Fruit Quality Detector lesson](../../README.md) by implementing an offline service adapter and deterministic evaluation of confusion matrices, precision, and recall.

## Concept & Curriculum Connection

In smart manufacturing quality assurance, binary classification models evaluate whether harvested fruit meets quality standards (e.g. ripe vs unripe, unblemished vs bruised). Edge gateways must evaluate performance metrics reliably, particularly when handling edge cases with zero positive predictions.

### Metrics & Zero-Denominator Policy
Given binary ground truth $y_{\text{true}}$ and predicted labels $y_{\text{pred}} \in \{0, 1\}$:
- **True Positives (TP):** $y_{\text{true}} = 1 \land y_{\text{pred}} = 1$
- **False Negatives (FN):** $y_{\text{true}} = 1 \land y_{\text{pred}} = 0$
- **False Positives (FP):** $y_{\text{true}} = 0 \land y_{\text{pred}} = 1$
- **True Negatives (TN):** $y_{\text{true}} = 0 \land y_{\text{pred}} = 0$

**Zero-Denominator Rules:**
$$\text{Precision} = \begin{cases} \frac{\text{TP}}{\text{TP} + \text{FP}} & \text{if } \text{TP} + \text{FP} > 0 \\ 0.0 & \text{otherwise} \end{cases}$$
$$\text{Recall} = \begin{cases} \frac{\text{TP}}{\text{TP} + \text{FN}} & \text{if } \text{TP} + \text{FN} > 0 \\ 0.0 & \text{otherwise} \end{cases}$$

## Benchmark Fixture
- Input: `y_true = [1, 1, 0, 0]`, `y_pred = [1, 0, 1, 0]`
- Output: `TP = 1, FN = 1, FP = 1, TN = 1`
- Metrics: $\text{Precision} = 0.5, \text{Recall} = 0.5$
- Zero-positive case: `y_true = [1, 1, 0, 0]`, `y_pred = [0, 0, 0, 0]` yields $\text{Precision} = 0.0$.

## Service Adapter Pattern
The `OfflineFruitDetectorAdapter` wraps the classification service behind a standard callable protocol (`predict(samples)`). This enables automated unit tests and continuous integration checks without requiring cloud API keys or live cameras.

### What This Mock Does NOT Establish
- **Model Generalization:** The deterministic adapter returns predetermined outputs; it does not measure real-world ML generalization or dataset bias.
- **Hardware/Environmental Realities:** Does not simulate lighting variations, conveyor speed, lens distortion, or camera sensor noise.

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example
```bash
python3 4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t015/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t015 -p "test_*.py"
```
