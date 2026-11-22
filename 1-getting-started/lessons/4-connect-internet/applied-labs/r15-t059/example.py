import json
from typing import Any, Dict, List, Union


def validate_and_order_messages(raw_messages: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Validates JSON sensor messages with device_id, timestamp, and numeric reading.
    Orders accepted messages by timestamp and rejects duplicate (device_id, timestamp) pairs.
    """
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen_pairs = set()

    for idx, item in enumerate(raw_messages):
        if isinstance(item, str):
            try:
                msg = json.loads(item)
            except json.JSONDecodeError as exc:
                rejected.append({"index": idx, "raw": item, "reason": f"Malformed JSON: {exc.msg}"})
                continue
        elif isinstance(item, dict):
            msg = item
        else:
            rejected.append({"index": idx, "raw": item, "reason": "Message must be a JSON object"})
            continue

        if not isinstance(msg, dict):
            rejected.append({"index": idx, "raw": item, "reason": "Decoded JSON must be an object"})
            continue

        device_id = msg.get("device_id")
        timestamp = msg.get("timestamp")
        reading = msg.get("reading")

        if not isinstance(device_id, str) or not device_id.strip():
            rejected.append({"index": idx, "message": msg, "reason": "Invalid or missing device_id"})
            continue

        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            rejected.append({"index": idx, "message": msg, "reason": "Invalid or missing numeric timestamp"})
            continue

        if isinstance(reading, bool) or not isinstance(reading, (int, float)):
            rejected.append({"index": idx, "message": msg, "reason": "Reading must be numeric (int or float)"})
            continue

        pair = (device_id, timestamp)
        if pair in seen_pairs:
            rejected.append({
                "index": idx,
                "message": msg,
                "reason": f"Duplicate device_id/timestamp pair: {device_id}/{timestamp}",
            })
            continue

        seen_pairs.add(pair)
        accepted.append({
            "device_id": device_id,
            "timestamp": timestamp,
            "reading": reading,
        })

    ordered_accepted = sorted(accepted, key=lambda m: (m["timestamp"], m["device_id"]))
    return {
        "accepted": ordered_accepted,
        "rejected": rejected,
    }


def evaluate_applied_questions() -> List[Dict[str, Any]]:
    """Three applied scenario-assessment questions with rationales and executable checks."""
    q1_input = [
        {"device_id": "A", "timestamp": 2, "reading": 41.5},
        {"device_id": "A", "timestamp": 1, "reading": 39.0},
    ]
    q1_out = validate_and_order_messages(q1_input)
    q1_timestamps = [m["timestamp"] for m in q1_out["accepted"]]

    q2_input = [
        {"device_id": "A", "timestamp": 1, "reading": "42.0"},
        {"device_id": "A", "timestamp": 1, "reading": 42.0},
    ]
    q2_out = validate_and_order_messages(q2_input)

    q3_input = [
        {"device_id": "A", "timestamp": 1, "reading": 20.0},
        {"device_id": "A", "timestamp": 1, "reading": 25.0},
    ]
    q3_out = validate_and_order_messages(q3_input)

    return [
        {
            "id": "Q1-PREDICT-OUTPUT",
            "type": "predict_output",
            "question": "Given messages for device A arriving out-of-order at timestamps 2 then 1, what timestamp order is returned?",
            "answer": [1, 2],
            "rationale": "Accepted messages are sorted chronologically by timestamp so downstream telemetry consumers process events in event-time order rather than arrival order.",
            "check_passed": q1_timestamps == [1, 2] and len(q1_out["rejected"]) == 0,
        },
        {
            "id": "Q2-DIAGNOSE-FAILURE",
            "type": "diagnose_failure",
            "question": "Why is the first message {device_id: A, timestamp: 1, reading: '42.0'} rejected while the second identical-key numeric message succeeds?",
            "answer": "String reading rejected before deduplication key registration",
            "rationale": "Schema validation runs prior to recording (device_id, timestamp) in seen_pairs, so a malformed string reading fails type checking without poisoning the deduplication set for a subsequent valid retry.",
            "check_passed": len(q2_out["rejected"]) == 1 and len(q2_out["accepted"]) == 1,
        },
        {
            "id": "Q3-BOUNDARY-POLICY",
            "type": "choose_boundary_policy",
            "question": "When two valid messages share the exact same (device_id, timestamp) key (A/1), which boundary policy is enforced?",
            "answer": "First-seen wins; subsequent duplicate (device_id, timestamp) pairs are rejected",
            "rationale": "Enforcing idempotent first-seen retention prevents duplicate telemetry packets from double-counting readings while reporting duplicates explicitly for auditability.",
            "check_passed": len(q3_out["accepted"]) == 1 and q3_out["accepted"][0]["reading"] == 20.0 and len(q3_out["rejected"]) == 1,
        },
    ]


FIXTURE_MESSAGES = [
    json.dumps({"device_id": "A", "timestamp": 2, "reading": 24.5}),
    json.dumps({"device_id": "A", "timestamp": 1, "reading": 22.0}),
    json.dumps({"device_id": "A", "timestamp": 1, "reading": 22.0}),
    json.dumps({"device_id": "B", "timestamp": 3, "reading": "bad_string"}),
]


if __name__ == "__main__":
    output = {
        "validation_result": validate_and_order_messages(FIXTURE_MESSAGES),
        "applied_questions": evaluate_applied_questions(),
    }
    print(json.dumps(output, indent=2))
