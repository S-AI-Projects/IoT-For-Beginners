# R15-T003: Sensor-Message Validation — Compare Two Approaches

An applied laboratory extension for the [Introduction to IoT](../../README.md) lesson.

## Educational Context & Scope

IoT systems collect data streams from remote sensors over network protocols. Because network packets can arrive out-of-order, be duplicated during transmission, or suffer payload corruption, ingestion gateways must validate data types, discard duplicates, and chronological sort incoming observations.

This lab demonstrates sensor-message validation with schema verification, deduplication on `(device_id, timestamp)`, and chronological sorting, comparing a direct procedural pipeline with a functional reference implementation.

**Scope:** Python 3 standard library simulation. No MQTT broker, cloud event hub, or physical sensors required.

## Run

```bash
python3 1-getting-started/lessons/1-introduction-to-iot/applied-labs/r15-t003/example.py
python3 -m unittest discover -s 1-getting-started/lessons/1-introduction-to-iot/applied-labs/r15-t003 -p "test_*.py"
```

## Comparison Matrix

| Input Message | Direct Approach | Reference Approach | Outcome / Reason |
|---|---|---|---|
| `{"device_id": "A", "timestamp": 2, "reading": 23.5}` | Accepted | Accepted | Valid numeric reading |
| `{"device_id": "A", "timestamp": 1, "reading": 22.0}` | Accepted | Accepted | Valid numeric reading; sorted before t=2 |
| `{"device_id": "A", "timestamp": 1, "reading": 99.9}` | Duplicate | Duplicate | Duplicate `(A, 1)` pair detected |
| `{"device_id": "A", "timestamp": 3, "reading": "bad"}` | Rejected | Rejected | String reading rejected; must be numeric |

Both approaches produce identical sets of accepted, duplicated, and rejected messages.

## Where the Simplification Stops

In real IoT architectures:
1. Distributed clock skew requires logical clocks (Lamport timestamps or vector clocks)
2. In-memory deduplication is replaced by sliding time-window caches (e.g. Redis TTL or Bloom filters)
3. Schema validation often utilizes formal JSON Schema or binary formats (Protobuf / Avro)
