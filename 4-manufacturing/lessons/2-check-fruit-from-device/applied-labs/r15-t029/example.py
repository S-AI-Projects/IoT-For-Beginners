#!/usr/bin/env python3
"""Sensor-Message Validation and Evaluation Experiment.

Coursework Task: R15-T029
Context Lesson: 4-manufacturing/lessons/2-check-fruit-from-device

This module implements a local Python standard-library-only message validation,
deduplication, stable ordering, and evaluation benchmarking pipeline.

Contract:
  Each message is a JSON object with:
    - device_id: non-empty string
    - timestamp: finite numeric timestamp (reject booleans and strings)
    - reading: finite numeric reading (reject booleans and strings)
  Duplicate identity: (device_id, timestamp)
  Accepted messages: sorted by timestamp ascending with stable tie-breaking.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import statistics
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class ValidatedMessage:
    """A valid, accepted sensor message."""

    device_id: str
    timestamp: float
    reading: float
    raw_input: Any
    original_index: int


@dataclass
class DuplicateMessage:
    """A valid message that duplicates an already-accepted (device_id, timestamp)."""

    device_id: str
    timestamp: float
    reading: float
    raw_input: Any
    original_index: int
    first_seen_index: int


@dataclass
class RejectedMessage:
    """An invalid message rejected during schema or type validation."""

    raw_input: Any
    original_index: int
    reason: str


@dataclass
class PipelineResult:
    """Complete summary of a batch message validation run."""

    accepted: List[ValidatedMessage]
    duplicates: List[DuplicateMessage]
    rejected: List[RejectedMessage]
    total_processed: int
    is_sorted: bool


def validate_message_schema(raw_msg: Union[str, Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse JSON and validate required fields and types.

    Returns:
      (parsed_dict, None) on success.
      (None, error_reason) on failure.
    """
    if isinstance(raw_msg, str):
        try:
            parsed = json.loads(raw_msg)
        except (json.JSONDecodeError, TypeError) as exc:
            return None, f"Malformed JSON: {exc}"
    elif isinstance(raw_msg, dict):
        parsed = raw_msg
    else:
        return None, f"Message must be a JSON string or dict, got {type(raw_msg).__name__}."

    if not isinstance(parsed, dict):
        return None, f"JSON payload must be an object (dict), got {type(parsed).__name__}."

    # 1. Validate device_id
    if "device_id" not in parsed:
        return None, "Missing required field: 'device_id'."
    dev_id = parsed["device_id"]
    if not isinstance(dev_id, str):
        return None, f"Field 'device_id' must be a string, got {type(dev_id).__name__}."
    if len(dev_id.strip()) == 0:
        return None, "Field 'device_id' cannot be empty or whitespace."

    # 2. Validate timestamp
    if "timestamp" not in parsed:
        return None, "Missing required field: 'timestamp'."
    ts = parsed["timestamp"]
    if isinstance(ts, bool):
        return None, f"Field 'timestamp' cannot be a boolean ({ts!r})."
    if not isinstance(ts, (int, float)):
        return None, f"Field 'timestamp' must be numeric, got {type(ts).__name__} ({ts!r})."
    try:
        ts_float = float(ts)
    except OverflowError:
        return None, "Field 'timestamp' is outside the supported numeric range (magnitude too large for float conversion)."
    if math.isnan(ts_float) or math.isinf(ts_float):
        return None, f"Field 'timestamp' must be a finite number, got {ts_float!r}."

    # 3. Validate reading
    if "reading" not in parsed:
        return None, "Missing required field: 'reading'."
    rd = parsed["reading"]
    if isinstance(rd, bool):
        return None, f"Field 'reading' cannot be a boolean ({rd!r})."
    if not isinstance(rd, (int, float)):
        return None, f"Field 'reading' must be numeric, got {type(rd).__name__} ({rd!r})."
    try:
        rd_float = float(rd)
    except OverflowError:
        return None, "Field 'reading' is outside the supported numeric range (magnitude too large for float conversion)."
    if math.isnan(rd_float) or math.isinf(rd_float):
        return None, f"Field 'reading' must be a finite number, got {rd_float!r}."

    return {
        "device_id": dev_id.strip(),
        "timestamp": ts_float,
        "reading": rd_float,
    }, None


