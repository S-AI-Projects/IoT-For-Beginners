"""Security Scenario Rubric Checker (Task R15-T023).

Demonstrates a beginner-friendly rubric checker for evaluating IoT security scenarios
in a multi-language smart timer translation workflow using Python's standard library.

Translation Architecture Context (Lesson 6-4):
  Japanese Voice Input -> English Translation -> Timer Logic -> Japanese Response Translation -> Speech Feedback

Educational Disclaimer:
  This checker is a local simulation using small, deterministic rules. It does NOT
  claim to understand natural language security explanations generally or prove
  that any security control is effective in production.
"""

from typing import Any, Dict, List, Tuple

# Security relevance keywords mapping common threats to relevant mitigation concepts
SECURITY_RELEVANCE_MAP: Dict[str, List[str]] = {
    "credential": ["key", "vault", "environment", "secret", "token", "backend", "serverless", "auth"],
    "key": ["vault", "environment", "secret", "backend", "serverless", "storage", "protect", "token"],
    "theft": ["vault", "environment", "secret", "backend", "serverless", "encrypt", "protect"],
    "quota": ["limit", "rate", "backend", "serverless", "monitor", "restrict"],
    "injection": ["sanitize", "validate", "filter", "limit", "escape", "schema", "length"],
    "eavesdropping": ["tls", "encrypt", "https", "secure", "transit"],
    "transit": ["tls", "encrypt", "https", "secure", "transit"],
    "tampering": ["validate", "sign", "integrity", "hash", "tls", "mask", "sanitize"],
    "offensive": ["profanity", "mask", "filter", "moderate", "validate", "clean"],
    "misleading": ["validate", "profanity", "review", "schema", "filter"],
}

REQUIRED_FIELDS = ("asset", "threat", "control", "residual_risk")


def is_control_related(threat: str, control: str) -> bool:
    """Determine whether a proposed control addresses concepts named in the threat.

    Note: This is a transparent keyword-overlap heuristic, NOT an AI comprehension model.

    Args:
        threat: Text describing the security threat.
        control: Text describing the proposed security control.

    Returns:
        True if the control shares thematic security terms with the threat, False otherwise.
    """
    threat_lower = threat.lower()
    control_lower = control.lower()

    matched_threat_concept = False
    for threat_key, control_terms in SECURITY_RELEVANCE_MAP.items():
        if threat_key in threat_lower:
            matched_threat_concept = True
            if any(term in control_lower for term in control_terms):
                return True

    # Fallback heuristic: check general word overlap for terms longer than 4 characters
    if not matched_threat_concept:
        threat_words = {w.strip(".,;:()\"'") for w in threat_lower.split() if len(w) > 4}
        control_words = {w.strip(".,;:()\"'") for w in control_lower.split() if len(w) > 4}
        return bool(threat_words & control_words)

    return False


def evaluate_scenario(scenario: Dict[str, Any]) -> Tuple[str, str]:
    """Evaluate a single security scenario against the transparent rubric.

    Rubric Rules:
      1. A scenario missing an asset (or other required field) returns FAIL.
      2. A control clearly unrelated to its named threat returns REVIEW.
      3. A complete scenario with all 4 non-empty fields and a related control returns PASS.

    Args:
        scenario: Dictionary containing 'asset', 'threat', 'control', and 'residual_risk'.

    Returns:
        A tuple of (VERDICT, REASON) where VERDICT is 'PASS', 'FAIL', or 'REVIEW'.
    """
    # Rule 1: Check for missing asset specifically
    asset = scenario.get("asset")
    if not isinstance(asset, str) or not asset.strip():
        return "FAIL", "Missing or empty required field: 'asset'."

    # Check remaining required fields
    for field in ("threat", "control", "residual_risk"):
        val = scenario.get(field)
        if not isinstance(val, str) or not val.strip():
            return "FAIL", f"Missing or empty required field: '{field}'."

    # Rule 2: Check if control is clearly related to its named threat
    threat = scenario["threat"]
    control = scenario["control"]
    if not is_control_related(threat, control):
        return (
            "REVIEW",
            "Control appears unrelated to the named threat; requires human security review.",
        )

    # Rule 3: Complete scenario with clearly related control
    return "PASS", "Scenario is complete with all 4 fields and a related control."


def compare_approaches(
    actual_results: Dict[str, str], expected_results: Dict[str, str]
) -> bool:
    """Compare Approach A (rubric output) against Approach B (explicit expected-result table).

    Checks for:
      1. Missing scenario IDs (expected in B, but absent from A).
      2. Unexpected extra scenario IDs (present in A, but not defined in B).
      3. Verdict mismatches (present in both, but actual != expected).

    Args:
        actual_results: Dictionary of scenario_id -> actual rubric verdict.
        expected_results: Dictionary of scenario_id -> expected verdict.

    Returns:
        True if all scenarios match their expected results and scenario sets are identical.

    Raises:
        AssertionError: If any missing scenario, extra scenario, or verdict mismatch is found.
    """
    mismatches: List[str] = []

    # 1. Check for expected scenario IDs that are missing from actual results
    for scenario_id in expected_results:
        if scenario_id not in actual_results:
            mismatches.append(
                f"  - Missing scenario ID: '{scenario_id}' was expected but not found in actual results."
            )

    # 2. Check for unexpected extra scenario IDs in actual results
    for scenario_id in actual_results:
        if scenario_id not in expected_results:
            mismatches.append(
                f"  - Unexpected extra scenario ID: '{scenario_id}' was present in actual results but not in expected table."
            )

    # 3. Check for verdict mismatches on scenarios present in both
    for scenario_id, expected_status in expected_results.items():
        if scenario_id in actual_results:
            actual_status = actual_results[scenario_id]
            if actual_status != expected_status:
                mismatches.append(
                    f"  - Verdict mismatch for '{scenario_id}': expected '{expected_status}', got '{actual_status}'."
                )

    if mismatches:
        raise AssertionError("Approach comparison mismatch detected:\n" + "\n".join(mismatches))

    return True


