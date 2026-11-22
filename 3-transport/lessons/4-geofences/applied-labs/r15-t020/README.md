# Applied Lab: Geofence Membership — Scenario Assessment (R15-T020)

This lab extends the [Geofences lesson](../../README.md) by implementing an inclusive rectangular teaching geofence, validating geographic boundary checks, and answering three applied scenario questions.

## Concept & Curriculum Connection

Geofencing is a fundamental location-based service in transport and logistics, used to detect when vehicles or refrigerated containers arrive at warehouses or deviate from approved transit corridors.

### Teaching Model vs Real-World Spherical Modeling
> **Explicit Model Boundary:** This lab implements a planar rectangular bounding box for educational clarity. It directly checks whether $\text{lat} \in [\min, \max]$ and $\text{lon} \in [\min, \max]$. It does **not** model Earth's ellipsoid (WGS-84), nor does it calculate spherical Great-Circle or Haversine distances. In high-latitude real-world applications, geodesic polygon intersection algorithms must be used instead.

## Geofence Contract & Benchmark
- **Geofence Parameters:**
  - Latitude: $[10.0, 20.0]$ (inclusive)
  - Longitude: $[70.0, 80.0]$ (inclusive)
- **Coordinate Domain Limits:**
  - Latitude: $[-90.0, 90.0]$
  - Longitude: $[-180.0, 180.0]$
- **Benchmark Classification:**
  - `(15, 75)`: `INSIDE` (interior coordinate)
  - `(10, 70)`: `INSIDE` (inclusive perimeter boundary)
  - `(21, 75)`: `OUTSIDE` (latitude $21 > 20$)
  - `(100, 75)`: `REJECTED` (`ValueError`: latitude exceeds $90^\circ$ physical limit)

## Applied Scenario Questions

### 1. Predict an Output
- **Question:** Predict the classification of coordinate `(20.0, 80.0)`.
- **Answer:** `INSIDE`.
- **Rationale:** The bounding box uses inclusive comparison operators ($\le$); coordinates resting precisely on upper limits are included.

### 2. Diagnose a Failure
- **Question:** Diagnose why coordinate `(100.0, 75.0)` triggers an unhandled or validation error.
- **Answer:** Geographic invalidity.
- **Rationale:** Valid latitude on the terrestrial sphere spans $[-90^\circ, +90^\circ]$. A latitude of $100^\circ$ signifies corrupted GPS telemetry or sensor parsing failure.

### 3. Choose a Boundary Policy
- **Question:** Choose between an inclusive ($\le$) and exclusive ($<$) boundary policy for a fleet depot perimeter.
- **Answer:** `INCLUSIVE`.
- **Rationale:** GPS receivers produce jitter (multipath error). When a delivery truck parks along a yard fence, an exclusive policy causes high-frequency state oscillation ("border chattering"), triggering false departure alerts.

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example
```bash
python3 3-transport/lessons/4-geofences/applied-labs/r15-t020/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 3-transport/lessons/4-geofences/applied-labs/r15-t020 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Arithmetic:** Planar bounding box computation; requires no live GPS NMEA hardware, cellular modems, or Azure Maps subscriptions.
