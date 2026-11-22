# R15-T006: Security-Scenario Rubric — Refactor the Teaching Example

An applied laboratory extension for the [Run your fruit detector on the edge](../../README.md) lesson.

## Educational Context & Scope

Deploying computer vision models to edge IoT devices introduces threats that differ from centralized cloud services. Edge devices are physically exposed on factory floors and process telemetry locally. Analyzing risk requires structured scenarios detailing:
- **Asset:** The physical or digital resource requiring protection.
- **Threat:** Potential adverse action (tampering, extraction, spoofing, unauthorized commands).
- **Control:** Countermeasure mitigating the threat (hardware roots of trust, mTLS, signed commands).
- **Residual Risk:** Remaining exposure accepted after controls are deployed.

This lab implements an automated rubric checker verifying structural completeness and threat-control alignment. Human review judges the qualitative depth of the explanation, while the automated checker verifies the structural schema.

**Scope:** Python 3 standard library simulation. No physical edge hardware, cameras, or cloud vision endpoints required.

## Run

```bash
python3 4-manufacturing/lessons/3-run-fruit-detector-edge/applied-labs/r15-t006/example.py
python3 -m unittest discover -s 4-manufacturing/lessons/3-run-fruit-detector-edge/applied-labs/r15-t006 -p "test_*.py"
```

## Fictional Edge Security Scenarios & Rubric Outcomes

| Scenario | Asset | Threat | Control | Residual Risk | Rubric Outcome |
|---|---|---|---|---|---|
| 1. Complete Model Protection | Edge AI camera & weights | Physical tampering or extraction of ML weights | Secure boot & encrypted flash with TPM/TEE | Side-channel bus probing | **PASS** |
| 2. Complete Network Telemetry | Factory sorting telemetry | Interception or spoofing of classification packets | Mutual TLS (mTLS) with pinned certificates | Telemetry DDoS | **PASS** |
| 3. Complete Actuator Control | Conveyor rejection channel | Unauthorized injection of actuator commands | Digitally signed commands with nonces | Mechanical failure | **PASS** |
| 4. Missing Field | *(missing / empty)* | Physical tampering of device | Tamper switch enclosure | Forced entry | **FAIL** (missing asset) |
| 5. Unrelated Control | Model weights | Physical tampering via debug port | Website cookie policy disclosure | Regulatory breach | **REVIEW** (unrelated control) |

## Refactoring Responsibility Extraction

The implementation demonstrates code maintainability by refactoring:
1. **Baseline (`evaluate_scenario_baseline`):** Monolithic validator performing both schema parsing and threat-control alignment.
2. **Refactored (`SecurityRubricChecker` & `ThreatControlAlignmentValidator`):** Extracts semantic threat-control keyword analysis into a dedicated validator class, maintaining identical contract and behavior verified through equivalence testing.

## Where the Simplification Stops

Real threat modeling frameworks (e.g. STRIDE, DREAD, MITRE ATT&CK for ICS) include risk scoring calculations, attack surface trees, compliance mapping (IEC 62443), and formal cryptographic policy verification.
