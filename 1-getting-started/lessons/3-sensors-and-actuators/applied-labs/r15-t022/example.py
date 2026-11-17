"""Sensor-Message Validation Example (Task R15-T022).

Demonstrates local validation, duplicate filtering, and deterministic sorting
for IoT sensor telemetry messages using Python's standard library.

Lesson Context:
In IoT systems, sensors measure physical properties (such as temperature or light)
and convert them into electrical and digital signals. When these measurements are
packed into telemetry messages and transmitted across networks, receiver software must
validate message structure, enforce correct datatypes, discard duplicate transmissions
caused by network retries, and ensure chronological processing.
"""

from dataclasses import dataclass
import math
from typing import Any, Dict, List


@dataclass(frozen=True)
class ProcessingResult:
    """Represents the categorized results of processing a batch of sensor messages."""

    accepted: List[Dict[str, Any]]
    duplicates: List[Dict[str, Any]]
    invalid: List[Dict[str, Any]]


def validate_sensor_message(message: Any) -> None:
    """Validate schema and data types for a single sensor message.

    Each message must be a dictionary containing:
      - 'device_id': non-empty string.
      - 'timestamp': finite numeric value (int or float; bool rejected).
      - 'reading': finite numeric value (int or float; bool rejected).

    Zero (0 or 0.0) is explicitly accepted as a valid numeric reading.
    Strings such as "25.5" are strictly rejected because sensor ingestion
    requires strongly-typed numeric data to avoid type confusion.

    Args:
        message: The candidate message dictionary.

    Raises:
        TypeError: If the message is not a dict, or fields have incorrect types
                   (including boolean values masquerading as ints).
        ValueError: If required fields are missing, empty, or non-finite.
    """
    if not isinstance(message, dict):
        raise TypeError(f"Message must be a dict, got {type(message).__name__}.")

    for required_key in ("device_id", "timestamp", "reading"):
        if required_key not in message:
            raise ValueError(f"Missing required field: '{required_key}'.")

    # 1. Validate device_id: must be a non-empty string
    device_id = message["device_id"]
    if not isinstance(device_id, str):
        raise TypeError(
            f"Field 'device_id' must be a str, got {type(device_id).__name__}."
        )
    if not device_id.strip():
        raise ValueError("Field 'device_id' must be a non-empty string.")

    # 2. Validate timestamp: finite numeric value (reject bools)
    timestamp = message["timestamp"]
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        raise TypeError(
            f"Field 'timestamp' must be a numeric value (int or float), got {type(timestamp).__name__}."
        )
    if not math.isfinite(timestamp):
        raise ValueError(
            f"Field 'timestamp' must be a finite number, got {timestamp}."
        )

    # 3. Validate reading: finite numeric value (reject bools; zero is valid)
    reading = message["reading"]
    if isinstance(reading, bool) or not isinstance(reading, (int, float)):
        raise TypeError(
            f"Field 'reading' must be a numeric value (int or float), got {type(reading).__name__}."
        )
    if not math.isfinite(reading):
        raise ValueError(
            f"Field 'reading' must be a finite number, got {reading}."
        )