def process_message_stream(raw_messages: List[Union[str, Dict[str, Any]]]) -> PipelineResult:
    """Validate, deduplicate, and stably sort a stream of messages."""
    accepted: List[ValidatedMessage] = []
    duplicates: List[DuplicateMessage] = []
    rejected: List[RejectedMessage] = []

    # Map (device_id, timestamp) to the original_index of the first valid message
    seen_identities: Dict[Tuple[str, float], int] = {}

    for idx, raw in enumerate(raw_messages):
        clean_dict, error = validate_message_schema(raw)
        if error is not None:
            rejected.append(RejectedMessage(raw_input=raw, original_index=idx, reason=error))
            continue

        assert clean_dict is not None
        dev_id = clean_dict["device_id"]
        ts = clean_dict["timestamp"]
        reading = clean_dict["reading"]
        identity = (dev_id, ts)

        if identity in seen_identities:
            duplicates.append(
                DuplicateMessage(
                    device_id=dev_id,
                    timestamp=ts,
                    reading=reading,
                    raw_input=raw,
                    original_index=idx,
                    first_seen_index=seen_identities[identity],
                )
            )
        else:
            seen_identities[identity] = idx
            accepted.append(
                ValidatedMessage(
                    device_id=dev_id,
                    timestamp=ts,
                    reading=reading,
                    raw_input=raw,
                    original_index=idx,
                )
            )

    # Stably sort accepted messages by timestamp ascending
    accepted.sort(key=lambda m: m.timestamp)

    # Verify ordering
    is_sorted = all(accepted[i].timestamp <= accepted[i + 1].timestamp for i in range(len(accepted) - 1))

    return PipelineResult(
        accepted=accepted,
        duplicates=duplicates,
        rejected=rejected,
        total_processed=len(raw_messages),
        is_sorted=is_sorted,
    )


# --- Deterministic Evaluation Experiment ---

def generate_synthetic_dataset(size: int) -> List[Dict[str, Any]]:
    """Generate a deterministic synthetic dataset of specified size.

    Contract proportions per 10-message block (70% accepted, 20% duplicate, 10% rejected):
      - Items 0..6: Valid messages with distinct device/timestamp pairs.
      - Items 7..8: Duplicate identities repeating valid items 0 and 1.
      - Item 9: Rejected message with a string reading.
    """
    messages: List[Dict[str, Any]] = []
    num_blocks = size // 10

    for b in range(num_blocks):
        base_ts = b * 20
        # 7 valid messages with varied, non-sequential timestamps to test sorting
        valid_items = [
            {"device_id": "sensor_A", "timestamp": base_ts + 5, "reading": 10.5},
            {"device_id": "sensor_A", "timestamp": base_ts + 2, "reading": 12.0},
            {"device_id": "sensor_B", "timestamp": base_ts + 2, "reading": 15.2},  # Same ts, diff dev
            {"device_id": "sensor_B", "timestamp": base_ts + 8, "reading": 18.0},
            {"device_id": "sensor_C", "timestamp": base_ts + 1, "reading": 22.4},
            {"device_id": "sensor_C", "timestamp": base_ts + 12, "reading": 25.1},
            {"device_id": "sensor_A", "timestamp": base_ts + 15, "reading": 28.9},
        ]
        messages.extend(valid_items)

        # 2 duplicates repeating items 0 and 1
        messages.append({"device_id": "sensor_A", "timestamp": base_ts + 5, "reading": 99.9})
        messages.append({"device_id": "sensor_A", "timestamp": base_ts + 2, "reading": 88.8})

        # 1 invalid message (string reading)
        messages.append({"device_id": "sensor_B", "timestamp": base_ts + 10, "reading": "corrupt_data"})

    return messages


