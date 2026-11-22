import unittest
from example import FIXTURE_SCENARIOS, evaluate_batch_with_recovery, evaluate_scenario


class TestSecurityScenarioRubric(unittest.TestCase):
    def test_complete_scenario_passes(self):
        complete = FIXTURE_SCENARIOS[1]
        res = evaluate_scenario(complete)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["errors"], [])

    def test_missing_asset_fails_and_recovers_on_next_valid_input(self):
        batch = evaluate_batch_with_recovery(FIXTURE_SCENARIOS)
        by_id = {r["scenario_id"]: r for r in batch["results"]}
        self.assertEqual(by_id["SC-01-MISSING-ASSET"]["status"], "FAIL")
        self.assertIn("Missing or empty required field: asset", by_id["SC-01-MISSING-ASSET"]["errors"])
        self.assertEqual(by_id["SC-02-COMPLETE-PASS"]["status"], "PASS")
        self.assertTrue(batch["summary"]["recovered_on_subsequent_valid_input"])

    def test_unrelated_control_flagged_for_review(self):
        unrelated = FIXTURE_SCENARIOS[2]
        res = evaluate_scenario(unrelated)
        self.assertEqual(res["status"], "FLAG_FOR_REVIEW")
        self.assertIn("human review", res["review_note"].lower())


if __name__ == "__main__":
    unittest.main()
