Description
This PR implements geofence membership evaluation and scenario assessment as a lesson extension for Geofences (3-transport/lessons/4-geofences). It models an inclusive rectangular bounding box on geographic coordinates, enforces valid latitude/longitude bounds, explicitly identifies planar vs spherical limitations, and answers three applied scenario questions.

Related Issue
Fixes: #24

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `3-transport/lessons/4-geofences/applied-labs/r15-t020/example.py` implementing `RectangularTeachingGeofence` and rationale functions for three scenario assessment questions.
- Added `3-transport/lessons/4-geofences/applied-labs/r15-t020/test_example.py` with 9 unit tests verifying benchmark classification ((15, 75) inside, (10, 70) inside, (21, 75) outside, invalid latitude 100 rejected), planar model checks, scenario question verification, and intentional assertion failures.
- Added `3-transport/lessons/4-geofences/applied-labs/r15-t020/README.md` documenting geofence logic, spherical vs planar limitations, and scenario rationales.
- Updated `3-transport/lessons/4-geofences/README.md` to link to the new applied lab with verification commands.
- Captured test execution results in `work/R15-T020/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 3-transport/lessons/4-geofences/applied-labs/r15-t020 -p "test_*.py" -v
```
All 9 unit tests passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
The rectangular model is intended for educational demonstrations and does not replace geodesic spherical distance algorithms for large-scale logistics.