def demonstrate_mismatch_detection() -> bool:
    """Demonstrate that a deliberately incorrect expected result table is detected as a mismatch.

    Returns:
        True if the mismatch was successfully caught by raising AssertionError.
    """
    actual_sample = {
        "scenario_credentials": "PASS",
        "scenario_missing_asset": "FAIL",
    }
    # Deliberately incorrect expected table (falsely claiming missing asset should PASS)
    deliberately_wrong_table = {
        "scenario_credentials": "PASS",
        "scenario_missing_asset": "PASS",
    }

    try:
        compare_approaches(actual_sample, deliberately_wrong_table)
    except AssertionError:
        return True  # Caught as expected

    return False


def get_fixture_scenarios() -> List[Dict[str, Any]]:
    """Return the documented fixture scenarios based on the lesson's translation flow."""
    return [
        # 1. Translation API credentials scenario
        {
            "id": "scenario_credentials",
            "name": "Translation API Credentials Protection",
            "asset": "Cloud translation API subscription keys and service endpoints",
            "threat": "Hardcoded credentials in IoT client code or public repositories leading to unauthorized API quota exhaustion or credential theft",
            "control": "Store keys in environment variables or Azure Key Vault, and route translation calls through backend Azure Functions rather than embedding keys on the IoT device",
            "residual_risk": "Compromise of the backend deployment environment or host server access could still expose secrets",
        },
        # 2. User-provided translation input scenario
        {
            "id": "scenario_user_input",
            "name": "User-Provided Translation Input Handling",
            "asset": "Spoken and textual user voice input (Japanese speech translated to English)",
            "threat": "Malicious prompt injection, oversized payload causing denial of service, or eavesdropping of unencrypted voice/text transcripts in transit",
            "control": "Enforce TLS 1.3 encryption in transit, restrict input payload length to 500 characters, and sanitize text before passing to language understanding",
            "residual_risk": "Third-party translation provider logs may retain transient voice samples subject to the cloud provider's privacy policy",
        },
        # 3. Translated response scenario
        {
            "id": "scenario_translated_response",
            "name": "Translated Response Verification",
            "asset": "Synthesized audio feedback and translated response text (English response translated back to Japanese)",
            "threat": "Tampering with translated response causing offensive synthesized audio, or unauthorized audio interception revealing private timer schedules",
            "control": "Validate translation output schema and apply profanity masking before passing translated text to the text-to-speech synthesizer",
            "residual_risk": "Subtle translation inaccuracies or culturally misleading phrasing might not be caught by automated profanity filters",
        },
        # 4. Boundary test scenario: missing asset
        {
            "id": "scenario_missing_asset",
            "name": "Missing Asset Boundary Case",
            # 'asset' intentionally omitted
            "threat": "Eavesdropping on unencrypted local WiFi communication",
            "control": "Enable WPA3 encryption on the local wireless network",
            "residual_risk": "Physical access to the local router could still allow packet capture",
        },
        # 5. Boundary test scenario: unrelated control
        {
            "id": "scenario_unrelated_control",
            "name": "Unrelated Control Boundary Case",
            "asset": "Translation API subscription keys",
            "threat": "Hardcoded credentials in client code leading to API key theft",
            "control": "Mount the IoT device in an aesthetically pleasing blue plastic case with extra ventilation",
            "residual_risk": "Keys remain completely unprotected in source code",
        },
    ]


def get_expected_results_table() -> Dict[str, str]:
    """Return Approach B's explicitly authored expected-result table."""
    return {
        "scenario_credentials": "PASS",
        "scenario_user_input": "PASS",
        "scenario_translated_response": "PASS",
        "scenario_missing_asset": "FAIL",
        "scenario_unrelated_control": "REVIEW",
    }


def main() -> None:
    """Run the rubric checker, compare approaches, and demonstrate mismatch detection."""
    print("=" * 80)
    print("Task R15-T023: Security Scenario Rubric Checker")
    print("Context: Lesson 6-4 Multi-Language Smart Timer Translation Architecture")
    print("Flow: Japanese Input -> English Translation -> Processing -> Japanese Response")
    print("=" * 80)
    print()

    scenarios = get_fixture_scenarios()
    expected_table = get_expected_results_table()

    print("APPROACH A: Direct Rubric Evaluation Results")
    print("-" * 80)
    actual_results: Dict[str, str] = {}
    for sc in scenarios:
        sc_id = sc["id"]
        name = sc["name"]
        verdict, reason = evaluate_scenario(sc)
        actual_results[sc_id] = verdict
        print(f"[{verdict:<6}] {name:<42} -> {reason}")
    print()

    print("APPROACH B: Comparison with Explicit Expected-Result Table")
    print("-" * 80)
    try:
        compare_approaches(actual_results, expected_table)
        print("✓ All 5 fixture scenarios matched Approach B's expected table perfectly!")
    except AssertionError as err:
        print(f"✗ Approach comparison failed: {err}")
    print()

    print("DEMONSTRATION: Intentional Mismatch Detection")
    print("-" * 80)
    if demonstrate_mismatch_detection():
        print("✓ Confirmed: A deliberately altered expected table is detected and raises AssertionError.")
    else:
        print("✗ Warning: Mismatch was not detected.")
    print("=" * 80)


if __name__ == "__main__":
    main()
