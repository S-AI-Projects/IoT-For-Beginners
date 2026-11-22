Description
This PR implements sensor-message validation and chronological ordering as a boundary-case lesson extension for the Deeper Dive into IoT lesson (1-getting-started/lessons/2-deeper-dive). It enforces strict numeric typing for telemetry readings, deduplicates device/timestamp pairs, and sorts accepted packets chronologically.

Related Issue
Fixes: #16

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t012/example.py` implementing message validation, deduplication, and timestamp ordering.
- Added `1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t012/test_example.py` covering out-of-order sequencing, duplicate detection, string reading rejection, boundary values, and intentional test failure assertions.
- Added `1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t012/README.md` detailing contracts, verification steps, and simulation boundaries.
- Updated `1-getting-started/lessons/2-deeper-dive/README.md` to link to the new applied lab with verification commands.
- Saved test run logs in `work/R15-T012/check_results.txt`.

Screenshots / Recordings
N/A (Backend verification and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 1-getting-started/lessons/2-deeper-dive/applied-labs/r15-t012 -p "test_*.py" -v
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
Pure Python 3 standard library; requires no physical hardware or cloud brokers.
