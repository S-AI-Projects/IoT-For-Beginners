# R15-T039: geofence membership, scenario assessment

Extends the [Store location data](../../README.md) lesson. Once GPS readings
are stored, you can classify each `(latitude, longitude)` record against an
area. This example asks three applied questions about that classification, each
with a rationale and an executable check.

**Scope:** a local simulation in standard-library Python 3. No IoT Hub, storage
account, GPS device, model or paid provider. The geofence is a flat rectangle,
**not a spherical-distance model**: it ignores Earth's curvature, the
antimeridian and the poles.

## Fixture

Coordinates are `(latitude, longitude)`. The fence is latitude 10 to 20 and
longitude 70 to 80, inclusive. Invalid input (latitude outside -90..90, longitude
outside -180..180, or not a number) raises `ValueError`.

| Input (lat, lon) | Result |
|---|---|
| (15, 75) | inside |
| (10, 70) | inside (boundary, inclusive) |
| (21, 75) | outside |
| (100, 75) | rejected as invalid |

## Three applied questions

Each answer is stored next to a check that **computes** it from the code, and a
test fails if the two disagree.

**Q1 predict.** What does `classify` return for (15, 75), (10, 70) and (21, 75)?
Answer: `inside`, `inside`, `outside`. Rationale: (15, 75) is within both ranges;
(10, 70) is exactly on the lower bounds and the policy is inclusive; 21 is above 20.

**Q2 diagnose.** A tracker reports (75, 15) for a vehicle known to be inside the
fence, but it is classified outside. Why? Answer: the coordinate order is swapped,
so (75, 15) is read as latitude 75. Swapping gives (15, 75), which is inside.
`diagnose()` reports this, and reports `rejected: ...` for invalid input such as latitude 100.

**Q3 policy.** Two fences share the latitude-20 edge. How many contain the edge
point (20, 75)? Answer: **2 under the inclusive policy, 1 under half-open**
(lower bound in, upper bound out). Rationale: inclusive counts the shared edge in
both fences, so a vehicle on it is in two fences at once; half-open gives each edge
point to exactly one. This lesson uses **inclusive** because its stated rule is that
boundary points are inside; the cost is the double count on shared edges.

## Run

```
python3 3-transport/lessons/2-store-location-data/applied-labs/r15-t039/example.py
python3 -m unittest discover -s 3-transport/lessons/2-store-location-data/applied-labs/r15-t039 -p "test_*.py"
```
