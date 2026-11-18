# Applied Lab R15-T024: Sensor-Message Validation — Invariant and State Trace

This applied lab demonstrates how to validate incoming IoT JSON telemetry messages, detect and filter duplicate transmissions, order events chronologically, record step-by-step intermediate processing state traces, and enforce end-to-end pipeline invariants using Python's standard library.

> ⚠️ **Educational Simulation Disclaimer**
>
> This lab is a **local Python simulation** using predefined fixture data. It does **not** connect to a physical IoT sensor, a live MQTT broker (such as `test.mosquitto.org`), a cloud service (such as Azure IoT Hub), or a production stream-processing cluster. It focuses strictly on the algorithmic principles of data validation, deduplication, chronological state tracing, and invariant verification.

---

## Lesson Context: JSON Telemetry & MQTT Ingestion

In [Lesson 4: Connect your device to the Internet](../../README.md), IoT devices gather measurements from sensors and publish telemetry as JSON payloads over MQTT topics.

In real-world distributed IoT networks:
1. **Network Retries & At-Least-Once Delivery (QoS 1):** Unreliable wireless connections cause devices to retry publishing, resulting in duplicate deliveries with the same `(device_id, timestamp)` identity.
2. **Out-of-Order Message Delivery:** Packets transmitted across internet routes can arrive out of chronological order.
3. **Payload Corruption:** Flawed firmware, serialization bugs, or transmission truncations introduce malformed JSON or non-numeric sensor readings (such as strings or non-finite numbers).
4. **State Traceability & Invariants:** Ingestion systems must maintain verifiable guarantees (invariants) that every message has a single outcome, accepted data is strictly sorted, duplicates are safely isolated, and malformed messages never reserve identity.

---

## Message Schema and Rules

Each sensor telemetry message is expected to be a JSON object (or dictionary) with three required fields:

```json
{
  "device_id": "Device-A",
  "timestamp": 1600000000,
  "reading": 25.5
}
```

### Validation & Processing Rules

1. **`device_id` Validation:** Must be a non-empty string. Non-string types raise `TypeError`; empty strings raise `ValueError`.
2. **`timestamp` Validation:** Must be a finite numeric value (`int` or `float`). Booleans (subclasses of `int` in Python) are rejected with `TypeError`. Non-finite values (`NaN`, `Inf`) raise `ValueError`.
3. **`reading` Validation:** Must be a finite numeric value (`int` or `float`). Booleans are rejected with `TypeError`. Non-finite values raise `ValueError`. Zero (`0` or `0.0`) is accepted as a valid physical measurement.
4. **Malformed JSON Handling:** Invalid JSON syntax or non-dictionary payloads are rejected.
5. **No Identity Reservation on Rejection:** If a message is rejected due to invalid fields or syntax, its `(device_id, timestamp)` is **not** registered in the deduplication cache, allowing any subsequent valid message with that timestamp to be accepted.
6. **Deduplication:** Valid messages are checked against previously seen `(device_id, timestamp)` pairs. The first valid occurrence is accepted; subsequent messages with the same device and timestamp identity are marked `DUPLICATE`. Timestamps are not required or expected to be globally unique across distinct devices; independent IoT devices can legitimately transmit readings at the same timestamp.
7. **Deterministic Chronological Sorting:** Accepted messages are maintained in deterministic ascending order using the tuple `(timestamp, device_id, reading)`. Chronological timestamp ordering is preserved as the primary key, with device ID and sensor reading providing a strict, deterministic tie-breaking sequence when telemetry from multiple devices arrives with matching timestamps.

---

## State Trace and Pipeline Invariants

### Intermediate State Trace
The pipeline captures a `TraceStep` snapshot after processing every individual input message:
* **Step Number:** Sequential 1-based step counter (`1, 2, ...`).
* **Current Input:** The raw message payload processed.
* **Step Outcome:** `ACCEPTED`, `DUPLICATE`, or `REJECTED` with a human-readable reason.
* **Accepted So Far:** The ordered list of accepted messages up to this step.
* **Duplicates So Far:** The list of duplicate messages identified so far.
* **Rejected So Far:** The list of rejected messages identified so far.

### Verified Pipeline Invariants
The function `check_pipeline_invariant(inputs, result)` verifies core system invariants:
1. **Sequential Step Numbering:** Every trace step records a sequential `step_number` starting at 1.
2. **Outcome Completeness:** Every input message has exactly one recorded outcome in the trace, and trace length equals total inputs.
3. **Intermediate Snapshot Consistency & State Reconstruction:** At every step $k$, the invariant checker independently reconstructs expected state from the inputs. It verifies that cumulative counts satisfy $\text{len}(accepted\_so\_far) + \text{len}(duplicates\_so\_far) + \text{len}(rejected\_so\_far) = k$, step raw inputs match input indices, outcome statuses are correct, and complete snapshot lists (`accepted_so_far`, `duplicates_so_far`, `rejected_so_far`) match reconstructed state exactly, detecting content tampering even when list lengths and sorting remain unchanged.
4. **Final State Agreement:** Final accepted, duplicate, and rejected lists agree with the last recorded trace snapshot.
5. **Classification Consistency:** Final accepted, duplicate, and rejected counts match the respective `ACCEPTED`, `DUPLICATE`, and `REJECTED` outcome counts in the trace.
6. **Accepted Field Validity:** Every accepted message contains valid, finite fields conforming to the schema.
7. **No Duplicate Identity in Accepted:** No two accepted messages share the same `(device_id, timestamp)` key (timestamps are not assumed to be unique across different devices).
8. **Deterministic Chronological Ordering:** Accepted messages strictly follow the sorting rule `(timestamp, device_id, reading)`, ensuring proper ordering and tie-breaking across different devices.

