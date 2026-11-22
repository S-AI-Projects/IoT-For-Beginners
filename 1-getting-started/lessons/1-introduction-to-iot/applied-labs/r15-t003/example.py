"""Sensor-message validation — compare two approaches (R15-T003).

Standard library only. A SIMULATION: does not connect to real IoT broker or cloud.

Contract:
  - Input: list of sensor message records (dict or JSON string).
  - Required fields:
      - 'device_id': non-empty string
      - 'timestamp': numeric (int or float)
      - 'reading': numeric (int or float; strings, booleans, null rejected)
  - Processing:
      - Valid messages are deduplicated on (device_id, timestamp) pair.
      - Duplicates are rejected / reported as duplicate.
      - Malformed or type-violating messages (e.g. string reading) are rejected.
      - Accepted messages are sorted by timestamp in ascending order.
  - Focus: Compare the direct procedural implementation with a functional
    reference / table-driven model on identical input fixtures.
"""

import json


def parse_message(raw):
    """Parses raw input into a dictionary if provided as a JSON string."""
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    elif isinstance(raw, dict):
        return raw
    return None


def validate_message(msg):
    """Validates message schema.

    Returns (is_valid, error_reason).
    """
    if not isinstance(msg, dict):
        return False, "Malformed message: not a valid dictionary"

    device_id = msg.get("device_id")
    if not isinstance(device_id, str) or not device_id.strip():
        return False, "Invalid or missing 'device_id': must be non-empty string"

    timestamp = msg.get("timestamp")
    if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
        return False, "Invalid or missing 'timestamp': must be numeric"

    reading = msg.get("reading")
    if not isinstance(reading, (int, float)) or isinstance(reading, bool):
        return False, "Invalid or missing 'reading': must be numeric (strings/booleans rejected)"

    return True, None


# ==========================================
# Approach 1: Direct Procedural Implementation
# ==========================================
def process_messages_direct(raw_messages):
    """Processes, deduplicates, and sorts messages using procedural set tracking."""
    accepted = []
    duplicates = []
    rejected = []
    seen_keys = set()

    for item in raw_messages:
        msg = parse_message(item)
        is_valid, reason = validate_message(msg)
        if not is_valid:
            rejected.append({"raw": item, "reason": reason})
            continue

        key = (msg["device_id"], msg["timestamp"])
        if key in seen_keys:
            duplicates.append({"device_id": msg["device_id"], "timestamp": msg["timestamp"]})
        else:
            seen_keys.add(key)
            accepted.append(msg)

    accepted.sort(key=lambda m: m["timestamp"])
    return {
        "accepted": accepted,
        "duplicates": duplicates,
        "rejected": rejected,
    }


# ==========================================
# Approach 2: Functional / Reference Approach
# ==========================================
def process_messages_reference(raw_messages):
    """Processes messages using an independent pipeline / table comparison."""
    parsed = [parse_message(m) for m in raw_messages]

    valid = []
    rejected = []
    for raw, msg in zip(raw_messages, parsed):
        ok, reason = validate_message(msg)
        if ok:
            valid.append(msg)
        else:
            rejected.append({"raw": raw, "reason": reason})

    accepted = []
    duplicates = []
    seen = set()
    for m in valid:
        k = (m["device_id"], m["timestamp"])
        if k in seen:
            duplicates.append({"device_id": m["device_id"], "timestamp": m["timestamp"]})
        else:
            seen.add(k)
            accepted.append(m)

    accepted = sorted(accepted, key=lambda x: x["timestamp"])
    return {
        "accepted": accepted,
        "duplicates": duplicates,
        "rejected": rejected,
    }


if __name__ == "__main__":
    sample = [
        {"device_id": "A", "timestamp": 2, "reading": 23.5},
        {"device_id": "A", "timestamp": 1, "reading": 22.0},
        {"device_id": "A", "timestamp": 1, "reading": 22.1},  # duplicate A/1
        {"device_id": "A", "timestamp": 3, "reading": "bad_reading"},  # string reading
    ]
    res1 = process_messages_direct(sample)
    res2 = process_messages_reference(sample)
    print("Direct approach:", res1)
    print("Equivalence verified:", res1 == res2)
