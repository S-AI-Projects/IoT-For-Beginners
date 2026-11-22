# Security-Scenario Rubric: Compare Two Approaches (`R15-T060`)

## Overview
This local example extends the **Run your fruit detector on the edge** lesson by encoding three edge fruit-detector security scenarios (`asset`, `threat`, `control`, `residual-risk`) and comparing a direct threat-to-control keyword rubric checker (`evaluate_scenario_direct`) against an explicit expected-result lookup table (`evaluate_scenario_simple_table`) on identical inputs.

## Scope & Limits of Automated Grading
* **Local Simulation Only:** Evaluates deterministic in-memory Python dictionaries rather than edge cameras, Custom Vision models, or cloud IoT services.
* **Structural Rubric vs. Human Review:** Automated checks verify required field presence (`asset`, `threat`, `control`, `residual-risk`) and keyword alignment between `threat` and `control`, flagging unrelated controls for human review. **Human review** judges the qualitative security rationale and real-world adequacy of the explanation.

## Approach Comparison (`compare_approaches`)
1. **`SC-01-MISSING-ASSET`** (`asset: ""`) -> **`FAIL`** (both approaches reject missing `asset`).
2. **`SC-02-COMPLETE-PASS`** (all fields present; `model_tampering` mitigated via `signed_tflite_model_hash_verification`) -> **`PASS`** (both approaches approve).
3. **`SC-03-UNRELATED-CONTROL`** (`model_tampering` paired with `conveyor_belt_lubrication_schedule`) -> **`FLAG_FOR_REVIEW`** (both approaches flag mismatched control for human review).

## Running the Example & Tests
Run the standalone comparison:
    python3 4-manufacturing/lessons/3-run-fruit-detector-edge/applied-labs/r15-t060/example.py

Run the automated regression tests:
    python3 -m unittest discover -s 4-manufacturing/lessons/3-run-fruit-detector-edge/applied-labs/r15-t060 -p "test_*.py"
