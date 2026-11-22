"""
Sensor-Message Validation — Failure and Recovery Example (R15-T018)

Lesson reference: 6-consumer/lessons/1-speech-recognition/README.md
Concept: Smart consumer audio devices stream microphone telemetry and audio energy levels.
Due to wireless packet drops or transmission glitches, packets may arrive with missing data,
corrupted string types, or duplicates. The ingestion handler must reject malformed frames
with explanatory error diagnostics and seamlessly recover on the next valid packet.

Focus:
Exercise documented invalid/missing-data cases, log error diagnostics, and demonstrate
resilient state recovery upon receiving subsequent valid inputs.

Contract:
1. Valid message requires: device_id (str), timestamp (numeric: int or float), reading (numeric).
2. 'reading' must be numeric (int/float, not bool or str); string readings rejected.
3. Duplicate (device_id, timestamp) pairs are reported and rejected.
4. Accepted messages are ordered by timestamp ascending.
5. Ingestion pipeline preserves state and recovers immediately when valid data resumes.
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class ResilientTelemetryIngestor:
    """
    Stateful ingestion processor that records accepted telemetry and handles
    invalid/missing-data failures without crashing.
    """

    def __init__(self):
        self.accepted_messages: List[Dict[str, Any]] = []
        self.seen_keys: Set[Tuple[str, float]] = set()
        self.error_log: List[Dict[str, Any]] = []

    def ingest_single(self, msg: Any) -> Tuple[bool, str]:
        """
        Ingests a single packet. Returns (success: bool, status_message: str).
        Demonstrates per-packet validation, error explanation, and instant recovery.
        """
        if not isinstance(msg, dict):
            err = "MALFORMED_PACKET: Expected JSON object"
            self.error_log.append({"message": msg, "error": err})
            return False, err

        # Check for missing data
        missing = [k for k in ("device_id", "timestamp", "reading") if k not in msg]
        if missing:
            err = f"MISSING_DATA: Missing required field(s): {', '.join(missing)}"
            self.error_log.append({"message": msg, "error": err})
            return False, err

        dev = msg["device_id"]
        ts = msg["timestamp"]
        val = msg["reading"]

        if not isinstance(dev, str) or not dev.strip():
            err = "INVALID_FIELD: device_id must be a non-empty string"
            self.error_log.append({"message": msg, "error": err})
            return False, err

        if isinstance(ts, bool) or not isinstance(ts, (int, float)):
            err = "INVALID_FIELD: timestamp must be numeric"
            self.error_log.append({"message": msg, "error": err})
            return False, err

        # Reject string or boolean readings
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            err = f"TYPE_ERROR: reading must be numeric (got {type(val).__name__}: {val!r})"
            self.error_log.append({"message": msg, "error": err})
            return False, err

        # Check duplicate
        key = (dev, float(ts))
        if key in self.seen_keys:
            err = f"DUPLICATE: Record already exists for device '{dev}' at timestamp {ts}"
            self.error_log.append({"message": msg, "error": err})
            return False, err

        # Accepted
        self.seen_keys.add(key)
        self.accepted_messages.append(msg)
        return True, f"ACCEPTED: Device '{dev}' timestamp {ts}"

    def ingest_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ingests a sequence of packets and returns sorted accepted records."""
        for packet in batch:
            self.ingest_single(packet)

        sorted_accepted = sorted(self.accepted_messages, key=lambda m: m["timestamp"])
        return {
            "accepted": sorted_accepted,
            "errors": list(self.error_log),
        }


def run_demo():
    stream = [
        {"device_id": "A", "timestamp": 2, "reading": 15.0},
        {"device_id": "A", "timestamp": 1, "reading": 12.5},
        {"device_id": "A", "timestamp": 1, "reading": 12.8},  # duplicate A/1
        {"device_id": "B", "timestamp": 3, "reading": "invalid_audio_level"},  # string reading error
        {"device_id": "B", "timestamp": 4},  # missing reading field
        {"device_id": "B", "timestamp": 5, "reading": 18.2},  # recovery on next valid input!
    ]
    ingestor = ResilientTelemetryIngestor()
    result = ingestor.ingest_batch(stream)
    print("Accepted & Sorted:", result["accepted"])
    print("Errors Encountered:")
    for e in result["errors"]:
        print(f"  {e['error']} -> {e['message']}")
    return result


if __name__ == "__main__":
    run_demo()
