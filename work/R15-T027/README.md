# Task R15-T027: Bounding-box Intersection over Union (IoU) — Evidence Summary

## 1. Task Summary
Coursework task **R15-T027** implements axis-aligned bounding-box Intersection over Union (IoU) in the `IoT-For-Beginners` repository, scoped to `5-retail/lessons/1-train-stock-detector`.

Key accomplishments:
- Implemented standard coordinate convention `[x_min, y_min, x_max, y_max]` where $x$ increases rightward and $y$ increases downward in digital image pixel space.
- Provided strict coordinate validation rejecting booleans, non-numeric types, non-finite values (NaN and infinity), and inverted coordinates ($x_{\min} > x_{\max}$ or $y_{\min} > y_{\max}$) without silent reordering.
- Permitted degenerate zero-width and zero-height boxes ($0.0$ area) and handled zero union area without division-by-zero errors.
- Implemented the mandatory worked fixture (Box A `[0, 0, 2, 2]`, Box B `[1, 1, 3, 3]` yielding IoU = 1/7 ≈ 0.142857142857).
- Provided CLI scenarios: `normal` (default), `boundary` (edge-touching and zero-area boxes), and `failure` (deliberate non-zero exit status demonstration).
- Created a comprehensive test suite of 20 unit tests covering geometry, validation, edge cases, and fresh-process subprocess execution.
- Extended the lesson README with applied-lab guidance and educational scope limitations.

---

## 2. Files Created and Modified

### Created Implementation & Lab Files:
- `5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py`
- `5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/test_example.py`
- `5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/README.md`

### Modified Lesson File:
- `5-retail/lessons/1-train-stock-detector/README.md`

### Created Evidence Files:
- `work/R15-T027/README.md` (this file)
- `work/R15-T027/environment.txt`
- `work/R15-T027/sample_results.txt`
- `work/R15-T027/test_run.txt`
- `work/R15-T027/comparison.txt`

---

## 3. Verification Overview

1. **CLI Normal Scenario**:
   `python3 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py normal`
   - Exit code: 0
   - Correctly verified Box A, Box B, Intersection (1.0), Union (7.0), and IoU (1/7).

2. **CLI Boundary Scenario**:
   `python3 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py boundary`
   - Exit code: 0
   - Confirmed horizontal/vertical edge-touching, corner-touching, and zero-area box IoUs evaluate to 0.0.

3. **CLI Failure Scenario**:
   `python3 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py failure`
   - Exit code: 1 (non-zero)
   - Raised intentional `AssertionError` verifying that incorrect assertions terminate with a non-zero exit code.

4. **Unit Test Suite**:
   `python3 -m unittest discover -s 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027 -p "test_*.py" -v`
   - Ran 20 tests in 0.192s: All passed (OK), Exit code: 0.

5. **Code Style & Git Status**:
   - `git diff --check`: Clean (no trailing whitespace or formatting errors).
   - Python standard-library only; no external dependencies or cloud calls.