---

## Prerequisites

* **Python 3.x**
* **Python Standard Library only** (no external packages, cloud services, or MQTT libraries required).

---

## Running the Example

Run the script from the repository root:

```bash
python3 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t024/example.py
```

### Required Fixture Inputs

The fixture executes the following four inputs in sequence:
1. `{"device_id": "Device-A", "timestamp": 2, "reading": 20}` (Valid Device A, timestamp 2)
2. `{"device_id": "Device-A", "timestamp": 1, "reading": 10}` (Valid Device A, timestamp 1)
3. `{"device_id": "Device-A", "timestamp": 1, "reading": 11}` (Duplicate Device A, timestamp 1)
4. `{"device_id": "Device-A", "timestamp": 3, "reading": "not-a-number"}` (Invalid string reading)

### Expected Output

```output
================================================================================
Task R15-T024: Sensor-Message Validation — Invariant & State Trace
Context: Lesson 1-4 Internet Telemetry Ingestion over MQTT
================================================================================

STEP-BY-STEP INTERMEDIATE STATE TRACE:
--------------------------------------------------------------------------------
Step 1:
  Input:   {'device_id': 'Device-A', 'timestamp': 2, 'reading': 20}
  Outcome: [ACCEPTED] Valid message accepted and sorted chronologically.
  Accepted (1):   [{'device_id': 'Device-A', 'timestamp': 2, 'reading': 20}]
  Duplicates (0): []
  Rejected (0):   []
--------------------------------------------------------------------------------
Step 2:
  Input:   {'device_id': 'Device-A', 'timestamp': 1, 'reading': 10}
  Outcome: [ACCEPTED] Valid message accepted and sorted chronologically.
  Accepted (2):   [{'device_id': 'Device-A', 'timestamp': 1, 'reading': 10}, {'device_id': 'Device-A', 'timestamp': 2, 'reading': 20}]
  Duplicates (0): []
  Rejected (0):   []
--------------------------------------------------------------------------------
Step 3:
  Input:   {'device_id': 'Device-A', 'timestamp': 1, 'reading': 11}
  Outcome: [DUPLICATE] Duplicate (device_id, timestamp) pair already seen: ('Device-A', 1).
  Accepted (2):   [{'device_id': 'Device-A', 'timestamp': 1, 'reading': 10}, {'device_id': 'Device-A', 'timestamp': 2, 'reading': 20}]
  Duplicates (1): [{'message': {'device_id': 'Device-A', 'timestamp': 1, 'reading': 11}, 'reason': "Duplicate (device_id, timestamp) pair already seen: ('Device-A', 1)."}]
  Rejected (0):   []
--------------------------------------------------------------------------------
Step 4:
  Input:   {'device_id': 'Device-A', 'timestamp': 3, 'reading': 'not-a-number'}
  Outcome: [REJECTED] Field 'reading' must be a finite number (int or float), got str.
  Accepted (2):   [{'device_id': 'Device-A', 'timestamp': 1, 'reading': 10}, {'device_id': 'Device-A', 'timestamp': 2, 'reading': 20}]
  Duplicates (1): [{'message': {'device_id': 'Device-A', 'timestamp': 1, 'reading': 11}, 'reason': "Duplicate (device_id, timestamp) pair already seen: ('Device-A', 1)."}]
  Rejected (1):   [{'input': {'device_id': 'Device-A', 'timestamp': 3, 'reading': 'not-a-number'}, 'reason': "Field 'reading' must be a finite number (int or float), got str."}]
--------------------------------------------------------------------------------

FINAL SUMMARY:
  • Accepted Messages (2):
      Device: Device-A   Timestamp: 1    Reading: 10
      Device: Device-A   Timestamp: 2    Reading: 20
  • Duplicates Detected (1):
      {'device_id': 'Device-A', 'timestamp': 1, 'reading': 11} -> Duplicate (device_id, timestamp) pair already seen: ('Device-A', 1).
  • Rejected Messages (1):
      {'device_id': 'Device-A', 'timestamp': 3, 'reading': 'not-a-number'} -> Field 'reading' must be a finite number (int or float), got str.

PIPELINE INVARIANT VERIFICATION:
--------------------------------------------------------------------------------
✓ Pipeline Invariant Check PASSED: All invariants successfully verified.

DEMONSTRATION: Intentional Corruption Detection
--------------------------------------------------------------------------------
✓ Confirmed: Corrupted result was successfully caught by invariant checker:
  -> Invariant violation: Final accepted messages do not agree with the last trace state.
================================================================================
```

---

## Running the Unit Tests

Execute the unit test suite using Python's standard `unittest` test discovery from the repository root:

```bash
python3 -m unittest discover -s 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t024 -p "test_*.py"
```

You can also run tests with verbose descriptions:

```bash
python3 -m unittest discover -s 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t024 -p "test_*.py" -v
```

### Expected Test Output

```output
Ran 17 tests in 0.003s

OK
```

---

## Limitations and Simplifications

1. **In-Memory State:** Deduplication keys are tracked in-memory using a Python `set`. A production IoT service would use a persistent, distributed store (such as Redis or a database index) with time-to-live (TTL) expiration.
2. **Synchronous Batching:** This lab processes a finite list of messages synchronously, whereas production MQTT consumers handle infinite asynchronous event streams.
3. **No Network Protocol Overhead:** Messages are fed directly to Python functions; network connection handling, TLS handshakes, packet parsing, and MQTT QoS handshakes are abstracted away.
