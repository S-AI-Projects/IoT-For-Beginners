import unittest
from example import FIXTURE_MESSAGES, evaluate_applied_questions, validate_and_order_messages


class TestSensorMessageScenarioAssessment(unittest.TestCase):
    def test_ordering_deduplication_and_string_rejection(self):
        res = validate_and_order_messages(FIXTURE_MESSAGES)
        self.assertEqual(
            res["accepted"],
            [
                {"device_id": "A", "timestamp": 1, "reading": 22.0},
                {"device_id": "A", "timestamp": 2, "reading": 24.5},
            ],
        )
        self.assertEqual(len(res["rejected"]), 2)
        reasons = " ".join(r["reason"] for r in res["rejected"])
        self.assertIn("Duplicate device_id/timestamp pair: A/1", reasons)
        self.assertIn("Reading must be numeric", reasons)

    def test_applied_questions_executable_checks(self):
        questions = evaluate_applied_questions()
        self.assertEqual(len(questions), 3)
        for q in questions:
            qid = q["id"]
            self.assertTrue(q["check_passed"], f"Failed check for {qid}")

    def test_malformed_json_and_boolean_rejected(self):
        res = validate_and_order_messages([
            "{bad-json",
            {"device_id": "C", "timestamp": 10, "reading": True},
        ])
        self.assertEqual(res["accepted"], [])
        self.assertEqual(len(res["rejected"]), 2)


if __name__ == "__main__":
    unittest.main()
