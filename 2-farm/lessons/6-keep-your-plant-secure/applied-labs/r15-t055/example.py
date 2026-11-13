import json
import math
from typing import Any


def process_messages_baseline(raw_payloads: list[str]) -> dict[str, Any]:
    """
    Monolithic baseline implementation: parses JSON, validates schema and numeric
    reading, deduplicates (device_id, timestamp), and orders accepted messages.
    """
    seen_keys: set[tuple[str, int | float]] = set()
    accepted: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []

    for raw in raw_payloads:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON payload: {raw!r}") from exc

        if not isinstance(msg, dict):
            raise ValueError(f"Payload must be a JSON object: {msg!r}")

        for field in ("device_id", "timestamp", "reading"):
            if field not in msg:
                raise ValueError(f"Missing required field {field!r}: {msg!r}")

        device_id = msg["device_id"]
        timestamp = msg["timestamp"]
        reading = msg["reading"]

        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError(f"Invalid device_id {device_id!r}")
        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)) or not math.isfinite(timestamp):
            raise ValueError(f"Invalid timestamp {timestamp!r}")
        if isinstance(reading, bool) or not isinstance(reading, (int, float)) or not math.isfinite(reading):
            raise ValueError(f"Non-numeric reading rejected: {reading!r}")

        key = (device_id, timestamp)
        if key in seen_keys:
            duplicates.append({"device_id": device_id, "timestamp": timestamp, "reason": "duplicate"})
            continue

        seen_keys.add(key)
        accepted.append({
            "device_id": device_id,
            "timestamp": timestamp,
            "reading": float(reading),
        })

    accepted.sort(key=lambda item: (item["timestamp"], item["device_id"]))
    return {"accepted": accepted, "duplicates": duplicates}


def validate_and_parse_message(raw: str) -> dict[str, Any]:
    """Extracted single responsibility: decode JSON and validate message schema/types."""
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON payload: {raw!r}") from exc

    if not isinstance(msg, dict):
        raise ValueError(f"Payload must be a JSON object: {msg!r}")

    for field in ("device_id", "timestamp", "reading"):
        if field not in msg:
            raise ValueError(f"Missing required field {field!r}: {msg!r}")

    device_id = msg["device_id"]
    timestamp = msg["timestamp"]
    reading = msg["reading"]

    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError(f"Invalid device_id {device_id!r}")
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)) or not math.isfinite(timestamp):
        raise ValueError(f"Invalid timestamp {timestamp!r}")
    if isinstance(reading, bool) or not isinstance(reading, (int, float)) or not math.isfinite(reading):
        raise ValueError(f"Non-numeric reading rejected: {reading!r}")

    return {
        "device_id": device_id,
        "timestamp": timestamp,
        "reading": float(reading),
    }


def process_messages_refactored(raw_payloads: list[str]) -> dict[str, Any]:
    """
    Refactored implementation delegating schema/type validation to
    `validate_and_parse_message` while preserving the exact output contract.
    """
    seen_keys: set[tuple[str, int | float]] = set()
    accepted: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []

    for raw in raw_payloads:
        record = validate_and_parse_message(raw)
        key = (record["device_id"], record["timestamp"])
        if key in seen_keys:
            duplicates.append({
                "device_id": record["device_id"],
                "timestamp": record["timestamp"],
                "reason": "duplicate",
            })
            continue

        seen_keys.add(key)
        accepted.append(record)

    accepted.sort(key=lambda item: (item["timestamp"], item["device_id"]))
    return {"accepted": accepted, "duplicates": duplicates}


if __name__ == "__main__":
    fixture = [
        '{"device_id": "A", "timestamp": 2, "reading": 24.5}',
        '{"device_id": "A", "timestamp": 1, "reading": 23.0}',
        '{"device_id": "A", "timestamp": 1, "reading": 23.0}',
    ]
    baseline_result = process_messages_baseline(fixture)
    refactored_result = process_messages_refactored(fixture)
    assert baseline_result == refactored_result
    print(json.dumps({
        "equivalent": baseline_result == refactored_result,
        "result": refactored_result,
    }, indent=2))
