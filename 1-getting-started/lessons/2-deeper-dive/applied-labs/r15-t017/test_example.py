"""
Unit tests & regression suite for Sensor Message Validation (R15-T017)

Tests verify:
1. Messages for A at times 2 then 1 are returned in order 1,2
2. A duplicate A/1 is reported
3. A string reading is rejected
4. Regression suite executes exact worked example
5. Deliberate wrong assertion failure test
"""

import unittest
from example import process_telemetry_batch, run_demo


class TestSensorMessageWorkedExample(unittest.TestCase):
    def test_exact_regression_example(self):
        """Exact worked example regression test."""
        input_data = [
            {"device_id": "A", "timestamp": 2, "reading": 25.1},
            {"device_id": "A", "timestamp": 1, "reading": 24.8},
            {"device_id": "A", "timestamp": 1, "reading": 24.9},  # duplicate A/1
            {"device_id": "B", "timestamp": 3, "reading": "invalid_string"},  # string reading
        ]
        res = process_telemetry_batch(input_data)

        # 1. Messages for A at times 2 then 1 returned in order 1,2
        accepted = res["accepted"]
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0]["device_id"], "A")
        self.assertEqual(accepted[0]["timestamp"], 1)
        self.assertEqual(accepted[1]["device_id"], "A")
        self.assertEqual(accepted[1]["timestamp"], 2)

        # 2. Duplicate A/1 is reported
        duplicates = res["rejected_duplicates"]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["message"]["device_id"], "A")
        self.assertEqual(duplicates[0]["message"]["timestamp"], 1)

        # 3. String reading is rejected
        invalid = res["rejected_invalid"]
        self.assertEqual(len(invalid), 1)
        self.assertIn("reading must be numeric", invalid[0]["reason"])

        # Check trace matches steps
        trace = res["trace"]
        self.assertEqual(len(trace), 4)
        self.assertEqual([t["outcome"] for t in trace], ["ACCEPTED", "ACCEPTED", "DUPLICATE", "INVALID"])

    def test_run_demo(self):
        res = run_demo()
        self.assertEqual(len(res["accepted"]), 2)
        self.assertEqual(len(res["rejected_duplicates"]), 1)
        self.assertEqual(len(res["rejected_invalid"]), 1)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        res = process_telemetry_batch([{"device_id": "A", "timestamp": 1, "reading": 10}])
        with self.assertRaises(AssertionError):
            self.assertEqual(len(res["accepted"]), 0)  # Should be 1, expecting 0 must fail


if __name__ == "__main__":
    unittest.main()
