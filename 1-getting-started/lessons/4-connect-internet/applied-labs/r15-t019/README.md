# Applied Lab: Sensor-Message Validation — Evaluation Experiment (R15-T019)

This lab extends the [Connect Your Device to the Internet lesson](../../README.md) by evaluating telemetry ingestion contracts across three controlled batch configurations.

## Concept & Curriculum Connection

Internet-connected IoT devices often queue sensor readings into batches before transmitting over constrained cellular or Wi-Fi networks. This evaluation experiment analyzes the behavior, correctness, and trade-offs of validating, deduplicating, and ordering incoming message batches across different payload volumes.

## Controlled Configurations & Metrics
Three controlled configurations are evaluated:
1. **Small (N=4):** Minimal benchmark fixture testing ordering, deduplication, and schema validation.
2. **Medium (N=16):** Moderate batch testing mixed valid, duplicate, and invalid ratios.
3. **Large (N=64):** Larger batch evaluating sorting overhead and hash set deduplication scaling.

### Evaluation Metrics
- **Acceptance Rate:** Fraction of input messages satisfying typing and uniqueness rules ($\text{accepted} / \text{total}$).
- **Duplicate Rate:** Fraction of messages flagged as duplicate device/timestamp transmissions ($\text{duplicates} / \text{total}$).
- **Ordering Invariant:** Verifies that all accepted messages are strictly sorted in ascending chronological order ($t_i \le t_{i+1}$).

> **Observed Trade-offs:** Larger batches amortize HTTP/TLS network connection establishment overhead at the expense of higher gateway memory buffer usage and $O(N \log N)$ sorting latency. This analysis models software batching trade-offs without making claims regarding physical radio signal strength or machine learning model accuracy.

## Benchmark Fixture
- Input: Messages for device `A` at timestamp 2, timestamp 1, duplicate `A/1`, and string reading on device `B`.
- Output: Accepted messages for device `A` ordered `1, 2`; duplicate `A/1` reported; string reading rejected.

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Experiment
```bash
python3 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t019/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t019 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Evaluation:** Simulates message buffering and sorting in memory without opening live internet sockets or cloud IoT Hub endpoints.
- **Hardware Boundary:** No physical Wi-Fi or cellular shield required.
