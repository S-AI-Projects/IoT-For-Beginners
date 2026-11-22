# R15-T009: Sensor-Message Validation — Evaluation Experiment

An applied laboratory extension for the [Check stock from an IoT device](../../README.md) lesson.

## Educational Context & Scope

Retail stock monitoring relies on distributed weight sensors and object-detection cameras to detect stock levels on shelves. In busy retail settings, message batches arriving at backend gateways vary in size, contain network duplicates from retry loops, and occasionally contain malformed sensor readings.

This lab implements an automated validation and deduplication pipeline and conducts a controlled evaluation experiment across three batch configurations ($N=4$, $N=20$, $N=100$).

**Scope:** Python 3 standard library simulation. No physical RFID readers, smart shelf scales, or cloud ERP systems required. Does not make claims about real-world computer vision model accuracy.

## Run

```bash
python3 5-retail/lessons/2-check-stock-device/applied-labs/r15-t009/example.py
python3 -m unittest discover -s 5-retail/lessons/2-check-stock-device/applied-labs/r15-t009 -p "test_*.py"
```

## Controlled Experiment Configurations & Metrics

| Configuration | Total Messages ($N$) | Accepted Count | Duplicate Count | Rejected Count | Correctness Invariant ($N = A + D + R$) |
|---|---|---|---|---|---|
| **Small Batch** | 4 | 2 | 1 (dup `A/1`) | 1 (string reading) | **Verified** ($4 = 2+1+1$) |
| **Medium Batch** | 20 | 14 | 4 (20% duplicate rate) | 2 (10% malformed) | **Verified** ($20 = 14+4+2$) |
| **Large Batch** | 100 | 70 | 20 (20% duplicate rate) | 10 (10% malformed) | **Verified** ($100 = 70+20+10$) |

### Observations & Trade-offs

- **Correctness:** In all configurations, duplicate `(device_id, timestamp)` pairs are isolated without polluting stock counts, and string/malformed readings are rejected before downstream processing.
- **Sorting Overhead:** In-memory $O(N \log N)$ sorting is efficient for small batches ($N \le 100$), but large-scale retail streams require priority queues or sliding time-window partitioning.

## Where the Simplification Stops

Real retail telemetry systems implement database transactions, inventory SKU reconciliation, and multi-tenant isolation rather than in-memory dictionary tracking.
