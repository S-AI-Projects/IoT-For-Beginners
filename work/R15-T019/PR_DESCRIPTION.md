Description
This PR implements an evaluation experiment measuring telemetry batch validation, deduplication, and sorting performance across three controlled input sizes for Connect Your Device to the Internet (1-getting-started/lessons/4-connect-internet).

Related Issue
Fixes: #23

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `1-getting-started/lessons/4-connect-internet/applied-labs/r15-t019/example.py` implementing `evaluate_batch_configuration` and `run_experiment` across Small, Medium, and Large batch sizes.
- Added `1-getting-started/lessons/4-connect-internet/applied-labs/r15-t019/test_example.py` with 3 unit tests verifying benchmark requirements (device A times 2 then 1 ordered to 1, 2; duplicate A/1 rejected; string reading rejected; 3-configuration metric reporting; deliberate failure test).
- Added `1-getting-started/lessons/4-connect-internet/applied-labs/r15-t019/README.md` documenting methodology, configuration details, and simulation scope.
- Updated `1-getting-started/lessons/4-connect-internet/README.md` with links and verification commands.
- Saved test run logs in `work/R15-T019/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 1-getting-started/lessons/4-connect-internet/applied-labs/r15-t019 -p "test_*.py" -v
```
All 3 unit tests passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
Focuses on software batching trade-offs without making claims regarding physical radio signals or ML model accuracy.
