"""Sensor-Message Validation — Invariant and State Trace (Task R15-T024).

Demonstrates local validation, duplicate filtering, chronological sorting,
intermediate state tracing, and pipeline invariant verification for IoT
JSON telemetry messages using Python's standard library.

Lesson Context:
In Lesson 1-4, IoT devices publish telemetry over MQTT formatted as JSON.
In practical networks, messages can arrive out of order, get duplicated by
network retries, or arrive malformed. Before processing telemetry or making
actuator decisions, ingestion pipelines must validate payloads, filter duplicates,
order events chronologically, and maintain verifiable processing invariants.
"""

from copy import deepcopy
from dataclasses import dataclass
import json
import math
from typing import Any, Dict, List, Tuple, Union


@dataclass(frozen=True)
class ProcessingOutcome:
    """Outcome of processing an individual sensor message."""

    status: str  # "ACCEPTED", "DUPLICATE", "REJECTED"
    reason: str  # Human-readable explanation


@dataclass
class TraceStep:
    """Snapshot of intermediate processing state after handling an input."""

    step_number: int
    raw_input: Any
    outcome: ProcessingOutcome
    accepted_so_far: List[Dict[str, Any]]
    duplicates_so_far: List[Dict[str, Any]]
    rejected_so_far: List[Dict[str, Any]]


@dataclass
class ProcessingResult:
    """Complete results of processing a sequence of sensor messages."""

    accepted: List[Dict[str, Any]]
    duplicates: List[Dict[str, Any]]
    rejected: List[Dict[str, Any]]
    trace: List[TraceStep]


def parse_and_validate_message(raw_message: Any) -> Dict[str, Any]:
    """Parse raw input into a dictionary and validate all required sensor fields.

    Accepts either a JSON-encoded string or an existing dictionary.

    Schema:
      - 'device_id': non-empty string.
      - 'timestamp': finite numeric value (int or float; bools rejected).
      - 'reading': finite numeric value (int or float; bools rejected; 0 accepted).

    Raises:
        ValueError: If JSON is malformed, required fields are missing, strings are empty,
                    or numbers are non-finite (NaN, Inf).
        TypeError: If fields have invalid types (e.g. booleans as numbers, non-strings).
    """
    # 1. Parse JSON if string or bytes
    if isinstance(raw_message, (str, bytes)):
        try:
            parsed = json.loads(raw_message)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"Malformed JSON payload: {exc}") from exc
    elif isinstance(raw_message, dict):
        parsed = raw_message
    else:
        raise TypeError(
            f"Message must be a JSON string or dict, got {type(raw_message).__name__}."
        )

    if not isinstance(parsed, dict):
        raise TypeError(
            f"Parsed message payload must be a JSON object (dict), got {type(parsed).__name__}."
        )

    # 2. Check required fields
    for field in ("device_id", "timestamp", "reading"):
        if field not in parsed:
            raise ValueError(f"Missing required field: '{field}'.")

    # 3. Validate device_id
    device_id = parsed["device_id"]
    if not isinstance(device_id, str):
        raise TypeError(
            f"Field 'device_id' must be a str, got {type(device_id).__name__}."
        )
    if not device_id.strip():
        raise ValueError("Field 'device_id' must be a non-empty string.")

    # 4. Validate timestamp: finite number, reject bools
    timestamp = parsed["timestamp"]
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        raise TypeError(
            f"Field 'timestamp' must be a finite number (int or float), got {type(timestamp).__name__}."
        )
    if not math.isfinite(timestamp):
        raise ValueError(f"Field 'timestamp' must be a finite number, got {timestamp}.")

    # 5. Validate reading: finite number, reject bools, accept zero
    reading = parsed["reading"]
    if isinstance(reading, bool) or not isinstance(reading, (int, float)):
        raise TypeError(
            f"Field 'reading' must be a finite number (int or float), got {type(reading).__name__}."
        )
    if not math.isfinite(reading):
        raise ValueError(f"Field 'reading' must be a finite number, got {reading}.")

    return parsed


