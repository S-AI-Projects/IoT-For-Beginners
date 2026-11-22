# R15-T010: Sensor-Message Validation — Scenario Assessment

An applied laboratory extension for the [Keep your plant secure](../../README.md) lesson.

## Educational Context & Scope

IoT telemetry security extends beyond cryptographic identity (such as X.509 certificates and TLS transport encryption). Ingestion microservices must also validate application-level payloads against replay attacks, data injection, and out-of-order state corruption.

This lab implements schema validation and stream deduplication, providing three applied assessment questions with rationales and executable automated checks.

**Scope:** Python 3 standard library simulation. No physical soil sensors, microcontrollers, or Azure IoT Hub accounts required.

## Run

```bash
python3 2-farm/lessons/6-keep-your-plant-secure/applied-labs/r15-t010/example.py
python3 -m unittest discover -s 2-farm/lessons/6-keep-your-plant-secure/applied-labs/r15-t010 -p "test_*.py"
```

## Applied Assessment Questions & Rationales

### 1. Predict an Output
- **Question:** When message `A@t=2` arrives before `A@t=1`, what is the timestamp sequence in the accepted output?
- **Answer:** `[1, 2]`.
- **Rationale:** The gateway sorts validated records chronologically to maintain causality in time-series processing regardless of transient network delays.

### 2. Diagnose a Failure
- **Question:** Why does message `{"device_id": "A", "timestamp": 3, "reading": "invalid"}` fail ingestion?
- **Answer:** The `reading` property is a string instead of a numeric float/integer.
- **Rationale:** Strict data type validation prevents type-confusion vulnerabilities, unexpected downstream arithmetic failures, and script injection.

### 3. Choose a Boundary Policy
- **Question:** When a duplicate message `(device_id, timestamp)` arrives containing a conflicting sensor value, which boundary deduplication policy should be chosen?
- **Answer:** First-seen retention (`reject_duplicate`).
- **Rationale:** Allowing subsequent duplicate packets to overwrite accepted state opens the ingestion pipeline to replay attacks and race conditions where an adversary alters recorded sensor history.

## Where the Simplification Stops

Production IoT deployments also incorporate HMAC message authentication, nonce verification, sequence number counters, and dead-letter queue routing for security analysis.
