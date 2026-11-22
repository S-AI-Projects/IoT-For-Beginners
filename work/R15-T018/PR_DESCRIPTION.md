Description
This PR implements sensor-message validation with failure and recovery handling as a lesson extension for Recognize Speech with an IoT Device (6-consumer/lessons/1-speech-recognition). It demonstrates resilient error diagnostics on missing and malformed data fields, duplicate handling, and seamless recovery when valid telemetry streams resume.

Related Issue
Fixes: #22

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `6-consumer/lessons/1-speech-recognition/applied-labs/r15-t018/example.py` implementing `ResilientTelemetryIngestor` with missing-data checks, type validation, deduplication, and chronological ordering.
- Added `6-consumer/lessons/1-speech-recognition/applied-labs/r15-t018/test_example.py` with 4 unit tests covering benchmark requirements (ordering device A times 2 then 1 to 1, 2; reporting duplicate A/1; rejecting string readings; verifying failure and recovery flow; deliberate failure check).
- Added `6-consumer/lessons/1-speech-recognition/applied-labs/r15-t018/README.md` detailing contracts, error taxonomy, and limitations.
- Updated `6-consumer/lessons/1-speech-recognition/README.md` to link to the new applied lab with test instructions.
- Captured test evidence in `work/R15-T018/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t018 -p "test_*.py" -v
```
All 4 unit tests passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
Pure Python 3 standard library; does not require physical microphones or cloud speech APIs.
