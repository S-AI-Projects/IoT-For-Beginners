# Security-Scenario Rubric: Failure & Recovery Example (`R15-T058`)

## Overview
This local example extends the **Support multiple languages** lesson by encoding three multilingual smart-speaker security scenarios (`asset`, `threat`, `control`, `residual-risk`) and verifying them with a structural rubric checker.

## Scope & Limits of Automated Grading
* **Local Simulation Only:** Evaluates deterministic in-memory Python dictionaries rather than live speech-to-text services, microphones, or cloud translators.
* **Structural Rubric vs. Human Review:** The automated checker enforces field completeness (`asset`, `threat`, `control`, `residual-risk`) and keyword alignment between the control and threat category, flagging mismatched controls for review. **Human review** is still required to judge the qualitative soundness and real-world adequacy of the security explanation.

## Documented Failure & Recovery Trace
1. **`SC-01-MISSING-ASSET`** (`asset: ""`) -> **`FAIL`**: Rejected because the required `asset` field is empty; the batch runner logs the error and continues processing.
2. **`SC-02-COMPLETE-PASS`** (all fields populated, `locale_injection` mitigated via BCP-47 allowlist validation) -> **`PASS`**: Demonstrates clean recovery on the next valid input after a documented failure.
3. **`SC-03-UNRELATED-CONTROL`** (`voice_spoofing` paired with screen brightness dimming) -> **`FLAG_FOR_REVIEW`**: Structurally complete, but control mitigation terms do not match the named threat category.

## Running the Example & Tests
Run the standalone example:
    python3 6-consumer/lessons/4-multiple-language-support/applied-labs/r15-t058/example.py

Run the automated regression tests:
    python3 -m unittest discover -s 6-consumer/lessons/4-multiple-language-support/applied-labs/r15-t058 -p "test_*.py"
