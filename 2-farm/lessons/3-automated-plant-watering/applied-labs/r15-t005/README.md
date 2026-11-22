# R15-T005: Moisture-Control Hysteresis — Offline Service Adapter

An applied laboratory extension for the [Automated plant watering](../../README.md) lesson.

## Educational Context & Scope

In automated plant watering, application logic controls an external actuator (such as a relay or digital water valve) in response to sensor telemetry. Rather than coupling control logic directly to hardware GPIO pins or network MQTT brokers, software engineering best practices place the actuator behind a callable interface.

This lab provides an `OfflineRelayAdapter` implementing the `RelayActuatorService` interface, allowing full unit testing of dual-threshold hysteresis without requiring physical hardware.

**Scope:** Python 3 standard library simulation. No physical relays, GPIO pins, pumps, or MQTT brokers required.

## Run

```bash
python3 2-farm/lessons/3-automated-plant-watering/applied-labs/r15-t005/example.py
python3 -m unittest discover -s 2-farm/lessons/3-automated-plant-watering/applied-labs/r15-t005 -p "test_*.py"
```

## Thresholds & Sequence Behavior

- **Lower threshold (< 300):** Soil dry; actuator commanded `on`.
- **Upper threshold (> 600):** Soil wet; actuator commanded `off`.
- **Deadband [300, 600]:** Retains prior state.
- **Sequence `[700, 250, 400, 650]` starting from `off`:** Produces `['off', 'on', 'on', 'off']`.

## What This Mock Does NOT Establish

While this in-memory mock verifies logical state transitions and threshold handling, it explicitly does **not** establish real-world hardware and operational characteristics:
1. **Mechanical Relay Dynamics:** Contact bounce, coil energization delay, or contact pitting over repeated switching cycles.
2. **Network Failures:** MQTT transport disconnects, TCP keep-alive timeouts, or cloud IoT hub throttling.
3. **Hydraulic Constraints:** Water reservoir exhaustion, pipe air locks, pump cavitation, or flow-rate limitations.
4. **Soil Moisture Dynamics:** Latency between water delivery at the surface and infiltration reaching the sensor probe.
