"""Sensor-message validation — evaluation experiment (R15-T009).

Standard library only. A SIMULATION: does not interact with physical smart shelves,
RFID readers, cameras, or cloud inventory platforms.

Contract:
  - Input: list of sensor message records (dict or JSON strings).
  - Validation:
      'device_id': non-empty string.
      'timestamp': numeric (int or float).
      'reading': numeric stock level/weight (strings/booleans rejected).
  - Processing:
      Valid messages deduplicated on (device_id, timestamp).
      Ordered chronologically by timestamp ascending.
      Duplicate A/1 is reported; string readings rejected.
  - Experiment Focus:
      Compare three small controlled configurations/batch sizes (Small N=4, Medium N=20, Large N=100).
      Evaluate throughput, classification counts, and correctness invariants without claiming
      real-world model accuracy.
"""

import json
import time


def validate_message(msg):
    """Validates schema for a stock sensor message."""
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


def process_stock_messages(messages):
    """Processes messages, performs deduplication, and returns sorted accepted records."""
    accepted = []
    duplicates = []
    rejected = []
    seen = set()

    for item in messages:
        ok, parsed, reason = validate_message(item)
        if not ok:
            rejected.append({"raw": item, "reason": reason})
            continue

        key = (parsed["device_id"], parsed["timestamp"])
        if key in seen:
            duplicates.append({"device_id": parsed["device_id"], "timestamp": parsed["timestamp"]})
        else:
            seen.add(key)
            accepted.append(parsed)

    accepted.sort(key=lambda m: m["timestamp"])
    return {
        "accepted": accepted,
        "duplicates": duplicates,
        "rejected": rejected,
    }


def generate_experiment_dataset(size: int, dup_ratio=0.2, bad_ratio=0.1):
    """Generates synthetic deterministic stock message dataset for evaluation."""
    dataset = []
    num_dup = int(size * dup_ratio)
    num_bad = int(size * bad_ratio)
    num_valid = size - num_dup - num_bad

    # Valid records with randomized/out-of-order timestamps
    for i in range(num_valid):
        dev = f"shelf_{i % 5}"
        ts = (num_valid - i) * 10
        dataset.append({"device_id": dev, "timestamp": ts, "reading": (i * 3) % 50})

    # Duplicates of earlier valid records
    for i in range(num_dup):
        target = dataset[i % max(1, num_valid)]
        dataset.append({
            "device_id": target["device_id"],
            "timestamp": target["timestamp"],
            "reading": target["reading"] + 1,  # different reading, same key
        })

    # Malformed / string readings
    for i in range(num_bad):
        dataset.append({
            "device_id": f"shelf_{i}",
            "timestamp": 9999 + i,
            "reading": "error_out_of_stock_str",
        })

    return dataset


def run_evaluation_experiment():
    """Runs controlled experiment across three batch configurations."""
    configs = {
        "Small (N=4)": [
            {"device_id": "A", "timestamp": 2, "reading": 15},
            {"device_id": "A", "timestamp": 1, "reading": 20},
            {"device_id": "A", "timestamp": 1, "reading": 20},  # dup
            {"device_id": "A", "timestamp": 3, "reading": "out_of_stock"},  # string reading
        ],
        "Medium (N=20)": generate_experiment_dataset(20),
        "Large (N=100)": generate_experiment_dataset(100),
    }

    report = {}
    for name, dataset in configs.items():
        t0 = time.perf_counter()
        result = process_stock_messages(dataset)
        elapsed_us = (time.perf_counter() - t0) * 1e6

        report[name] = {
            "total_input": len(dataset),
            "accepted_count": len(result["accepted"]),
            "duplicate_count": len(result["duplicates"]),
            "rejected_count": len(result["rejected"]),
            "elapsed_microseconds": round(elapsed_us, 2),
            "invariant_holds": len(dataset) == (
                len(result["accepted"]) + len(result["duplicates"]) + len(result["rejected"])
            ),
        }
    return report


if __name__ == "__main__":
    rep = run_evaluation_experiment()
    for cfg, stats in rep.items():
        print(f"[{cfg}] -> {stats}")
