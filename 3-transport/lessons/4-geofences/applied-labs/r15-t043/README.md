# R15-T043 — Geofence: direct check versus expected table

This **fictional**, hardware-free rectangle demonstrates geofence membership in the [Geofences lesson](../../README.md). Coordinates are `(latitude, longitude)`; the rectangle includes the boundary: latitude `[10,20]`, longitude `[70,80]`.

Run from repository root:

```sh
python3 3-transport/lessons/4-geofences/applied-labs/r15-t043/example.py
python3 -m unittest discover -s 3-transport/lessons/4-geofences/applied-labs/r15-t043 -p "test_*.py"
```

A direct inclusive comparison is checked against an **independently authored expected table** with identical inputs: `(15,75) -> inside`, `(10,70) -> inside`, `(21,75) -> outside`. `(100,75)` is rejected as invalid latitude. All four rectangle corners count as inside. Run `RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 3-transport/lessons/4-geofences/applied-labs/r15-t043 -p "test_*.py"` to see the intentionally wrong result make the test process exit nonzero.

This is **not** spherical-distance, polygon geofencing, NMEA parsing, actual GPS data, or an Azure Maps result. No network call is made.