def process_sensor_messages(messages: List[Any]) -> ProcessingResult:
    """Process, validate, deduplicate, and sort a collection of sensor messages.

    Rules:
      1. Messages failing schema or type validation are placed into 'invalid'.
      2. Valid messages are deduplicated on the (device_id, timestamp) pair.
         The first occurrence is accepted; subsequent occurrences are placed into 'duplicates'.
      3. Accepted messages are sorted in ascending order by timestamp.
      4. If timestamps are equal, sorting breaks ties deterministically using
         (timestamp, device_id, reading).

    Args:
        messages: A list of candidate sensor message dictionaries.

    Returns:
        ProcessingResult containing 'accepted', 'duplicates', and 'invalid' lists.
    """
    accepted: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []
    invalid: List[Dict[str, Any]] = []
    seen_keys = set()

    for item in messages:
        try:
            validate_sensor_message(item)
        except (TypeError, ValueError) as err:
            invalid.append({
                "message": item,
                "reason": str(err),
            })
            continue

        # Form deduplication key
        dedup_key = (item["device_id"], item["timestamp"])
        if dedup_key in seen_keys:
            duplicates.append({
                "message": item,
                "reason": f"Duplicate (device_id, timestamp) pair: {dedup_key}.",
            })
        else:
            seen_keys.add(dedup_key)
            accepted.append(item)

    # Sort accepted messages by timestamp ascending, with deterministic tie-breaking
    accepted.sort(key=lambda m: (m["timestamp"], m["device_id"], m["reading"]))

    return ProcessingResult(accepted=accepted, duplicates=duplicates, invalid=invalid)


def get_required_fixture() -> List[Dict[str, Any]]:
    """Return the documented local fixture dataset for Task R15-T022."""
    return [
        # Device A, timestamp 2, valid numeric reading
        {"device_id": "Device-A", "timestamp": 2, "reading": 24.5},
        # Device A, timestamp 1, valid numeric reading
        {"device_id": "Device-A", "timestamp": 1, "reading": 21.0},
        # Second Device A, timestamp 1 -> duplicate
        {"device_id": "Device-A", "timestamp": 1, "reading": 21.8},
        # Message with a string reading -> rejected (strings like "25.5" are not numeric)
        {"device_id": "Device-B", "timestamp": 3, "reading": "25.5"},
        # Valid zero reading -> accepted boundary case (demonstrating 0 is a valid measurement)
        {"device_id": "Device-C", "timestamp": 0, "reading": 0},
        # Invalid device case -> empty device_id string
        {"device_id": "", "timestamp": 4, "reading": 18.2},
        # Invalid timestamp case -> non-finite timestamp (NaN)
        {"device_id": "Device-D", "timestamp": float("nan"), "reading": 19.5},
    ]


def main() -> None:
    """Execute the sensor message validation pipeline on the required fixture."""
    print("=" * 75)
    print("Task R15-T022: Sensor-Message Validation & Boundary Processing")
    print("=" * 75)
    print()

    fixture = get_required_fixture()
    result = process_sensor_messages(fixture)

    print("1. ACCEPTED MESSAGES (Sorted chronologically, duplicates removed):")
    print("-" * 75)
    for msg in result.accepted:
        print(
            f"  Device: {msg['device_id']:<10} Timestamp: {msg['timestamp']:<5} Reading: {msg['reading']}"
        )
    print()

    print("2. DUPLICATE MESSAGES (Reported separately; first occurrence kept):")
    print("-" * 75)
    for dup in result.duplicates:
        msg = dup["message"]
        print(
            f"  Device: {msg['device_id']:<10} Timestamp: {msg['timestamp']:<5} Reading: {msg['reading']} | {dup['reason']}"
        )
    print()

    print("3. REJECTED / INVALID MESSAGES (Malformed schema or types):")
    print("-" * 75)
    for inv in result.invalid:
        print(f"  Message: {inv['message']} | Reason: {inv['reason']}")
    print()

    print("=" * 75)
    print("BOUNDARY & TYPE DECISION EXPLANATIONS:")
    print("-" * 75)
    print("• Zero Reading (0 / 0.0): ACCEPTED")
    print("  Zero is a valid physical sensor measurement (e.g., 0°C, 0 lux, 0 mm).")
    print("  Falsy checks (e.g. 'if not reading:') must not discard legitimate zero readings.")
    print()
    print("• String Reading (\"25.5\"): REJECTED")
    print("  Sensor payloads must enforce strong numeric types (int/float). Allowing strings")
    print("  leads to silent type coercion bugs, string concatenation errors, and incorrect")
    print("  lexicographical sorting in downstream IoT analytics.")
    print("=" * 75)


if __name__ == "__main__":
    main()
