# Applied Lab: Sensor-Message Validation — Worked Example with Checks (R15-T017)

This lab extends the [A Deeper Dive into IoT lesson](../../README.md) with a fully worked input-to-output validation walkthrough and regression test framework for streaming sensor data.

## Concept & Curriculum Connection

IoT telemetry data transmitted by microcontrollers (such as Raspberry Pi or Wio Terminal) is susceptible to transmission duplicates and network reordering. Before downstream aggregation or storage, edge processors must validate message integrity, drop duplicate packets, and order readings chronologically.

## Worked Input-to-Output Walkthrough

### Input Telemetry Batch
```json
[
  {"device_id": "A", "timestamp": 2, "reading": 25.1},
  {"device_id": "A", "timestamp": 1, "reading": 24.8},
  {"device_id": "A", "timestamp": 1, "reading": 24.9},
  {"device_id": "B", "timestamp": 3, "reading": "bad_reading"}
]
```

### Processing Steps & Explanations
1. **Message 0 `{"device_id": "A", "timestamp": 2, "reading": 25.1}`:**
   - Valid schema and numeric reading. Key `("A", 2.0)` added to seen set. Queued.
2. **Message 1 `{"device_id": "A", "timestamp": 1, "reading": 24.8}`:**
   - Valid schema and numeric reading. Key `("A", 1.0)` added to seen set. Queued.
3. **Message 2 `{"device_id": "A", "timestamp": 1, "reading": 24.9}`:**
   - Key `("A", 1.0)` is already present in seen set. Marked as **DUPLICATE** and discarded.
4. **Message 3 `{"device_id": "B", "timestamp": 3, "reading": "bad_reading"}`:**
   - Field `reading` is a string (`"bad_reading"`). Rejection triggered: `reading must be numeric`.

### Final Sorted Accepted Output
Messages for device `A` are sorted chronologically by timestamp ($1 \le 2$):
```json
[
  {"device_id": "A", "timestamp": 1, "reading": 24.8},
  {"device_id": "A", "timestamp": 2, "reading": 25.1}
]
```

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example Walkthrough
```bash
python3 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t017/example.py
```

### Run Regression Test Suite
```bash
python3 -m unittest discover -s 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t017 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Validation:** Pure Python validation logic without real-time socket connections or cloud event hubs.
- **Hardware Boundary:** No physical sensor hardware or network interface card (NIC) configuration required.