def process_message_stream(messages: List[Any]) -> ProcessingResult:
    """Process a stream of sensor messages, recording state trace and enforcing invariants.

    Rules:
      1. Messages failing JSON decoding, schema, or type checks are REJECTED.
         Invalid messages do NOT reserve their (device_id, timestamp) identity.
      2. Valid messages are checked against previously seen (device_id, timestamp) pairs.
         If already seen, the message is marked DUPLICATE.
      3. Valid, non-duplicate messages are ACCEPTED.
      4. Accepted messages are maintained in ascending order by timestamp (with
         deterministic tie-breaking on (timestamp, device_id, reading)).
      5. Intermediate state (accepted, duplicates, rejected) is recorded after every input.

    Args:
        messages: List of raw input messages (JSON strings or dictionaries).

    Returns:
        ProcessingResult containing accepted, duplicates, rejected, and full trace.
    """
    accepted: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    trace: List[TraceStep] = []
    seen_valid_keys: set = set()

    for idx, raw_input in enumerate(messages, start=1):
        try:
            validated = parse_and_validate_message(raw_input)
        except (ValueError, TypeError) as exc:
            # Message is rejected; its identity is NOT reserved in seen_valid_keys
            outcome = ProcessingOutcome(status="REJECTED", reason=str(exc))
            rejected.append({"input": raw_input, "reason": str(exc)})
            trace.append(
                TraceStep(
                    step_number=idx,
                    raw_input=raw_input,
                    outcome=outcome,
                    accepted_so_far=deepcopy(accepted),
                    duplicates_so_far=deepcopy(duplicates),
                    rejected_so_far=deepcopy(rejected),
                )
            )
            continue

        dedup_key = (validated["device_id"], validated["timestamp"])
        if dedup_key in seen_valid_keys:
            outcome = ProcessingOutcome(
                status="DUPLICATE",
                reason=f"Duplicate (device_id, timestamp) pair already seen: {dedup_key}.",
            )
            duplicates.append({
                "message": validated,
                "reason": outcome.reason,
            })
        else:
            seen_valid_keys.add(dedup_key)
            outcome = ProcessingOutcome(
                status="ACCEPTED",
                reason="Valid message accepted and sorted chronologically.",
            )
            accepted.append(validated)
            # Maintain accepted messages sorted by timestamp ascending
            accepted.sort(key=lambda m: (m["timestamp"], m["device_id"], m["reading"]))

        trace.append(
            TraceStep(
                step_number=idx,
                raw_input=raw_input,
                outcome=outcome,
                accepted_so_far=deepcopy(accepted),
                duplicates_so_far=deepcopy(duplicates),
                rejected_so_far=deepcopy(rejected),
            )
        )

    return ProcessingResult(
        accepted=accepted,
        duplicates=duplicates,
        rejected=rejected,
        trace=trace,
    )


