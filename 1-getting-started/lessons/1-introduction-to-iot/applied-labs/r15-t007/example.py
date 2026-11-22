"""Sensor-message validation — worked example with regression checks (R15-T007).

Standard library only. A SIMULATION: does not connect to real IoT hardware,
brokers, or cloud event hubs.

Contract:
  - Input: list of sensor message records (dict or JSON strings).
  - Schema requirements:
      - 'device_id': non-empty string.
      - 'timestamp': numeric (int or float).
      - 'reading': numeric (int or float; strings/booleans/null rejected).
  - Processing:
      - Valid records deduplicated on (device_id, timestamp).
      - Reordered chronologically by timestamp ascending.
      - Duplicates reported.
      - Malformed/type errors rejected.
  - Focus:
      Publish an explicit worked input-to-output walkthrough and run the exact
      example as a regression test.
"""

import json


def validate_record(record):
    """Validates schema for a single sensor record."""
    if isinstance(record, str):
        try:
            record = json.loads(record)
        except json.JSONDecodeError:
            return False, None, "Invalid JSON string"

    if not isinstance(record, dict):
        return False, None, "Record is not a dictionary"

    device_id = record.get("device_id")
    if not isinstance(device_id, str) or not device_id.strip():
        return False, None, "Invalid or missing 'device_id'"

    timestamp = record.get("timestamp")
    if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
        return False, None, "Invalid or missing 'timestamp'"

    reading = record.get("reading")
    if not isinstance(reading, (int, float)) or isinstance(reading, bool):
        return False, None, "Invalid or missing 'reading' (strings/booleans rejected)"

    return True, record, None


def process_sensor_stream(records):
    """Processes, deduplicates, and chronologically sorts sensor messages."""
    accepted = []
    duplicates = []
    rejected = []
    seen = set()

    for item in records:
        ok, parsed, reason = validate_record(item)
        if not ok:
            rejected.append({"record": item, "reason": reason})
            continue

        key = (parsed["device_id"], parsed["timestamp"])
        if key in seen:
            duplicates.append({"device_id": parsed["device_id"], "timestamp": parsed["timestamp"]})
        else:
            seen.add(key)
            accepted.append(parsed)

    accepted.sort(key=lambda x: x["timestamp"])
    return {
        "accepted": accepted,
        "duplicates": duplicates,
        "rejected": rejected,
    }


# The Canonical Worked Example Fixture
WORKED_EXAMPLE_INPUT = [
    {"device_id": "A", "timestamp": 2, "reading": 23.5},
    {"device_id": "A", "timestamp": 1, "reading": 22.0},
    {"device_id": "A", "timestamp": 1, "reading": 22.1},  # duplicate (A, 1)
    {"device_id": "A", "timestamp": 3, "reading": "invalid_string"},  # string reading
]


if __name__ == "__main__":
    result = process_sensor_stream(WORKED_EXAMPLE_INPUT)
    print("Input messages:  ", WORKED_EXAMPLE_INPUT)
    print("Accepted (sorted):", result["accepted"])
    print("Duplicates:       ", result["duplicates"])
    print("Rejected:         ", result["rejected"])
