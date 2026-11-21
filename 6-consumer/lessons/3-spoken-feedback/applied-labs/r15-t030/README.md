# Applied Lab: Security-Scenario Rubric — Scenario Assessment

Coursework Task: **R15-T030**
Context Lesson: `6-consumer/lessons/3-spoken-feedback`

---

## 1. Learning Objective & Lesson Relationship

In smart assistant and consumer IoT devices, spoken feedback introduces unique security and trust challenges:
1. **Voice Impersonation & Replay**: Synthesized voices or audio recordings can impersonate real users, rendering voice-only biometric authentication insecure.
2. **REST Timer Endpoint Manipulation**: IoT devices call serverless REST endpoints to request timer durations in seconds. Unauthenticated or unvalidated requests can disrupt cooking, safety, or timing workflows.
3. **SSML Injection**: Speech Synthesis Markup Language (SSML) controls text-to-speech rendering (pitch, volume, language, pauses). Untrusted markup can alter spoken feedback, mislead users, or trigger unexpected audio effects.

The objective of this lab is to implement and evaluate a deterministic security-scenario rubric checker that assesses threat modeling scenarios for IoT spoken feedback systems.

---

## 2. Security-Scenario Schema & Rubric Rules

Each security scenario must be structured as a dictionary with four required, non-empty fields:

- **`asset`**: What valuable asset, capability, or user trust is being protected.
- **`threat`**: The realistic threat or attack vector facing the system.
- **`control`**: The technical or operational security control proposed to mitigate the threat.
- **`residual_risk`**: The risk that remains after implementing the control.

### Deterministic Outcomes:
- **`PASS`**: All four required fields are populated with substantive text, and the `control` matched predefined control keywords for the identified threat domain. A `PASS` indicates that the scenario met the rubric's predefined keyword heuristic; it does not prove real-world security or control effectiveness.
- **`FAIL`**: Any of the four required fields is missing, `None`, empty, or whitespace-only.
- **`REVIEW`**: All four fields are populated, but the proposed control lacks relevant predefined keywords addressing the threat (or proposes an unrelated control), requiring human security reviewer assessment.

> ⚠️ **Educational Note**: This rubric uses predefined keyword-based heuristics for deterministic educational assessment. It does not perform natural language semantic understanding, nor does it prove that a control is effective in production.

---

## 3. Fictional Scenarios

### Complete Scenarios (PASS)
1. **Voice Impersonation (`SCENARIO_1_VOICE`)**:
   - **Asset**: Trust in spoken timer feedback and authorized user commands.
   - **Threat**: Replay attacks or synthetic-voice impersonation of the user using cloned audio.
   - **Control**: Avoid voice-only authentication and require separate authenticated confirmation on a companion device.
   - **Residual Risk**: Compromised companion device or social engineering via misleading audio output in shared environments.
   - **Verdict**: `PASS` (heuristic match; does not prove control effectiveness)

2. **REST Timer Request Manipulation (`SCENARIO_2_TIMER`)**:
   - **Asset**: Integrity and accuracy of timer duration seconds.
   - **Threat**: Unauthorized or manipulated REST requests or responses altering duration.
   - **Control**: Enforce mutual request authentication (HTTPS/tokens) and server-side duration bounds validation.
   - **Residual Risk**: Compromised API credentials or denial of service against the REST timer endpoint.
   - **Verdict**: `PASS` (heuristic match; does not prove control effectiveness)

3. **SSML Markup Injection (`SCENARIO_3_SSML`)**:
   - **Asset**: Integrity and safety of spoken audio feedback.
   - **Threat**: Untrusted markup altering speech output or injecting unauthorized SSML elements.
   - **Control**: Sanitize input by escaping untrusted text and enforce an allow-list of approved SSML elements.
   - **Residual Risk**: Syntactically valid but contextually misleading or socially engineered spoken phrasing.
   - **Verdict**: `PASS` (heuristic match; does not prove control effectiveness)

### Boundary Scenarios
4. **Missing Asset Field (`SCENARIO_4_MISSING_ASSET`)**:
   - Lacks the `asset` field.
   - **Verdict**: `FAIL` (diagnostic reports missing required field `asset`).
5. **Unrelated Control (`SCENARIO_5_UNRELATED_CONTROL`)**:
   - Threat is untrusted SSML markup, but proposed control is painting the device casing with water-resistant enamel.
   - **Verdict**: `REVIEW` (all fields present, but control lacks relevant predefined keywords addressing SSML manipulation).

---

## 4. Applied Questions & Answers

### Question 1 (Predict an Output):
- **Question**: What status does the complete voice-impersonation scenario receive?
- **Expected Answer**: `PASS`
- **Rationale**: All four required fields (`asset`, `threat`, `control`, `residual_risk`) are populated, and the control explicitly addresses voice impersonation by avoiding voice-only authentication and requiring separate authenticated confirmation on a companion device.
- **Unit Test**: Verified in `test_applied_question_1_predict_output` in `test_example.py`.

### Question 2 (Diagnose a Failure):
- **Question**: Why does a timer scenario with no asset fail?
- **Expected Answer**: `FAIL`
- **Rationale**: The rubric enforces that every threat model must identify what is being protected. Omitting the `asset` field violates this baseline schema requirement, triggering a deterministic `FAIL` with a diagnostic message identifying the missing `asset` field.
- **Unit Test**: Verified in `test_applied_question_2_diagnose_failure` in `test_example.py`.

