# Task R15-T029: Sensor-Message Validation: Evaluation Experiment — Evidence Summary

## 1. Task Summary
Coursework task **R15-T029** implements a robust, local Python standard-library-only message validation, deduplication, stable sorting, and evaluation benchmark pipeline in the `IoT-For-Beginners` repository, scoped to `4-manufacturing/lessons/2-check-fruit-from-device`.

Key deliverables:
- **Core Message Contract**:
  - Validates JSON parsing and field presence (`device_id`, `timestamp`, `reading`).
  - Strict type enforcement: rejects booleans as numbers, string timestamps, string readings, empty/whitespace `device_id`, and non-finite values (`NaN`, `inf`, `-inf`).
  - Deduplication: identity key `(device_id, timestamp)`. First seen valid message accepted; subsequent valid messages reported as duplicates.
  - Invalid messages never reserve an identity.
  - Same timestamp across different devices is supported.
  - Stable ascending chronological sorting by timestamp.
- **Mandatory 4-Message Fixture**:
  - Input 1: Device A, ts 2, reading 42 -> Accepted
  - Input 2: Device A, ts 1, reading 40 -> Accepted
  - Input 3: Device A, ts 1, reading 41 -> Duplicate of Input 2
  - Input 4: Device B, ts 3, reading "bad" -> Rejected (invalid reading)
  - Outcome: 2 accepted, 1 duplicate, 1 rejected. Sorted: timestamp 1.0 (reading 40.0), then timestamp 2.0 (reading 42.0).
- **Evaluation Experiment**:
  - Synthetic datasets scaled to 10, 100, and 1,000 messages with deterministic 70% accepted, 20% duplicate, 10% rejected proportions.
  - High-precision execution timing using `time.perf_counter()` over 5 iterations per size, reporting median latency and throughput (msg/s).
- **CLI Scenarios**:
  - `--scenario normal`: Runs mandatory fixture and evaluation benchmarks (exits 0).
  - `--scenario boundary`: Verifies empty stream, timestamp ties, malformed JSON, and type errors (exits 0).
  - `--scenario failure`: Demonstrates deliberate assertion failure with clear notification (exits 1).
- **Testing & Documentation**:
  - 18 unit tests verifying contract edge cases and fresh-process subprocess executions.
  - Comprehensive applied lab README and linked section in lesson README.

---

## 2. Files Created and Modified

### Created Implementation & Lab Files:
- `4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t029/example.py`
- `4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t029/test_example.py`
- `4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t029/README.md`

### Modified Lesson File:
- `4-manufacturing/lessons/2-check-fruit-from-device/README.md`

### Created Evidence Files:
- `work/R15-T029/README.md` (this file)
- `work/R15-T029/environment.txt`
- `work/R15-T029/sample_results.txt`
- `work/R15-T029/comparison.txt`
- `work/R15-T029/test_run.txt`

---

## 3. Evidence Index

- `environment.txt`: Execution platform, branch, runtime versions, and standard-library-only constraints.
- `sample_results.txt`: Captured console outputs from running `--scenario normal` and `--scenario boundary`.
- `comparison.txt`: Verification of mandatory fixture and detailed breakdown of the 3-size evaluation experiment (correctness counts, median latencies, throughput).
- `test_run.txt`: Complete verbose test log from `python3 -m unittest discover ...` demonstrating 18 passed tests and exit code 0.
