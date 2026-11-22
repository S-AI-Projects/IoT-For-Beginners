import unittest
from example import (
    FIXTURE_SCENARIOS,
    compare_approaches,
    evaluate_scenario_direct,
    evaluate_scenario_simple_table,
)


class TestSecurityScenarioCompareApproaches(unittest.TestCase):
    def test_complete_scenario_passes(self):
        res = evaluate_scenario_direct(FIXTURE_SCENARIOS[1])
        self.assertEqual(res["status"], "PASS")

    def test_missing_asset_fails(self):
        res = evaluate_scenario_direct(FIXTURE_SCENARIOS[0])
        self.assertEqual(res["status"], "FAIL")

    def test_unrelated_control_flagged_for_review(self):
        res = evaluate_scenario_direct(FIXTURE_SCENARIOS[2])
        self.assertEqual(res["status"], "FLAG_FOR_REVIEW")

    def test_direct_and_simple_table_approaches_match(self):
        comparisons = compare_approaches(FIXTURE_SCENARIOS)
        self.assertEqual(len(comparisons), 3)
        for item in comparisons:
            self.assertTrue(item["match"], f"Mismatch on {item}")
        self.assertEqual(evaluate_scenario_simple_table(FIXTURE_SCENARIOS[1]), "PASS")


if __name__ == "__main__":
    unittest.main()
