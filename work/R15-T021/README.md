# Task R15-T021 Evidence: Geofence Membership

This directory contains verification evidence for Task R15-T021 on branch `student/e26b07f0811`.

## Evidence Files

* **`environment.txt`**: Execution environment, platform details, tool versions (Python 3.14.3, git 2.56.0, macOS Darwin 27.0.0 arm64).
* **`sample_results.txt`**: Full table of sample coordinates, categories, expected vs. actual outcomes, demonstrating interior points, inclusive boundaries/corners, outside points, and invalid coordinate rejection.
* **`test_run.txt`**: Exact test discovery execution logs, verbose test runner outputs, controlled mutation test failure demonstration, and clean post-restoration test pass logs.

## Verification Summary

1. **Standalone Example:** `python3 3-transport/lessons/1-location-tracking/applied-labs/r15-t021/example.py` executes cleanly in a fresh process and formats outputs as expected.
2. **Test Discovery:** `python3 -m unittest discover -s 3-transport/lessons/1-location-tracking/applied-labs/r15-t021 -p "test_*.py"` discovers 9 tests and passes with exit code 0.
3. **Negative / Mutation Test:** A temporary mutation altering inclusive boundary checking was verified to immediately fail the test suite with exit code 1. The original implementation was restored and re-verified.
4. **Git Safety:** Only the specified applied-lab files, evidence directory, and updated lesson README were touched. No commits or pushes have been made.
