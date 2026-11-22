"""Sensor-message validation — scenario assessment (R15-T010).

Standard library only. A SIMULATION: does not use physical soil sensors,
microcontrollers, or real cloud IoT Hub instances.

Contract:
  - Input: list of sensor message records (dict or JSON strings).
  - Validation:
      'device_id': non-empty string.
      'timestamp': numeric (int or float).
      'reading': numeric sensor reading (strings/booleans rejected).
  - Processing:
      Valid messages deduplicated on (device_id, timestamp).
      Ordered chronologically by timestamp ascending.
      Messages for A at times 2 then 1 are returned in order 1,2.
      Duplicate A/1 is reported.
      String reading is rejected.
  - Scenario Assessment Focus:
      Adds three applied questions:
        1. Predict an output: chronological reordering of out-of-order packet arrival.
        2. Diagnose a failure: detection of unvalidated string reading payloads.
        3. Choose a boundary policy: first-seen vs overwrite deduplication to prevent replay tampering.
"""

import json


def validate_message(msg):
    """Validates schema for a sensor message."""
    if isinstance(msg, str):
        try:
            msg = json.loads(msg)
        except json.JSONDecodeError:
            return False, None, "Invalid JSON string"

    if not isinstance(msg, dict):
        return False, None, "Record is not a dictionary"

    device_id = msg.get("device_id")
    if not isinstance(device_id, str) or not device_id.strip():
        return False, None, "Invalid or missing 'device_id'"

    timestamp = msg.get("timestamp")
    if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
        return False, None, "Invalid or missing 'timestamp'"

    reading = msg.get("reading")
    if not isinstance(reading, (int, float)) or isinstance(reading, bool):
        return False, None, "Invalid or missing 'reading' (strings/booleans rejected)"

    return True, msg, None


def process_telemetry_stream(messages, deduplication_policy="reject_duplicate"):
    """Processes messages, performs deduplication, and returns sorted accepted records.

    Deduplication policies:
      - 'reject_duplicate': (default secure policy) keeps first-seen record, reports subsequent duplicates.
      - 'overwrite': insecure policy that updates on duplicate timestamps (exercised for assessment).
    """
    accepted_dict = {}
    duplicates = []
    rejected = []

    for item in messages:
        ok, parsed, reason = validate_message(item)
        if not ok:
            rejected.append({"raw": item, "reason": reason})
            continue

        key = (parsed["device_id"], parsed["timestamp"])
        if key in accepted_dict:
            duplicates.append({"device_id": parsed["device_id"], "timestamp": parsed["timestamp"]})
            if deduplication_policy == "overwrite":
                accepted_dict[key] = parsed
        else:
            accepted_dict[key] = parsed

    accepted = sorted(accepted_dict.values(), key=lambda m: m["timestamp"])
    return {
        "accepted": accepted,
        "duplicates": duplicates,
        "rejected": rejected,
    }


# Scenario Assessment Questions and Rationales
ASSESSMENT_QUESTIONS = {
    "Q1_PREDICT_OUTPUT": {
        "question": "Given messages arriving out-of-order [A@t=2, A@t=1], what is the order in accepted output?",
        "answer": [1, 2],
        "rationale": "The ingestion gateway guarantees chronological event-time ordering regardless of network arrival latency.",
    },
    "Q2_DIAGNOSE_FAILURE": {
        "question": "Why is payload {'device_id': 'A', 'timestamp': 3, 'reading': '50'} rejected?",
        "answer": "Non-numeric string reading rejected by schema validation.",
        "rationale": "Strict schema validation prevents type confusion, unauthorized code/script injection, and sensor spoofing.",
    },
    "Q3_CHOOSE_BOUNDARY_POLICY": {
        "question": "When a duplicate (device_id, timestamp) arrives with a conflicting value, what boundary policy should be chosen?",
        "answer": "reject_duplicate (First-seen retention)",
        "rationale": "Overwriting existing data on duplicate timestamps allows replay attacks to tamper with historical audit records.",
    },
}


if __name__ == "__main__":
    sample = [
        {"device_id": "A", "timestamp": 2, "reading": 23.5},
        {"device_id": "A", "timestamp": 1, "reading": 22.0},
        {"device_id": "A", "timestamp": 1, "reading": 22.1},
        {"device_id": "A", "timestamp": 3, "reading": "invalid"},
    ]
    res = process_telemetry_stream(sample)
    print("Accepted (Ordered):", res["accepted"])
    print("Duplicates:        ", res["duplicates"])
    print("Rejected:          ", res["rejected"])
