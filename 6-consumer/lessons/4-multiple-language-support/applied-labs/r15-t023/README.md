# Applied Lab R15-T023: Security Scenario Rubric Checker

This applied lab demonstrates how to structure and evaluate fictional IoT security threat models using a transparent, beginner-friendly rubric checker written with the Python standard library.

> ⚠️ **Educational Simulation Disclaimer**
>
> The scenarios in this lab are **fictional threat scenarios** created for learning purposes, and the rubric checker is a **local rule-based simulation**, not a real automated vulnerability scanner or production security analysis engine. It does **not** claim to comprehend natural language security rationales or prove that a security control is practically effective in a production system.

---

## Connection to the Lesson Architecture

In [Lesson 4: Support multiple languages](../../README.md#support-multiple-languages-in-applications-with-translations), you explored a smart timer application architecture that bridges language barriers using cloud translation services:

```text
User speaks Japanese ──► Translation API (Japanese to English)
                               │
                               ▼
                    Timer Logic (processes in English)
                               │
                               ▼
Text-to-Speech Output ◄── Translation API (English to Japanese)
```

Adding cloud translation introduces distinct security assets, potential threat vectors, and mitigation controls across this data pipeline:
1. **Translation API Credentials:** Secret subscription keys and endpoints that authenticate calls to cloud cognitive services.
2. **User-Provided Translation Input:** Raw spoken Japanese audio and transcribed text transmitted to external cloud translation APIs.
3. **Translated Response Text:** Translated Japanese text sent to the text-to-speech synthesizer that plays audible sound in the user's home or office.

---

## Security Scenario Schema

Each evaluated scenario consists of four mandatory non-empty fields:

| Field | Description |
| :--- | :--- |
| `asset` | The valuable component, data, credential, or hardware requiring protection. |
| `threat` | The potential security compromise, attack, or unauthorized access vector. |
| `control` | The defensive safeguard, policy, or mitigation implemented to counter the threat. |
| `residual_risk` | The remaining risk that persists even after the control is applied. |

---

## Rubric Checker Rules

The checker applies small, transparent, and deterministic evaluation rules:

* **`PASS`**: The scenario contains all four non-empty fields (`asset`, `threat`, `control`, `residual_risk`), and the proposed control shares terms matching a small predefined keyword mapping for the threat. A `PASS` result only indicates structural completeness and keyword relevance—it is **not** proof that the control is practically effective or secure against real attacks. Human review is always necessary for real security decisions.
* **`FAIL`**: The scenario is missing the `asset` field (or any other required field), or contains an empty string.
* **`REVIEW`**: All four fields are populated, but the proposed control does not match any keywords in the predefined mapping for the named threat (e.g. attempting to protect API keys by painting the device casing or adding a fan). A human security reviewer must inspect the scenario.

---

## Dual Approach Comparison (Approach A vs. Approach B)

To reinforce testability and deterministic validation, this lab compares two complementary verification approaches using identical fixture inputs:

* **Approach A (Direct Rubric Evaluation):** Evaluates candidate scenario dictionaries programmatically against the rule engine (`evaluate_scenario()`).
* **Approach B (Explicit Expected-Result Table):** A separately authored dictionary defining human-curated expected outcomes (`EXPECTED_RESULTS = {scenario_id: expected_status}`).
* **Comprehensive Mismatch Detection:** A dedicated comparator (`compare_approaches()`) asserts that Approach A matches Approach B across three criteria:
  1. No expected scenario IDs are missing from actual results.
  2. No unexpected extra scenario IDs appear in actual results.
  3. Verdicts match between common scenario IDs.
  If any mismatch or scenario ID discrepancy occurs, `compare_approaches()` raises an `AssertionError` with a clear explanation.

---

## Prerequisites

* **Python 3.x**
* **Python Standard Library only** (no external packages, cloud APIs, paid services, hardware, or model downloads).

---

## Running the Example

Run the script from the repository root:

```bash
python3 6-consumer/lessons/4-multiple-language-support/applied-labs/r15-t023/example.py
```

### Expected Output

```output
================================================================================
Task R15-T023: Security Scenario Rubric Checker
Context: Lesson 6-4 Multi-Language Smart Timer Translation Architecture
Flow: Japanese Input -> English Translation -> Processing -> Japanese Response
================================================================================

APPROACH A: Direct Rubric Evaluation Results
--------------------------------------------------------------------------------
[PASS  ] Translation API Credentials Protection     -> Scenario is complete with all 4 fields and a related control.
[PASS  ] User-Provided Translation Input Handling   -> Scenario is complete with all 4 fields and a related control.
[PASS  ] Translated Response Verification           -> Scenario is complete with all 4 fields and a related control.
[FAIL  ] Missing Asset Boundary Case                -> Missing or empty required field: 'asset'.
[REVIEW] Unrelated Control Boundary Case            -> Control appears unrelated to the named threat; requires human security review.

APPROACH B: Comparison with Explicit Expected-Result Table
--------------------------------------------------------------------------------
✓ All 5 fixture scenarios matched Approach B's expected table perfectly!

DEMONSTRATION: Intentional Mismatch Detection
--------------------------------------------------------------------------------
✓ Confirmed: A deliberately altered expected table is detected and raises AssertionError.
================================================================================
```

---

## Running the Unit Tests

Execute the unit test suite using Python's standard `unittest` test discovery from the repository root:

```bash
python3 -m unittest discover -s 6-consumer/lessons/4-multiple-language-support/applied-labs/r15-t023 -p "test_*.py"
```

You can also run tests with verbose descriptions:

```bash
python3 -m unittest discover -s 6-consumer/lessons/4-multiple-language-support/applied-labs/r15-t023 -p "test_*.py" -v
```

### Expected Test Output

```output
Ran 13 tests in 0.002s

OK
```

---

## Limitations and Simplifications

1. **Predefined Keyword-Based Relevance:** The relationship between a threat and control is evaluated solely using a small predefined keyword mapping (e.g. `credentials` -> `vault`, `tls`, `sanitize`). It does not understand natural language semantics, evaluate contextual meaning, or prove that a control will effectively stop an attack in production. **Human security review is always necessary for real-world security decisions.**
2. **Deterministic Rules:** In real-world security engineering, threat modeling frameworks (like STRIDE or PASTA) involve subjective, multi-disciplinary risk assessments and threat severity scoring (CVSS) rather than rigid binary pass/review gates.
3. **No Dynamic Vulnerability Scanning:** This lab tests documentation and threat model structure; it does not scan live firmware, run static code analysis, or probe live network ports.
