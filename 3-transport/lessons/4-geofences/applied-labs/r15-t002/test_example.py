import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    classify_point,
    classify_records,
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
)


class TestGeofenceMembership(unittest.TestCase):
    def test_required_examples(self):
        """(15,75) and boundary (10,70) are inside; (21,75) is outside."""
        self.assertEqual(classify_point(15, 75), "inside")
        self.assertEqual(classify_point(10, 70), "inside")
        self.assertEqual(classify_point(21, 75), "outside")

    def test_all_four_corners_inclusive(self):
        """Inclusive geofence includes all four boundary corners."""
        corners = [
            (LAT_MIN, LON_MIN),  # (10, 70)
            (LAT_MIN, LON_MAX),  # (10, 80)
            (LAT_MAX, LON_MIN),  # (20, 70)
            (LAT_MAX, LON_MAX),  # (20, 80)
        ]
        for lat, lon in corners:
            self.assertEqual(classify_point(lat, lon), "inside")

    def test_boundary_edges(self):
        """Points exactly on boundary lines are inside."""
        self.assertEqual(classify_point(10, 75), "inside")  # southern edge
        self.assertEqual(classify_point(20, 75), "inside")  # northern edge
        self.assertEqual(classify_point(15, 70), "inside")  # western edge
        self.assertEqual(classify_point(15, 80), "inside")  # eastern edge

    def test_just_outside_boundary(self):
        """Points just outside boundary edges are outside."""
        self.assertEqual(classify_point(9.999, 75), "outside")
        self.assertEqual(classify_point(20.001, 75), "outside")
        self.assertEqual(classify_point(15, 69.999), "outside")
        self.assertEqual(classify_point(15, 80.001), "outside")

    def test_invalid_latitude_rejected(self):
        """Invalid latitude 100 is rejected with ValueError."""
        with self.assertRaises(ValueError):
            classify_point(100, 75)
        with self.assertRaises(ValueError):
            classify_point(-91, 75)

    def test_invalid_longitude_rejected(self):
        """Invalid longitude outside [-180, 180] raises ValueError."""
        with self.assertRaises(ValueError):
            classify_point(15, 181)
        with self.assertRaises(ValueError):
            classify_point(15, -181)

    def test_invalid_types_rejected(self):
        """Non-numeric coordinates raise TypeError."""
        with self.assertRaises(TypeError):
            classify_point("15", 75)
        with self.assertRaises(TypeError):
            classify_point(15, None)
        with self.assertRaises(TypeError):
            classify_point(True, 75)

    def test_batch_records(self):
        """Batch classification preserves sequence and decisions."""
        records = [(15, 75), (10, 70), (21, 75)]
        self.assertEqual(classify_records(records), ["inside", "inside", "outside"])


if __name__ == "__main__":
    unittest.main()
