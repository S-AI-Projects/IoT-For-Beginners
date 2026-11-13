import unittest
from example import (
    process_messages_baseline,
    process_messages_refactored,
    validate_and_parse_message,
)


class TestSensorMessageRefactorEquivalence(unittest.TestCase):
    def test_ordering_duplicate_report_and_before_after_equivalence(self):
        fixture = [
            '{"device_id": "A", "timestamp": 2, "reading": 24.5}',
            '{"device_id": "A", "timestamp": 1, "reading": 23.0}',
            '{"device_id": "A", "timestamp": 1, "reading": 23.0}',
        ]
        baseline = process_messages_baseline(fixture)
        refactored = process_messages_refactored(fixture)

        # Prove before/after refactoring equivalence
        self.assertEqual(baseline, refactored)

        # Verify ordering 1, 2 and duplicate A/1 reporting
        self.assertEqual([m["timestamp"] for m in refactored["accepted"]], [1, 2])
        self.assertEqual(len(refactored["duplicates"]), 1)
        self.assertEqual(refactored["duplicates"][0]["device_id"], "A")
        self.assertEqual(refactored["duplicates"][0]["timestamp"], 1)

    def test_rejects_string_reading_in_both_baseline_and_refactored(self):
        bad_payload = ['{"device_id": "A", "timestamp": 1, "reading": "23.0"}']
        with self.assertRaises(ValueError):
            process_messages_baseline(bad_payload)
        with self.assertRaises(ValueError):
            process_messages_refactored(bad_payload)
        with self.assertRaises(ValueError):
            validate_and_parse_message(bad_payload[0])


if __name__ == "__main__":
    unittest.main()
