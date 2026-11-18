"""Applied Lab R15-T025: Sensor-Message Validation — Offline Service Adapter.

Demonstrates telemetry validation, deduplication, deterministic chronological sorting,
and decoupled service delivery through an injectable callable adapter in an
offline/edge IoT scenario.

Lesson Context:
In Lesson 2 ("A deeper dive into IoT"), edge devices or local gateway systems
often process sensor readings locally before deciding whether, when, and how
to transmit them to upstream services. Using a decoupled callable service adapter
allows local validation and processing logic to remain completely independent
of concrete cloud or transport dependencies.

Educational Simulation Notice:
This module is a local simulation using in-memory data structures and standard
library Python. It does not perform network I/O, connect to cloud services,
or interface with physical hardware.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import json
import math
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


@dataclass
class ServiceAcknowledgement:
    """Predictable acknowledgement record returned by a callable service adapter."""

    message_id: str
    device_id: str
    timestamp: Union[int, float]
    status: str  # "DELIVERED" or "FAILED"
    details: str

    def is_delivered(self) -> bool:
        """Return True if the service adapter confirmed delivery."""
        return self.status == "DELIVERED"


@dataclass
class ProcessingResult:
    """Complete summary of telemetry stream processing and service delivery."""

    accepted: List[Dict[str, Any]]
    duplicates: List[Dict[str, Any]]
    rejected: List[Dict[str, Any]]
    acknowledgements: List[ServiceAcknowledgement]
    delivered: List[Dict[str, Any]]
    failed_deliveries: List[Dict[str, Any]]


class InMemoryServiceAdapter:
    """Deterministic, in-memory callable service adapter simulating offline edge/cloud delivery.

    Demonstrates:
      - Receiving validated telemetry payloads via a standard callable interface.
      - Storing submitted messages in an in-memory audit log for inspection.
      - Producing deterministic, verifiable ServiceAcknowledgement records.
      - Simulating failure conditions (e.g. offline queue full or connection drop).

    Does NOT prove:
      - Real network connectivity or socket transmission.
      - Cloud persistence, database ACID transactions, or distributed consensus.
      - Authentication, authorization, or transport layer security (TLS).
      - Physical hardware behavior or production delivery guarantees.
    """

    def __init__(
        self,
        should_fail: bool = False,
        fail_on_device: Optional[str] = None,
        fail_on_timestamp: Optional[Union[int, float]] = None,
    ) -> None:
        self.submitted_messages: List[Dict[str, Any]] = []
        self.acknowledgements: List[ServiceAcknowledgement] = []
        self.should_fail = should_fail
        self.fail_on_device = fail_on_device
        self.fail_on_timestamp = fail_on_timestamp

    def __call__(self, message: Dict[str, Any]) -> ServiceAcknowledgement:
        """Process a submitted message and return an acknowledgement."""
        self.submitted_messages.append(deepcopy(message))

        device_id = str(message.get("device_id", "unknown"))
        timestamp = message.get("timestamp", 0)

        # Check failure triggers
        is_failure = (
            self.should_fail
            or (self.fail_on_device is not None and device_id == self.fail_on_device)
            or (self.fail_on_timestamp is not None and timestamp == self.fail_on_timestamp)
        )

        if is_failure:
            ack = ServiceAcknowledgement(
                message_id=f"ack-{device_id}-{timestamp}",
                device_id=device_id,
                timestamp=timestamp,
                status="FAILED",
                details="Service adapter simulated delivery failure (offline queue full or unreachable).",
            )
        else:
            ack = ServiceAcknowledgement(
                message_id=f"ack-{device_id}-{timestamp}",
                device_id=device_id,
                timestamp=timestamp,
                status="DELIVERED",
                details="Message accepted and acknowledged by in-memory mock service.",
            )

        self.acknowledgements.append(ack)
        return ack


def parse_and_validate_message(raw_input: Any) -> Dict[str, Any]:
    """Parse and validate a sensor telemetry message.

    Schema:
      - device_id: non-empty string.
      - timestamp: finite numeric value (int or float; not bool).
      - reading: finite numeric value (int or float; not bool).

    Accepts zero (0, 0.0) as valid timestamp and reading.
    Rejects booleans, non-finite floats, non-object JSON, and missing fields.
    """
    if isinstance(raw_input, str):
        try:
            payload = json.loads(raw_input)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"Malformed JSON: {exc}") from exc
    elif isinstance(raw_input, dict):
        payload = raw_input
    else:
        raise TypeError(
            f"Message payload must be a JSON object (dict), got {type(raw_input).__name__}."
        )

    if not isinstance(payload, dict):
        raise TypeError(
            f"Parsed JSON must be an object (dict), got {type(payload).__name__}."
        )

    # Required fields
    required_fields = ("device_id", "timestamp", "reading")
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: '{field}'.")

    # Validate device_id
    device_id = payload["device_id"]
    if not isinstance(device_id, str):
        raise TypeError(
            f"Field 'device_id' must be a str, got {type(device_id).__name__}."
        )
    if not device_id.strip():
        raise ValueError("Field 'device_id' cannot be empty or whitespace-only.")

    # Validate timestamp (reject booleans because bool is a subclass of int)
    timestamp = payload["timestamp"]
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        raise TypeError(
            f"Field 'timestamp' must be a finite number (int or float), got {type(timestamp).__name__}."
        )
    if math.isnan(timestamp) or math.isinf(timestamp):
        raise ValueError(f"Field 'timestamp' must be finite, got {timestamp}.")

    # Validate reading (reject booleans)
    reading = payload["reading"]
    if isinstance(reading, bool) or not isinstance(reading, (int, float)):
        raise TypeError(
            f"Field 'reading' must be a finite number (int or float), got {type(reading).__name__}."
        )
    if math.isnan(reading) or math.isinf(reading):
        raise ValueError(f"Field 'reading' must be finite, got {reading}.")

    return {
        "device_id": device_id,
        "timestamp": timestamp,
        "reading": reading,
    }


def process_message_stream(
    inputs: List[Any],
    service_adapter: Optional[Callable[[Dict[str, Any]], ServiceAcknowledgement]] = None,
) -> ProcessingResult:
    """Process incoming telemetry messages and submit accepted records to the service adapter.

    Pipeline stages:
      1. Parse and validate input messages.
      2. Detect and filter duplicate (device_id, timestamp) pairs.
      3. Sort accepted messages chronologically by (timestamp, device_id, reading).
      4. Submit sorted accepted messages to the injected service adapter.
      5. Collect acknowledgements and classify into delivered vs failed deliveries.
         Failed service submissions are never silently marked as delivered.

    Args:
        inputs: List of telemetry inputs (dicts or JSON strings).
        service_adapter: Callable receiving an accepted message dict and returning
                         a ServiceAcknowledgement. Defaults to InMemoryServiceAdapter.

    Returns:
        ProcessingResult containing accepted, duplicates, rejected, acknowledgements,
        delivered, and failed_deliveries.
    """
    if service_adapter is None:
        service_adapter = InMemoryServiceAdapter()

    accepted: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen_valid_keys: set = set()

    # Stage 1 & 2: Validate and deduplicate
    for raw_input in inputs:
        try:
            validated = parse_and_validate_message(raw_input)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            rejected.append({"input": raw_input, "reason": str(exc)})
            continue

        dedup_key = (validated["device_id"], validated["timestamp"])
        if dedup_key in seen_valid_keys:
            duplicates.append({
                "message": validated,
                "reason": f"Duplicate (device_id, timestamp) pair already seen: {dedup_key}.",
            })
        else:
            seen_valid_keys.add(dedup_key)
            accepted.append(validated)

    # Stage 3: Deterministic chronological sorting: (timestamp, device_id, reading)
    accepted.sort(key=lambda m: (m["timestamp"], m["device_id"], m["reading"]))

    # Stage 4 & 5: Pass accepted messages to injected callable adapter
    acknowledgements: List[ServiceAcknowledgement] = []
    delivered: List[Dict[str, Any]] = []
    failed_deliveries: List[Dict[str, Any]] = []

    for msg in accepted:
        try:
            raw_ack = service_adapter(deepcopy(msg))
        except Exception as exc:
            # Handle unhandled adapter exceptions safely without crashing the pipeline
            ack = ServiceAcknowledgement(
                message_id=f"ack-{msg['device_id']}-{msg['timestamp']}",
                device_id=msg["device_id"],
                timestamp=msg["timestamp"],
                status="FAILED",
                details=f"Service adapter raised exception: {exc}",
            )
        else:
            # 1. Validate the adapter return value before accessing fields
            if not isinstance(raw_ack, ServiceAcknowledgement):
                ack = ServiceAcknowledgement(
                    message_id=f"ack-{msg['device_id']}-{msg['timestamp']}",
                    device_id=msg["device_id"],
                    timestamp=msg["timestamp"],
                    status="FAILED",
                    details=(
                        f"Invalid service adapter return value: expected ServiceAcknowledgement instance, "
                        f"got {type(raw_ack).__name__} ({repr(raw_ack)})."
                    ),
                )
            elif raw_ack.status not in ("DELIVERED", "FAILED"):
                ack = ServiceAcknowledgement(
                    message_id=getattr(raw_ack, "message_id", f"ack-{msg['device_id']}-{msg['timestamp']}"),
                    device_id=msg["device_id"],
                    timestamp=msg["timestamp"],
                    status="FAILED",
                    details=(
                        f"Invalid service acknowledgement status: expected 'DELIVERED' or 'FAILED', "
                        f"got {repr(raw_ack.status)}."
                    ),
                )
            else:
                ack = raw_ack

        acknowledgements.append(ack)
        if ack.status == "DELIVERED":
            delivered.append(deepcopy(msg))
        else:
            failed_deliveries.append({
                "message": deepcopy(msg),
                "acknowledgement": ack,
            })

    return ProcessingResult(
        accepted=accepted,
        duplicates=duplicates,
        rejected=rejected,
        acknowledgements=acknowledgements,
        delivered=delivered,
        failed_deliveries=failed_deliveries,
    )


def verify_pipeline_contract(
    inputs: List[Any],
    result: ProcessingResult,
    adapter: Optional[InMemoryServiceAdapter] = None,
) -> bool:
    """Verify system invariants connecting inputs, adapter submissions, and delivery state.

    Invariants checked:
      1. Message conservation: len(accepted) + len(duplicates) + len(rejected) == len(inputs).
      2. No duplicate (device_id, timestamp) pairs exist in accepted messages.
      3. Accepted messages strictly adhere to the sorting rule: (timestamp, device_id, reading).
      4. Delivery accounting: len(delivered) + len(failed_deliveries) == len(accepted).
      5. Acknowledgements count matches len(accepted).
      6. No message in delivered has a FAILED acknowledgement status.
      7. No message in failed_deliveries is falsely recorded in delivered.
      8. If an InMemoryServiceAdapter is provided, its submitted_messages exactly
         match accepted messages in both content and order.

    Raises:
        AssertionError: If any contract property is violated.
    """
    total_inputs = len(inputs)

    # 1. Message conservation
    total_classified = len(result.accepted) + len(result.duplicates) + len(result.rejected)
    if total_classified != total_inputs:
        raise AssertionError(
            f"Contract violation: Total classified messages ({total_classified}) "
            f"does not match total inputs ({total_inputs})."
        )

    # 2. No duplicate keys in accepted
    seen_keys = set()
    for msg in result.accepted:
        key = (msg["device_id"], msg["timestamp"])
        if key in seen_keys:
            raise AssertionError(
                f"Contract violation: Duplicate key {key} found in accepted messages."
            )
        seen_keys.add(key)

    # 3. Deterministic chronological sorting
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
                f"Contract violation: Accepted messages violate sorting rule: {curr_key} > {next_key}."
            )

    # 4. Delivery accounting
    total_deliveries = len(result.delivered) + len(result.failed_deliveries)
    if total_deliveries != len(result.accepted):
        raise AssertionError(
            f"Contract violation: Total delivery outcomes ({total_deliveries}) "
            f"does not match accepted messages ({len(result.accepted)})."
        )

    # 5. Acknowledgement count and instance validation
    if len(result.acknowledgements) != len(result.accepted):
        raise AssertionError(
            f"Contract violation: Acknowledgements count ({len(result.acknowledgements)}) "
            f"does not match accepted messages count ({len(result.accepted)})."
        )

    for ack in result.acknowledgements:
        if not isinstance(ack, ServiceAcknowledgement):
            raise AssertionError(
                f"Contract violation: Acknowledgement must be a ServiceAcknowledgement instance, got {type(ack).__name__}."
            )
        if ack.status not in ("DELIVERED", "FAILED"):
            raise AssertionError(
                f"Contract violation: Acknowledgement status must be exactly 'DELIVERED' or 'FAILED', got {repr(ack.status)}."
            )

    # 6 & 7. Delivery integrity
    delivered_keys = {(m["device_id"], m["timestamp"]) for m in result.delivered}
    failed_keys = {(item["message"]["device_id"], item["message"]["timestamp"]) for item in result.failed_deliveries}

    # Delivered and failed sets must be mutually exclusive
    overlap = delivered_keys.intersection(failed_keys)
    if overlap:
        raise AssertionError(
            f"Contract violation: Keys {overlap} appear in both delivered and failed_deliveries."
        )

    # Check acknowledgement alignment
    for ack, msg in zip(result.acknowledgements, result.accepted):
        msg_key = (msg["device_id"], msg["timestamp"])
        if ack.status == "DELIVERED":
            if msg_key not in delivered_keys:
                raise AssertionError(
                    f"Contract violation: Message {msg_key} acknowledged as DELIVERED but missing from delivered list."
                )
        elif ack.status == "FAILED":
            if msg_key in delivered_keys:
                raise AssertionError(
                    f"Contract violation: Message {msg_key} has FAILED acknowledgement but was marked as delivered!"
                )
            if msg_key not in failed_keys:
                raise AssertionError(
                    f"Contract violation: Message {msg_key} has FAILED acknowledgement but missing from failed_deliveries."
                )
        else:
            raise AssertionError(
                f"Contract violation: Unknown acknowledgement status '{ack.status}'."
            )

    # 8. Adapter audit verification
    if adapter is not None:
        if adapter.submitted_messages != result.accepted:
            raise AssertionError(
                "Contract violation: Messages submitted to adapter do not match accepted list."
            )
        if adapter.acknowledgements != result.acknowledgements:
            raise AssertionError(
                "Contract violation: Adapter acknowledgements do not match result acknowledgements."
            )

    return True


def get_required_fixture() -> List[Any]:
    """Return the four required fixture messages for Task R15-T025."""
    return [
        {"device_id": "Device-A", "timestamp": 2, "reading": 20},
        {"device_id": "Device-A", "timestamp": 1, "reading": 10},
        {"device_id": "Device-A", "timestamp": 1, "reading": 10},  # duplicate
        {"device_id": "Device-A", "timestamp": 3, "reading": "hot"},  # invalid string reading
    ]


def main() -> None:
    """Execute the offline service adapter pipeline demonstration."""
    print("=" * 80)
    print("Task R15-T025: Sensor-Message Validation — Offline Service Adapter")
    print("Context: Lesson 1-2 Edge Ingestion & Offline Service Simulation")
    print("=" * 80)
    print()

    fixture = get_required_fixture()
    adapter = InMemoryServiceAdapter()

    print("INPUT TELEMETRY STREAM:")
    print("-" * 80)
    for idx, item in enumerate(fixture, start=1):
        print(f"  Input {idx}: {item}")
    print()

    # Process stream using the injected in-memory service adapter
    result = process_message_stream(fixture, service_adapter=adapter)

    print("PROCESSING OUTCOMES & CLASSIFICATION:")
    print("-" * 80)
    print(f"  • Accepted Messages ({len(result.accepted)}):")
    for msg in result.accepted:
        print(f"      Device: {msg['device_id']:<10} Timestamp: {msg['timestamp']:<6} Reading: {msg['reading']}")

    print(f"  • Duplicate Messages ({len(result.duplicates)}):")
    for dup in result.duplicates:
        print(f"      {dup['message']} -> {dup['reason']}")

    print(f"  • Rejected Messages ({len(result.rejected)}):")
    for rej in result.rejected:
        print(f"      {rej['input']} -> {rej['reason']}")
    print()

    print("LOCAL SERVICE ADAPTER ACKNOWLEDGEMENTS:")
    print("-" * 80)
    for ack in result.acknowledgements:
        print(f"  [{ack.status}] ID: {ack.message_id} | Device: {ack.device_id} | Ts: {ack.timestamp}")
        print(f"         Details: {ack.details}")
    print()

    print("SERVICE DELIVERY SUMMARY:")
    print("-" * 80)
    print(f"  • Confirmed Delivered: {len(result.delivered)} message(s)")
    for msg in result.delivered:
        print(f"      Device: {msg['device_id']}, Ts: {msg['timestamp']}, Reading: {msg['reading']}")
    print(f"  • Failed Deliveries:   {len(result.failed_deliveries)} message(s)")
    print()

    print("PIPELINE CONTRACT VERIFICATION:")
    print("-" * 80)
    try:
        verify_pipeline_contract(fixture, result, adapter=adapter)
        print("✓ Pipeline Contract Check PASSED: All delivery and sorting guarantees verified.")
    except AssertionError as exc:
        print(f"✗ Pipeline Contract Check FAILED: {exc}")
    print()

    print("DEMONSTRATION: Intentional Failure & Delivery Guard")
    print("-" * 80)
    # Demonstrate failure handling with a failing adapter
    failing_adapter = InMemoryServiceAdapter(should_fail=True)
    fail_result = process_message_stream(fixture, service_adapter=failing_adapter)
    print(f"  Simulated Service Outage:")
    print(f"    Accepted for delivery: {len(fail_result.accepted)}")
    print(f"    Confirmed Delivered:   {len(fail_result.delivered)} (Must be 0)")
    print(f"    Failed Deliveries:     {len(fail_result.failed_deliveries)} (Must match accepted count)")
    assert len(fail_result.delivered) == 0, "Security bug: failed delivery falsely marked delivered!"
    assert len(fail_result.failed_deliveries) == len(fail_result.accepted)
    print("  ✓ Confirmed: Pipeline never marks failed service submissions as delivered.")
    print()

    # Demonstrate that tampering with delivery state triggers AssertionError
    print("DEMONSTRATION: Contract Tampering Detection")
    print("-" * 80)
    corrupted_result = deepcopy(result)
    # Corrupt by falsely moving a failed delivery or corrupting order
    corrupted_result.accepted.reverse()
    try:
        verify_pipeline_contract(fixture, corrupted_result)
        print("  ✗ Corruption was NOT detected.")
    except AssertionError as exc:
        print(f"  ✓ Confirmed: Corrupted result was successfully caught by contract verifier:")
        print(f"    -> {exc}")

    print()
    print("EDUCATIONAL DISCLAIMER:")
    print("-" * 80)
    print("This simulation demonstrates local edge validation and a callable adapter interface.")
    print("It does NOT connect to real cloud services, physical networks, external APIs, or hardware.")
    print("=" * 80)


if __name__ == "__main__":
    main()
