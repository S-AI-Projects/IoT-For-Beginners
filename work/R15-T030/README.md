# Task R15-T030: Security-Scenario Rubric — Evidence Summary

## 1. Task Summary
Coursework task **R15-T030** implements a deterministic security-scenario rubric assessment system in the `IoT-For-Beginners` repository, scoped to `6-consumer/lessons/3-spoken-feedback`.

Key deliverables:
- **Security-Scenario Rubric Checker**:
  - Enforces schema containing four non-empty required fields: `asset`, `threat`, `control`, and `residual_risk`.
  - Implements deterministic verdicts:
    - `PASS`: All fields populated and control matched predefined control keywords for the identified threat (heuristic check; does not prove real-world control effectiveness).
    - `FAIL`: Any required field missing, None, or blank.
    - `REVIEW`: All fields populated, but control lacks relevant predefined keywords addressing the threat (or threat is unrecognized), requiring human security evaluation.
  - Explicitly documents that keyword matching does not understand natural language semantics or prove real-world control effectiveness.
- **Fictional Lesson Scenarios**:
  1. `SCENARIO_1_VOICE` (Voice Impersonation): Out-of-band authenticated confirmation (`PASS`).
  2. `SCENARIO_2_TIMER` (Timer REST Manipulation): Token auth & server-side bounds validation (`PASS`).
  3. `SCENARIO_3_SSML` (SSML Injection): Escaping & allow-listing approved elements (`PASS`).
  4. `SCENARIO_4_MISSING_ASSET` (Missing Asset): Omitted asset field (`FAIL`).
  5. `SCENARIO_5_UNRELATED_CONTROL` (Unrelated Control): Painting device casing for SSML threat (`REVIEW`).
- **Three Applied Questions**:
  - Q1 (Predict Output): Voice impersonation scenario status (`PASS`, all four fields populated).
  - Q2 (Diagnose Failure): Missing-asset timer scenario failure (`FAIL` with missing-field diagnostic).
  - Q3 (Choose Boundary Policy): Unrelated control routing policy (`REVIEW`, not automatic acceptance).
  - All three questions are documented in the README and verified via executable unit tests.
- **Expected-Result Verification & Diagnostics**:
  - `verify_scenario_expectations()` function detects:
    1. A scenario missing from the expected-results table.
    2. Unexpected scenario IDs in the expected table for which no scenario was supplied.
    3. Outcome status mismatches between expected and actual verdicts.
  - Raises `AssertionError` with detailed scenario ID diagnostics.
  - Verified via dedicated unit tests covering missing IDs, unexpected extra IDs, and deliberate mismatches.
- **CLI Scenarios**:
  - `--scenario normal`: Evaluates complete scenarios 1, 2, 3 (exits 0).
  - `--scenario boundary`: Evaluates missing-asset scenario 4 and unrelated-control scenario 5 (exits 0).
  - `--scenario failure`: Demonstrates deliberate assertion failure with clear notification (exits 1).
- **Testing & Lesson Integration**:
  - 19 unit tests verifying rubric logic, applied questions, expectation checks, and subprocess execution.
  - Concise linked section added to `6-consumer/lessons/3-spoken-feedback/README.md`.

---

## 2. Files Created and Modified

### Created Implementation & Lab Files:
- `6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t030/README.md`
- `6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t030/example.py`
- `6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t030/test_example.py`

### Modified Lesson File:
- `6-consumer/lessons/3-spoken-feedback/README.md`

### Created Evidence Files:
- `work/R15-T030/README.md` (this file)
- `work/R15-T030/environment.txt`
- `work/R15-T030/sample_results.txt`
- `work/R15-T030/comparison.txt`
- `work/R15-T030/test_run.txt`

---

## 3. Evidence Index

- `environment.txt`: Execution platform, branch, runtime versions, and standard-library-only constraints.
- `sample_results.txt`: Captured console outputs from running `--scenario normal` and `--scenario boundary`.
- `comparison.txt`: Scenario details, rubric evaluations, expected vs. actual outcomes, applied questions rationale, and intentional failure detection evidence.
- `test_run.txt`: Complete verbose test log from `python3 -m unittest discover ...` demonstrating 19 passed tests and exit code 0.
