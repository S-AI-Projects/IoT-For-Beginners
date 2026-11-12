# R15-T036: geofence membership, worked example

Extends the [Store location data](../../README.md) lesson. The lesson stores
GPS readings; once you have stored `(latitude, longitude)` records you can ask
whether each one is inside an area. This example walks four records through
that decision step by step, and the walk-through runs as a regression test.

**Scope:** a local simulation in standard-library Python 3. No IoT Hub,
storage account, GPS device, model or paid provider. The geofence is a flat
rectangle, **not a spherical-distance model**: it ignores Earth's curvature,
the antimeridian and the poles.

## Fixture

Coordinates are `(latitude, longitude)`. The rectangle is inclusive: latitude
10 to 20, longitude 70 to 80. Invalid input (latitude outside -90..90,
longitude outside -180..180, or not a number) is **rejected by raising `ValueError`**.

## Results

| Input (lat, lon) | Result | Why |
|---|---|---|
| (15, 75) | inside | both coordinates within range |
| (10, 70) | inside | boundary corner, bounds are inclusive |
| (21, 75) | outside | latitude 21 is above 20 |
| (100, 75) | invalid | latitude 100 is beyond 90, rejected |

## Worked example

Input `(21, 75)`:

```
input: latitude=21, longitude=75
latitude 21 in [10, 20]: False
longitude 75 in [70, 80]: True
result: outside
```

Input `(100, 75)`:

```
input: latitude=100, longitude=75
rejected: latitude 100 is outside -90..90
result: invalid
```

The test compares `explain()` output to these step lines exactly, and checks
that the table above matches the code, so the explanation cannot drift from the example.

## Run

```
python3 3-transport/lessons/2-store-location-data/applied-labs/r15-t036/example.py
python3 -m unittest discover -s 3-transport/lessons/2-store-location-data/applied-labs/r15-t036 -p "test_*.py"
```
