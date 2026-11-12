# R15-T033: classification evaluation, state trace and invariant

Extends the [Train a fruit quality detector](../../README.md) lesson. The
lesson shows Precision and Recall for a trained classifier; this example
computes them by hand from fixed labels so you can see where the numbers come from.

**Scope:** a local simulation in standard-library Python 3 on fixed label
lists. No Custom Vision, images, model, cloud service or hardware, and no claim
about how any trained model performs. Binary labels only, 1 = positive, 0 = negative.
Real evaluation also deals with class imbalance, thresholds and multiple classes.

## Contract

`evaluate(y_true, y_pred)` takes labels in that order (true first, predicted
second) and returns the counts, precision and recall, plus a **trace**: the
counts after each processed pair.

- TP: true 1, predicted 1. FN: true 1, predicted 0.
- FP: true 0, predicted 1. TN: true 0, predicted 0.
- precision = TP / (TP + FP), recall = TP / (TP + FN).
- **Zero-denominator policy:** if a denominator is 0, the ratio is defined as 0.0.

## Invariant

After step *i* the four counts sum to *i*, and the final trace entry equals the
final result. `check_invariant` tests this, and a test shows it catches corrupted state.

## Fixtures

| Input | Output |
|---|---|
| y_true=[1,1,0,0], y_pred=[1,0,1,0] | TP=1, FN=1, FP=1, TN=1, precision=0.5, recall=0.5 |
| y_true=[1,1,0], y_pred=[0,0,0] | no predicted positives, precision=0.0 (policy), recall=0.0 |
| y_true=[0,0], y_pred=[1,0] | no actual positives, recall=0.0 (policy) |

## Run

```
python3 4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t033/example.py
python3 -m unittest discover -s 4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t033 -p "test_*.py"
```
