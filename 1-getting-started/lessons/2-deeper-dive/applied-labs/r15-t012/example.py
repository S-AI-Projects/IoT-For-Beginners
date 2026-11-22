"""
Sensor Message Validation — Boundary-Case Lesson Extension (R15-T012)

Lesson reference: 1-getting-started/lessons/2-deeper-dive/README.md
Concept: IoT devices stream telemetry messages to gateways or cloud brokers.
Receiving services must validate telemetry schemas, ensure numeric reading integrity,
reject duplicate telemetry records, and order out-of-order arrivals chronologically.

Validation Rules:
1. JSON message must contain 'device_id' (str), 'timestamp' (int/float), and 'reading' (numeric, not bool/str).
2. 'reading' must be strictly numeric (int or float, rejecting string-encoded numbers, None, bools).
3. Duplicate (device_id, timestamp) pairs are rejected and reported.
4. Accepted messages are ordered chronologically by timestamp ascending.
"""

import json
from typing import Any, Dict, List, Set, Tuple


def validate_and_order_messages(
    messages: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates a list of message dicts.
    Returns:
        (accepted_sorted, rejected_invalid, rejected_duplicates)
    """
    accepted = []
    invalid = []
    duplicates = []
    seen_keys: Set[Tuple[str, float]] = set()

    for msg in messages:
        # Check basic type
        if not isinstance(msg, dict):
            invalid.append({"message": msg, "reason": "Message is not a JSON object/dict"})
            continue

        # Check required keys
        if "device_id" not in msg or "timestamp" not in msg or "reading" not in msg:
            invalid.append({"message": msg, "reason": "Missing required fields (device_id, timestamp, reading)"})
            continue

        device_id = msg["device_id"]
        timestamp = msg["timestamp"]
        reading = msg["reading"]

        # Validate device_id
        if not isinstance(device_id, str) or not device_id.strip():
            invalid.append({"message": msg, "reason": "device_id must be a non-empty string"})
            continue

        # Validate timestamp (numeric, not boolean)
        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            invalid.append({"message": msg, "reason": "timestamp must be numeric (int or float)"})
            continue

        # Validate reading (numeric, strictly not boolean or string)
        if isinstance(reading, bool) or not isinstance(reading, (int, float)):
            invalid.append({"message": msg, "reason": "reading must be numeric (int or float), strings/booleans rejected"})
            continue

        # Check for duplicate (device_id, timestamp)
        key = (device_id, float(timestamp))
        if key in seen_keys:
            duplicates.append({"message": msg, "reason": f"Duplicate record for device {device_id} at timestamp {timestamp}"})
            continue

        seen_keys.add(key)
        accepted.append(msg)

    # Order accepted messages by timestamp ascending
    accepted_sorted = sorted(accepted, key=lambda m: m["timestamp"])
    return accepted_sorted, invalid, duplicates


def run_demo():
    sample_data = [
        {"device_id": "A", "timestamp": 2, "reading": 22.4},
        {"device_id": "A", "timestamp": 1, "reading": 21.0},
        {"device_id": "A", "timestamp": 1, "reading": 21.5},  # duplicate
        {"device_id": "B", "timestamp": 3, "reading": "invalid_string"},  # string reading
    ]
    accepted, invalid, duplicates = validate_and_order_messages(sample_data)
    print("Accepted & Sorted:", accepted)
    print("Invalid:", invalid)
    print("Duplicates:", duplicates)
    return accepted, invalid, duplicates


if __name__ == "__main__":
    run_demo()
