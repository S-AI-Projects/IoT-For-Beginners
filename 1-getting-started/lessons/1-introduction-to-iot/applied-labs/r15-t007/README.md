# R15-T007: Sensor-Message Validation — Worked Example with Regression Checks

An applied laboratory extension for the [Introduction to IoT](../../README.md) lesson.

## Educational Context & Scope

IoT gateways receive streaming observations asynchronously. Because network paths can cause out-of-order delivery, dropped acks, and packet duplication, ingestion pipelines must validate message schemas, filter out retransmissions, and establish chronological order.

This lab publishes an explicit input-to-output walkthrough of a sensor telemetry stream and executes the exact scenario as an automated regression test.

**Scope:** Python 3 standard library simulation. No physical sensors, microcontrollers, or cloud event hubs required.

## Run

```bash
python3 1-getting-started/lessons/1-introduction-to-iot/applied-labs/r15-t007/example.py
python3 -m unittest discover -s 1-getting-started/lessons/1-introduction-to-iot/applied-labs/r15-t007 -p "test_*.py"
```

## Worked Example: Step-by-Step Walkthrough

### Input Stream

```json
[
  {"device_id": "A", "timestamp": 2, "reading": 23.5},
  {"device_id": "A", "timestamp": 1, "reading": 22.0},
  {"device_id": "A", "timestamp": 1, "reading": 22.1},
  {"device_id": "A", "timestamp": 3, "reading": "invalid_string"}
]
```

### Processing Steps

1. **Record 1 (`A`, $t=2$, $23.5$):** Valid schema; first time seeing key `(A, 2)`. Added to accepted queue.
2. **Record 2 (`A`, $t=1$, $22.0$):** Valid schema; first time seeing key `(A, 1)`. Added to accepted queue.
3. **Record 3 (`A`, $t=1$, $22.1$):** Valid schema, but key `(A, 1)` is already present in seen keys set. Discarded and recorded in `duplicates`.
4. **Record 4 (`A`, $t=3$, `"invalid_string"`):** Schema validation fails: `reading` must be numeric (strings and booleans rejected). Discarded and recorded in `rejected`.
5. **Reordering:** Accepted queue `[{"device_id": "A", "timestamp": 2, ...}, {"device_id": "A", "timestamp": 1, ...}]` is sorted by timestamp ascending.

### Output Result

- **Accepted (Ordered):**
  1. `{"device_id": "A", "timestamp": 1, "reading": 22.0}`
  2. `{"device_id": "A", "timestamp": 2, "reading": 23.5}`
- **Duplicates Reported:** `[{"device_id": "A", "timestamp": 1}]`
- **Rejected:** `[{"record": {"device_id": "A", "timestamp": 3, "reading": "invalid_string"}, "reason": "...reading..."}]`

## Where the Simplification Stops

Real IoT stream processing systems (e.g. Apache Flink, Azure Stream Analytics) handle out-of-order data using event-time watermarking, windowed deduplication, and late-arrival thresholds instead of unbounded in-memory collection.
