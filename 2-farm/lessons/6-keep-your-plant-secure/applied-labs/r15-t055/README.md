# R15-T055: Sensor-Message Validation — Refactor the Teaching Example

## Overview & Lesson Connection
This local simulation example illustrates payload schema integrity, identity deduplication, and deterministic timestamp ordering for IoT device telemetry in **Keep your plant secure**, demonstrating how to refactor a working baseline (`process_messages_baseline`) by extracting a single named responsibility (`validate_and_parse_message`) into `process_messages_refactored` while preserving identical behavior.

- **What it illustrates:** Decoding JSON telemetry (`device_id`, `timestamp`, numeric `reading`), rejecting malformed payloads or string readings (`ValueError`), reporting duplicate `(device_id, timestamp)` pairs, sorting accepted messages chronologically by `timestamp`, and proving before/after refactoring equivalence.
- **Where simplifications & simulation stop:**
  - Uses small in-memory JSON string fixtures with Python standard library (`0` external dependencies).
  - Does **not** perform X.509 certificate verification, TLS handshakes, Azure IoT Hub DPS provisioning, or physical sensor/microcontroller I/O.

## Boundary Decisions & Refactoring Equivalence
- **Fixture:** Messages for device `"A"` at timestamps `2`, `1`, and duplicate `1`.
- **Expected behavior:** Accepted messages for `"A"` are returned ordered `1, 2`; duplicate `("A", 1)` is reported in `duplicates`; a string reading such as `"23.0"` is rejected with `ValueError`.
- **Equivalence guarantee:** Both `process_messages_baseline` and `process_messages_refactored` satisfy the exact same contract and produce identical output on all valid and invalid inputs.

## Exact Invocation
    python3 2-farm/lessons/6-keep-your-plant-secure/applied-labs/r15-t055/example.py

## Run Unit Tests
    python3 -m unittest discover -v -s 2-farm/lessons/6-keep-your-plant-secure/applied-labs/r15-t055 -p "test_*.py"
