import json
from typing import Any, Dict, List

REQUIRED_FIELDS = ("asset", "threat", "control", "residual-risk")

THREAT_CONTROL_KEYWORDS = {
    "model_tampering": ("sign", "hash", "checksum", "integrity", "verify", "read-only"),
    "camera_spoofing": ("tls", "auth", "certificate", "mutual", "encrypt", "allowlist"),
    "telemetry_interception": ("tls", "encrypt", "https", "certificate", "sas"),
}


def evaluate_scenario_direct(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Direct structural rubric checker verifying field completeness and threat-control alignment."""
    missing = [
        field for field in REQUIRED_FIELDS
        if not isinstance(scenario.get(field), str) or not scenario.get(field).strip()
    ]
    if missing:
        return {
            "id": scenario.get("id", "UNKNOWN"),
            "status": "FAIL",
            "reason": f"Missing required field(s): {missing}",
        }

    threat = scenario["threat"].strip().lower()
    control = scenario["control"].strip().lower()
    expected_terms = THREAT_CONTROL_KEYWORDS.get(threat, ())
    if expected_terms and not any(term in control for term in expected_terms):
        return {
            "id": scenario["id"],
            "status": "FLAG_FOR_REVIEW",
            "reason": f"Control does not address named threat ({threat}); human review required.",
        }

    return {
        "id": scenario["id"],
        "status": "PASS",
        "reason": "All required fields present and control aligns with named threat.",
    }


EXPECTED_STATUS_TABLE = {
    "SC-01-MISSING-ASSET": "FAIL",
    "SC-02-COMPLETE-PASS": "PASS",
    "SC-03-UNRELATED-CONTROL": "FLAG_FOR_REVIEW",
}


def evaluate_scenario_simple_table(scenario: Dict[str, Any]) -> str:
    """Simpler independent lookup against an explicit expected-result table."""
    sid = scenario.get("id", "")
    if not str(scenario.get("asset", "")).strip():
        return "FAIL"
    return EXPECTED_STATUS_TABLE.get(sid, "FLAG_FOR_REVIEW")


FIXTURE_SCENARIOS: List[Dict[str, str]] = [
    {
        "id": "SC-01-MISSING-ASSET",
        "asset": "",
        "threat": "model_tampering",
        "control": "signed_tflite_model_hash_verification",
        "residual-risk": "Unsigned model weights could be swapped on local storage.",
    },
    {
        "id": "SC-02-COMPLETE-PASS",
        "asset": "edge_fruit_detector_camera_node",
        "threat": "model_tampering",
        "control": "signed_tflite_model_hash_verification",
        "residual-risk": "Compromised signing key still requires key rotation.",
    },
    {
        "id": "SC-03-UNRELATED-CONTROL",
        "asset": "edge_fruit_detector_camera_node",
        "threat": "model_tampering",
        "control": "conveyor_belt_lubrication_schedule",
        "residual-risk": "Mechanical maintenance does not prevent model tampering.",
    },
]


def compare_approaches(scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compares the direct implementation with the simpler explicit expected-result table on identical inputs."""
    comparisons = []
    for sc in scenarios:
        direct_res = evaluate_scenario_direct(sc)
        table_status = evaluate_scenario_simple_table(sc)
        comparisons.append({
            "id": sc.get("id", "UNKNOWN"),
            "direct_status": direct_res["status"],
            "simple_table_status": table_status,
            "match": direct_res["status"] == table_status,
            "reason": direct_res["reason"],
        })
    return comparisons


if __name__ == "__main__":
    print(json.dumps({"approach_comparison": compare_approaches(FIXTURE_SCENARIOS)}, indent=2))
