# Task R15-T026 Evidence: Geofence Membership — Refactor Teaching Example

This directory contains execution and verification evidence for Task R15-T026 on branch `R15-T026`.

## Task Overview

Task R15-T026 implements and refactors a rectangular geofence membership teaching example for Lesson 3-3 (`3-transport/lessons/3-visualize-location-data/`).

The implementation addresses key aspects of spatial location handling in IoT:
- Local evaluation of rectangular geofence boundaries in decimal degrees.
- Clarification of spatial coordinate conventions: local Python fixtures use `(latitude, longitude)`, while GeoJSON (RFC 7946) requires `[longitude, latitude]`.
- Inclusive boundary logic: minimum (`10.0, 70.0`) and maximum (`20.0, 80.0`) boundaries are inside the geofence.
- Strict input validation rejecting booleans, strings, missing values, non-finite numbers, and invalid coordinate ranges (`[-90, 90]` for latitude, `[-180, 180]` for longitude).
- Distinct categorization: invalid records are classified as `REJECTED`, never misclassified as `OUTSIDE`.
- Architectural refactoring: extracting the boundary check responsibility into `is_inside_geofence(latitude, longitude, bounds)`, while retaining the reference baseline (`classify_record_baseline`) and proving 100% equivalence via `verify_equivalence()`.

## Evidence Files Summary

* **`environment.txt`**: Records the exact system environment, execution timestamp, Python version (3.14.3), Git version (2.56.0), platform details (macOS Darwin 27.0.0 arm64), and standard library dependency information.
* **`sample_results.txt`**: Captures genuine command output from running `example.py`, including geofence definitions, fixture coordinates, baseline vs refactored classification table, equivalence proof, and deliberate failure detection.
* **`test_run.txt`**: Captures full verbose test execution output from the standard `unittest` test discovery runner (17 tests passing, 0 failures, exit code 0).
* **`comparison.txt`**: Details the four required fixture records, expected vs. actual outcomes, baseline vs refactored architectural comparison, equivalence guarantees, and captured outputs demonstrating that deliberate wrong expectations cause `AssertionError` with nonzero process exit codes.
