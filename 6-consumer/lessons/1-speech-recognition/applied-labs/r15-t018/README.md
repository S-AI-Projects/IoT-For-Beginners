# Applied Lab: Sensor-Message Validation — Failure and Recovery Example (R15-T018)

This lab extends the [Recognize Speech with an IoT Device lesson](../../README.md) by demonstrating robust ingestion failure handling, descriptive error reporting, and state recovery for streaming audio telemetry.

## Concept & Curriculum Connection

In smart consumer devices equipped with microphones, continuous audio streaming and sensor telemetry may suffer packet drops, partial serialization, or type corruption over wireless links. Instead of crashing or dropping subsequent valid inputs, an IoT gateway must isolate corrupt packets, emit diagnostics, and maintain continuity for subsequent frames.

## Contract & Recovery Flow
1. **Validation Checks:**
   - Strict typing: `device_id` (str), `timestamp` (numeric: int or float), and `reading` (numeric: int or float).
   - Rejection: String readings (`"bad_reading"`), missing fields (`device_id`, `timestamp`, or `reading`), and duplicate `(device_id, timestamp)` tuples.
2. **Error Diagnostic:** Failed packets trigger an explicit error classification (`MISSING_DATA`, `TYPE_ERROR`, `DUPLICATE`, `MALFORMED_PACKET`) and are logged.
3. **Resilient Recovery:** The ingestion pipeline does not enter a broken state; subsequent valid messages are accepted and sorted seamlessly.

## Fixture & Benchmark
- Input stream:
  1. `{"device_id": "A", "timestamp": 2, "reading": 20.0}` -> Accepted
  2. `{"device_id": "A", "timestamp": 1, "reading": 18.0}` -> Accepted
  3. `{"device_id": "A", "timestamp": 1, "reading": 18.5}` -> Reported as duplicate and discarded
  4. `{"device_id": "B", "timestamp": 3, "reading": "bad_str"}` -> Rejected: string reading
- Output: Accepted records for device `A` are sorted in order `1, 2`.

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example
```bash
python3 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t018/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t018 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Simulation:** Telemetry and audio energy level frames are handled in-memory without requiring live microphone audio drivers or cloud speech-to-text APIs.
- **Hardware Boundary:** No physical microphone, smart speaker, or development kit required.
