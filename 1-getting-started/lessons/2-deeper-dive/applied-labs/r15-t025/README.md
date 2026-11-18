# Applied Lab R15-T025: Sensor-Message Validation — Offline Service Adapter

This applied lab demonstrates how an IoT application running on an edge device validates incoming telemetry payloads, filters duplicate transmissions, sorts accepted records chronologically, and decouples downstream transmission using an injectable callable service adapter.

> ⚠️ **Educational Simulation Disclaimer**
>
> This lab is a **local Python simulation** using in-memory data structures and the standard library. It does **not** connect to a physical sensor, a live MQTT broker, a cloud IoT hub (such as Azure IoT Hub or AWS IoT Core), or an external network API. It models the algorithmic and architectural principles of offline edge processing and callable service adapters.

---

## Lesson Context: Edge Processing & Decoupled Services

In [Lesson 2: A deeper dive into IoT](../../README.md), IoT applications are structured around:
- **The Thing:** Microcontrollers and single-board computers reading physical signals from sensors.
- **The Internet:** Cloud services that aggregate telemetry, store historical measurements, and issue actuator commands.
- **IoT on the Edge:** Gateway or local devices that process data locally on the edge network without depending on a continuous internet connection.

In real-world deployments, edge systems face intermittent network availability, bandwidth limitations, and air-gapped environments. Rather than hard-coding network calls directly into the telemetry ingestion pipeline, robust edge software decouples ingestion from delivery using an **injected callable service adapter**.

This separation ensures:
1. **Local Autonomy:** Telemetry is validated, deduplicated, and organized chronologically even when offline.
2. **Pluggable Transports:** The processing pipeline remains agnostic to the underlying communication medium (MQTT, HTTP, local SQLite queue, or mock test harness).
3. **Delivery Integrity:** Delivery failures reported by the adapter are caught and classified explicitly; failed service submissions are never silently marked as delivered.

---

## Message Schema and Contract

Each sensor telemetry message is expected to be a JSON object (or dictionary) containing three required fields:

```json
{
  "device_id": "Device-A",
  "timestamp": 1600000000,
  "reading": 25.5
}
```

### Validation & Processing Rules

1. **`device_id` Validation:** Must be a non-empty string. Non-string types raise `TypeError`; empty strings or whitespace-only strings raise `ValueError`.
2. **`timestamp` Validation:** Must be a finite numeric value (`int` or `float`). Booleans (subclasses of `int` in Python) are rejected with `TypeError`. Non-finite values (`NaN`, `Inf`, `-Inf`) raise `ValueError`.
3. **`reading` Validation:** Must be a finite numeric value (`int` or `float`). Booleans are rejected with `TypeError`. Non-finite values raise `ValueError`.
4. **Valid Zero Values:** Zero (`0` or `0.0`) is accepted as a valid physical measurement or timestamp.
5. **JSON Object Enforcement:** Malformed JSON strings or non-object JSON values (lists, numbers, strings, booleans) are rejected.
6. **No Identity Reservation on Rejection:** If a message is rejected due to invalid fields or syntax, its `(device_id, timestamp)` is **not** registered in the deduplication cache, allowing any subsequent valid message with that timestamp to be accepted.
7. **Deduplication:** Valid messages are checked against previously seen `(device_id, timestamp)` pairs. The first valid occurrence is accepted; subsequent messages are classified as `DUPLICATE`.
8. **Deterministic Chronological Sorting:** Accepted messages are sorted in ascending order using the tuple `(timestamp, device_id, reading)`. Primary sorting is chronological by `timestamp`, with `device_id` and `reading` serving as deterministic tie-breakers when multiple devices report during the same epoch.

---

## Callable Service Interface & Adapter

### Callable Interface Design

The pipeline entry point `process_message_stream(inputs, service_adapter=None)` accepts an optional callable argument:

```python
def process_message_stream(
    inputs: List[Any],
    service_adapter: Optional[Callable[[Dict[str, Any]], ServiceAcknowledgement]] = None,
) -> ProcessingResult:
```

The processing pipeline:
1. Validates and categorizes raw input into `accepted`, `duplicates`, and `rejected`.
2. Sorts `accepted` messages chronologically.
3. Passes each accepted message to `service_adapter(deepcopy(msg))` in sorted order.
4. Validates the adapter return value before accessing fields: requires a `ServiceAcknowledgement` instance with `status` exactly `"DELIVERED"` or `"FAILED"`. If the adapter returns `None`, a non-acknowledgement type (e.g. string), an unsupported status, or raises an exception, the pipeline constructs a descriptive `FAILED` acknowledgement.
5. Classifies delivery into `delivered` (where `ack.status == "DELIVERED"`) and `failed_deliveries` (where `ack.status != "DELIVERED"`). Failed service submissions are never silently reported as delivered.

### In-Memory Service Adapter

The default `InMemoryServiceAdapter` implements the callable protocol (`__call__`):
- Records every submitted message in an in-memory audit list `submitted_messages`.
- Returns a deterministic `ServiceAcknowledgement` containing `message_id`, `device_id`, `timestamp`, `status`, and `details`.
- Can simulate network/service failures using `should_fail=True`, `fail_on_device="Device-X"`, or `fail_on_timestamp=T`.
- Contains no network, socket, or thread overhead.

