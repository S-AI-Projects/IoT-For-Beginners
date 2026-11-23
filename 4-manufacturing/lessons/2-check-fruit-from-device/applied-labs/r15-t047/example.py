"""Deterministic OFFLINE JSON-message validation: no hardware or service calls."""
import json
import math

# Local, fictional sensor-message data; no actual readings or recognition results.
FIXTURE = (
    '{"device_id":"A","timestamp":2,"reading":10.5}',
    '{"device_id":"A","timestamp":1,"reading":8}',
    '{"device_id":"A","timestamp":1,"reading":999}',
    '{"device_id":"A","timestamp":3,"reading":"bad"}',
)


def validate(raw):
    """Parse one JSON string and check shape/types, not authenticity of sensors."""
    if not isinstance(raw, str):
        raise ValueError("invalid_json")
    try:
        message = json.loads(raw)
    except (ValueError, TypeError):
        raise ValueError("invalid_json") from None
    if not isinstance(message, dict):
        raise ValueError("invalid_object")
    if not isinstance(message.get("device_id"), str) or not message["device_id"].strip():
        raise ValueError("invalid_device_id")
    if type(message.get("timestamp")) is not int:
        raise ValueError("invalid_timestamp")
    reading = message.get("reading")
    if type(reading) not in (int, float) or (type(reading) is float and not math.isfinite(reading)):
        raise ValueError("invalid_reading")
    return {"device_id": message["device_id"], "timestamp": message["timestamp"], "reading": reading}


def process(messages, trace=False):
    """Keep first valid device/time pair; sort accepted records by timestamp."""
    accepted, rejected, seen, history = [], [], set(), []
    for index, raw in enumerate(messages):
        try:
            record = validate(raw)
        except ValueError as exc:
            rejected.append({"index": index, "reason": str(exc)})
        else:
            key = (record["device_id"], record["timestamp"])
            if key in seen:
                rejected.append({"index": index, "reason": "duplicate_device_timestamp"})
            else:
                seen.add(key)
                accepted.append(record)
        if trace:
            history.append({"step": index + 1, "accepted_count": len(accepted),
                            "rejected_count": len(rejected), "keys": sorted(seen)})
    accepted.sort(key=lambda item: (item["timestamp"], item["device_id"]))
    result = {"accepted": accepted, "rejected": rejected}
    if trace:
        result["trace"] = history
    return result


def brief(result):
    """A stable textual report for comparison with the lesson's fixture."""
    keys = ["{}@{}".format(r["device_id"], r["timestamp"]) for r in result["accepted"]]
    reasons = [str(r["index"]) + ":" + r["reason"] for r in result["rejected"]]
    return "accepted=[{}] rejected=[{}]".format(",".join(keys), ",".join(reasons))


def worked_steps(messages=FIXTURE):
    """Explain actual computed decisions, then show the sorted final output."""
    seen = set()
    lines = []
    for index, raw in enumerate(messages):
        try:
            record = validate(raw)
        except ValueError as exc:
            lines.append("{}: reject {}".format(index, exc))
            continue
        key = (record["device_id"], record["timestamp"])
        if key in seen:
            lines.append("{}: reject duplicate_device_timestamp".format(index))
        else:
            seen.add(key)
            lines.append("{}: accept {}@{}".format(index, *key))
    lines.append("sorted " + brief(process(messages)))
    return lines


def main():
    print("FICTIONAL fruit-device message records (not image classification)")
    for line in worked_steps():
        print(line)


if __name__ == "__main__":
    main()
