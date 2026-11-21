# Task R15-T028: Growing-Degree Calculation — Evidence Summary

## 1. Task Summary
Coursework task **R15-T028** implements a local mathematical simulation of Growing Degree Days (GDD) with input validation, error handling, and stream recovery in the `IoT-For-Beginners` repository, scoped to `2-farm/lessons/1-predict-plant-growth`.

Key accomplishments:
- Implemented standard daily GDD formula in Celsius:
  $$\text{GDD} = \max\left(0, \frac{T_{\min} + T_{\max}}{2} - T_{\text{base}}\right)$$
- Enforced strict validation:
  - Rejection of missing `minimum` or `maximum` temperature fields.
  - Rejection of inverted temperatures ($T_{\min} > T_{\max}$).
  - Explicit rejection of Python booleans (`True`, `False`) and non-numeric types.
  - Rejection of non-finite numbers (`NaN`, `inf`, `-inf`).
  - Validation of plant base temperature ($T_{\text{base}}$).
- Implemented fault-tolerant streaming:
  - Corrupt or invalid records are rejected with descriptive diagnostic errors.
  - Invalid records contribute exactly $0.0$ to the accumulated total.
  - Processing resumes automatically on the next valid record (recovery guarantee).
- Evaluated the mandatory 3-day normal fixture ($T_{\text{base}} = 10^\circ\text{C}$):
  - Day 1: min 8, max 16 → GDD 2
  - Day 2: min 12, max 20 → GDD 6
  - Day 3: min 2, max 8 → GDD 0
  - Accumulated Total = 8 GDD
- Demonstrated the 3-step failure/recovery stream:
  - Day 1: min 8, max 16 → GDD 2
  - Day 2: min 8 (missing max) → Rejected, GDD 0, running total preserved at 2
  - Day 3: min 12, max 20 → Accepted, GDD 6, running total becomes 8
- Implemented three CLI scenarios: `--scenario normal`, `--scenario boundary`, and `--scenario failure` (deliberate non-zero exit).
- Created a 17-test unit test suite covering calculations, boundaries, edge cases, validations, recovery, and subprocess execution.
- Updated lesson README with a linked applied-lab section.

---

## 2. Files Created and Modified

### Created Implementation & Lab Files:
- `2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/example.py`
- `2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/test_example.py`
- `2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/README.md`

### Modified Lesson File:
- `2-farm/lessons/1-predict-plant-growth/README.md`

### Created Evidence Files:
- `work/R15-T028/README.md` (this file)
- `work/R15-T028/environment.txt`
- `work/R15-T028/sample_results.txt`
- `work/R15-T028/test_run.txt`
- `work/R15-T028/comparison.txt`

---

## 3. Verification Overview

1. **CLI Normal Scenario**:
   `python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/example.py --scenario normal`
   - Exit code: 0
   - Correctly verified Day 1 (2.0), Day 2 (6.0), Day 3 (0.0), and final accumulated total (8.0).

2. **CLI Boundary Scenario**:
   `python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/example.py --scenario boundary`
   - Exit code: 0
   - Confirmed zero-GDD when average $\le$ base, inverted temperature rejection, and 3-record failure/recovery stream reaching total 8.0.

3. **CLI Failure Scenario**:
   `python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/example.py --scenario failure`
   - Exit code: 1 (non-zero)
   - Raised intentional `AssertionError` verifying that incorrect assertions terminate with a non-zero exit code.

4. **Unit Test Suite**:
   `python3 -m unittest discover -s 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028 -p "test_*.py" -v`
   - Ran 17 tests in 0.207s: All passed (OK), Exit code: 0.

5. **Code Style & Git Status**:
   - `git diff --check`: Clean (no trailing whitespace or formatting errors).
   - Python standard-library only; no external dependencies or hardware requirements.
