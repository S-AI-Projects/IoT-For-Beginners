# R15-T038: sensor-message validation, failure and recovery

Extends the [Interact with the physical world with sensors and actuators](../../README.md)
lesson. Sensors send readings from a device; this example checks JSON sensor
messages on arrival, explains each rejection, and shows the stream carrying on
with the next valid message.

**Scope:** a local simulation in standard-library Python 3 on JSON strings. No
real sensor, device, broker, IoT service, model or paid provider. It does not
model network loss, clock drift, out-of-range physical values or units.

## Message contract

A JSON object with `device_id` (non-empty string), `timestamp` (integer >= 0)
and `reading` (a number; a string like `"21.5"` is rejected).

- Accepted messages are returned ordered by `(timestamp, device_id)`.
- A repeated `(device_id, timestamp)` pair is rejected as a duplicate.
- Every rejection raises `MessageError` with an explanation, and a rejected
  message never changes the stream state.

## Fixture and expected output

| # | Message | Outcome |
|---|---|---|
| 0 | A, timestamp 2, reading 21.5 | accepted |
| 1 | A, timestamp 1, reading 20.0 | accepted |
| 2 | A, timestamp 1, reading 20.0 | rejected: `duplicate message for device A at timestamp 1` |
| 3 | A, timestamp 3, reading `"22.0"` (string) | rejected: `reading must be a number, got str` |
| 4 | A, timestamp 3, no reading | rejected: `missing field: reading` |
| 5 | A, timestamp 3, reading 22.0, closing brace missing | rejected: `malformed JSON: ...` (the rest of the text comes from Python's `json` module) |
| 6 | A, timestamp 3, reading 22.0 | **accepted (recovery)** |

Result: messages for A sent as timestamp 2 then 1 come back in order 1, 2, and
timestamp 3 is accepted at the end. Accepted: `('A', 1, 20.0)`, `('A', 2, 21.5)`, `('A', 3, 22.0)`.

## Failure and recovery

Message 5 is the documented failure: the JSON is cut off. The error says it is
malformed JSON. Message 6 is the same reading, correctly formed, and is accepted
because messages 3 to 5 left no trace in the stream state (they never reserved
timestamp 3). A test asserts exactly this.

## Run

```
python3 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t038/example.py
python3 -m unittest discover -s 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t038 -p "test_*.py"
```
