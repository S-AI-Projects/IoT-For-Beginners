# Applied Lab: Sensor-Message Validation — Evaluation Experiment

Coursework Task: **R15-T029**
Context Lesson: `4-manufacturing/lessons/2-check-fruit-from-device`

---

## 1. Learning Objective & Lesson Relationship

In smart manufacturing and fruit quality inspection, IoT devices capture fruit sensor measurements (e.g. ambient temperatures, spectrometer readings, camera quality scores) and transmit telemetry streams. Before telemetry can be analyzed or logged, ingestion servers must validate message structure, reject malformed or invalid inputs, detect duplicate transmissions, and enforce stable chronological ordering.

The objective of this lab is to:
1. Implement a local Python standard-library-only message validation and deduplication contract.
2. Ensure stable, ascending chronological sorting of accepted messages.
3. Conduct an evaluation experiment measuring processing correctness, execution latency, and throughput across synthetic datasets of 10, 100, and 1,000 messages.

---

## 2. Message Contract & Schema

Each incoming message is represented as a JSON object:

```json
{
  "device_id": "sensor_fruit_01",
  "timestamp": 1620000000.5,
  "reading": 42.0
}
```

### Validation Rules:
- **`device_id`**: Non-empty string. Empty strings `""` or whitespace-only values are rejected.
- **`timestamp`**: Finite numeric value (int or float). String numbers, booleans (`True`/`False`), `NaN`, and `inf` are rejected without silent coercion.
- **`reading`**: Finite numeric value (int or float). String numbers, booleans, `NaN`, and `inf` are rejected without silent coercion.
- **Malformed JSON**: Syntactically invalid JSON strings are caught and rejected with diagnostic messages.

### Duplicate Identity:
- A message identity is defined by the pair `(device_id, timestamp)`.
- **First Seen Wins**: The first valid message for a given identity is accepted; subsequent valid messages with the same identity are marked duplicates.
- **No False Reservations**: Invalid messages are rejected immediately and **never** reserve an identity. If a later valid message arrives with that identity, it is accepted.
- **Multi-Device Concurrency**: Different devices may use identical timestamps without conflict.

### Sorting & Stability:
- Accepted messages are sorted by `timestamp` in ascending order.
- Equal timestamps preserve original stream order (stable sort).

---

## 3. Mandatory Logical Fixture

The lab verifies the following exact 4-message sequence:

| Input # | Raw JSON Content | Validation Outcome | Reason / Status |
|:---:|:---|:---:|:---|
| **1** | `{"device_id": "A", "timestamp": 2, "reading": 42}` | **ACCEPTED** | Valid message |
| **2** | `{"device_id": "A", "timestamp": 1, "reading": 40}` | **ACCEPTED** | Valid message |
| **3** | `{"device_id": "A", "timestamp": 1, "reading": 41}` | **DUPLICATE** | Identity `('A', 1.0)` already seen in Input 2 |
| **4** | `{"device_id": "B", "timestamp": 3, "reading": "bad"}` | **REJECTED** | Reading `"bad"` is not a numeric value |

### Expected Outcome:
- Total Processed: **4**
- Accepted Count: **2**
- Duplicate Count: **1**
- Rejected Count: **1**
- **Sorted Accepted Output**:
  1. Timestamp `1.0`: Device `A`, Reading `40.0` (Original Index 1)
  2. Timestamp `2.0`: Device `A`, Reading `42.0` (Original Index 0)

---

## 4. Evaluation Experiment Method & Metrics

The evaluation experiment measures pipeline behavior across three deterministic input scales: **10**, **100**, and **1,000** messages.

### Synthetic Data Distribution (70% / 20% / 10% Ratio):
For every 10-message block:
- **70% Valid**: 7 unique messages with permuted timestamps to exercise sorting.
- **20% Duplicates**: 2 messages repeating previously accepted identities.
- **10% Rejected**: 1 corrupt message with a string reading.

### Measured Metrics:
1. **Input Message Count ($N$)**: Total messages ingested.
2. **Accepted Count**: Valid, unique messages ($0.7 \times N$).
3. **Duplicate Count**: Duplicate identities reported ($0.2 \times N$).
4. **Rejected Count**: Invalid messages filtered ($0.1 \times N$).
5. **Ordering Verification**: Confirms $T_i \le T_{i+1}$ for all accepted records.
6. **Median Execution Latency**: Measured using `time.perf_counter()` over 5 iterations per size.
7. **Throughput (messages/sec)**: $N / \text{median\_time}$.

---

## 5. How to Run CLI Scenarios

The script `example.py` supports three scenarios:

### 1. Normal Scenario (Mandatory Fixture & Evaluation Experiment)
```bash
python3 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t029/example.py --scenario normal
```

### 2. Boundary Scenario (Edge Cases & Invariants)
```bash
python3 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t029/example.py --scenario boundary
```

### 3. Failure Scenario (Intentional Assertion Failure)
```bash
python3 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t029/example.py --scenario failure
```
*(Exits with non-zero exit code `1` via an uncaught AssertionError)*

---

## 6. How to Run Unit Tests

Execute the test suite using Python `unittest`:

```bash
python3 -m unittest discover -s 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t029 -p "test_*.py" -v
```

---

## 7. Prerequisites and Scope Limitations

- **Prerequisites**: Python 3.8+ (standard library only; no pip dependencies).
- **Scope & Limitations**:
  - This is a local algorithmic simulation of message parsing, deduplication, and sorting.
  - It does **not** capture images from camera hardware, connect to MQTT brokers, call Azure Custom Vision or cloud APIs, or evaluate computer vision model accuracy.
  - Performance timings and throughput values are local synthetic measurements and do not represent production cloud service SLAs.
