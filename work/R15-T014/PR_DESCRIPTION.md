Description
This PR implements capability negotiation and state tracing as a lesson extension for Trigger Fruit Quality Detection from a Sensor (4-manufacturing/lessons/4-trigger-fruit-detector). It models client-server capability set intersection, ensures unnegotiated capabilities are rejected before dispatch, and verifies state invariant consistency.

Related Issue
Fixes: #18

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `4-manufacturing/lessons/4-trigger-fruit-detector/applied-labs/r15-t014/example.py` implementing `NegotiationSession`, capability set intersection, pre-dispatch guards, state tracing, and invariant validation.
- Added `4-manufacturing/lessons/4-trigger-fruit-detector/applied-labs/r15-t014/test_example.py` covering negotiation between `{"tools", "resources"}` and `{"tools", "prompts"}`, rejection of `resources`, dispatch of `tools`, trace integrity, invariant verification, and deliberate assertion failure.
- Added `4-manufacturing/lessons/4-trigger-fruit-detector/applied-labs/r15-t014/README.md` documenting usage, execution traces, and simulation boundaries.
- Updated `4-manufacturing/lessons/4-trigger-fruit-detector/README.md` with links and verification instructions.
- Saved test output in `work/R15-T014/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 4-manufacturing/lessons/4-trigger-fruit-detector/applied-labs/r15-t014 -p "test_*.py" -v
```
All 7 unit tests passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
Pure Python 3 standard library; does not require physical proximity sensors or external AI servers.
