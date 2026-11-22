import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    process_sensor_stream,
    validate_record,
    WORKED_EXAMPLE_INPUT,
)


class TestSensorMessageWorkedExample(unittest.TestCase):
    def test_exact_worked_example_regression(self):
        """Execute the exact published worked example as a regression test."""
        result = process_sensor_stream(WORKED_EXAMPLE_INPUT)

        # 1. Accepted messages are ordered 1, 2
        accepted = result["accepted"]
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0], {"device_id": "A", "timestamp": 1, "reading": 22.0})
        self.assertEqual(accepted[1], {"device_id": "A", "timestamp": 2, "reading": 23.5})

        # 2. Duplicate A/1 is reported
        duplicates = result["duplicates"]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0], {"device_id": "A", "timestamp": 1})

        # 3. String reading is rejected
        rejected = result["rejected"]
        self.assertEqual(len(rejected), 1)
        self.assertIn("reading", rejected[0]["reason"])

    def test_multiple_devices_and_float_timestamps(self):
        """Deduplication is scoped to (device_id, timestamp), allowing identical timestamps for different devices."""
        stream = [
            {"device_id": "B", "timestamp": 1.5, "reading": 10},
            {"device_id": "A", "timestamp": 1.5, "reading": 20},
            {"device_id": "A", "timestamp": 0.5, "reading": 30},
            {"device_id": "B", "timestamp": 1.5, "reading": 99},  # dup for B
        ]
        result = process_sensor_stream(stream)
        self.assertEqual(len(result["accepted"]), 3)
        self.assertEqual([m["timestamp"] for m in result["accepted"]], [0.5, 1.5, 1.5])
        self.assertEqual(len(result["duplicates"]), 1)
        self.assertEqual(result["duplicates"][0], {"device_id": "B", "timestamp": 1.5})

    def test_schema_validations(self):
        """Ensure boundary types and malformed payloads are correctly flagged."""
        self.assertFalse(validate_record("invalid-json")[0])
        self.assertFalse(validate_record([])[0])
        self.assertFalse(validate_record({"device_id": "", "timestamp": 1, "reading": 5})[0])
        self.assertFalse(validate_record({"device_id": "A", "timestamp": None, "reading": 5})[0])
        self.assertFalse(validate_record({"device_id": "A", "timestamp": 1, "reading": "5"})[0])
        self.assertFalse(validate_record({"device_id": "A", "timestamp": 1, "reading": True})[0])
        self.assertTrue(validate_record({"device_id": "A", "timestamp": 1, "reading": 0})[0])


if __name__ == "__main__":
    unittest.main()
