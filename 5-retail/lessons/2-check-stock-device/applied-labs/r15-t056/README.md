# Worked Example: Sensor Message Validation (`R15-T056`)

## Overview
This local simulated example extends the **Check stock from an IoT device** lesson by validating incoming JSON sensor payloads before downstream stock counting.

## Scope & Limitations
* **Local Simulation Only:** Uses in-memory JSON string fixtures rather than live MQTT/IoT Hub streams or physical cameras/sensors.
* **Contract Enforced:** Requires `device_id` (non-empty string), `timestamp` (int/float), and `reading` (int/float). Rejects malformed JSON, non-numeric readings, and duplicate `(device_id, timestamp)` pairs, then sorts accepted records by `timestamp`.

## Running the Example & Tests
Run the standalone worked example:
    python3 5-retail/lessons/2-check-stock-device/applied-labs/r15-t056/example.py

Run the automated regression tests:
    python3 -m unittest discover -s 5-retail/lessons/2-check-stock-device/applied-labs/r15-t056 -p "test_*.py"

## Worked Input-to-Output Trace
1. `{"device_id": "A", "timestamp": 2, "reading": 15}` -> **Accepted** (first occurrence of `A/2`).
2. `{"device_id": "A", "timestamp": 1, "reading": 12}` -> **Accepted** (first occurrence of `A/1`).
3. `{"device_id": "A", "timestamp": 1, "reading": 99}` -> **Rejected** (`Duplicate device/timestamp pair: A/1`).
4. `{"device_id": "A", "timestamp": 3, "reading": "invalid_str"}` -> **Rejected** (`Reading must be numeric`).

**Final Ordered Output:** `[A/1 (reading: 12), A/2 (reading: 15)]`.
