# R15-T001: Moisture-Control Hysteresis

A runnable concept example extending the [Detect soil moisture](../../README.md) lesson.
In automated irrigation, switching watering on and off at a single threshold causes rapid actuator oscillation (chattering) when readings hover around that point. This lab implements a dual-threshold hysteresis controller.

**Scope:** Simulated, Python 3 standard library only. Does not require physical hardware, sensors, microcontrollers, or cloud services.

## Run

```bash
python3 2-farm/lessons/2-detect-soil-moisture/applied-labs/r15-t001/example.py
python3 -m unittest discover -s 2-farm/lessons/2-detect-soil-moisture/applied-labs/r15-t001 -p "test_*.py"
```

## Rules & Thresholds

1. **Lower threshold (< 300):** Soil is too dry; turn watering `on`.
2. **Upper threshold (> 600):** Soil has sufficient moisture; turn watering `off`.
3. **Deadband [300, 600]:** Retains the previous watering state to avoid rapid cycling.
4. **Sensor range [0, 1023]:** Valid analog readings; values outside this range are rejected with `ValueError`.

## Test Scenarios

| Category | Input / Scenario | Expected State | Rationale |
|---|---|---|---|
| Initial | Starting state | `off` | Safe default |
| Normal | Sequence `[700, 250, 400, 650]` | `['off', 'on', 'on', 'off']` | 700 is wet (off), 250 is dry (on), 400 in deadband (retains on), 650 is wet (off) |
| Lower boundary | Reading `300` (from `off`) | `off` | Retains previous state |
| Lower boundary | Reading `300` (from `on`) | `on` | Retains previous state |
| Upper boundary | Reading `600` (from `on`) | `on` | Retains previous state |
| Upper boundary | Reading `600` (from `off`) | `off` | Retains previous state |
| Invalid reading | `-1`, `1024` | `ValueError` | Out of valid ADC sensor range [0, 1023] |
| Invalid type | `"400"`, `350.5` | `TypeError` | Non-integer sensor reading |

## Where the Simplification Stops

In a physical IoT deployment, readings are subject to analog noise, sensor drift, temperature fluctuations, and soil salinity variations. A production system may also require digital low-pass filtering, moving averages, relay dead-time enforcement, and watchdog timeouts.
