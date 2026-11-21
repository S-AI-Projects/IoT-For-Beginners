#!/usr/bin/env python3
"""Unit tests for sensor-message validation, deduplication, and evaluation.

Coursework Task: R15-T029
Context Lesson: 4-manufacturing/lessons/2-check-fruit-from-device
"""

import math
import os
import subprocess
import sys
import unittest

from example import (
    generate_synthetic_dataset,
    get_mandatory_fixture,
    process_message_stream,
    validate_message_schema,
)


class TestSensorMessageValidation(unittest.TestCase):
    """Test suite for sensor message validation, deduplication, ordering, and evaluation."""

    def test_mandatory_fixture_counts_and_order(self):
        """Verify the exact mandatory 4-message fixture requirements."""
        fixture = get_mandatory_fixture()
        res = process_message_stream(fixture)

        self.assertEqual(res.total_processed, 4)
        self.assertEqual(len(res.accepted), 2)
        self.assertEqual(len(res.duplicates), 1)
        self.assertEqual(len(res.rejected), 1)

        # Check accepted messages: sorted ascending by timestamp (1.0 then 2.0)
        self.assertEqual(res.accepted[0].device_id, "A")
        self.assertEqual(res.accepted[0].timestamp, 1.0)
        self.assertEqual(res.accepted[0].reading, 40.0)

        self.assertEqual(res.accepted[1].device_id, "A")
        self.assertEqual(res.accepted[1].timestamp, 2.0)
        self.assertEqual(res.accepted[1].reading, 42.0)

        self.assertTrue(res.is_sorted)

        # Check duplicate details
        dup = res.duplicates[0]
        self.assertEqual(dup.device_id, "A")
        self.assertEqual(dup.timestamp, 1.0)
        self.assertEqual(dup.reading, 41.0)
        self.assertEqual(dup.original_index, 2)
        self.assertEqual(dup.first_seen_index, 1)

        # Check rejected details
        rej = res.rejected[0]
        self.assertEqual(rej.original_index, 3)
        self.assertIn("reading", rej.reason.lower())

    def test_duplicate_device_timestamp_detection(self):
        """Verify that identical (device_id, timestamp) pairs are reported as duplicates."""
        msgs = [
            {"device_id": "sensor_1", "timestamp": 100.0, "reading": 10.0},
            {"device_id": "sensor_1", "timestamp": 100.0, "reading": 20.0},
            {"device_id": "sensor_1", "timestamp": 100.0, "reading": 30.0},
        ]
        res = process_message_stream(msgs)
        self.assertEqual(len(res.accepted), 1)
        self.assertEqual(len(res.duplicates), 2)
        self.assertEqual(res.accepted[0].reading, 10.0)

    def test_same_timestamp_across_different_devices_allowed(self):
        """Different devices may share the exact same timestamp without collision."""
        msgs = [
            {"device_id": "dev_A", "timestamp": 50.0, "reading": 1.0},
            {"device_id": "dev_B", "timestamp": 50.0, "reading": 2.0},
            {"device_id": "dev_C", "timestamp": 50.0, "reading": 3.0},
        ]
        res = process_message_stream(msgs)
        self.assertEqual(len(res.accepted), 3)
        self.assertEqual(len(res.duplicates), 0)

    def test_stable_order_for_equal_timestamps(self):
        """Ties in timestamp must preserve original arrival order (stable sort)."""
        msgs = [
            {"device_id": "Z", "timestamp": 10.0, "reading": 1.0},
            {"device_id": "A", "timestamp": 10.0, "reading": 2.0},
            {"device_id": "M", "timestamp": 10.0, "reading": 3.0},
        ]
        res = process_message_stream(msgs)
        self.assertEqual([m.device_id for m in res.accepted], ["Z", "A", "M"])

    def test_missing_required_fields(self):
        """Missing device_id, timestamp, or reading must be rejected with clear reasons."""
        res_no_dev = process_message_stream([{"timestamp": 1.0, "reading": 10.0}])
        self.assertEqual(len(res_no_dev.rejected), 1)
        self.assertIn("device_id", res_no_dev.rejected[0].reason)

        res_no_ts = process_message_stream([{"device_id": "A", "reading": 10.0}])
        self.assertEqual(len(res_no_ts.rejected), 1)
        self.assertIn("timestamp", res_no_ts.rejected[0].reason)

        res_no_rd = process_message_stream([{"device_id": "A", "timestamp": 1.0}])
        self.assertEqual(len(res_no_rd.rejected), 1)
        self.assertIn("reading", res_no_rd.rejected[0].reason)

    def test_malformed_json_rejected(self):
        """Malformed JSON strings must be rejected cleanly."""
        res = process_message_stream(['{"device_id": "A", "timestamp": 1, reading: broken}'])
        self.assertEqual(len(res.rejected), 1)
        self.assertIn("Malformed JSON", res.rejected[0].reason)

        res_type = process_message_stream([12345])
        self.assertEqual(len(res_type.rejected), 1)

    def test_empty_and_whitespace_device_id_rejected(self):
        """Empty or whitespace-only device_id must be rejected."""
        res = process_message_stream([
            {"device_id": "", "timestamp": 1.0, "reading": 10.0},
            {"device_id": "   ", "timestamp": 2.0, "reading": 20.0},
            {"device_id": "\t\n", "timestamp": 3.0, "reading": 30.0},
        ])
        self.assertEqual(len(res.rejected), 3)
        for r in res.rejected:
            self.assertIn("empty or whitespace", r.reason)

    def test_string_reading_rejected(self):
        """String readings must not be silently coerced into numbers."""
        res = process_message_stream([
            {"device_id": "A", "timestamp": 1.0, "reading": "42"},
            {"device_id": "B", "timestamp": 2.0, "reading": "bad_reading"},
        ])
        self.assertEqual(len(res.rejected), 2)
        for r in res.rejected:
            self.assertIn("reading", r.reason)

    def test_string_timestamp_rejected(self):
        """String timestamps must not be silently coerced into numbers."""
        res = process_message_stream([
            {"device_id": "A", "timestamp": "100", "reading": 42.0},
        ])
        self.assertEqual(len(res.rejected), 1)
        self.assertIn("timestamp", res.rejected[0].reason)

    def test_boolean_numeric_values_rejected(self):
        """Booleans must be rejected as timestamps and readings."""
        res = process_message_stream([
            {"device_id": "A", "timestamp": True, "reading": 42.0},
            {"device_id": "B", "timestamp": 1.0, "reading": False},
        ])
        self.assertEqual(len(res.rejected), 2)
        self.assertIn("boolean", res.rejected[0].reason)
        self.assertIn("boolean", res.rejected[1].reason)

    def test_nan_and_infinity_rejected(self):
        """NaN and positive/negative infinity values must be rejected."""
        res = process_message_stream([
            {"device_id": "A", "timestamp": float("nan"), "reading": 42.0},
            {"device_id": "B", "timestamp": 1.0, "reading": float("inf")},
            {"device_id": "C", "timestamp": 1.0, "reading": float("-inf")},
        ])
        self.assertEqual(len(res.rejected), 3)
        for r in res.rejected:
            self.assertIn("finite number", r.reason)

    def test_overflow_enormous_integer_rejected(self):
        """Enormous integers causing OverflowError on float conversion must be rejected."""
        huge_int = 10**10000

        # Timestamp overflow
        res_ts = process_message_stream([{"device_id": "dev1", "timestamp": huge_int, "reading": 42.0}])
        self.assertEqual(len(res_ts.rejected), 1)
        self.assertIn("supported numeric range", res_ts.rejected[0].reason)

        # Reading overflow
        res_rd = process_message_stream([{"device_id": "dev1", "timestamp": 1.0, "reading": huge_int}])
        self.assertEqual(len(res_rd.rejected), 1)
        self.assertIn("supported numeric range", res_rd.rejected[0].reason)

        # Subsequent valid message with same device/timestamp accepted after invalid overflow message
        stream = [
            {"device_id": "dev1", "timestamp": 1.0, "reading": huge_int},  # Rejected due to reading overflow
            {"device_id": "dev1", "timestamp": 1.0, "reading": 50.0},      # Accepted!
        ]
        res_stream = process_message_stream(stream)
        self.assertEqual(len(res_stream.rejected), 1)
        self.assertEqual(len(res_stream.accepted), 1)
        self.assertEqual(len(res_stream.duplicates), 0)
        self.assertEqual(res_stream.accepted[0].reading, 50.0)

    def test_invalid_message_does_not_reserve_identity(self):
        """An invalid message must not prevent a subsequent valid message from being accepted."""
        msgs = [
            {"device_id": "A", "timestamp": 10.0, "reading": "invalid"},  # Rejected
            {"device_id": "A", "timestamp": 10.0, "reading": 55.5},       # Accepted!
        ]
        res = process_message_stream(msgs)
        self.assertEqual(len(res.rejected), 1)
        self.assertEqual(len(res.accepted), 1)
        self.assertEqual(len(res.duplicates), 0)
        self.assertEqual(res.accepted[0].reading, 55.5)

    def test_empty_input(self):
        """Empty input stream returns empty accepted, duplicate, and rejected lists."""
        res = process_message_stream([])
        self.assertEqual(res.total_processed, 0)
        self.assertEqual(len(res.accepted), 0)
        self.assertEqual(len(res.duplicates), 0)
        self.assertEqual(len(res.rejected), 0)
        self.assertTrue(res.is_sorted)

    def test_evaluation_synthetic_dataset_sizes_and_ordering(self):
        """Verify each evaluation input size (10, 100, 1000) has correct counts and sorted output."""
        for size in (10, 100, 1000):
            dataset = generate_synthetic_dataset(size)
            self.assertEqual(len(dataset), size)

            res = process_message_stream(dataset)
            expected_accepted = (size * 7) // 10
            expected_duplicates = (size * 2) // 10
            expected_rejected = (size * 1) // 10

            self.assertEqual(len(res.accepted), expected_accepted, f"Failed for size {size}")
            self.assertEqual(len(res.duplicates), expected_duplicates, f"Failed for size {size}")
            self.assertEqual(len(res.rejected), expected_rejected, f"Failed for size {size}")
            self.assertTrue(res.is_sorted, f"Sorting check failed for size {size}")

    def test_cli_normal_scenario_subprocess(self):
        """Run --scenario normal in a fresh process and verify exit 0 and expected output."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "normal"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(proc.returncode, 0, f"Error:\n{proc.stderr}")
        self.assertIn("MANDATORY LOGICAL FIXTURE", proc.stdout)
        self.assertIn("Accepted Count:  2", proc.stdout)
        self.assertIn("EVALUATION EXPERIMENT", proc.stdout)

    def test_cli_boundary_scenario_subprocess(self):
        """Run --scenario boundary in a fresh process and verify exit 0."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "boundary"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(proc.returncode, 0, f"Error:\n{proc.stderr}")
        self.assertIn("All Boundary Checks PASSED", proc.stdout)

    def test_cli_failure_scenario_subprocess(self):
        """Run --scenario failure in a fresh process and verify non-zero exit."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "failure"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("INTENTIONAL FAILURE", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
