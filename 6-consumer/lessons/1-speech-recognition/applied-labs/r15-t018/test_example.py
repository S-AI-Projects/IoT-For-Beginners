"""
Unit tests for Sensor-Message Validation — Failure & Recovery (R15-T018)

Tests verify:
1. Messages for A at times 2 then 1 are returned in order 1,2
2. A duplicate A/1 is reported
3. A string reading is rejected
4. Exercise missing-data failure and demonstrate instant recovery on subsequent valid packet
5. Deliberate wrong assertion failure test
"""

import unittest
from example import ResilientTelemetryIngestor, run_demo


class TestFailureAndRecoveryValidation(unittest.TestCase):
    def test_required_benchmark_and_recovery(self):
        batch = [
            {"device_id": "A", "timestamp": 2, "reading": 20.0},
            {"device_id": "A", "timestamp": 1, "reading": 18.0},
            {"device_id": "A", "timestamp": 1, "reading": 18.5},  # duplicate A/1
            {"device_id": "B", "timestamp": 3, "reading": "bad_str"},  # string reading rejected
        ]
        ingestor = ResilientTelemetryIngestor()
        result = ingestor.ingest_batch(batch)

        # 1. Messages for A at times 2 then 1 are returned in order 1,2
        accepted = result["accepted"]
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0]["timestamp"], 1)
        self.assertEqual(accepted[1]["timestamp"], 2)

        # 2. Duplicate A/1 is reported
        errors = result["errors"]
        duplicate_errors = [e for e in errors if "DUPLICATE" in e["error"]]
        self.assertEqual(len(duplicate_errors), 1)
        self.assertEqual(duplicate_errors[0]["message"]["device_id"], "A")
        self.assertEqual(duplicate_errors[0]["message"]["timestamp"], 1)

        # 3. String reading is rejected
        type_errors = [e for e in errors if "TYPE_ERROR" in e["error"]]
        self.assertEqual(len(type_errors), 1)
        self.assertEqual(type_errors[0]["message"]["device_id"], "B")

    def test_missing_data_and_recovery_flow(self):
        """Exercises missing data error, explains error, and tests recovery on next valid input."""
        ingestor = ResilientTelemetryIngestor()

        # Step 1: Valid initial message
        ok1, _ = ingestor.ingest_single({"device_id": "dev1", "timestamp": 10, "reading": 42.0})
        self.assertTrue(ok1)

        # Step 2: Missing field failure
        bad_msg = {"device_id": "dev1", "timestamp": 11}  # missing reading
        ok2, err_msg = ingestor.ingest_single(bad_msg)
        self.assertFalse(ok2)
        self.assertIn("MISSING_DATA", err_msg)
        self.assertIn("reading", err_msg)

        # Step 3: Immediate recovery on next valid packet
        recovery_msg = {"device_id": "dev1", "timestamp": 12, "reading": 45.0}
        ok3, success_msg = ingestor.ingest_single(recovery_msg)
        self.assertTrue(ok3)
        self.assertIn("ACCEPTED", success_msg)

        # Ensure accepted contains both 10 and 12, excluding 11
        self.assertEqual(len(ingestor.accepted_messages), 2)
        self.assertEqual(ingestor.accepted_messages[0]["timestamp"], 10)
        self.assertEqual(ingestor.accepted_messages[1]["timestamp"], 12)

    def test_run_demo(self):
        result = run_demo()
        self.assertEqual(len(result["accepted"]), 3)
        self.assertEqual(len(result["errors"]), 3)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        ingestor = ResilientTelemetryIngestor()
        ok, _ = ingestor.ingest_single({"device_id": "A", "timestamp": 1, "reading": "str"})
        with self.assertRaises(AssertionError):
            self.assertTrue(ok)  # Deliberate failure: string reading must not be True


if __name__ == "__main__":
    unittest.main()
