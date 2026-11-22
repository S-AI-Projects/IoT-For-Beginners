import json
from typing import Any, Dict, List


REQUIRED_FIELDS = ("asset", "threat", "control", "residual-risk")

# Maps threat categories to expected control keywords for structural consistency checks
THREAT_CONTROL_KEYWORDS = {
    "voice_spoofing": ("speaker", "voiceprint", "authentication", "verification", "biometric"),
    "locale_injection": ("sanitize", "allowlist", "locale", "encoding", "validation"),
    "transcript_leakage": ("encrypt", "tls", "redact", "retention", "anonymize"),
}


def evaluate_scenario(scenario: Any) -> Dict[str, Any]:
    """
    Evaluates a security scenario against the structural rubric:
    - Missing/empty asset or required fields -> status = "FAIL"
    - Control unrelated to named threat category -> status = "FLAG_FOR_REVIEW"
    - Complete and internally consistent -> status = "PASS"
    """
    if not isinstance(scenario, dict):
        return {
            "scenario_id": None,
            "status": "FAIL",
            "errors": ["Scenario payload must be a JSON object/dict"],
            "review_note": None,
        }

    sid = scenario.get("id", "unknown")
    errors: List[str] = []

    for field in REQUIRED_FIELDS:
        val = scenario.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"Missing or empty required field: {field}")

    if errors:
        return {
            "scenario_id": sid,
            "status": "FAIL",
            "errors": errors,
            "review_note": "Rejected due to incomplete structural fields; fix missing fields to recover.",
        }

    threat_cat = scenario.get("threat_category", "").strip().lower()
    control_text = scenario["control"].lower()
    expected_keywords = THREAT_CONTROL_KEYWORDS.get(threat_cat, ())

    if not expected_keywords or not any(kw in control_text for kw in expected_keywords):
        return {
            "scenario_id": sid,
            "status": "FLAG_FOR_REVIEW",
            "errors": [],
            "review_note": (
                f"Control does not reference expected mitigation terms for threat_category={threat_cat!r}; "
                "flagged for human review."
            ),
        }

    return {
        "scenario_id": sid,
        "status": "PASS",
        "errors": [],
        "review_note": "Structural rubric passed; human reviewer still evaluates qualitative rationale.",
    }


def evaluate_batch_with_recovery(scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Processes a batch of scenarios, logging invalid/missing-data failures and recovering on valid entries."""
    results = []
    recovered_after_failure = False
    saw_failure = False

    for sc in scenarios:
        res = evaluate_scenario(sc)
        if res["status"] == "FAIL":
            saw_failure = True
        elif saw_failure and res["status"] == "PASS":
            recovered_after_failure = True
        results.append(res)

    return {
        "results": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == "PASS"),
            "failed": sum(1 for r in results if r["status"] == "FAIL"),
            "flagged_for_review": sum(1 for r in results if r["status"] == "FLAG_FOR_REVIEW"),
            "recovered_on_subsequent_valid_input": recovered_after_failure,
        },
    }


FIXTURE_SCENARIOS = [
    {
        "id": "SC-01-MISSING-ASSET",
        "asset": "",
        "threat_category": "transcript_leakage",
        "threat": "Unencrypted multilingual voice transcripts intercepted in transit.",
        "control": "Enforce TLS 1.3 transport encryption and redact PII before storage.",
        "residual-risk": "Low risk if device root certificates are compromised.",
    },
    {
        "id": "SC-02-COMPLETE-PASS",
        "asset": "Multilingual Smart Speaker Speech-to-Text Pipeline",
        "threat_category": "locale_injection",
        "threat": "Maliciously crafted BCP-47 locale tags trigger parser errors or fallback bypass.",
        "control": "Enforce strict allowlist validation on supported locale codes before routing audio.",
        "residual-risk": "Unsupported regional dialects may fail closed and require manual selection.",
    },
    {
        "id": "SC-03-UNRELATED-CONTROL",
        "asset": "On-Device Wake-Word & Language Selector",
        "threat_category": "voice_spoofing",
        "threat": "Replay attack using recorded multilingual wake-word audio.",
        "control": "Enable automatic screen brightness dimming after 30 seconds of inactivity.",
        "residual-risk": "High residual risk because display dimming does not authenticate speaker audio.",
    },
]


if __name__ == "__main__":
    print(json.dumps(evaluate_batch_with_recovery(FIXTURE_SCENARIOS), indent=2))
