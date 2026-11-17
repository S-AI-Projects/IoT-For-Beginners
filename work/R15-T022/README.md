# Task R15-T022 Evidence: Sensor-Message Validation

This directory contains verification evidence for Task R15-T022 on branch `student/e26b07f0811`.

## Evidence Files

* **`environment.txt`**: Execution environment, operating system (macOS Darwin 27.0.0 arm64), Python version (3.14.3), and Git version (2.56.0).
* **`sample_results.txt`**: Full table of fixture inputs, categories, expected vs. actual outputs, chronological ordering verification (Device-A timestamp 1 before timestamp 2), and boundary/type decision rationales.
* **`test_run.txt`**: Execution logs of the discovery test runner, 13 passing unit tests, deliberate mutation failure log demonstrating exit code 1, and restored clean test pass logs.

## Verification Summary

1. **Standalone Example:** `python3 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t022/example.py` executes cleanly in a fresh process and displays formatted results for accepted, duplicate, and invalid messages.
2. **Test Discovery:** `python3 -m unittest discover -s 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t022 -p "test_*.py"` discovers and runs 13 unit tests, all passing with exit code 0.
3. **Negative / Mutation Test:** A temporary mutation allowing boolean readings was introduced; test discovery immediately caught the failure and exited nonzero (code 1). The fix was restored and re-verified.
4. **Git Safety:** Only the specified applied-lab files for R15-T022, evidence directory `work/R15-T022/`, and updated lesson README for Lesson 3 were created or touched. Task 1 files were left untouched.
