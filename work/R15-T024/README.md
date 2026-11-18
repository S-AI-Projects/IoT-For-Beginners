# Task R15-T024 Evidence: Sensor-Message Validation — Invariant and State Trace

This directory contains execution and verification evidence for Task R15-T024 on branch `R15-T024`.

## Task Overview

Task R15-T024 implements an intermediate state tracer and pipeline invariant verifier for IoT telemetry message processing in Lesson 1-4 (`1-getting-started/lessons/4-connect-internet/`).

The implementation addresses key challenges in internet-connected IoT systems:
- Network retries causing duplicate messages with the same `(device_id, timestamp)` pair.
- Messages arriving out of chronological order over MQTT.
- Telemetry from different devices sharing identical timestamps, requiring deterministic tie-breaking `(timestamp, device_id, reading)`.
- Malformed payloads and non-numeric readings (such as strings or non-finite values).
- The requirement that invalid messages do not reserve identity in the deduplication cache.
- Maintaining a step-by-step intermediate state trace and enforcing verifiable pipeline invariants connecting intermediate state snapshots to final classified output.
- Independent state reconstruction during invariant verification to validate full content matches for every trace snapshot, detecting message replacements even when list lengths remain unchanged.

## Evidence Files Summary

* **`environment.txt`**: Records the exact system environment, execution timestamp, Python version (3.14.3), Git version (2.56.0), platform details (macOS Darwin 27.0.0 arm64), and standard library dependency information.
* **`sample_results.txt`**: Captures genuine command output from running `example.py`, including the step-by-step state trace, final categorized summary, invariant validation, and deliberate corruption detection.
* **`test_run.txt`**: Captures full verbose test execution output from the standard `unittest` test discovery runner (17 tests passing, 0 failures).
* **`comparison.txt`**: Details the four required fixture inputs, expected vs. actual outcomes, step-by-step intermediate state trace, invariant check results, multi-device tie-breaking notes, independent state reconstruction behavior, and seven captured outputs demonstrating that deliberate corruptions (ordering, tie-breaking, desynchronization, step numbers, snapshot counts, outcome statuses, and message replacements without length changes) cause `AssertionError` with nonzero process exit codes.
