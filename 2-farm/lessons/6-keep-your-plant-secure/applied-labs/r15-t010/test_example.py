import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    process_telemetry_stream,
    validate_message,
    ASSESSMENT_QUESTIONS,
)


class TestSensorMessageScenarioAssessment(unittest.TestCase):
    def test_required_ordering_and_duplicates_and_string_rejection(self):
        """Messages for A at times 2 then 1 are returned in order 1,2; duplicate reported; string reading rejected."""
        messages = [
            {"device_id": "A", "timestamp": 2, "reading": 23.5},
            {"device_id": "A", "timestamp": 1, "reading": 22.0},
            {"device_id": "A", "timestamp": 1, "reading": 22.1},  # duplicate
            {"device_id": "A", "timestamp": 3, "reading": "invalid"},  # string reading
        ]
        res = process_telemetry_stream(messages)

        # 1. Returned in order 1, 2
        accepted = res["accepted"]
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0]["timestamp"], 1)
        self.assertEqual(accepted[1]["timestamp"], 2)

        # 2. Duplicate A/1 reported
        self.assertEqual(len(res["duplicates"]), 1)
        self.assertEqual(res["duplicates"][0], {"device_id": "A", "timestamp": 1})

        # 3. String reading rejected
        self.assertEqual(len(res["rejected"]), 1)
        self.assertIn("reading", res["rejected"][0]["reason"])

    def test_question_1_predict_output(self):
        """Executable check for Q1: Out-of-order messages are reordered chronologically."""
        test_stream = [
            {"device_id": "A", "timestamp": 2, "reading": 10},
            {"device_id": "A", "timestamp": 1, "reading": 20},
        ]
        res = process_telemetry_stream(test_stream)
        predicted_order = ASSESSMENT_QUESTIONS["Q1_PREDICT_OUTPUT"]["answer"]
        actual_order = [m["timestamp"] for m in res["accepted"]]
        self.assertEqual(actual_order, predicted_order)

    def test_question_2_diagnose_failure(self):
        """Executable check for Q2: Non-numeric string reading fails validation."""
        bad_msg = {"device_id": "A", "timestamp": 3, "reading": "50"}
        ok, _, reason = validate_message(bad_msg)
        self.assertFalse(ok)
        self.assertIn("reading", reason)

    def test_question_3_choose_boundary_policy(self):
        """Executable check for Q3: Default policy protects first-seen reading from replay modification."""
        stream = [
            {"device_id": "A", "timestamp": 1, "reading": 100},
            {"device_id": "A", "timestamp": 1, "reading": 999},  # conflicting duplicate
        ]
        # Secure default policy retains first-seen
        res_secure = process_telemetry_stream(stream, deduplication_policy="reject_duplicate")
        self.assertEqual(res_secure["accepted"][0]["reading"], 100)
        self.assertEqual(len(res_secure["duplicates"]), 1)

        # Insecure overwrite policy alters reading
        res_insecure = process_telemetry_stream(stream, deduplication_policy="overwrite")
        self.assertEqual(res_insecure["accepted"][0]["reading"], 999)


if __name__ == "__main__":
    unittest.main()