def check_pipeline_invariant(inputs: List[Any], result: ProcessingResult) -> bool:
    """Verify system invariants connecting inputs, intermediate trace, and final output.

    Invariants checked:
      1. Every trace step has the correct sequential step_number starting at 1.
      2. Every input has exactly one recorded outcome in the trace, matching input count.
      3. Each intermediate snapshot is consistent with the outcomes processed up to that step.
      4. Final output counts and contents agree with the last recorded trace step.
      5. Accepted, duplicate, and rejected classifications match corresponding trace outcomes.
      6. Every accepted message contains valid, finite fields conforming to the schema.
      7. No two accepted messages share the same (device_id, timestamp) pair.
      8. Accepted messages strictly follow the deterministic sorting rule:
         (timestamp, device_id, reading).

    Args:
        inputs: Original list of input messages.
        result: ProcessingResult containing accepted, duplicates, rejected, and trace.

    Returns:
        True if all invariants hold.

    Raises:
        AssertionError: If any invariant condition is violated, with a detailed message.
    """
    total_inputs = len(inputs)

    # Invariant 1 & 2: Trace length must match input count
    if len(result.trace) != total_inputs:
        raise AssertionError(
            f"Invariant violation: Trace steps count ({len(result.trace)}) does not match input count ({total_inputs})."
        )

    # If no inputs, all outputs must be empty
    if total_inputs == 0:
        if result.accepted or result.duplicates or result.rejected:
            raise AssertionError(
                "Invariant violation: Empty input produced non-empty results."
            )
        return True

    # Invariant 1: Sequential step numbers starting at 1
    for expected_num, step in enumerate(result.trace, start=1):
        if step.step_number != expected_num:
            raise AssertionError(
                f"Invariant violation: Step at index {expected_num - 1} has step_number {step.step_number}; "
                f"expected sequential step_number {expected_num}."
            )

    # Invariant 3: Independent state reconstruction and intermediate snapshot verification
    reconstructed_accepted: List[Dict[str, Any]] = []
    reconstructed_duplicates: List[Dict[str, Any]] = []
    reconstructed_rejected: List[Dict[str, Any]] = []
    reconstructed_seen_keys: set = set()

    prev_acc_len = 0
    prev_dup_len = 0
    prev_rej_len = 0

    for idx, raw_input in enumerate(inputs, start=1):
        step = result.trace[idx - 1]

        # 3.1 Verify raw_input corresponds to input at that index
        if step.raw_input != raw_input:
            raise AssertionError(
                f"Invariant violation: Step {idx} raw_input ({step.raw_input}) "
                f"does not match input at index {idx - 1} ({raw_input})."
            )

        # 3.2 Independently reconstruct expected state for this input
        try:
            val_msg = parse_and_validate_message(raw_input)
            dedup_key = (val_msg["device_id"], val_msg["timestamp"])
            if dedup_key in reconstructed_seen_keys:
                expected_status = "DUPLICATE"
                reconstructed_duplicates.append({
                    "message": val_msg,
                    "reason": f"Duplicate (device_id, timestamp) pair already seen: {dedup_key}.",
                })
            else:
                expected_status = "ACCEPTED"
                reconstructed_seen_keys.add(dedup_key)
                reconstructed_accepted.append(val_msg)
                reconstructed_accepted.sort(
                    key=lambda m: (m["timestamp"], m["device_id"], m["reading"])
                )
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            expected_status = "REJECTED"
            reconstructed_rejected.append({
                "input": raw_input,
                "reason": str(exc),
            })

        # 3.3 Verify step outcome status matches reconstructed expectation
        if step.outcome.status != expected_status:
            raise AssertionError(
                f"Invariant violation: Step {idx} outcome status '{step.outcome.status}' "
                f"does not match expected reconstructed status '{expected_status}' for input {raw_input}."
            )

        # 3.4 Verify intermediate snapshot lengths and count progression
        acc_len = len(step.accepted_so_far)
        dup_len = len(step.duplicates_so_far)
        rej_len = len(step.rejected_so_far)
        expected_cumulative = step.step_number

        if acc_len + dup_len + rej_len != expected_cumulative:
            raise AssertionError(
                f"Invariant violation: Step {step.step_number} snapshot total ({acc_len + dup_len + rej_len}) "
                f"does not match cumulative inputs processed ({expected_cumulative})."
            )

        if step.outcome.status == "ACCEPTED":
            if acc_len != prev_acc_len + 1 or dup_len != prev_dup_len or rej_len != prev_rej_len:
                raise AssertionError(
                    f"Invariant violation: Step {step.step_number} outcome ACCEPTED is inconsistent with intermediate snapshot counts."
                )
        elif step.outcome.status == "DUPLICATE":
            if dup_len != prev_dup_len + 1 or acc_len != prev_acc_len or rej_len != prev_rej_len:
                raise AssertionError(
                    f"Invariant violation: Step {step.step_number} outcome DUPLICATE is inconsistent with intermediate snapshot counts."
                )
        elif step.outcome.status == "REJECTED":
            if rej_len != prev_rej_len + 1 or acc_len != prev_acc_len or dup_len != prev_dup_len:
                raise AssertionError(
                    f"Invariant violation: Step {step.step_number} outcome REJECTED is inconsistent with intermediate snapshot counts."
                )
        else:
            raise AssertionError(
                f"Invariant violation: Step {step.step_number} has unknown outcome status '{step.outcome.status}'."
            )

        # 3.5 Verify intermediate accepted list is properly sorted
        for j in range(acc_len - 1):
            curr_k = (
                step.accepted_so_far[j]["timestamp"],
                step.accepted_so_far[j]["device_id"],
                step.accepted_so_far[j]["reading"],
            )
            next_k = (
                step.accepted_so_far[j + 1]["timestamp"],
                step.accepted_so_far[j + 1]["device_id"],
                step.accepted_so_far[j + 1]["reading"],
            )
            if curr_k > next_k:
                raise AssertionError(
                    f"Invariant violation: Intermediate accepted list at step {step.step_number} violates sorting rule: "
                    f"{curr_k} > {next_k}."
                )

        # 3.6 Verify complete intermediate lists match reconstructed state (detects content tampering)
        if step.accepted_so_far != reconstructed_accepted:
            raise AssertionError(
                f"Invariant violation: Step {step.step_number} accepted_so_far snapshot does not match reconstructed accepted state."
            )

        if step.duplicates_so_far != reconstructed_duplicates:
            raise AssertionError(
                f"Invariant violation: Step {step.step_number} duplicates_so_far snapshot does not match reconstructed duplicate state."
            )

        if step.rejected_so_far != reconstructed_rejected:
            raise AssertionError(
                f"Invariant violation: Step {step.step_number} rejected_so_far snapshot does not match reconstructed rejected state."
            )

        prev_acc_len = acc_len
        prev_dup_len = dup_len
        prev_rej_len = rej_len

    # Invariant 4: Final output agrees with the last recorded state
    last_step = result.trace[-1]
    if result.accepted != last_step.accepted_so_far:
        raise AssertionError(
            "Invariant violation: Final accepted messages do not agree with the last trace state."
        )
    if result.duplicates != last_step.duplicates_so_far:
        raise AssertionError(
            "Invariant violation: Final duplicate messages do not agree with the last trace state."
        )
    if result.rejected != last_step.rejected_so_far:
        raise AssertionError(
            "Invariant violation: Final rejected messages do not agree with the last trace state."
        )

    # Invariant 5: Classification counts match trace outcome counts
    accepted_outcomes = sum(1 for s in result.trace if s.outcome.status == "ACCEPTED")
    duplicate_outcomes = sum(1 for s in result.trace if s.outcome.status == "DUPLICATE")
    rejected_outcomes = sum(1 for s in result.trace if s.outcome.status == "REJECTED")

    if len(result.accepted) != accepted_outcomes:
        raise AssertionError(
            f"Invariant violation: Final accepted count ({len(result.accepted)}) does not match ACCEPTED outcomes in trace ({accepted_outcomes})."
        )
    if len(result.duplicates) != duplicate_outcomes:
        raise AssertionError(
            f"Invariant violation: Final duplicate count ({len(result.duplicates)}) does not match DUPLICATE outcomes in trace ({duplicate_outcomes})."
        )
    if len(result.rejected) != rejected_outcomes:
        raise AssertionError(
            f"Invariant violation: Final rejected count ({len(result.rejected)}) does not match REJECTED outcomes in trace ({rejected_outcomes})."
        )

    # Invariant 6: Every accepted message has valid fields
    for msg in result.accepted:
        try:
            parse_and_validate_message(msg)
        except Exception as exc:
            raise AssertionError(
                f"Invariant violation: Accepted message contains invalid fields ({msg}): {exc}"
            ) from exc

    # Invariant 7: No accepted messages share the same (device_id, timestamp) pair
    seen_pairs = set()
    for msg in result.accepted:
        pair = (msg["device_id"], msg["timestamp"])
        if pair in seen_pairs:
            raise AssertionError(
                f"Invariant violation: Duplicate (device_id, timestamp) pair {pair} found in accepted messages."
            )
        seen_pairs.add(pair)

    # Invariant 8: Accepted messages strictly adhere to the sorting rule: (timestamp, device_id, reading)
    for i in range(len(result.accepted) - 1):
        curr_key = (
            result.accepted[i]["timestamp"],
            result.accepted[i]["device_id"],
            result.accepted[i]["reading"],
        )
        next_key = (
            result.accepted[i + 1]["timestamp"],
            result.accepted[i + 1]["device_id"],
            result.accepted[i + 1]["reading"],
        )
        if curr_key > next_key:
            raise AssertionError(
                f"Invariant violation: Accepted messages violate sorting rule (timestamp, device_id, reading): "
                f"{curr_key} > {next_key}."
            )

    return True