def run_evaluation_experiment(sizes: Tuple[int, ...] = (10, 100, 1000), runs_per_size: int = 5) -> Dict[int, Dict[str, Any]]:
    """Execute the multi-size evaluation experiment and measure timings."""
    metrics: Dict[int, Dict[str, Any]] = {}

    for size in sizes:
        dataset = generate_synthetic_dataset(size)
        durations: List[float] = []
        result: Optional[PipelineResult] = None

        for _ in range(runs_per_size):
            t_start = time.perf_counter()
            result = process_message_stream(dataset)
            t_end = time.perf_counter()
            durations.append(t_end - t_start)

        assert result is not None
        median_time = statistics.median(durations)
        throughput = size / median_time if median_time > 0 else 0.0

        expected_accepted = (size * 7) // 10
        expected_duplicates = (size * 2) // 10
        expected_rejected = (size * 1) // 10

        metrics[size] = {
            "size": size,
            "accepted_count": len(result.accepted),
            "expected_accepted": expected_accepted,
            "duplicate_count": len(result.duplicates),
            "expected_duplicates": expected_duplicates,
            "rejected_count": len(result.rejected),
            "expected_rejected": expected_rejected,
            "is_sorted": result.is_sorted,
            "median_time_sec": median_time,
            "throughput_msg_per_sec": throughput,
        }

    return metrics


# --- CLI Scenarios ---

def get_mandatory_fixture() -> List[str]:
    """Return the exact 4-message mandatory logical sequence."""
    return [
        json.dumps({"device_id": "A", "timestamp": 2, "reading": 42}),
        json.dumps({"device_id": "A", "timestamp": 1, "reading": 40}),
        json.dumps({"device_id": "A", "timestamp": 1, "reading": 41}),  # Duplicate
        json.dumps({"device_id": "B", "timestamp": 3, "reading": "bad"}),  # Invalid string reading
    ]


def run_normal_scenario() -> None:
    """Run the mandatory fixture and the 3-size evaluation experiment."""
    print("=" * 80)
    print("Task R15-T029: Sensor-Message Validation & Evaluation Experiment")
    print("Scenario: normal (Mandatory Fixture & Evaluation Benchmark)")
    print("=" * 80)
    print()

    # 1. Mandatory Fixture
    print("1. MANDATORY LOGICAL FIXTURE (4 Messages):")
    print("-" * 80)
    fixture = get_mandatory_fixture()
    for idx, raw in enumerate(fixture, start=1):
        print(f"  Input {idx}: {raw}")
    print()

    res = process_message_stream(fixture)

    print("PROCESSING OUTCOME:")
    print(f"  Total Processed: {res.total_processed}")
    print(f"  Accepted Count:  {len(res.accepted)} (Expected: 2)")
    print(f"  Duplicate Count: {len(res.duplicates)} (Expected: 1)")
    print(f"  Rejected Count:  {len(res.rejected)} (Expected: 1)")
    print()

    print("ACCEPTED MESSAGES (Sorted by timestamp ascending):")
    for m in res.accepted:
        print(f"  Device: {m.device_id:<4} | Timestamp: {m.timestamp:<5.1f} | Reading: {m.reading:<5.1f} | Original Index: {m.original_index}")
    print()

    print("DUPLICATE MESSAGES:")
    for d in res.duplicates:
        print(f"  Device: {d.device_id:<4} | Timestamp: {d.timestamp:<5.1f} | Reading: {d.reading:<5.1f} | First Seen Index: {d.first_seen_index}")
    print()

    print("REJECTED MESSAGES:")
    for r in res.rejected:
        print(f"  Input: {r.raw_input} | Reason: {r.reason}")
    print()

    # Verify mandatory assertions
    assert len(res.accepted) == 2, f"Expected 2 accepted, got {len(res.accepted)}"
    assert len(res.duplicates) == 1, f"Expected 1 duplicate, got {len(res.duplicates)}"
    assert len(res.rejected) == 1, f"Expected 1 rejected, got {len(res.rejected)}"
    assert res.accepted[0].timestamp == 1.0 and res.accepted[0].reading == 40.0
    assert res.accepted[1].timestamp == 2.0 and res.accepted[1].reading == 42.0
    assert res.is_sorted, "Accepted messages are not sorted"
    print("✓ Mandatory Fixture Verification: PASSED (Exact match with contract requirements)")
    print()

    # 2. Evaluation Experiment (10, 100, 1000 messages)
    print("2. EVALUATION EXPERIMENT (Synthetic Scaled Benchmarks):")
    print("-" * 80)
    benchmarks = run_evaluation_experiment(sizes=(10, 100, 1000), runs_per_size=5)

    print(f"{'Input Size':<12} {'Accepted':<10} {'Duplicates':<12} {'Rejected':<10} {'Sorted?':<8} {'Median Time (s)':<18} {'Throughput (msg/s)'}")
    print("-" * 88)
    for sz in (10, 100, 1000):
        b = benchmarks[sz]
        sorted_str = "YES" if b["is_sorted"] else "NO"
        print(
            f"{b['size']:<12} {b['accepted_count']:<10} {b['duplicate_count']:<12} "
            f"{b['rejected_count']:<10} {sorted_str:<8} {b['median_time_sec']:<18.6f} {b['throughput_msg_per_sec']:<12.1f}"
        )
    print("-" * 88)
    print()
    print("Notice: Timings are local synthetic measurements and do not reflect real cloud/hardware performance.")
    print("=" * 80)


