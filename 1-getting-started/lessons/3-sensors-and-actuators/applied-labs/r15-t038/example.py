"""Sensor-message validation with failure and recovery (R15-T038).

Standard library only. A SIMULATION on local JSON strings: no real sensor,
device, broker or cloud service is used.

A message is a JSON object with:
  device_id : non-empty string
  timestamp : integer >= 0 (not a bool)
  reading   : number (int or float, finite; a string such as "21.5" is rejected)

Rules:
  * accepted messages are returned ordered by (timestamp, device_id)
  * a second message with the same (device_id, timestamp) is rejected
  * a rejected message never changes the stream state, so the next valid
    message is accepted normally (recovery)
"""

import json
import math


class MessageError(ValueError):
    """A message was rejected. The text explains why."""


def parse_message(raw):
    """Validate one raw JSON string and return (device_id, timestamp, reading)."""
    try:
        data = json.loads(raw)
    except (TypeError, ValueError) as err:
        raise MessageError("malformed JSON: %s" % err)
    if not isinstance(data, dict):
        raise MessageError("message must be a JSON object")
    for field in ("device_id", "timestamp", "reading"):
        if field not in data:
            raise MessageError("missing field: %s" % field)

    device_id, timestamp, reading = data["device_id"], data["timestamp"], data["reading"]
    if not isinstance(device_id, str) or not device_id.strip():
        raise MessageError("device_id must be a non-empty string")
    if isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp < 0:
        raise MessageError("timestamp must be an integer >= 0")
    if isinstance(reading, bool) or not isinstance(reading, (int, float)):
        raise MessageError("reading must be a number, got %s" % type(reading).__name__)
    if isinstance(reading, float) and not math.isfinite(reading):
        raise MessageError("reading must be finite")
    return device_id, timestamp, reading


class SensorStream:
    """Accepts messages one at a time and remembers what it has accepted."""

    def __init__(self):
        self._seen = set()
        self._accepted = []

    def ingest(self, raw):
        """Return the accepted (device_id, timestamp, reading) or raise MessageError."""
        device_id, timestamp, reading = parse_message(raw)
        key = (device_id, timestamp)
        if key in self._seen:
            raise MessageError("duplicate message for device %s at timestamp %d"
                               % (device_id, timestamp))
        self._seen.add(key)
        self._accepted.append((device_id, timestamp, reading))
        return self._accepted[-1]

    def ordered(self):
        """Accepted messages ordered by (timestamp, device_id)."""
        return sorted(self._accepted, key=lambda m: (m[1], m[0]))


def process(raw_messages):
    """Run a list of raw messages. Returns (ordered_accepted, errors) where
    errors is a list of (index, explanation). Processing continues after an error."""
    stream = SensorStream()
    errors = []
    for i, raw in enumerate(raw_messages):
        try:
            stream.ingest(raw)
        except MessageError as err:
            errors.append((i, str(err)))
    return stream.ordered(), errors


# Documented fixture: a bad message in the middle, then recovery.
FIXTURE = [
    '{"device_id": "A", "timestamp": 2, "reading": 21.5}',
    '{"device_id": "A", "timestamp": 1, "reading": 20.0}',
    '{"device_id": "A", "timestamp": 1, "reading": 20.0}',   # duplicate A/1
    '{"device_id": "A", "timestamp": 3, "reading": "22.0"}',  # string reading
    '{"device_id": "A", "timestamp": 3}',                     # missing reading
    '{"device_id": "A", "timestamp": 3, "reading": 22.0',     # malformed JSON
    '{"device_id": "A", "timestamp": 3, "reading": 22.0}',    # recovery
]


if __name__ == "__main__":
    accepted, errors = process(FIXTURE)
    print("accepted:")
    for m in accepted:
        print("  ", m)
    print("errors:")
    for i, e in errors:
        print("  message %d: %s" % (i, e))
