# Task R15-T025 Evidence: Sensor-Message Validation — Offline Service Adapter

This directory contains execution and verification evidence for Task R15-T025 on branch `R15-T025`.

## Task Overview

Task R15-T025 implements a sensor-message validation pipeline with a decoupled callable service adapter for Lesson 1-2 (`1-getting-started/lessons/2-deeper-dive/`).

The implementation addresses key requirements of IoT edge and offline systems:
- Local edge validation of incoming JSON telemetry without external network dependencies.
- Deduplication using `(device_id, timestamp)` identity, ensuring rejected messages never reserve identity.
- Deterministic chronological sorting by `(timestamp, device_id, reading)` prior to downstream dispatch.
- A decoupled, pluggable callable service adapter interface (`service_adapter`), demonstrated via an in-memory test adapter (`InMemoryServiceAdapter`).
- Explicit delivery tracking: confirmed deliveries (`delivered`) vs failed deliveries (`failed_deliveries`), ensuring failed submissions are never silently marked as delivered.
- Adapter response validation: validates adapter return values before accessing fields, requiring a `ServiceAcknowledgement` instance with status `DELIVERED` or `FAILED`, and routing invalid returns (`None`, strings, unsupported statuses) safely to `failed_deliveries` with descriptive details.
- Contract verification (`verify_pipeline_contract`) validating end-to-end delivery guarantees and detecting deliberate tampering.

## Evidence Files Summary

* **`environment.txt`**: Records the exact system environment, execution timestamp, Python version (3.14.3), Git version (2.56.0), platform details (macOS Darwin 27.0.0 arm64), and standard library dependency information.
* **`sample_results.txt`**: Captures genuine command output from running `example.py`, including classification summary, adapter acknowledgements, delivery summary, contract verification, and deliberate corruption detection.
* **`test_run.txt`**: Captures full verbose test execution output from the standard `unittest` test discovery runner (22 tests passing, 0 failures, exit code 0).
* **`comparison.txt`**: Details the four required fixture inputs, expected vs. actual outcomes, adapter delivery order, contract guarantees, adapter return validation rules, and captured outputs demonstrating that deliberate corruptions (delivery tampering, order inversion, count manipulation) cause `AssertionError` with nonzero process exit codes.
