# Sensor-Message Validation: Scenario Assessment (`R15-T059`)

## Overview
This local scenario assessment extends the **Connect your device to the Internet** lesson by validating JSON sensor telemetry (`device_id`, `timestamp`, numeric `reading`), ordering accepted payloads chronologically by `timestamp`, and rejecting duplicate `(device_id, timestamp)` pairs.

## Scope & Limitations
* **Local Simulation Only:** Evaluates deterministic in-memory JSON fixtures using Python 3 standard library modules rather than physical microcontrollers, MQTT brokers, or live cloud IoT hubs.
* **No Real-World Hardware or Model Claims:** Verifies deterministic message schema, idempotency, and event-time ordering rules without making claims about physical sensor accuracy or network latency.

## Applied Scenario Assessment Questions
1. **Predict an Output (`Q1-PREDICT-OUTPUT`):**
   * *Question:* Given messages for device `A` arriving out-of-order at timestamps `2` then `1`, what timestamp order is returned?
   * *Answer:* `[1, 2]`
   * *Rationale:* Accepted messages are sorted by `timestamp` so downstream consumers process telemetry in chronological event order rather than network arrival order.
2. **Diagnose a Failure (`Q2-DIAGNOSE-FAILURE`):**
   * *Question:* Why is `{device_id: "A", timestamp: 1, reading: "42.0"}` rejected while a subsequent numeric message for `A/1` succeeds?
   * *Answer:* String reading rejected before deduplication key registration.
   * *Rationale:* Schema type validation executes before adding `(device_id, timestamp)` to `seen_pairs`, preventing malformed payloads from poisoning deduplication state for valid retries.
3. **Choose a Boundary Policy (`Q3-BOUNDARY-POLICY`):**
   * *Question:* When two valid messages share the exact same `(device_id, timestamp)` key (`A/1`), which boundary policy is enforced?
   * *Answer:* First-seen wins; subsequent duplicate `(device_id, timestamp)` pairs are rejected.
   * *Rationale:* Idempotent first-seen retention prevents duplicate telemetry deliveries from double-counting readings while explicitly logging duplicates in `rejected`.

## Running the Example & Tests
Run the standalone scenario assessment:
    python3 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t059/example.py

Run the automated regression tests:
    python3 -m unittest discover -s 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t059 -p "test_*.py"
