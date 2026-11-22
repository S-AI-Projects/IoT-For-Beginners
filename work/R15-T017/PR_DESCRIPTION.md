Description
This PR implements a worked example and regression test suite for sensor-message validation under A Deeper Dive into IoT (1-getting-started/lessons/2-deeper-dive). It documents and executes a step-by-step walkthrough validating telemetry formats, detecting duplicate device/timestamp pairs, and sorting messages into chronological sequence.

Related Issue
Fixes: #21

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t017/example.py` providing `process_telemetry_batch` with audit step logging.
- Added `1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t017/test_example.py` executing the regression suite on the benchmark fixture (device A at times 2, 1 ordered to 1, 2; duplicate A/1 rejected; string reading on B rejected; deliberate failure assertion).
- Added `1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t017/README.md` explaining the worked walkthrough, step-by-step trace, and boundaries.
- Updated `1-getting-started/lessons/2-deeper-dive/README.md` with links and verification commands.
- Saved check output in `work/R15-T017/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t017 -p "test_*.py" -v
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
Operates purely via Python 3 standard library; requires no live cloud brokers or physical sensors.
