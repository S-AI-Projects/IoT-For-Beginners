import json
from typing import Any, Dict, List, Tuple


def validate_and_order_messages(raw_payloads: List[str]) -> Dict[str, Any]:
    """
    Validates JSON sensor messages, rejects malformed payloads or duplicates,
    and returns accepted messages ordered by timestamp.
    """
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen_pairs: set[Tuple[str, int | float]] = set()

    for raw in raw_payloads:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as e:
            rejected.append({"raw": raw, "reason": f"Invalid JSON: {e.msg}"})
            continue

        if not isinstance(msg, dict):
            rejected.append({"raw": raw, "reason": "Payload must be a JSON object"})
            continue

        device_id = msg.get("device_id")
        timestamp = msg.get("timestamp")
        reading = msg.get("reading")

        if not isinstance(device_id, str) or not device_id.strip():
            rejected.append({"message": msg, "reason": "Missing or invalid device_id"})
            continue

        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            rejected.append({"message": msg, "reason": "Timestamp must be numeric"})
            continue

        if isinstance(reading, bool) or not isinstance(reading, (int, float)):
            rejected.append({"message": msg, "reason": "Reading must be numeric"})
            continue

        pair = (device_id, timestamp)
        if pair in seen_pairs:
            rejected.append({
                "message": msg,
                "reason": f"Duplicate device/timestamp pair: {device_id}/{timestamp}"
            })
            continue

        seen_pairs.add(pair)
        accepted.append({
            "device_id": device_id,
            "timestamp": timestamp,
            "reading": reading
        })

    accepted.sort(key=lambda item: item["timestamp"])
    return {"accepted": accepted, "rejected": rejected}


if __name__ == "__main__":
    sample_inputs = [
        '{"device_id": "A", "timestamp": 2, "reading": 15}',
        '{"device_id": "A", "timestamp": 1, "reading": 12}',
        '{"device_id": "A", "timestamp": 1, "reading": 99}',
        '{"device_id": "A", "timestamp": 3, "reading": "invalid_str"}'
    ]
    print(json.dumps(validate_and_order_messages(sample_inputs), indent=2))
