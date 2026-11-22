"""Security-scenario rubric — refactor the teaching example (R15-T006).

Standard library only. A SIMULATION: does not interact with physical edge
devices, cameras, or real hardware security modules (TPM/TEE).

Requirements:
  - Three fictional security scenarios tied to running edge fruit detectors:
      Fields: 'asset', 'threat', 'control', 'residual_risk'.
  - Rubric checker evaluates scenarios:
      - Complete, internally consistent scenario -> 'PASS'
      - Scenario missing 'asset' (or any required field) -> 'FAIL'
      - Control unrelated to named threat -> 'REVIEW'
  - Human review judges the explanation; the automated checker only verifies
    the stated structural rubric.
  - Refactoring focus: Implement a correct monolithic baseline, then extract
    one named responsibility (ControlThreatAlignmentValidator). Prove before/after
    equivalence on test fixtures.
"""

REQUIRED_FIELDS = ("asset", "threat", "control", "residual_risk")

# Threat domain keyword mappings for heuristic alignment
THREAT_CONTROL_KEYWORDS = {
    "tamper": ("secure boot", "encryption", "encrypted", "tpm", "tee", "physical lock", "enclosure"),
    "extract": ("secure boot", "encryption", "encrypted", "tpm", "tee", "obfuscation"),
    "spoof": ("mtls", "tls", "certificate", "signature", "auth", "hmac"),
    "intercept": ("mtls", "tls", "encryption", "encrypted", "vpn"),
    "inject": ("signature", "signed", "nonce", "hmac", "validation", "sanitization"),
    "unauthorized": ("rbac", "auth", "permission", "signature", "signed", "credentials"),
}

# Three fictional scenarios
SCENARIO_1_COMPLETE = {
    "asset": "Edge AI camera hardware and model weights",
    "threat": "Physical tampering or extraction of edge ML model weights from flash storage",
    "control": "Hardware secure boot and encrypted flash storage with TPM/TEE",
    "residual_risk": "Side-channel analysis through physical bus probing",
}

SCENARIO_2_COMPLETE = {
    "asset": "Factory floor sorting telemetry stream",
    "threat": "Network interception or spoofing of fruit quality classification packets",
    "control": "Mutual TLS (mTLS) with pinned device certificates",
    "residual_risk": "DDoS disrupting edge-to-cloud classification reporting",
}

SCENARIO_3_COMPLETE = {
    "asset": "Conveyor actuator control command channel",
    "threat": "Unauthorized injection of actuator rejection commands causing conveyor jam",
    "control": "Digitally signed commands with replay-prevention nonces",
    "residual_risk": "Actuator hardware mechanical failure independent of commands",
}

SCENARIO_MISSING_ASSET = {
    "asset": "",  # missing / empty asset
    "threat": "Physical tampering of edge device",
    "control": "Hardware enclosure with tamper switch",
    "residual_risk": "Forced entry",
}

SCENARIO_UNRELATED_CONTROL = {
    "asset": "Edge fruit detection model weights",
    "threat": "Physical tampering and extraction of weights via debug port",
    "control": "Website cookie policy and banner disclosure",  # completely unrelated
    "residual_risk": "Regulatory non-compliance",
}


# ==========================================
# 1. Monolithic Baseline Implementation
# ==========================================
def evaluate_scenario_baseline(scenario: dict) -> tuple:
    """Baseline rubric checker in a single monolithic function."""
    if not isinstance(scenario, dict):
        return "FAIL", "Scenario must be a dictionary"

    # Field presence and non-empty check
    for field in REQUIRED_FIELDS:
        val = scenario.get(field)
        if not isinstance(val, str) or not val.strip():
            return "FAIL", f"Missing or empty required field: {field}"

    # Heuristic threat-control alignment check
    threat_lower = scenario["threat"].lower()
    control_lower = scenario["control"].lower()

    matched_threat_domain = False
    control_matches = False
    for threat_key, keywords in THREAT_CONTROL_KEYWORDS.items():
        if threat_key in threat_lower:
            matched_threat_domain = True
            if any(kw in control_lower for kw in keywords):
                control_matches = True
                break

    if matched_threat_domain and not control_matches:
        return "REVIEW", "Control appears unrelated to named threat; human review required"

    return "PASS", "Scenario meets structural rubric and demonstrated alignment"


# ==========================================
# 2. Refactored Implementation (Extracted Responsibility)
# ==========================================
class ThreatControlAlignmentValidator:
    """Extracted named responsibility: evaluates semantic/keyword consistency between threat and control."""

    def __init__(self, mapping=THREAT_CONTROL_KEYWORDS):
        self.mapping = mapping

    def check_alignment(self, threat: str, control: str) -> tuple:
        """Returns (is_aligned, reason)."""
        threat_lower = threat.lower()
        control_lower = control.lower()

        matched_domain = False
        aligned = False
        for threat_key, keywords in self.mapping.items():
            if threat_key in threat_lower:
                matched_domain = True
                if any(kw in control_lower for kw in keywords):
                    aligned = True
                    break

        if matched_domain and not aligned:
            return False, "Control appears unrelated to named threat; human review required"
        return True, "Aligned or domain unconstrained"


class SecurityRubricChecker:
    """Refactored checker composing structural validation and extracted alignment validator."""

    def __init__(self, alignment_validator=None):
        self.alignment_validator = alignment_validator or ThreatControlAlignmentValidator()

    def evaluate(self, scenario: dict) -> tuple:
        if not isinstance(scenario, dict):
            return "FAIL", "Scenario must be a dictionary"

        for field in REQUIRED_FIELDS:
            val = scenario.get(field)
            if not isinstance(val, str) or not val.strip():
                return "FAIL", f"Missing or empty required field: {field}"

        aligned, reason = self.alignment_validator.check_alignment(
            scenario["threat"], scenario["control"]
        )
        if not aligned:
            return "REVIEW", reason

        return "PASS", "Scenario meets structural rubric and demonstrated alignment"


def check_rubric(scenario: dict) -> tuple:
    """Entry point using the refactored checker."""
    checker = SecurityRubricChecker()
    return checker.evaluate(scenario)


if __name__ == "__main__":
    for name, sc in [
        ("Complete Scenario 1", SCENARIO_1_COMPLETE),
        ("Missing Asset", SCENARIO_MISSING_ASSET),
        ("Unrelated Control", SCENARIO_UNRELATED_CONTROL),
    ]:
        print(f"{name}: {check_rubric(sc)}")
