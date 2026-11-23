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


def make_fixture(group_count):
    """Repeat the same four input classes using distinct fictional devices."""
    if type(group_count) is not int or group_count < 1:
        raise ValueError("group_count must be a positive integer")
    messages = []
    for index in range(group_count):
        ident = "A" + str(index)
        for timestamp, reading in ((2, 10.5), (1, 8), (1, 999), (3, "bad")):
            messages.append(json.dumps({"device_id": ident, "timestamp": timestamp, "reading": reading}))
    return messages


def evaluate():
    """Compare 4/8/16 inputs using exact count correctness, not time/accuracy."""
    output = []
    for groups in (1, 2, 4):
        messages = make_fixture(groups)
        actual = process(messages)
        accepted, rejected = len(actual["accepted"]), len(actual["rejected"])
        expected = (groups * 2, groups * 2)
        output.append({"inputs": len(messages), "accepted": accepted,
                       "rejected": rejected, "expected": expected,
                       "count_correct": (accepted, rejected) == expected,
                       "acceptance_fraction": accepted / len(messages)})
    return output


def main():
    print("FICTIONAL offline validation size comparison; no performance benchmark")
    for row in evaluate():
        print("inputs={inputs} accepted={accepted} rejected={rejected} acceptance_fraction={acceptance_fraction:.2f} correct={count_correct}".format(**row))
    print("Trade-off: more records require processing more inputs; correctness ratio unchanged.")


if __name__ == "__main__":
    main()
