import os
import unittest
from example import SCENARIOS, check_scenario, failure_and_recovery


class EdgeSecurityRubricTests(unittest.TestCase):
    def test_all_three_complete_scenarios_pass_structure(self):
        self.assertEqual(len(SCENARIOS), 3)
        for name, scenario in SCENARIOS.items():
            with self.subTest(scenario=name):
                self.assertEqual(check_scenario(scenario)[0], "PASS")

    def test_missing_asset_is_failure(self):
        scenario = dict(SCENARIOS["Altered edge model package"])
        del scenario["asset"]
        self.assertEqual(check_scenario(scenario)[0], "FAIL")

    def test_unrelated_control_flagged_not_failed(self):
        scenario = dict(SCENARIOS["Altered edge model package"])
        scenario["control"] = "[privacy] Hide a screen from passersby."
        self.assertEqual(check_scenario(scenario)[0], "REVIEW")

    def test_missing_and_blank_fields(self):
        for key in ("asset", "threat", "control", "residual_risk"):
            item = dict(SCENARIOS["Offline classifier interruption"])
            item[key] = "  "
            with self.subTest(key=key):
                self.assertEqual(check_scenario(item)[0], "FAIL")
        self.assertEqual(check_scenario(None)[0], "FAIL")

    def test_failure_is_followed_by_valid_recovery(self):
        invalid, recovered = failure_and_recovery()
        self.assertEqual([invalid[0], recovered[0]], ["FAIL", "PASS"])

    @unittest.skipUnless(os.getenv("RUN_INTENTIONAL_FAILURE") == "1", "negative test runs separately")
    def test_deliberately_wrong_result_fails(self):
        self.assertEqual(check_scenario(SCENARIOS["Altered edge model package"])[0], "FAIL")


if __name__ == "__main__":
    unittest.main()
