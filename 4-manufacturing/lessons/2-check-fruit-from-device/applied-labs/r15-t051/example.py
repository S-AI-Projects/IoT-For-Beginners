"""R15-T051: sensor-message validation.

Local simulation only: no real device, cloud service or trained model is used.
A message is a JSON object with device_id, timestamp and a numeric reading.
"""
import json

REQUIRED_FIELDS = ("device_id", "timestamp", "reading")


def _is_number(value):
    # bool is a subclass of int in Python, so exclude it explicitly
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_messages(raw_messages):
    """Return (accepted, errors).

    accepted: valid messages, ordered by timestamp.
    errors: list of (index, reason) for rejected or duplicate messages.
    """
    accepted = []
    errors = []
    seen = set()

    for index, raw in enumerate(raw_messages):
        try:
            message = json.loads(raw)
        except (TypeError, ValueError):
            errors.append((index, "malformed JSON"))
            continue

        if not isinstance(message, dict):
            errors.append((index, "message must be a JSON object"))
            continue

        missing = [f for f in REQUIRED_FIELDS if f not in message]
        if missing:
            errors.append((index, "missing field: " + ", ".join(missing)))
            continue

        if not isinstance(message["device_id"], str) or not message["device_id"]:
            errors.append((index, "device_id must be a non-empty string"))
            continue
        if not _is_number(message["timestamp"]):
            errors.append((index, "timestamp must be numeric"))
            continue
        if not _is_number(message["reading"]):
            errors.append((index, "reading must be numeric"))
            continue

        key = (message["device_id"], message["timestamp"])
        if key in seen:
            errors.append((index, "duplicate device/timestamp: %s/%s" % key))
            continue
        seen.add(key)
        accepted.append(message)

    accepted.sort(key=lambda m: m["timestamp"])
    return accepted, errors


if __name__ == "__main__":
    demo = [
        '{"device_id": "A", "timestamp": 2, "reading": 0.9}',
        '{"device_id": "A", "timestamp": 1, "reading": 0.8}',
        '{"device_id": "A", "timestamp": 1, "reading": 0.7}',
        '{"device_id": "A", "timestamp": 3, "reading": "high"}',
    ]
    ok, bad = validate_messages(demo)
    print("accepted:", ok)
    print("errors:", bad)
