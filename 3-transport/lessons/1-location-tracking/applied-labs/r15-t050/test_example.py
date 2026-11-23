import os
import unittest
from example import POINTS, answers, classify


class ScenarioAssessmentTests(unittest.TestCase):
    def test_core_fixtures(self):
        self.assertEqual([classify(*p) for p in POINTS], ["inside", "inside", "outside"])

    def test_question_one_predict(self):
        self.assertEqual(answers()["predict"], "inside")
        self.assertEqual(classify(15, 75), "inside")

    def test_question_two_diagnose_invalid_latitude(self):
        self.assertEqual(answers()["diagnose"], "rejected: invalid latitude")
        with self.assertRaisesRegex(ValueError, "invalid latitude"):
            classify(100, 75)

    def test_question_three_inclusive_boundary_policy(self):
        self.assertEqual(answers()["boundary_policy"], "inside")
        self.assertEqual(classify(10, 70, inclusive=True), "inside")
        self.assertEqual(classify(10, 70, inclusive=False), "outside")
        for corner in ((10,70),(10,80),(20,70),(20,80)):
            self.assertEqual(classify(*corner), "inside")

    def test_invalid_coordinate_and_option(self):
        for point in ((-91,70),(20,181),(float("inf"),70),("15",75),(True,70)):
            with self.subTest(point=point), self.assertRaises(ValueError):
                classify(*point)
        with self.assertRaises(ValueError):
            classify(15,75,inclusive="yes")

    @unittest.skipUnless(os.getenv("RUN_INTENTIONAL_FAILURE") == "1", "negative test runs separately")
    def test_deliberately_wrong_result_fails(self):
        self.assertEqual(classify(10, 70), "outside")


if __name__ == "__main__":
    unittest.main()
