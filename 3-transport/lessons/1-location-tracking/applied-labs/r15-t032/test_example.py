import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import EXPECTED, classify, classify_by_clamp  # noqa: E402


class ExpectedTable(unittest.TestCase):
    def test_direct_matches_table(self):
        for point, expected in EXPECTED.items():
            with self.subTest(point=point):
                self.assertEqual(classify(*point), expected)

    def test_clamp_matches_table(self):
        for point, expected in EXPECTED.items():
            with self.subTest(point=point):
                self.assertEqual(classify_by_clamp(*point), expected)


class Comparison(unittest.TestCase):
    def test_two_approaches_agree_on_identical_inputs(self):
        points = [(la, lo) for la in range(-100, 111, 5) for lo in range(-190, 191, 10)]
        for p in points:
            with self.subTest(point=p):
                self.assertEqual(classify(*p), classify_by_clamp(*p))


class Required(unittest.TestCase):
    def test_stated_cases(self):
        self.assertEqual(classify(15, 75), "inside")
        self.assertEqual(classify(10, 70), "inside")
        self.assertEqual(classify(21, 75), "outside")
        self.assertEqual(classify(100, 75), "invalid")

    def test_bad_types(self):
        for bad in [(None, 75), ("15", 75), (True, 75), (float("nan"), 75)]:
            self.assertEqual(classify(*bad), "invalid")


if __name__ == "__main__":
    unittest.main()
