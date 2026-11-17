# Applied Lab R15-T021: Geofence Membership

This applied lab demonstrates how to evaluate whether a geographic point falls inside a rectangular geofence using Python.

## Overview

In IoT location tracking applications (such as vehicle fleet monitoring), a geofence represents a virtual perimeter. When vehicles enter or leave this zone, systems can trigger notifications, compliance checks, or logistical workflows.

This lab implements an inclusive rectangular geofence defined by coordinate boundaries:
* **Minimum Latitude:** `10.0`
* **Maximum Latitude:** `20.0`
* **Minimum Longitude:** `70.0`
* **Maximum Longitude:** `80.0`

### Scope and Constraints

* **Local Sample Data:** The example evaluates local sample/mock coordinate records in decimal degrees.
* **No Hardware Connection:** It does not connect to a real GPS device or read serial NMEA sentences.
* **No Live/Cloud Services:** It does not use live location data, cloud services, or external mapping APIs.
* **Containment Logic Only:** It demonstrates rectangular coordinate containment logic only.

### Coordinate Ordering & Representation

Coordinates are represented in standard decimal degrees and use **`(latitude, longitude)`** ordering:
* **Latitude:** Measures degrees north (+) or south (-) of the Equator, bounded between `-90.0` and `90.0`.
* **Longitude:** Measures degrees east (+) or west (-) of the Prime Meridian, bounded between `-180.0` and `180.0`.

### Inclusive Boundary Behavior

The boundary edges and corners of the geofence are **inclusive** (`<=` and `>=`). Any point lying exactly on the border is classified as **inside**:
* $(15.0, 75.0)$ is strictly **inside** (interior).
* $(10.0, 70.0)$ is **inside** (on the southwest corner).
* $(20.0, 80.0)$ is **inside** (on the northeast corner).
* $(21.0, 75.0)$ is **outside** (latitude exceeds maximum boundary $20.0$).
* Coordinates outside Earth bounds (e.g., latitude $100.0$) are **rejected** as invalid.

### Important Concept: Planar Coordinate Boundary vs. Spherical Distance

> ⚠️ **Not a Spherical-Distance Model**
>
> This lab implements an **axis-aligned planar coordinate-boundary containment check** ($min \le coord \le max$).
>
> It does **NOT** compute spherical or geodesic distance (such as the Haversine formula, great-circle distance, or ellipsoidal distance on WGS84). While Earth is an oblate spheroid where lines of longitude converge at the poles, this example serves as a straightforward introductory demonstration of coordinate filtering before tackling complex polygonal geofences or geospatial cloud APIs (such as Azure Maps).

---

## Prerequisites

* **Python 3.x**
* **Python Standard Library only** (no external packages or third-party dependencies required).

---

## Running the Example

Run the example from the repository root:

```bash
python3 3-transport/lessons/1-location-tracking/applied-labs/r15-t021/example.py
```

### Expected Output

```output
======================================================================
Task R15-T021: Rectangular Geofence Membership Example
Geofence Boundaries (Inclusive): Latitude [10.0, 20.0], Longitude [70.0, 80.0]
Model: Planar Coordinate Boundary Containment (NOT a spherical-distance model)
======================================================================

Latitude   Longitude  Result       Description
----------------------------------------------------------------------
15.0       75.0       INSIDE       Required inside case (interior)
10.0       70.0       INSIDE       Required boundary case (SW corner, inclusive)
20.0       80.0       INSIDE       Boundary case (NE corner, inclusive)
21.0       75.0       OUTSIDE      Required outside case (latitude > 20)
15.0       85.0       OUTSIDE      Outside case (longitude > 80)
100.0      75.0       REJECTED     Required invalid case (latitude 100 > 90) -> Invalid latitude 100.0: must be between -90.0 and 90.0 degrees.
-95.0      75.0       REJECTED     Invalid case (latitude -95 < -90) -> Invalid latitude -95.0: must be between -90.0 and 90.0 degrees.
15.0       185.0      REJECTED     Invalid case (longitude 185 > 180) -> Invalid longitude 185.0: must be between -180.0 and 180.0 degrees.
15.0       -185.0     REJECTED     Invalid case (longitude -185 < -180) -> Invalid longitude -185.0: must be between -180.0 and 180.0 degrees.
----------------------------------------------------------------------
Sample execution completed successfully.
```

---

## Running the Unit Tests

Execute the test suite using Python's standard `unittest` test runner via discovery from the repository root:

```bash
python3 -m unittest discover -s 3-transport/lessons/1-location-tracking/applied-labs/r15-t021 -p "test_*.py"
```

You can also run tests with verbose details:

```bash
python3 -m unittest discover -s 3-transport/lessons/1-location-tracking/applied-labs/r15-t021 -p "test_*.py" -v
```

### Expected Test Output

```output
Ran 9 tests in 0.001s

OK
```
