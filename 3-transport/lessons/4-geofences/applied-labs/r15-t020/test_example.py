"""
Unit tests for Geofence Membership & Scenario Assessment (R15-T020)

Tests verify:
1. (15,75) and boundary (10,70) are inside
2. (21,75) is outside
3. Invalid latitude 100 is rejected
4. Explicit statement and checks that model is planar rectangular, not spherical
5. Executable checks for all three applied scenario questions
6. Deliberate wrong assertion failure test
"""

import unittest
from example import (
    RectangularTeachingGeofence,
    answer_question_1_predict_output,
    answer_question_2_diagnose_failure,
    answer_question_3_choose_boundary_policy,
    run_demo,
)


class TestGeofenceMembership(unittest.TestCase):
    def setUp(self):
        self.geofence = RectangularTeachingGeofence(min_lat=10.0, max_lat=20.0, min_lon=70.0, max_lon=80.0)

    def test_required_benchmark_points(self):
        # 1. (15, 75) is inside
        self.assertTrue(self.geofence.contains(15.0, 75.0))

        # 2. Boundary (10, 70) is inside (inclusive)
        self.assertTrue(self.geofence.contains(10.0, 70.0))

        # 3. (21, 75) is outside
        self.assertFalse(self.geofence.contains(21.0, 75.0))

    def test_invalid_latitude_100_rejected(self):
        # Invalid latitude 100 must be rejected
        with self.assertRaises(ValueError) as ctx:
            self.geofence.contains(100.0, 75.0)
        self.assertIn("must be between -90 and 90", str(ctx.exception))

    def test_invalid_longitude_rejected(self):
        with self.assertRaises(ValueError):
            self.geofence.contains(15.0, 200.0)

    def test_planar_model_limitation_check(self):
        """Verifies explicit planar model behavior."""
        # Near poles, longitude convergence is ignored in planar boxes
        fence = RectangularTeachingGeofence(min_lat=80.0, max_lat=85.0, min_lon=10.0, max_lon=20.0)
        self.assertTrue(fence.contains(82.0, 15.0))

    def test_question_1_predict_output(self):
        is_inside, rationale = answer_question_1_predict_output(20.0, 80.0)
        self.assertTrue(is_inside)
        self.assertIn("upper corner boundary", rationale)

    def test_question_2_diagnose_failure(self):
        diagnosed, explanation = answer_question_2_diagnose_failure(100.0, 75.0)
        self.assertTrue(diagnosed)
        self.assertIn("Correctly diagnosed", explanation)

    def test_question_3_choose_boundary_policy(self):
        choice, rationale = answer_question_3_choose_boundary_policy((10.0, 70.0))
        self.assertEqual(choice, "INCLUSIVE")
        self.assertIn("prevents false exit alerts", rationale)

    def test_run_demo(self):
        # Should execute cleanly without unhandled exceptions
        run_demo()

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        # Point (21, 75) is outside (False); asserting True must fail
        with self.assertRaises(AssertionError):
            self.assertTrue(self.geofence.contains(21.0, 75.0))


if __name__ == "__main__":
    unittest.main()
