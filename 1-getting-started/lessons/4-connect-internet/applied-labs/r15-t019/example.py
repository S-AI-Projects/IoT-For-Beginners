"""
Sensor-Message Validation — Evaluation Experiment (R15-T019)

Lesson reference: 1-getting-started/lessons/4-connect-internet/README.md
Concept: Connecting an IoT device to the Internet involves sending telemetry over MQTT/HTTP.
To manage network overhead, devices often buffer telemetry into batches.
This lab evaluates the message validation and deduplication contract across three controlled
batch size configurations, measuring acceptance rate, duplicate rate, and sorting efficiency.

Contract:
1. Message contains device_id (str), timestamp (numeric: int or float), and reading (numeric).
2. 'reading' must be strictly numeric (rejecting string/bool/None).
3. Duplicate (device_id, timestamp) pairs are detected and reported.
4. Accepted messages are ordered by timestamp ascending.
5. Evaluates 3 controlled configurations (Small, Medium, Large) reporting correctness
   and observed performance trade-offs without claiming real-world model accuracy.
"""

import time
from typing import Any, Dict, List, Set, Tuple


def validate_and_order_telemetry(
    messages: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates a telemetry batch, filters invalid/duplicate entries,
    and returns (accepted_sorted, invalid, duplicates).
    """
    accepted = []
    invalid = []
    duplicates = []
    seen: Set[Tuple[str, float]] = set()

    for msg in messages:
        if not isinstance(msg, dict):
            invalid.append({"message": msg, "reason": "Not a dict"})
            continue

        if "device_id" not in msg or "timestamp" not in msg or "reading" not in msg:
            invalid.append({"message": msg, "reason": "Missing keys"})
            continue

        dev = msg["device_id"]
        ts = msg["timestamp"]
        val = msg["reading"]

        if not isinstance(dev, str) or not dev.strip():
            invalid.append({"message": msg, "reason": "Invalid device_id"})
            continue

        if isinstance(ts, bool) or not isinstance(ts, (int, float)):
            invalid.append({"message": msg, "reason": "Invalid timestamp"})
            continue

        # Reject string/boolean readings
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            invalid.append({"message": msg, "reason": "Reading must be numeric"})
            continue

        key = (dev, float(ts))
        if key in seen:
            duplicates.append({"message": msg, "reason": f"Duplicate for {dev} at {ts}"})
            continue

        seen.add(key)
        accepted.append(msg)

    # Sort accepted messages chronologically
    sorted_accepted = sorted(accepted, key=lambda m: m["timestamp"])
    return sorted_accepted, invalid, duplicates


def evaluate_batch_configuration(name: str, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluates a batch configuration reporting contract metrics."""
    start_time = time.perf_counter()
    accepted, invalid, duplicates = validate_and_order_telemetry(batch)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    total = len(batch)
    accept_rate = (len(accepted) / total) if total > 0 else 0.0
    duplicate_rate = (len(duplicates) / total) if total > 0 else 0.0
    invalid_rate = (len(invalid) / total) if total > 0 else 0.0

    return {
        "config_name": name,
        "total_messages": total,
        "accepted_count": len(accepted),
        "invalid_count": len(invalid),
        "duplicate_count": len(duplicates),
        "accept_rate": accept_rate,
        "duplicate_rate": duplicate_rate,
        "invalid_rate": invalid_rate,
        "elapsed_ms": elapsed_ms,
        "is_sorted": all(accepted[i]["timestamp"] <= accepted[i + 1]["timestamp"] for i in range(len(accepted) - 1)),
    }


def run_experiment() -> Dict[str, Dict[str, Any]]:
    """Runs evaluation across three controlled configurations."""
    # Config 1: Small benchmark batch (4 messages)
    small_batch = [
        {"device_id": "A", "timestamp": 2, "reading": 22.0},
        {"device_id": "A", "timestamp": 1, "reading": 21.0},
        {"device_id": "A", "timestamp": 1, "reading": 21.5},  # duplicate
        {"device_id": "B", "timestamp": 3, "reading": "str_err"},  # invalid
    ]

    # Config 2: Medium batch (16 messages) with 25% duplicates, 25% invalid
    medium_batch = []
    for i in range(16):
        if i % 4 == 0:
            # duplicate
            medium_batch.append({"device_id": "M1", "timestamp": 100, "reading": 20.0})
        elif i % 4 == 1:
            # invalid string
            medium_batch.append({"device_id": "M2", "timestamp": i, "reading": "bad"})
        else:
            # valid out-of-order
            medium_batch.append({"device_id": "M3", "timestamp": 16 - i, "reading": float(i * 2)})

    # Config 3: Large batch (64 messages) with synthetic traffic
    large_batch = []
    for i in range(64):
        if i % 8 == 0:
            large_batch.append({"device_id": "L_dup", "timestamp": 500, "reading": 30.0})
        elif i % 8 == 1:
            large_batch.append({"device_id": "L_bad", "timestamp": i, "reading": "err"})
        else:
            large_batch.append({"device_id": f"dev_{i % 5}", "timestamp": 64 - i, "reading": float(i)})

    configs = {
        "Small": small_batch,
        "Medium": medium_batch,
        "Large": large_batch,
    }

    results = {}
    print("=== Evaluation Experiment: Telemetry Batch Configurations ===")
    for name, batch in configs.items():
        metrics = evaluate_batch_configuration(name, batch)
        results[name] = metrics
        print(f"[{name}] Total: {metrics['total_messages']}, Accepted: {metrics['accepted_count']} "
              f"({metrics['accept_rate']:.1%}), Duplicates: {metrics['duplicate_count']} "
              f"({metrics['duplicate_rate']:.1%}), Sorted: {metrics['is_sorted']}")
    return results


if __name__ == "__main__":
    run_experiment()
