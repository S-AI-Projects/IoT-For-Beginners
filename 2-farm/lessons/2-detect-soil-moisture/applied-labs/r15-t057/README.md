# Evaluation Experiment: Moisture-Control Hysteresis (`R15-T057`)

## Overview
This local simulation extends the **Detect soil moisture** lesson by implementing a hysteresis band controller (`< 300` -> `on`, `> 600` -> `off`, `300..600` inclusive -> retain state) and evaluating threshold width trade-offs.

## Scope & Limitations
* **Local Simulation Only:** Uses deterministic integer lists (`0..1023`) rather than physical capacitive soil moisture sensors, relays, or Wio Terminal hardware.
* **No Real-World Model Claims:** Metrics measure rule-based actuator state transitions (chatter) and active watering ticks on synthetic sequences; no claims are made regarding real soil absorption rates or crop yield.

## Controlled Configuration Comparison
Evaluated on noisy sequence `[650, 280, 450, 550, 290, 520, 620, 350]` (initial state: `off`):

| Configuration | Band (`low`, `high`) | Transitions (Chatter) | Watering (`on`) Ticks | Observed Trade-off |
| :--- | :--- | :---: | :---: | :--- |
| **Narrow Band** | `(400, 500)` | 5 | 4 | High responsiveness, but rapid relay switching on minor sensor noise. |
| **Contract Band** | `(300, 600)` | 2 | 5 | Balanced deadband prevents chatter while maintaining target moisture bounds. |
| **Wide Band** | `(200, 700)` | 0 | 0 | Eliminates switching wear, but fails to trigger watering during moderate dryness (`280–290`). |

## Running the Experiment & Tests
Run the standalone experiment:
    python3 2-farm/lessons/2-detect-soil-moisture/applied-labs/r15-t057/example.py

Run the automated regression tests:
    python3 -m unittest discover -s 2-farm/lessons/2-detect-soil-moisture/applied-labs/r15-t057 -p "test_*.py"
