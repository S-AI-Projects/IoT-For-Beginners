# R15-T041 — fictional security-scenario rubric

This **local, fictional, runnable concept example** extends the lesson [Set a timer and provide spoken feedback](../../README.md). The lesson describes confirming a timer using spoken feedback and announcing when the timer finishes. These mock security scenarios ask what needs protection when a spoken message is trusted, overheard, or based on a changed timer duration.

The example needs only Python 3 and its standard library. It does **not** start a timer, generate speech, use hardware, contact a cloud service, download models, or measure model performance.

## Run from the repository root

```sh
python3 6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t041/example.py
python3 -m unittest discover -s 6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t041 -p "test_*.py"
```

The example prints the three **fictional** scenario names and results:

```text
FICTIONAL spoken-timer scenarios — STRUCTURE ONLY (not correctness)
Spoofed timer completion: PASS — four fields present; shared topic tag(s): authenticity
Overheard timer feedback: PASS — four fields present; shared topic tag(s): privacy
Changed timer duration: PASS — four fields present; shared topic tag(s): integrity
```

Each named scenario has exactly four non-empty string fields:

- `asset`: what needs protecting
- `threat`: a fictional way the asset could be harmed
- `control`: a proposed response to the threat
- `residual_risk`: what could remain even with the control

`check_scenario` reports `PASS` when all fields are non-empty and the **author-supplied** topic tags in `threat` and `control` overlap; `FAIL` when any required field is absent/blank; and `REVIEW` when the fields are present but those topic tags do not overlap. The three tags used in the fixtures are `[authenticity]`, `[privacy]`, and `[integrity]`. A missing tag is also sent for review, not automatically failed. These tags are only a transparent **structure heuristic**; the checker does **not** understand language, establish whether a control addresses a threat, or judge security correctness. Two unrelated descriptions can reuse the same tag and receive `PASS`. A **human reviewer must judge the actual explanation and control rationale**.

## Negative test (deliberate failure)

To prove an incorrect expected result causes a non-zero exit, run this from the repository root:

```sh
R15_T041_NEGATIVE_TEST=1 python3 -m unittest discover -s 6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t041 -p "test_*.py"
```

One opt-in test deliberately asserts that a valid fixture is `FAIL`; its **expected result is one test failure and exit code 1**. Do not use this opt-in mode as a passing test run. The normal command skips this intentional failure and exercises the passing, missing-asset, blank-asset and mismatch cases. Evidence is saved locally under `work/R15-T041/` and should not be included in an upstream PR.
