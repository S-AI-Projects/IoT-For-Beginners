import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    process_stock_messages,
    run_evaluation_experiment,
    validate_message,
)


class TestStockMessageValidationExperiment(unittest.TestCase):
    def test_required_ordering_and_duplicates_and_string_rejection(self):
        """Messages for A at times 2 then 1 are returned in order 1,2; duplicate reported; string reading rejected."""
        messages = [
            {"device_id": "A", "timestamp": 2, "reading": 10},
            {"device_id": "A", "timestamp": 1, "reading": 15},
            {"device_id": "A", "timestamp": 1, "reading": 15},  # duplicate
            {"device_id": "A", "timestamp": 3, "reading": "ten"},  # string reading
        ]
        res = process_stock_messages(messages)

        # Reordered timestamps 1, 2
        accepted = res["accepted"]
        self.assertEqual(len(accepted), 2)
        self.assertEqual([m["timestamp"] for m in accepted], [1, 2])

        # Duplicate A/1 reported
        self.assertEqual(len(res["duplicates"]), 1)
        self.assertEqual(res["duplicates"][0], {"device_id": "A", "timestamp": 1})

        # String reading rejected
        self.assertEqual(len(res["rejected"]), 1)
        self.assertIn("reading", res["rejected"][0]["reason"])

    def test_experiment_configurations_and_invariants(self):
        """Compare three small controlled configurations and verify correctness invariants."""
        report = run_evaluation_experiment()
        self.assertIn("Small (N=4)", report)
        self.assertIn("Medium (N=20)", report)
        self.assertIn("Large (N=100)", report)

        for cfg_name, stats in report.items():
            # Invariant: Total == Accepted + Duplicates + Rejected
            self.assertTrue(stats["invariant_holds"])
            self.assertEqual(
                stats["total_input"],
                stats["accepted_count"] + stats["duplicate_count"] + stats["rejected_count"],
            )

    def test_schema_validations(self):
        """Verify schema edge cases."""
        self.assertTrue(validate_message({"device_id": "shelf_1", "timestamp": 100, "reading": 0})[0])
        self.assertFalse(validate_message({"device_id": "shelf_1", "timestamp": 100, "reading": "0"})[0])
        self.assertFalse(validate_message({"device_id": "shelf_1", "timestamp": "100", "reading": 5})[0])
        self.assertFalse(validate_message({"device_id": "", "timestamp": 100, "reading": 5})[0])


if __name__ == "__main__":
    unittest.main()