def get_required_fixture() -> List[Dict[str, Any]]:
    """Return the four required fixture inputs in the exact specified order."""
    return [
        # 1. Device A, timestamp 2, numeric reading 20
        {"device_id": "Device-A", "timestamp": 2, "reading": 20},
        # 2. Device A, timestamp 1, numeric reading 10
        {"device_id": "Device-A", "timestamp": 1, "reading": 10},
        # 3. Device A, timestamp 1, numeric reading 11 (duplicate)
        {"device_id": "Device-A", "timestamp": 1, "reading": 11},
        # 4. Device A, timestamp 3, reading "not-a-number" (invalid string reading)
        {"device_id": "Device-A", "timestamp": 3, "reading": "not-a-number"},
    ]


def main() -> None:
    """Execute the pipeline on the required fixture, displaying state trace and invariant check."""
    print("=" * 80)
    print("Task R15-T024: Sensor-Message Validation — Invariant & State Trace")
    print("Context: Lesson 1-4 Internet Telemetry Ingestion over MQTT")
    print("=" * 80)
    print()

    fixture = get_required_fixture()
    result = process_message_stream(fixture)

    print("STEP-BY-STEP INTERMEDIATE STATE TRACE:")
    print("-" * 80)
    for step in result.trace:
        print(f"Step {step.step_number}:")
        print(f"  Input:   {step.raw_input}")
        print(f"  Outcome: [{step.outcome.status}] {step.outcome.reason}")
        print(f"  Accepted ({len(step.accepted_so_far)}):   {step.accepted_so_far}")
        print(f"  Duplicates ({len(step.duplicates_so_far)}): {step.duplicates_so_far}")
        print(f"  Rejected ({len(step.rejected_so_far)}):   {step.rejected_so_far}")
        print("-" * 80)
    print()

    print("FINAL SUMMARY:")
    print(f"  • Accepted Messages ({len(result.accepted)}):")
    for msg in result.accepted:
        print(f"      Device: {msg['device_id']:<10} Timestamp: {msg['timestamp']:<4} Reading: {msg['reading']}")
    print(f"  • Duplicates Detected ({len(result.duplicates)}):")
    for dup in result.duplicates:
        print(f"      {dup['message']} -> {dup['reason']}")
    print(f"  • Rejected Messages ({len(result.rejected)}):")
    for rej in result.rejected:
        print(f"      {rej['input']} -> {rej['reason']}")
    print()

    print("PIPELINE INVARIANT VERIFICATION:")
    print("-" * 80)
    try:
        check_pipeline_invariant(fixture, result)
        print("✓ Pipeline Invariant Check PASSED: All invariants successfully verified.")
    except AssertionError as exc:
        print(f"✗ Pipeline Invariant Check FAILED: {exc}")
    print()

    print("DEMONSTRATION: Intentional Corruption Detection")
    print("-" * 80)
    # Deliberately corrupt result by swapping timestamp order in accepted list
    corrupted_result = deepcopy(result)
    corrupted_result.accepted.reverse()  # Out of order: timestamp 2 before 1
    try:
        check_pipeline_invariant(fixture, corrupted_result)
        print("✗ Corruption was NOT detected.")
    except AssertionError as exc:
        print(f"✓ Confirmed: Corrupted result was successfully caught by invariant checker:")
        print(f"  -> {exc}")
    print("=" * 80)


if __name__ == "__main__":
    main()
