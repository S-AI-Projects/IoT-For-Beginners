# R15-T002: Geofence Membership — Inclusive Rectangular Boundary Case

An applied laboratory extension for the [Geofences](../../README.md) lesson.

## Educational Context & Scope

This lab implements an inclusive planar rectangular geofence with:
- **Latitude bounds:** `[10, 20]` inclusive
- **Longitude bounds:** `[70, 80]` inclusive

> **Note on Geodesics:** This implementation operates on a 2D planar coordinate bounding box for teaching boundary classification logic. It is **not** a spherical-distance model (such as Haversine or geodesic distance on the WGS84 ellipsoid). Real-world applications near the poles or across coordinate boundaries require spherical geometry algorithms or geospatial indexing libraries.

**Scope:** Python 3 standard library simulation. No GPS hardware, map tiles, external servers, or Azure Maps accounts required.

## Run

```bash
python3 3-transport/lessons/4-geofences/applied-labs/r15-t002/example.py
python3 -m unittest discover -s 3-transport/lessons/4-geofences/applied-labs/r15-t002 -p "test_*.py"
```

## Boundary Decision & Test Scenarios

| Category | Coordinates `(lat, lon)` | Expected Result | Explanation |
|---|---|---|---|
| Inside (Interior) | `(15, 75)` | `inside` | Strictly inside `[10, 20]` lat and `[70, 80]` lon |
| Boundary Corner | `(10, 70)` | `inside` | Exact Southwest corner; boundaries are inclusive (`<=`) |
| Boundary Corner | `(20, 80)` | `inside` | Exact Northeast corner; boundaries are inclusive (`<=`) |
| Boundary Edges | `(10, 75)`, `(20, 75)` | `inside` | Points exactly on perimeter lines are inside |
| Outside | `(21, 75)` | `outside` | Latitude 21 exceeds maximum latitude 20 |
| Near Boundary | `(9.999, 75)` | `outside` | Latitude strictly below 10 |
| Invalid Coordinate | `(100, 75)` | `ValueError` | Latitude 100 exceeds global spherical range `[-90, 90]` |
| Invalid Coordinate | `(15, 185)` | `ValueError` | Longitude 185 exceeds global spherical range `[-180, 180]` |
| Invalid Type | `("15", 75)` | `TypeError` | Non-numeric coordinate representation |

## Where the Simplification Stops

Real IoT geospatial applications must handle:
1. Ellipsoidal Earth models (e.g. WGS84 geodesics, Haversine formula)
2. GPS drift, sensor jitter, and precision dilution (HDOP/PDOP)
3. Complex multi-point polygons or GeoJSON polygons instead of simple axis-aligned rectangles
4. Anti-meridian crossing (longitude wrapping at +/- 180 degrees)
