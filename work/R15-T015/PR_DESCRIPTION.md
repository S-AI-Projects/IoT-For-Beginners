Description
This PR implements offline classification evaluation and a service adapter as a lesson extension for Train a Fruit Quality Detector (4-manufacturing/lessons/1-train-fruit-detector). It computes confusion matrix counts (TP, FN, FP, TN), precision, and recall, explicitly handling zero denominators and isolating model prediction behind a callable adapter.

Related Issue
Fixes: #19

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t015/example.py` implementing `compute_metrics` with zero-denominator policies and `OfflineFruitDetectorAdapter`.
- Added `4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t015/test_example.py` with 7 unit tests covering benchmark fixture y_true=[1,1,0,0], y_pred=[1,0,1,0] (TP=1, FN=1, FP=1, TN=1, precision=0.5, recall=0.5), zero positive predictions policy, adapter determinism, error bounds, and deliberate test failures.
- Added `4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t015/README.md` documenting usage, metrics, and simulation limitations.
- Updated `4-manufacturing/lessons/1-train-fruit-detector/README.md` with links and test instructions.
- Captured test evidence in `work/R15-T015/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 4-manufacturing/lessons/1-train-fruit-detector/applied-labs/r15-t015 -p "test_*.py" -v
```
All 7 unit tests passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
The offline adapter allows verifying metric computation logic deterministically without requiring cloud computer vision subscriptions or live hardware.
