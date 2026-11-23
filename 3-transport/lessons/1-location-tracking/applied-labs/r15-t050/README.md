# R15-T050 — Location geofence scenario assessment

This **fictional, local** coordinate exercise extends the [location-tracking lesson](../../README.md) with three questions and executable checks. Input order is `(latitude, longitude)`. Latitude must be in `[-90,90]`, longitude in `[-180,180]`; non-finite or nonnumeric coordinates are rejected. The teaching rectangle is latitude `[10,20]` and longitude `[70,80]` with **inclusive** boundaries.

From the repository root:

```sh
python3 3-transport/lessons/1-location-tracking/applied-labs/r15-t050/example.py
python3 -m unittest discover -s 3-transport/lessons/1-location-tracking/applied-labs/r15-t050 -p "test_*.py"
```

Core fixtures: `(15,75) -> inside`, `(10,70) -> inside`, `(21,75) -> outside`, and `(100,75) -> rejected: invalid latitude`.

### Three applied questions, answers, and executable checks

1. **Predict an output:** Is `(15,75)` inside? **Yes, `inside`**, because both values lie within the specified ranges. `test_question_one_predict` asserts the computed output.
2. **Diagnose a failure:** Why is `(100,75)` rejected? **Invalid latitude**, because 100 is outside the valid global latitude range of -90 to 90. `test_question_two_diagnose_invalid_latitude` checks the raised error and the readable diagnosis.
3. **Choose a boundary policy:** Should `(10,70)` count? **Yes, `inside`** under the explicitly inclusive policy; with exclusive bounds it would be `outside`. `test_question_three_inclusive_boundary_policy` compares both policies and all four corners.

The script prints the fixture results plus `predict: inside`, `diagnose: rejected: invalid latitude`, and `boundary_policy: inside`. Run `RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 3-transport/lessons/1-location-tracking/applied-labs/r15-t050 -p "test_*.py"` to demonstrate a deliberately wrong expected result exits nonzero.

The rectangle is **not a spherical-distance model**, an accurate polygon geofence, a route or a GPS observation. It does not test physical GPS accuracy, NMEA parsing, or cloud functionality.
