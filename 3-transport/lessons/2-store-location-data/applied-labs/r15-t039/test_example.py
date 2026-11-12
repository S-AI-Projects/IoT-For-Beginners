import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from example import QUESTIONS, classify, diagnose, run_checks  # noqa: E402


class Fixture(unittest.TestCase):
    def test_four_expected_results(self):
        self.assertEqual(classify(15, 75), "inside")
        self.assertEqual(classify(10, 70), "inside")
        self.assertEqual(classify(21, 75), "outside")
        with self.assertRaises(ValueError):
            classify(100, 75)

    def test_invalid_input(self):
        for bad in [(-91, 75), (15, 181), (None, 75), ("15", 75), (True, 75),
                    (float("nan"), 75)]:
            with self.assertRaises(ValueError):
                classify(*bad)
        with self.assertRaises(ValueError):
            classify(15, 75, policy="nope")


class Questions(unittest.TestCase):
    def test_three_questions(self):
        self.assertEqual([q["id"][:2] for q in QUESTIONS], ["Q1", "Q2", "Q3"])

    def test_each_has_rationale_and_runnable_check(self):
        for q in QUESTIONS:
            with self.subTest(q=q["id"]):
                self.assertTrue(q["rationale"].strip())
                self.assertTrue(callable(q["check"]))

    def test_each_stated_answer_matches_computed(self):
        for qid, stated, computed, ok in run_checks():
            with self.subTest(q=qid):
                self.assertEqual(stated, computed)
                self.assertTrue(ok)

    def test_q1_values(self):
        self.assertEqual(QUESTIONS[0]["check"](), ["inside", "inside", "outside"])

    def test_q2_diagnosis(self):
        self.assertIn("swapped", diagnose(75, 15, "inside"))
        self.assertEqual(diagnose(15, 75, "inside"), "ok")
        self.assertTrue(diagnose(100, 75, "inside").startswith("rejected"))
        self.assertEqual(diagnose(21, 75, "inside"), "genuinely outside the fence")

    def test_q3_policy_counts(self):
        self.assertEqual(QUESTIONS[2]["check"](), {"inclusive": 2, "half_open": 1})

    def test_wrong_stated_answer_would_be_caught(self):
        wrong = dict(QUESTIONS[0], answer=["inside", "outside", "outside"])
        self.assertNotEqual(wrong["check"](), wrong["answer"])


class ReadmeAgrees(unittest.TestCase):
    def test_readme_states_the_answers(self):
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("not a spherical-distance model", text)
        for q in QUESTIONS:
            self.assertIn(q["id"], text)


if __name__ == "__main__":
    unittest.main()
