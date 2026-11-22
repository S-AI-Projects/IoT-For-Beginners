import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    process_messages_direct,
    process_messages_reference,
    validate_message,
)


class TestSensorMessageValidation(unittest.TestCase):
    def setUp(self):
        self.sample = [
            {"device_id": "A", "timestamp": 2, "reading": 23.5},
            {"device_id": "A", "timestamp": 1, "reading": 22.0},
            {"device_id": "A", "timestamp": 1, "reading": 99.9},  # duplicate A/1
            {"device_id": "A", "timestamp": 3, "reading": "invalid_string"},  # string reading
        ]

    def test_ordering_and_duplicates_and_string_rejection(self):
        """Messages for A at times 2 then 1 are returned in order 1,2; duplicate reported; string reading rejected."""
        res = process_messages_direct(self.sample)

        # 1. Order 1, 2
        accepted = res["accepted"]
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0]["timestamp"], 1)
        self.assertEqual(accepted[1]["timestamp"], 2)
        self.assertEqual(accepted[0]["device_id"], "A")
        self.assertEqual(accepted[1]["device_id"], "A")

        # 2. Duplicate A/1 reported
        duplicates = res["duplicates"]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["device_id"], "A")
        self.assertEqual(duplicates[0]["timestamp"], 1)

        # 3. String reading rejected
        rejected = res["rejected"]
        self.assertEqual(len(rejected), 1)
        self.assertIn("reading", rejected[0]["reason"])

    def test_compare_two_approaches_equivalence(self):
        """Both direct and reference approaches produce identical results across diverse inputs."""
        test_suite = [
            self.sample,
            # Empty list
            [],
            # Multiple devices interleaved
            [
                {"device_id": "B", "timestamp": 10, "reading": 100},
                {"device_id": "A", "timestamp": 5, "reading": 50},
                {"device_id": "B", "timestamp": 2, "reading": 20},
                {"device_id": "A", "timestamp": 5, "reading": 55},  # dup
            ],
            # Invalid payloads
            [
                "not-a-json",
                {"device_id": "", "timestamp": 1, "reading": 10},
                {"device_id": "A", "timestamp": "not-a-number", "reading": 10},
                {"device_id": "A", "timestamp": 1, "reading": True},  # boolean rejected
            ],
        ]

        for dataset in test_suite:
            r1 = process_messages_direct(dataset)
            r2 = process_messages_reference(dataset)
            self.assertEqual(r1, r2)

    def test_schema_validations(self):
        """Unit checks on validate_message."""
        self.assertTrue(validate_message({"device_id": "A", "timestamp": 1, "reading": 10})[0])
        self.assertFalse(validate_message({"device_id": "A", "timestamp": 1, "reading": "10"})[0])
        self.assertFalse(validate_message({"device_id": "A", "timestamp": 1, "reading": None})[0])
        self.assertFalse(validate_message({"device_id": "A", "timestamp": 1, "reading": False})[0])
        self.assertFalse(validate_message("invalid")[0])


if __name__ == "__main__":
    unittest.main()