### Question 3 (Choose a Boundary Policy):
- **Question**: What should happen when a complete SSML scenario proposes an unrelated control (e.g. painting the device casing)?
- **Expected Answer**: `REVIEW`, not automatic acceptance.
- **Rationale**: An unrelated physical control does not address software-level SSML markup injection. However, because all fields are grammatically present, automatically failing or accepting it would be inappropriate; routing it to `REVIEW` alerts human security evaluators to inspect the proposed control.
- **Unit Test**: Verified in `test_applied_question_3_choose_boundary_policy` in `test_example.py`.

---

## 5. How to Run CLI Scenarios

The script `example.py` supports three command-line modes:

### Normal Run
Evaluates the three complete scenarios and confirms they pass:
```bash
python3 6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t030/example.py --scenario normal
```

Representative expected output:
```text
================================================================================
Task R15-T030: Security-Scenario Rubric — Scenario Assessment
Scenario: normal (Three Complete Lesson Scenarios)
================================================================================

[SCENARIO_1_VOICE] Voice Impersonation & Replay Attack
--------------------------------------------------------------------------------
  Asset:         Trust in spoken timer feedback and authorized user commands
  Threat:        Replay attacks or synthetic-voice impersonation of the user using cloned audio
  Control:       Avoid voice-only authentication and require separate authenticated confirmation on a companion device
  Residual Risk: Compromised companion device or social engineering via misleading audio output in shared environments
  Verdict:       PASS
  Explanation:   All required fields populated and control matched predefined control keywords for 'voice_impersonation' (predefined keyword heuristic; does not prove control effectiveness).

[SCENARIO_2_TIMER] REST Timer Endpoint Manipulation
--------------------------------------------------------------------------------
  Asset:         Integrity and accuracy of timer duration seconds
  Threat:        Unauthorized or manipulated REST requests or responses altering duration
  Control:       Enforce mutual request authentication (HTTPS/tokens) and server-side duration bounds validation
  Residual Risk: Compromised API credentials or denial of service against the REST timer endpoint
  Verdict:       PASS
  Explanation:   All required fields populated and control matched predefined control keywords for 'timer_request' (predefined keyword heuristic; does not prove control effectiveness).

[SCENARIO_3_SSML] SSML Markup Injection
--------------------------------------------------------------------------------
  Asset:         Integrity and safety of spoken audio feedback
  Threat:        Untrusted markup altering speech output or injecting unauthorized SSML elements
  Control:       Sanitize input by escaping untrusted text and enforce an allow-list of approved SSML elements
  Residual Risk: Syntactically valid but contextually misleading or socially engineered spoken phrasing
  Verdict:       PASS
  Explanation:   All required fields populated and control matched predefined control keywords for 'ssml_manipulation' (predefined keyword heuristic; does not prove control effectiveness).

--------------------------------------------------------------------------------
VERIFICATION SUMMARY:
  ✓ SCENARIO_1_VOICE             Expected: PASS   Actual: PASS   (MATCH)
  ✓ SCENARIO_2_TIMER             Expected: PASS   Actual: PASS   (MATCH)
  ✓ SCENARIO_3_SSML              Expected: PASS   Actual: PASS   (MATCH)
All normal scenarios successfully passed the rubric check.
================================================================================
```

### Boundary Run
Evaluates missing-field and unrelated-control boundary cases:
```bash
python3 6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t030/example.py --scenario boundary
```

Representative expected output:
```text
================================================================================
Task R15-T030: Security-Scenario Rubric — Scenario Assessment
Scenario: boundary (Missing Asset & Unrelated Control Checks)
================================================================================

[SCENARIO_4_MISSING_ASSET] Timer Scenario with Missing Asset Field
--------------------------------------------------------------------------------
  Asset:         <MISSING>
  Threat:        Unauthorized or manipulated REST requests or responses
  Control:       Enforce request authentication and duration bounds validation
  Residual Risk: Compromised API credentials
  Verdict:       FAIL
  Explanation:   Missing required field: 'asset'.

[SCENARIO_5_UNRELATED_CONTROL] SSML Scenario with Unrelated Physical Control
--------------------------------------------------------------------------------
  Asset:         Integrity and safety of spoken audio feedback
  Threat:        Untrusted markup altering speech output
  Control:       Paint the device casing with water-resistant enamel to protect against moisture
  Residual Risk: Scratches on the casing enamel over prolonged usage
  Verdict:       REVIEW
  Explanation:   All fields populated, but control lacks relevant predefined keywords addressing 'ssml_manipulation' (requires human reviewer assessment).

--------------------------------------------------------------------------------
BOUNDARY VERIFICATION SUMMARY:
  ✓ SCENARIO_4_MISSING_ASSET         Expected: FAIL   Actual: FAIL   (MATCH)
  ✓ SCENARIO_5_UNRELATED_CONTROL     Expected: REVIEW Actual: REVIEW (MATCH)
All boundary conditions handled cleanly and correctly.
================================================================================
```

### Deliberate Failure Run
Demonstrates deliberate expectation mismatch detection, exiting non-zero:
```bash
python3 6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t030/example.py --scenario failure
```
*(Exits with status code `1` via an uncaught AssertionError)*

---

## 6. How to Run Unit Tests

Execute test discovery using Python standard library `unittest`:

```bash
python3 -m unittest discover -s 6-consumer/lessons/3-spoken-feedback/applied-labs/r15-t030 -p "test_*.py" -v
```

---

## 7. Prerequisites and Scope Limitations

- **Prerequisites**: Python 3.8+ (standard library only; no pip dependencies).
- **Scope & Limitations**:
  - This is a local educational simulation using rule-based keyword rubrics.
  - It does **not** connect to physical speakers, microphones, or IoT boards.
  - It does **not** call cloud Text-to-Speech (TTS) endpoints, Azure Speech Services, REST timer functions, or deep learning speech models.
  - Keyword matching is an educational rubric and does not replace human threat-modeling reviews.
