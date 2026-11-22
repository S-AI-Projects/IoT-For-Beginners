"""
Unit tests for Sensor-Message Validation — Evaluation Experiment (R15-T019)

Tests verify:
1. Messages for A at times 2 then 1 are returned in order 1,2
2. A duplicate A/1 is reported
3. A string reading is rejected
4. Comparison of 3 controlled configurations reporting correctness and metrics
5. Deliberate wrong assertion failure test
"""

import unittest
from example import (
    validate_and_order_telemetry,
    evaluate_batch_configuration,
    run_experiment,
)


class TestValidationExperiment(unittest.TestCase):
    def test_required_benchmark_fixture(self):
        batch = [
            {"device_id": "A", "timestamp": 2, "reading": 22.0},
            {"device_id": "A", "timestamp": 1, "reading": 21.0},
            {"device_id": "A", "timestamp": 1, "reading": 21.5},  # duplicate A/1
            {"device_id": "B", "timestamp": 3, "reading": "str_err"},  # string reading
        ]
        accepted, invalid, duplicates = validate_and_order_telemetry(batch)

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
        self.assertIn("Reading must be numeric", invalid[0]["reason"])

    def test_three_configurations_experiment(self):
        """Validates that all three configurations run, preserve sort invariants, and produce metrics."""
        results = run_experiment()
        self.assertEqual(set(results.keys()), {"Small", "Medium", "Large"})

        for name, metrics in results.items():
            self.assertTrue(metrics["is_sorted"], f"Configuration {name} was not sorted")
            self.assertGreaterEqual(metrics["accept_rate"], 0.0)
            self.assertLessEqual(metrics["accept_rate"], 1.0)
            self.assertGreaterEqual(metrics["duplicate_rate"], 0.0)
            self.assertEqual(
                metrics["total_messages"],
                metrics["accepted_count"] + metrics["invalid_count"] + metrics["duplicate_count"],
            )

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        batch = [{"device_id": "A", "timestamp": 1, "reading": 10}]
        accepted, _, _ = validate_and_order_telemetry(batch)
        with self.assertRaises(AssertionError):
            self.assertEqual(len(accepted), 99)  # Should be 1, expecting 99 must fail


if __name__ == "__main__":
    unittest.main()
