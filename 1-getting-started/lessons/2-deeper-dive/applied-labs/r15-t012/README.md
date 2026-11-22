# Applied Lab: Sensor-Message Validation — Boundary-Case Lesson Extension (R15-T012)

This lab extends the [A Deeper Dive into IoT lesson](../../README.md) by demonstrating schema validation, timestamp re-ordering, and duplicate prevention for streaming IoT telemetry messages.

## Concept & Curriculum Connection

IoT sensors transmit readings as JSON payloads over MQTT or HTTP. Due to network jitter or retries:
1. Packets may arrive out-of-order.
2. Duplicate messages may be re-sent.
3. Payloads may contain malformed values (such as strings instead of raw numbers).

This local module demonstrates how an ingestion pipeline validates telemetry messages, orders them chronologically, and discards duplicate or invalid records.

## Contract & Boundary Decisions
- **Required Fields:** Each record requires `device_id` (str), `timestamp` (numeric: int or float), and `reading` (numeric: int or float).
- **String Rejection:** String values (even numeric strings like `"25.0"`) are rejected to enforce strong typing at the gateway boundary.
- **Boolean Guard:** Booleans (`True`/`False`) are rejected despite being Python `int` subclasses.
- **Deduplication:** A composite key `(device_id, timestamp)` is tracked; subsequent occurrences are reported as duplicates.
- **Ordering:** Accepted messages are sorted ascending by timestamp.

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example
```bash
python3 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t012/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t012 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Ingestion:** Simulates message validation in-memory without requiring an MQTT broker or physical microcontroller.
- **Hardware Boundary:** No physical sensor hardware or cloud IoT hub is required.
