Description
This PR refactors the Growing Degree Day (GDD) calculation teaching example for the Predict Plant Growth with IoT lesson (2-farm/lessons/1-predict-plant-growth). It extracts single-responsibility functions for daily temperature evaluation, enforces strict domain validation (rejecting minimum > maximum), and proves mathematical equivalence between baseline and refactored code.

Related Issue
Fixes: #20

Type of Change
* Refactoring / Maintenance
* Tests
* Documentation

Changes Made
- Added `2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t016/example.py` with both baseline monolithic calculation and refactored modular design extracting `compute_single_day_gdd`.
- Added `2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t016/test_example.py` with 5 unit tests validating the benchmark fixture (base 10, days (8,16),(12,20),(2,8) -> contributions 2,6,0 and total 8), minimum > maximum rejection, before/after refactoring equivalence, and intentional test failure assertions.
- Added `2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t016/README.md` documenting formula derivations, contracts, and limitations.
- Updated `2-farm/lessons/1-predict-plant-growth/README.md` to link to the new applied lab with verification steps.
- Saved check results in `work/R15-T016/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t016 -p "test_*.py" -v
```
All 5 unit tests passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
Pure Python 3 standard library; does not require physical soil probes or external weather APIs.
