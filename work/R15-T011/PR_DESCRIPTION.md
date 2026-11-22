Description
This PR implements explicit access-policy evaluation as a local concept example for the Language Understanding lesson (6-consumer/lessons/2-language-understanding). It provides a deterministic local role/action/resource policy matrix enforcing default deny and deny-precedence rules.

Related Issue
Fixes: #2

Type of Change
* New Feature
* Tests
* Documentation

Changes Made
- Added `6-consumer/lessons/2-language-understanding/applied-labs/r15-t011/example.py` implementing role/action/resource evaluation with default-deny and deny-override semantics.
- Added `6-consumer/lessons/2-language-understanding/applied-labs/r15-t011/test_example.py` with 7 unit tests verifying normal, boundary, and error cases (reader permissions, deny overriding allow, unknown role, deliberate failure check).
- Added `6-consumer/lessons/2-language-understanding/applied-labs/r15-t011/README.md` documenting usage, inputs, outputs, and simulation scope.
- Updated `6-consumer/lessons/2-language-understanding/README.md` with links and verification instructions.
- Captured automated check results in `work/R15-T011/check_results.txt`.

Screenshots / Recordings
N/A (Console and unit test suite only)

Testing
Tested locally using unittest discovery:
```bash
python3 -m unittest discover -s 6-consumer/lessons/2-language-understanding/applied-labs/r15-t011 -p "test_*.py" -v
```
Ran 7 tests, all passed (OK).

Checklist
* I have tested my changes locally.
* I have added or updated tests, if needed.
* I have updated documentation, if needed.
* I have followed the project's coding guidelines.
* I have run the relevant tests and checks.
* I have addressed previous review feedback, if applicable.

Additional Notes
The lab uses only Python 3 standard library without requiring external cloud credentials or physical hardware.
