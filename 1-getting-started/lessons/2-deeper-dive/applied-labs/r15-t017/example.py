"""
Sensor Message Validation — Worked Example with Checks (R15-T017)

Lesson reference: 1-getting-started/lessons/2-deeper-dive/README.md
Concept: Edge IoT gateways ingest streaming sensor telemetry. To preserve downstream integrity,
gateways perform schema validation, reject duplicate device/timestamp transmissions,
and chronologically sort accepted messages before emitting to message brokers.

Focus:
Worked input-to-output explanation tracing each input message through validation,
deduplication, and timestamp ordering, executed as a strict regression test suite.

Contract:
1. Message must have device_id (str), timestamp (numeric: int or float), reading (numeric).
2. 'reading' must be strictly numeric (float or int); string readings are rejected.
3. Duplicate (device_id, timestamp) pairs are reported and discarded.
4. Accepted messages are ordered by timestamp ascending.
"""

from typing import Any, Dict, List, Set, Tuple


def process_telemetry_batch(
    messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Ingests and validates a raw telemetry message batch.
    Returns structured results with step-by-step audit details:
    {
        "accepted": [...], # sorted by timestamp
        "rejected_invalid": [...],
        "rejected_duplicates": [...],
        "trace": [...] # worked trace explaining each message's outcome
    }
    """
    accepted = []
    rejected_invalid = []
    rejected_duplicates = []
    seen_keys: Set[Tuple[str, float]] = set()
    trace = []

    for idx, msg in enumerate(messages):
        step_log = {"index": idx, "input": msg}

        if not isinstance(msg, dict):
            reason = "Not a valid JSON object"
            rejected_invalid.append({"message": msg, "reason": reason})
            step_log["outcome"] = "INVALID"
            step_log["reason"] = reason
            trace.append(step_log)
            continue

        if "device_id" not in msg or "timestamp" not in msg or "reading" not in msg:
            reason = "Missing required keys (device_id, timestamp, reading)"
            rejected_invalid.append({"message": msg, "reason": reason})
            step_log["outcome"] = "INVALID"
            step_log["reason"] = reason
            trace.append(step_log)
            continue

        dev = msg["device_id"]
        ts = msg["timestamp"]
        val = msg["reading"]

        if not isinstance(dev, str) or not dev.strip():
            reason = "device_id must be non-empty string"
            rejected_invalid.append({"message": msg, "reason": reason})
            step_log["outcome"] = "INVALID"
            step_log["reason"] = reason
            trace.append(step_log)
            continue

        if isinstance(ts, bool) or not isinstance(ts, (int, float)):
            reason = "timestamp must be numeric"
            rejected_invalid.append({"message": msg, "reason": reason})
            step_log["outcome"] = "INVALID"
            step_log["reason"] = reason
            trace.append(step_log)
            continue

        # Reject string or boolean readings
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            reason = "reading must be numeric (strings and booleans rejected)"
            rejected_invalid.append({"message": msg, "reason": reason})
            step_log["outcome"] = "INVALID"
            step_log["reason"] = reason
            trace.append(step_log)
            continue

        # Check duplicates
        key = (dev, float(ts))
        if key in seen_keys:
            reason = f"Duplicate detected for device '{dev}' at timestamp {ts}"
            rejected_duplicates.append({"message": msg, "reason": reason})
            step_log["outcome"] = "DUPLICATE"
            step_log["reason"] = reason
            trace.append(step_log)
            continue

        seen_keys.add(key)
        accepted.append(msg)
        step_log["outcome"] = "ACCEPTED"
        step_log["reason"] = f"Valid message queued (timestamp {ts})"
        trace.append(step_log)

    sorted_accepted = sorted(accepted, key=lambda m: m["timestamp"])
    return {
        "accepted": sorted_accepted,
        "rejected_invalid": rejected_invalid,
        "rejected_duplicates": rejected_duplicates,
        "trace": trace,
    }


def run_demo():
    input_batch = [
        {"device_id": "A", "timestamp": 2, "reading": 25.1},
        {"device_id": "A", "timestamp": 1, "reading": 24.8},
        {"device_id": "A", "timestamp": 1, "reading": 24.9},  # duplicate A/1
        {"device_id": "B", "timestamp": 3, "reading": "bad_reading"},  # string reading
    ]
    res = process_telemetry_batch(input_batch)
    print("=== Worked Input-to-Output Walkthrough ===")
    for t in res["trace"]:
        print(f"[{t['outcome']}] Index {t['index']}: {t['input']} -> {t['reason']}")
    print("\nFinal Sorted Accepted Telemetry:")
    for m in res["accepted"]:
        print(f"  {m}")
    return res


if __name__ == "__main__":
    run_demo()
