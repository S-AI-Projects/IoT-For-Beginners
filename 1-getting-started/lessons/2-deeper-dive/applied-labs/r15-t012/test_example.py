"""
Unit tests for Sensor Message Validation (R15-T012)

Tests verify:
1. Messages for A at times 2 then 1 are returned in order 1,2
2. A duplicate A/1 is reported
3. A string reading is rejected
4. Boundary cases (numeric boundaries, empty payloads, smallest valid fixture)
5. Deliberate wrong assertion failure test
"""

import unittest
from example import validate_and_order_messages, run_demo


class TestSensorMessageValidation(unittest.TestCase):
    def test_ordering_and_duplicate_and_string_reading(self):
        """Covers core requirement from issue description."""
        batch = [
            {"device_id": "A", "timestamp": 2, "reading": 20.5},
            {"device_id": "A", "timestamp": 1, "reading": 19.8},
            {"device_id": "A", "timestamp": 1, "reading": 20.0},  # duplicate A/1
            {"device_id": "B", "timestamp": 5, "reading": "25.0"},  # string reading rejected
        ]
        accepted, invalid, duplicates = validate_and_order_messages(batch)

        # 1. Messages for A at times 2 then 1 are returned in order 1,2
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0]["timestamp"], 1)
        self.assertEqual(accepted[1]["timestamp"], 2)

        # 2. Duplicate A/1 is reported
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["message"]["device_id"], "A")
        self.assertEqual(duplicates[0]["message"]["timestamp"], 1)

        # 3. String reading is rejected
        self.assertEqual(len(invalid), 1)
        self.assertIn("reading must be numeric", invalid[0]["reason"])

    def test_smallest_valid_boundary(self):
        """Smallest valid fixture."""
        batch = [{"device_id": "X", "timestamp": 0, "reading": 0}]
        accepted, invalid, duplicates = validate_and_order_messages(batch)
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0], {"device_id": "X", "timestamp": 0, "reading": 0})
        self.assertEqual(len(invalid), 0)
        self.assertEqual(len(duplicates), 0)

    def test_boolean_rejection_boundary(self):
        """In Python, bool is a subclass of int (True==1). Ensure booleans are rejected."""
        batch = [
            {"device_id": "A", "timestamp": True, "reading": 10},
            {"device_id": "B", "timestamp": 10, "reading": False},
        ]
        accepted, invalid, duplicates = validate_and_order_messages(batch)
        self.assertEqual(len(accepted), 0)
        self.assertEqual(len(invalid), 2)

    def test_run_demo(self):
        accepted, invalid, duplicates = run_demo()
        self.assertEqual(len(accepted), 2)
        self.assertEqual(len(invalid), 1)
        self.assertEqual(len(duplicates), 1)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates deliberate test failure detection."""
        batch = [{"device_id": "A", "timestamp": 1, "reading": "bad"}]
        accepted, invalid, duplicates = validate_and_order_messages(batch)
        with self.assertRaises(AssertionError):
            self.assertEqual(len(accepted), 1)  # should be 0 because reading is string


if __name__ == "__main__":
    unittest.main()