def run_boundary_scenario() -> None:
    """Run edge-case boundary tests (empty input, ties, malformed JSON, etc.)."""
    print("=" * 80)
    print("Task R15-T029: Sensor-Message Validation & Evaluation Experiment")
    print("Scenario: boundary (Edge Cases & Fault Invariant Verifications)")
    print("=" * 80)

    # 1. Empty input
    res_empty = process_message_stream([])
    assert len(res_empty.accepted) == 0 and len(res_empty.duplicates) == 0 and len(res_empty.rejected) == 0
    print("✓ Empty input handled cleanly (0 accepted, 0 duplicate, 0 rejected).")

    # 2. Same timestamp on different devices (allowed)
    same_ts_inputs = [
        {"device_id": "sensor_1", "timestamp": 10.0, "reading": 100.0},
        {"device_id": "sensor_2", "timestamp": 10.0, "reading": 200.0},
    ]
    res_diff_dev = process_message_stream(same_ts_inputs)
    assert len(res_diff_dev.accepted) == 2 and len(res_diff_dev.duplicates) == 0
    print("✓ Same timestamp across different devices is allowed (both accepted).")

    # 3. Stable sorting for equal timestamps
    equal_ts_inputs = [
        {"device_id": "B", "timestamp": 5.0, "reading": 1.0},
        {"device_id": "A", "timestamp": 5.0, "reading": 2.0},
        {"device_id": "C", "timestamp": 5.0, "reading": 3.0},
    ]
    res_stable = process_message_stream(equal_ts_inputs)
    assert [m.device_id for m in res_stable.accepted] == ["B", "A", "C"]
    print("✓ Equal timestamps preserve original input order (stable sorting).")

    # 4. Malformed JSON string
    res_malformed = process_message_stream(['{"device_id": "A", "timestamp": 1, reading: bad}'])
    assert len(res_malformed.rejected) == 1 and "Malformed JSON" in res_malformed.rejected[0].reason
    print("✓ Malformed JSON string rejected with clear diagnostic.")

    # 5. Invalid message does NOT reserve an identity
    inv_reserve_inputs = [
        {"device_id": "sensor_X", "timestamp": 50.0, "reading": "not_a_number"},  # Rejected
        {"device_id": "sensor_X", "timestamp": 50.0, "reading": 42.0},  # Must be ACCEPTED
    ]
    res_reserve = process_message_stream(inv_reserve_inputs)
    assert len(res_reserve.rejected) == 1
    assert len(res_reserve.accepted) == 1 and res_reserve.accepted[0].reading == 42.0
    print("✓ Invalid messages do NOT reserve an identity (subsequent valid message accepted).")

    # 6. Boolean numeric values rejected
    res_bools = process_message_stream([
        {"device_id": "dev1", "timestamp": True, "reading": 10.0},
        {"device_id": "dev2", "timestamp": 1.0, "reading": False},
    ])
    assert len(res_bools.rejected) == 2
    print("✓ Boolean values rejected as timestamps and readings.")

    # 7. Empty or whitespace device_id rejected
    res_empty_dev = process_message_stream([
        {"device_id": "", "timestamp": 1.0, "reading": 10.0},
        {"device_id": "   ", "timestamp": 2.0, "reading": 20.0},
    ])
    assert len(res_empty_dev.rejected) == 2
    print("✓ Empty and whitespace-only device IDs rejected.")

    # 8. NaN and infinity rejected
    res_nan = process_message_stream([
        {"device_id": "dev1", "timestamp": float("nan"), "reading": 10.0},
        {"device_id": "dev2", "timestamp": 1.0, "reading": float("inf")},
    ])
    assert len(res_nan.rejected) == 2
    print("✓ Non-finite (NaN, inf) numbers rejected.")

    # 9. Enormous integer overflow handled cleanly
    huge_int = 10**10000
    res_overflow = process_message_stream([
        {"device_id": "dev_ovf", "timestamp": huge_int, "reading": 10.0},
        {"device_id": "dev_ovf", "timestamp": 1.0, "reading": huge_int},
        {"device_id": "dev_ovf", "timestamp": 1.0, "reading": 25.0},
    ])
    assert len(res_overflow.rejected) == 2
    assert len(res_overflow.accepted) == 1 and res_overflow.accepted[0].reading == 25.0
    print("✓ Enormous integer overflow rejected cleanly without reserving identity.")

    print("=" * 80)
    print("All Boundary Checks PASSED.")
    print("=" * 80)