### What the Adapter Demonstrates vs. What It Does Not Prove

| Demonstrates | Does NOT Prove |
| :--- | :--- |
| Decoupled callable interface design | Real network connectivity or socket transmission |
| Chronological submission order to downstream sinks | Remote cloud service availability or SLA |
| In-memory delivery auditability and message isolation | Persistent cloud storage or database ACID guarantees |
| Failure handling without falsely reporting delivery | Authentication, TLS security, or authorization |
| Safe error trapping when service callable crashes | Physical sensor hardware or network interface behavior |

---

## Prerequisites

* **Python 3.x**
* **Python Standard Library only** (no external packages, cloud services, or MQTT libraries required).

---

## Running the Example

Run the script from the repository root:

```bash
python3 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t025/example.py
```

### Required Fixture Inputs

The fixture executes the following four inputs in sequence:
1. `{"device_id": "Device-A", "timestamp": 2, "reading": 20}` (Valid Device A, timestamp 2)
2. `{"device_id": "Device-A", "timestamp": 1, "reading": 10}` (Valid Device A, timestamp 1)
3. `{"device_id": "Device-A", "timestamp": 1, "reading": 10}` (Duplicate Device A, timestamp 1)
4. `{"device_id": "Device-A", "timestamp": 3, "reading": "hot"}` (Invalid string reading)

### Expected Output

```output
================================================================================
Task R15-T025: Sensor-Message Validation — Offline Service Adapter
Context: Lesson 1-2 Edge Ingestion & Offline Service Simulation
================================================================================

INPUT TELEMETRY STREAM:
--------------------------------------------------------------------------------
  Input 1: {'device_id': 'Device-A', 'timestamp': 2, 'reading': 20}
  Input 2: {'device_id': 'Device-A', 'timestamp': 1, 'reading': 10}
  Input 3: {'device_id': 'Device-A', 'timestamp': 1, 'reading': 10}
  Input 4: {'device_id': 'Device-A', 'timestamp': 3, 'reading': 'hot'}

PROCESSING OUTCOMES & CLASSIFICATION:
--------------------------------------------------------------------------------
  • Accepted Messages (2):
      Device: Device-A   Timestamp: 1      Reading: 10
      Device: Device-A   Timestamp: 2      Reading: 20
  • Duplicate Messages (1):
      {'device_id': 'Device-A', 'timestamp': 1, 'reading': 10} -> Duplicate (device_id, timestamp) pair already seen: ('Device-A', 1).
  • Rejected Messages (1):
      {'device_id': 'Device-A', 'timestamp': 3, 'reading': 'hot'} -> Field 'reading' must be a finite number (int or float), got str.

LOCAL SERVICE ADAPTER ACKNOWLEDGEMENTS:
--------------------------------------------------------------------------------
  [DELIVERED] ID: ack-Device-A-1 | Device: Device-A | Ts: 1
         Details: Message accepted and acknowledged by in-memory mock service.
  [DELIVERED] ID: ack-Device-A-2 | Device: Device-A | Ts: 2
         Details: Message accepted and acknowledged by in-memory mock service.

SERVICE DELIVERY SUMMARY:
--------------------------------------------------------------------------------
  • Confirmed Delivered: 2 message(s)
      Device: Device-A, Ts: 1, Reading: 10
      Device: Device-A, Ts: 2, Reading: 20
  • Failed Deliveries:   0 message(s)

PIPELINE CONTRACT VERIFICATION:
--------------------------------------------------------------------------------
✓ Pipeline Contract Check PASSED: All delivery and sorting guarantees verified.

DEMONSTRATION: Intentional Failure & Delivery Guard
--------------------------------------------------------------------------------
  Simulated Service Outage:
    Accepted for delivery: 2
    Confirmed Delivered:   0 (Must be 0)
    Failed Deliveries:     2 (Must match accepted count)
  ✓ Confirmed: Pipeline never marks failed service submissions as delivered.

DEMONSTRATION: Contract Tampering Detection
--------------------------------------------------------------------------------
  ✓ Confirmed: Corrupted result was successfully caught by contract verifier:
    -> Contract violation: Accepted messages violate sorting rule: (2, 'Device-A', 20) > (1, 'Device-A', 10).

EDUCATIONAL DISCLAIMER:
--------------------------------------------------------------------------------
This simulation demonstrates local edge validation and a callable adapter interface.
It does NOT connect to real cloud services, physical networks, external APIs, or hardware.
================================================================================
```

---

## Running the Unit Tests

Execute the unit test suite using Python's standard `unittest` test discovery from the repository root:

```bash
python3 -m unittest discover -s 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t025 -p "test_*.py"
```

You can also run tests with verbose descriptions:

```bash
python3 -m unittest discover -s 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t025 -p "test_*.py" -v
```

### Expected Test Output

```output
Ran 22 tests in 0.002s

OK
```
