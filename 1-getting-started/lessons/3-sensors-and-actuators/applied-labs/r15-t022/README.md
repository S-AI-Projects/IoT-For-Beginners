# Applied Lab R15-T022: Sensor-Message Validation

This applied lab demonstrates schema validation, type safety, deduplication, and deterministic chronological ordering of IoT sensor telemetry messages using Python's standard library.

> ⚠️ **Simulation / Mock Scope**
>
> This lab is a **local Python simulation and educational demonstration** using mock fixture data. It does **not** connect to real sensor hardware (such as Grove or Raspberry Pi GPIO pins) and does **not** integrate with live network protocols (such as MQTT or HTTP) or cloud IoT ingestion pipelines (such as Azure IoT Hub).

---

## Overview

In Lesson 3, you learned how IoT sensors convert physical real-world phenomena (e.g. ambient light, temperature, voltage) into electrical signals and digital values. Before these measurements can be used in decision-making, analytics, or automated actuator triggers (like turning on a nightlight), telemetry payloads sent from devices must be validated.

In real-world networks:
1. **Network Retries Cause Duplicates:** Due to transient wireless or cellular interruptions, an IoT device or gateway may send the same telemetry packet more than once.
2. **Schema & Type Corruptions Occur:** Serialization flaws or corrupted transmissions can introduce non-numeric data, missing fields, or empty device identifiers.
3. **Out-of-Order Delivery Happens:** Network packets may arrive out of chronological sequence, requiring deterministic sorting by timestamp before processing.

---

## Message Schema and Rules

Each sensor message is expected to be a dictionary with three fields:

```python
{
    "device_id": str,     # Non-empty string identifying the device
    "timestamp": float,   # Finite numeric value (int or float)
    "reading": float      # Finite numeric value (int or float)
}
```

### Validation & Duplicate-Handling Rules

1. **`device_id` Validation:** Must be an instance of `str` and non-empty (cannot be blank or whitespace-only). Non-string types (e.g. `None`, numbers) are rejected with `TypeError`; empty strings are rejected with `ValueError`.
2. **`timestamp` Validation:** Must be a finite numeric value (`int` or `float`). Booleans (even though `isinstance(True, int)` is `True` in Python) are strictly rejected with `TypeError`. Non-finite numbers (`NaN`, `+Inf`, `-Inf`) are rejected with `ValueError`.
3. **`reading` Validation:** Must be a finite numeric value (`int` or `float`). Booleans are rejected with `TypeError`. Non-finite floats are rejected with `ValueError`.
4. **Boundary Case — Zero Reading:** Zero (`0` or `0.0`) is explicitly accepted as a valid measurement. Zero is a legitimate reading for many physical sensors (e.g., $0^\circ\text{C}$ temperature, $0\text{ lux}$ darkness, $0\text{ mm}$ distance). Falsy checks (such as `if not reading:`) must not discard valid zero readings. No artificial physical sensor bounds are assumed.
5. **String Readings Rejected:** Strings like `"25.5"` are rejected with `TypeError`. Telemetry pipelines require explicit numeric types to prevent silent type coercion, formatting anomalies, and lexicographical sorting bugs in downstream systems.
6. **Deduplication:** Duplicates are identified by the tuple `(device_id, timestamp)`. The first valid occurrence is retained in `accepted`; subsequent occurrences are logged separately in `duplicates` (distinguished from malformed `invalid` records).
7. **Deterministic Ordering:** Accepted messages are sorted in ascending order by `timestamp`. When timestamps are identical across different devices, ties are broken deterministically by sorting on `(timestamp, device_id, reading)`.

---

## Prerequisites

* **Python 3.x**
* **Python Standard Library only** (no external packages or pip installations required).

---

## Running the Example

Run the script from the repository root:

```bash
python3 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t022/example.py
```

### Fixture Inputs

The example evaluates a local mock dataset:
1. `{"device_id": "Device-A", "timestamp": 2, "reading": 24.5}` (Valid Device A, timestamp 2)
2. `{"device_id": "Device-A", "timestamp": 1, "reading": 21.0}` (Valid Device A, timestamp 1)
3. `{"device_id": "Device-A", "timestamp": 1, "reading": 21.8}` (Duplicate Device A, timestamp 1)
4. `{"device_id": "Device-B", "timestamp": 3, "reading": "25.5"}` (Invalid reading: string `"25.5"`)
5. `{"device_id": "Device-C", "timestamp": 0, "reading": 0}` (Valid boundary reading: `0`)
6. `{"device_id": "", "timestamp": 4, "reading": 18.2}` (Invalid: empty `device_id`)
7. `{"device_id": "Device-D", "timestamp": float("nan"), "reading": 19.5}` (Invalid: NaN `timestamp`)

### Expected Output

```output
===========================================================================
Task R15-T022: Sensor-Message Validation & Boundary Processing
===========================================================================

1. ACCEPTED MESSAGES (Sorted chronologically, duplicates removed):
---------------------------------------------------------------------------
  Device: Device-C   Timestamp: 0     Reading: 0
  Device: Device-A   Timestamp: 1     Reading: 21.0
  Device: Device-A   Timestamp: 2     Reading: 24.5

2. DUPLICATE MESSAGES (Reported separately; first occurrence kept):
---------------------------------------------------------------------------
  Device: Device-A   Timestamp: 1     Reading: 21.8 | Duplicate (device_id, timestamp) pair: ('Device-A', 1).

3. REJECTED / INVALID MESSAGES (Malformed schema or types):
---------------------------------------------------------------------------
  Message: {'device_id': 'Device-B', 'timestamp': 3, 'reading': '25.5'} | Reason: Field 'reading' must be a numeric value (int or float), got str.
  Message: {'device_id': '', 'timestamp': 4, 'reading': 18.2} | Reason: Field 'device_id' must be a non-empty string.
  Message: {'device_id': 'Device-D', 'timestamp': nan, 'reading': 19.5} | Reason: Field 'timestamp' must be a finite number, got nan.

===========================================================================
BOUNDARY & TYPE DECISION EXPLANATIONS:
---------------------------------------------------------------------------
• Zero Reading (0 / 0.0): ACCEPTED
  Zero is a valid physical sensor measurement (e.g., 0°C, 0 lux, 0 mm).
  Falsy checks (e.g. 'if not reading:') must not discard legitimate zero readings.

• String Reading ("25.5"): REJECTED
  Sensor payloads must enforce strong numeric types (int/float). Allowing strings
  leads to silent type coercion bugs, string concatenation errors, and incorrect
  lexicographical sorting in downstream IoT analytics.
===========================================================================
```

---

## Running the Unit Tests

Execute the unit test suite using Python's standard `unittest` test discovery from the repository root:

```bash
python3 -m unittest discover -s 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t022 -p "test_*.py"
```

You can also run tests with verbose output:

```bash
python3 -m unittest discover -s 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t022 -p "test_*.py" -v
```

### Expected Test Output

```output
Ran 13 tests in 0.001s

OK
```

---

## Limitations and Simplifications

1. **In-Memory State:** Deduplication state is maintained in-memory using a Python `set`. A production IoT service would typically use distributed caching (e.g. Redis) or message deduplication features in message brokers (e.g. Azure Service Bus, Kafka).
2. **Batch Processing:** This example processes a batch list of messages at once rather than handling streaming asynchronous event streams.
3. **No Sensor Range Enforcement:** The validator checks numeric finiteness but intentionally avoids asserting arbitrary physical sensor ranges (e.g. $-40^\circ\text{C}$ to $125^\circ\text{C}$), leaving physical range constraints to domain-specific downstream logic.