def run_failure_scenario() -> None:
    """Run deliberate incorrect assertion to demonstrate non-zero exit."""
    print("=" * 80)
    print("Task R15-T029: Sensor-Message Validation & Evaluation Experiment")
    print("Scenario: failure (Intentional Failure Demonstration)")
    print("=" * 80)
    print("Notice: This scenario intentionally asserts an incorrect expected count.")
    print("It demonstrates that verification checks properly fail with a non-zero exit code.")
    print()

    fixture = get_mandatory_fixture()
    res = process_message_stream(fixture)
    actual_accepted = len(res.accepted)
    deliberate_false_expected = 999

    print(f"Actual Accepted Count:        {actual_accepted}")
    print(f"False Expected Accepted Count: {deliberate_false_expected}")
    print()
    print("Triggering deliberate assertion failure now...")
    print("INTENTIONAL FAILURE: Deliberately asserting actual_accepted == 999")

    assert actual_accepted == deliberate_false_expected, (
        f"INTENTIONAL FAILURE: Actual accepted count ({actual_accepted}) != Expected ({deliberate_false_expected})"
    )


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Sensor-Message Validation and Evaluation Experiment."
    )
    parser.add_argument(
        "--scenario",
        default=None,
        choices=["normal", "boundary", "failure"],
        help="CLI scenario: 'normal', 'boundary', or 'failure'.",
    )
    parser.add_argument(
        "positional_scenario",
        nargs="?",
        default=None,
        choices=["normal", "boundary", "failure"],
        help="Optional positional scenario name.",
    )

    args = parser.parse_args()
    scenario = args.scenario or args.positional_scenario or "normal"

    if scenario == "normal":
        run_normal_scenario()
    elif scenario == "boundary":
        run_boundary_scenario()
    elif scenario == "failure":
        run_failure_scenario()


if __name__ == "__main__":
    main()
