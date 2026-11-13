# R15-T054: Geofence Membership — Invariant and State Trace

## Overview & Lesson Connection
This local simulation example illustrates location coordinate validation and geofence tagging prior to persistent storage in **Store location data**, recording intermediate state transitions at each processing step and verifying the invariant linking intermediate state to the final classification output.

- **What it illustrates:** Validating coordinate bounds (`lat` in `[-90, 90]`, `lon` in `[-180, 180]`), checking inclusive rectangular membership (`lat` in `[10, 20]`, `lon` in `[70, 80]`), recording per-step intermediate state (`validated_lat`, `validated_lon`, `lat_in_bounds`, `lon_in_bounds`, `computed_inside`), and asserting the state-to-output invariant (`inside == (lat_in_bounds and lon_in_bounds)`).
- **Where simplifications & simulation stop:**
  - This rectangular lat/lon bounding box is a teaching fixture, **not** a spherical-distance (Haversine/geodesic) model.
  - No cloud storage (Azure Blob Storage / Cosmos DB / Azure Functions), network I/O, or physical GPS hardware is invoked.

## Boundary Decisions
- **Inclusive geofence bounds:** `10.0 <= lat <= 20.0` and `70.0 <= lon <= 80.0`.
- **Fixture points:**
  - `(15, 75)` -> `inside: true` (interior point)
  - `(10, 70)` -> `inside: true` (inclusive boundary point)
  - `(21, 75)` -> `inside: false` (outside northern boundary)
  - `lat = 100` -> rejected with `ValueError` (outside valid Earth latitude `[-90, 90]`)

## Exact Invocation
    python3 3-transport/lessons/2-store-location-data/applied-labs/r15-t054/example.py

## Run Unit Tests
    python3 -m unittest discover -v -s 3-transport/lessons/2-store-location-data/applied-labs/r15-t054 -p "test_*.py"
