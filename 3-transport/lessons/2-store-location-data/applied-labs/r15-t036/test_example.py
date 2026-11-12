import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from example import WORKED, classify, explain  # noqa: E402


class WorkedExamples(unittest.TestCase):
    def test_explanations_match_exactly(self):
        for point, expected in WORKED.items():
            with self.subTest(point=point):
                self.assertEqual(explain(*point), expected)

    def test_four_expected_results(self):
        self.assertEqual(classify(15, 75), "inside")
        self.assertEqual(classify(10, 70), "inside")
        self.assertEqual(classify(21, 75), "outside")
        with self.assertRaises(ValueError):
            classify(100, 75)


class Boundaries(unittest.TestCase):
    def test_every_corner_inside(self):
        for lat in (10, 20):
            for lon in (70, 80):
                self.assertEqual(classify(lat, lon), "inside")

    def test_just_outside_each_edge(self):
        for lat, lon in [(9.999, 75), (20.001, 75), (15, 69.999), (15, 80.001)]:
            self.assertEqual(classify(lat, lon), "outside")

    def test_invalid_values_rejected(self):
        for lat, lon in [(-91, 75), (15, 181), (None, 75), ("15", 75),
                         (True, 75), (float("nan"), 75)]:
            with self.assertRaises(ValueError):
                classify(lat, lon)

    def test_swapped_order_is_a_different_answer(self):
        # (75, 15) is latitude 75, longitude 15: outside the rectangle
        self.assertEqual(classify(75, 15), "outside")


class ReadmeAgrees(unittest.TestCase):
    """The README results table must match what the code returns."""

    def test_readme_table(self):
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            text = f.read()
        rows = re.findall(r"^\|\s*\((-?\d+),\s*(-?\d+)\)\s*\|\s*(\w+)\s*\|", text, re.M)
        self.assertEqual(len(rows), 4)
        for lat, lon, expected in rows:
            lat, lon = int(lat), int(lon)
            try:
                actual = classify(lat, lon)
            except ValueError:
                actual = "invalid"
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
