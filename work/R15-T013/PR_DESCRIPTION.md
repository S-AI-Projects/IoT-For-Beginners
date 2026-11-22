Description
This PR implements tensor-shape contract validation and image batch normalization as a lesson extension for Migrate Your Plant to the Cloud (2-farm/lessons/4-migrate-your-plant-to-the-cloud). It ensures incoming image batches maintain exact (N, H, W) dimensionality, validates pixel bounds in [0..255], and normalizes values to [0..1] prior to cloud model ingestion.

Related Issue
Fixes: #17

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t013/example.py` implementing batch dimension validation, pixel normalization, and an independent cross-validation reference model.
- Added `2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t013/test_example.py` with 8 unit tests covering batch [[[0, 255], [128, 64]]] shape preservation (1, 2, 2), pixel scaling (0 -> 0.0, 255 -> 1.0), negative and >255 pixel rejection, ragged shape errors, cross-model equivalence, and deliberate assertion failures.
- Added `2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t013/README.md` documenting contracts and limitations.
- Updated `2-farm/lessons/4-migrate-your-plant-to-the-cloud/README.md` with links and test commands.
- Saved test run logs in `work/R15-T013/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t013 -p "test_*.py" -v
```
All 8 unit tests passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
Verifies preprocessing pipeline integrity without making claims regarding downstream ML model performance or cloud latency.
