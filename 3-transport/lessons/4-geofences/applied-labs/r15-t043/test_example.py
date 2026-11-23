import os
import unittest
from example import SAMPLES, classify, compare_expected


class GeofenceTests(unittest.TestCase):
    def test_required_cases_and_independent_table(self):
        self.assertEqual([(x[0], x[1], x[2]) for x in compare_expected()], list(SAMPLES))
        for lat, lon, expected, actual in compare_expected():
            with self.subTest(lat=lat, lon=lon):
                self.assertEqual(actual, expected)

    def test_inclusive_all_corners(self):
        for point in ((10,70),(10,80),(20,70),(20,80)):
            self.assertEqual(classify(*point), "inside")

    def test_outside_cases(self):
        self.assertEqual(classify(9.999,75), "outside")
        self.assertEqual(classify(15,80.001), "outside")

    def test_invalid_coordinates(self):
        for args in ((100,75),(-91,75),(15,181),(float("nan"),75),(True,75),("15",75)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                classify(*args)

    @unittest.skipUnless(os.getenv("RUN_INTENTIONAL_FAILURE") == "1", "negative test runs separately")
    def test_deliberately_wrong_result_fails(self):
        self.assertEqual(classify(10,70), "outside")


if __name__ == "__main__":
    unittest.main()
