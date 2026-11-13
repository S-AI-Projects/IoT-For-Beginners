# R15-T051: Sensor-Message Validation (Applied Lab)

## Lesson Connection
In *Check fruit quality from an IoT device*, an edge camera/device classifies fruit quality and publishes JSON telemetry messages. This example models the downstream ingestion boundary:
- **`device_id`**: Identifies the specific edge sensor/camera publishing telemetry.
- **`timestamp`**: Orders out-of-order sensor messages chronologically.
- **`reading`**: Numeric quality/confidence value (non-numeric strings and invalid numbers are rejected).
- **Deduplication**: Rejects duplicate `(device_id, timestamp)` pairs caused by network retries.

## Scope & Limitations (Local Simulation)
- **Simulation only**: Uses small, static in-memory JSON fixtures with Python's standard library (`json`, `math`).
- **No external services**: Does not connect to Azure IoT Hub, run a trained Custom Vision model, use a GPU, or interface with physical hardware.

## Invocation & Expected Output
Run the example:
```bash
python3 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t051/example.py
python3 -m unittest discover -s 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t051 -p "test_*.py"
