# R15-T053: Geofence Membership — Offline Service Adapter

## Overview & Lesson Connection
This local simulation example illustrates spatial geofence classification for GPS telemetry in **Visualize location data** by decoupling geofence membership checks behind a callable adapter interface (`GeofenceAdapter`).

- **What it illustrates:** Validating coordinate bounds (`lat` in `[-90, 90]`, `lon` in `[-180, 180]`), checking inclusive rectangular membership (`lat` in `[10, 20]`, `lon` in `[70, 80]`), and injecting a deterministic offline adapter (`local_rectangular_geofence_adapter`).
- **Where simplifications & mock behavior stop:**
  - This rectangular lat/lon bounding box is a teaching fixture, **not** a spherical-distance (Haversine/geodesic) or polygon geofence model.
  - The local adapter does **not** establish real Azure Maps API authentication, network latency, rate limits, cloud map rendering, or physical GPS receiver drift.

## Boundary Decisions
- **Inclusive geofence bounds:** `10.0 <= lat <= 20.0` and `70.0 <= lon <= 80.0`.
- **Fixture points:**
  - `(15, 75)` -> `inside: true` (interior point)
  - `(10, 70)` -> `inside: true` (inclusive lower-left boundary corner)
  - `(21, 75)` -> `inside: false` (outside northern latitude boundary)
  - `lat = 100` -> rejected with `ValueError` (outside valid Earth latitude `[-90, 90]`)

## Exact Invocation
    python3 3-transport/lessons/3-visualize-location-data/applied-labs/r15-t053/example.py

## Run Unit Tests
    python3 -m unittest discover -v -s 3-transport/lessons/3-visualize-location-data/applied-labs/r15-t053 -p "test_*.py"
