# R15-T032: geofence membership, comparing two approaches

Extends the [Location tracking](../../README.md) lesson. The lesson explains
latitude and longitude; this example decides whether a coordinate record is
inside a teaching geofence.

**Scope:** a local simulation in standard-library Python 3. No GPS hardware,
cloud service, model or paid provider. The geofence is a flat rectangle,
**not a spherical-distance model**. It ignores Earth's curvature, the
antimeridian (longitude wrap-around) and the poles.

## Fixture

Coordinates are `(latitude, longitude)`. The rectangle is inclusive: latitude
10 to 20, longitude 70 to 80. Valid input ranges are latitude -90..90 and
longitude -180..180; anything else, or a non-number, is `invalid`.

## Two approaches, identical inputs

1. `classify`: direct bound comparisons.
2. `classify_by_clamp`: independent calculation. A point is inside if clamping
   it to the rectangle leaves it unchanged.

The tests also check both against an explicit expected-result table.

| Point | Expected | Why |
|---|---|---|
| (15, 75) | inside | well within both ranges |
| (10, 70) | inside | boundary corner, bounds are inclusive |
| (21, 75) | outside | latitude just above 20 |
| (100, 75) | invalid | latitude beyond 90 |

## Run

```
python3 3-transport/lessons/1-location-tracking/applied-labs/r15-t032/example.py
python3 -m unittest discover -s 3-transport/lessons/1-location-tracking/applied-labs/r15-t032 -p "test_*.py"
```
