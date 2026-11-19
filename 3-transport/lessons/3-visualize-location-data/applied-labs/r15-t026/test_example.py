"""Unit tests for Geofence Membership — Refactor Teaching Example (Task R15-T026).

Verifies boundary evaluation, coordinate validation, baseline and refactored
equivalence, rejection of invalid coordinates, and deliberate failure detection.
"""

import math
import os
import sys
import unittest

# Ensure the module directory is accessible for direct execution or discovery
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (  # noqa: E402
    ClassificationResult,
    GeofenceBounds,
    classify_all_baseline,
    classify_all_refactored,
    classify_record_baseline,
    classify_record_refactored,
    get_required_fixture,
    is_inside_geofence,
    validate_coordinate_fields,
    verify_equivalence,
)


class TestGeofenceMembershipRefactor(unittest.TestCase):
    """Test suite for rectangular geofence membership and refactoring equivalence."""

    def setUp(self) -> None:
        """Set up standard inclusive geofence bounds."""
        self.bounds = GeofenceBounds(min_lat=10.0, max_lat=20.0, min_lon=70.0, max_lon=80.0)

    # 1. Required four fixture records on refactored
    def test_required_fixture_records(self) -> None:
        """Verify the exact required 4-record fixture against refactored classifier."""
        fixture = get_required_fixture()
        results = classify_all_refactored(fixture, self.bounds)

        self.assertEqual(len(results), 4)

        # Record A: (15, 75) -> INSIDE
        self.assertEqual(results[0].id, "A")
        self.assertEqual(results[0].status, "INSIDE")

        # Record B: (10, 70) -> INSIDE (Inclusive boundary)
        self.assertEqual(results[1].id, "B")
        self.assertEqual(results[1].status, "INSIDE")

        # Record C: (21, 75) -> OUTSIDE
        self.assertEqual(results[2].id, "C")
        self.assertEqual(results[2].status, "OUTSIDE")

        # Record D: (100, 75) -> REJECTED (Latitude > 90)
        self.assertEqual(results[3].id, "D")
        self.assertEqual(results[3].status, "REJECTED")

    # 1b. Required four fixture records on baseline
    def test_required_fixture_records_baseline(self) -> None:
        """Verify the exact required 4-record fixture against baseline classifier."""
        fixture = get_required_fixture()
        results = classify_all_baseline(fixture, self.bounds)

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].status, "INSIDE")
        self.assertEqual(results[1].status, "INSIDE")
        self.assertEqual(results[2].status, "OUTSIDE")
        self.assertEqual(results[3].status, "REJECTED")

    # 2. Baseline and refactored equivalence across the complete fixture
    def test_baseline_refactored_equivalence_on_fixture(self) -> None:
        """Verify that baseline and refactored implementations return identical results."""
        fixture = get_required_fixture()
        self.assertTrue(verify_equivalence(fixture, self.bounds))

        baseline_res = classify_all_baseline(fixture, self.bounds)
        refactored_res = classify_all_refactored(fixture, self.bounds)

        for b, r in zip(baseline_res, refactored_res):
            self.assertEqual(b.id, r.id)
            self.assertEqual(b.status, r.status)
            self.assertEqual(b.latitude, r.latitude)
            self.assertEqual(b.longitude, r.longitude)

    # 3. Inclusive minimum and maximum boundaries
    def test_inclusive_boundaries(self) -> None:
        """Verify that coordinates exactly on minimum and maximum boundaries are classified INSIDE."""
        # Minimum boundary corner
        min_corner = {"id": "min-corner", "latitude": 10.0, "longitude": 70.0}
        self.assertEqual(classify_record_refactored(min_corner, self.bounds).status, "INSIDE")
        self.assertEqual(classify_record_baseline(min_corner, self.bounds).status, "INSIDE")

        # Maximum boundary corner
        max_corner = {"id": "max-corner", "latitude": 20.0, "longitude": 80.0}
        self.assertEqual(classify_record_refactored(max_corner, self.bounds).status, "INSIDE")
        self.assertEqual(classify_record_baseline(max_corner, self.bounds).status, "INSIDE")

        # Other corners
        top_left = {"id": "top-left", "latitude": 20.0, "longitude": 70.0}
        bottom_right = {"id": "bottom-right", "latitude": 10.0, "longitude": 80.0}
        self.assertEqual(classify_record_refactored(top_left, self.bounds).status, "INSIDE")
        self.assertEqual(classify_record_refactored(bottom_right, self.bounds).status, "INSIDE")

    # 4. Just outside each boundary
    def test_just_outside_each_boundary(self) -> None:
        """Verify coordinates immediately outside each of the four rectangular boundaries."""
        eps = 1e-4
        just_below_min_lat = {"id": "O1", "latitude": 10.0 - eps, "longitude": 75.0}
        just_above_max_lat = {"id": "O2", "latitude": 20.0 + eps, "longitude": 75.0}
        just_below_min_lon = {"id": "O3", "latitude": 15.0, "longitude": 70.0 - eps}
        just_above_max_lon = {"id": "O4", "latitude": 15.0, "longitude": 80.0 + eps}

        for rec in (just_below_min_lat, just_above_max_lat, just_below_min_lon, just_above_max_lon):
            res = classify_record_refactored(rec, self.bounds)
            self.assertEqual(res.status, "OUTSIDE", f"Expected OUTSIDE for {rec}, got {res.status}")
            self.assertEqual(classify_record_baseline(rec, self.bounds).status, "OUTSIDE")

    # 5. Invalid latitude out of valid range [-90, 90]
    def test_invalid_latitude_range(self) -> None:
        """Verify that latitudes exceeding [-90, 90] are REJECTED, not classified OUTSIDE."""
        too_high = {"id": "LAT-HIGH", "latitude": 90.001, "longitude": 75.0}
        too_low = {"id": "LAT-LOW", "latitude": -90.001, "longitude": 75.0}
        extreme = {"id": "LAT-100", "latitude": 100.0, "longitude": 75.0}

        for rec in (too_high, too_low, extreme):
            res = classify_record_refactored(rec, self.bounds)
            self.assertEqual(res.status, "REJECTED", f"Expected REJECTED for {rec}, got {res.status}")
            self.assertIn("range", res.reason.lower())
            self.assertEqual(classify_record_baseline(rec, self.bounds).status, "REJECTED")

    # 6. Invalid longitude out of valid range [-180, 180]
    def test_invalid_longitude_range(self) -> None:
        """Verify that longitudes exceeding [-180, 180] are REJECTED, not classified OUTSIDE."""
        too_high = {"id": "LON-HIGH", "latitude": 15.0, "longitude": 180.001}
        too_low = {"id": "LON-LOW", "latitude": 15.0, "longitude": -180.001}
        extreme = {"id": "LON-200", "latitude": 15.0, "longitude": 200.0}

        for rec in (too_high, too_low, extreme):
            res = classify_record_refactored(rec, self.bounds)
            self.assertEqual(res.status, "REJECTED", f"Expected REJECTED for {rec}, got {res.status}")
            self.assertIn("range", res.reason.lower())
            self.assertEqual(classify_record_baseline(rec, self.bounds).status, "REJECTED")

    # 7. Booleans rejected as numeric values
    def test_booleans_rejected(self) -> None:
        """Verify that booleans (subclasses of int) are rejected for latitude and longitude."""
        bool_lat_true = {"id": "B1", "latitude": True, "longitude": 75.0}
        bool_lat_false = {"id": "B2", "latitude": False, "longitude": 75.0}
        bool_lon_true = {"id": "B3", "latitude": 15.0, "longitude": True}
        bool_lon_false = {"id": "B4", "latitude": 15.0, "longitude": False}

        for rec in (bool_lat_true, bool_lat_false, bool_lon_true, bool_lon_false):
            res = classify_record_refactored(rec, self.bounds)
            self.assertEqual(res.status, "REJECTED")
            self.assertIn("numeric", res.reason.lower())
            self.assertEqual(classify_record_baseline(rec, self.bounds).status, "REJECTED")

    # 8. String coordinates rejected (no silent conversion)
    def test_string_coordinates_rejected(self) -> None:
        """Verify that string representations are not silently converted to floats."""
        str_lat = {"id": "S1", "latitude": "15", "longitude": 75.0}
        str_lon = {"id": "S2", "latitude": 15.0, "longitude": "75"}
        alpha_lat = {"id": "S3", "latitude": "north", "longitude": 75.0}

        for rec in (str_lat, str_lon, alpha_lat):
            res = classify_record_refactored(rec, self.bounds)
            self.assertEqual(res.status, "REJECTED")
            self.assertEqual(classify_record_baseline(rec, self.bounds).status, "REJECTED")

    # 9. Missing coordinate fields
    def test_missing_coordinate_fields(self) -> None:
        """Verify that records with missing latitude or longitude are REJECTED."""
        missing_lat = {"id": "M1", "longitude": 75.0}
        missing_lon = {"id": "M2", "latitude": 15.0}
        empty_rec = {"id": "M3"}

        for rec in (missing_lat, missing_lon, empty_rec):
            res = classify_record_refactored(rec, self.bounds)
            self.assertEqual(res.status, "REJECTED")
            self.assertIn("missing", res.reason.lower())
            self.assertEqual(classify_record_baseline(rec, self.bounds).status, "REJECTED")

    # 10. Non-finite numbers rejected (NaN and Infinity)
    def test_non_finite_numbers_rejected(self) -> None:
        """Verify that NaN and Infinity values are rejected."""
        nan_lat = {"id": "N1", "latitude": float("nan"), "longitude": 75.0}
        inf_lat = {"id": "N2", "latitude": float("inf"), "longitude": 75.0}
        neg_inf_lon = {"id": "N3", "latitude": 15.0, "longitude": float("-inf")}

        for rec in (nan_lat, inf_lat, neg_inf_lon):
            res = classify_record_refactored(rec, self.bounds)
            self.assertEqual(res.status, "REJECTED")
            self.assertIn("finite", res.reason.lower())
            self.assertEqual(classify_record_baseline(rec, self.bounds).status, "REJECTED")

    # 11. Invalid records never classified as OUTSIDE
    def test_invalid_records_never_classified_outside(self) -> None:
        """Verify that invalid coordinates cannot be misinterpreted as OUTSIDE geofence."""
        invalid_cases = [
            {"id": "INV-1", "latitude": 150.0, "longitude": 75.0},
            {"id": "INV-2", "latitude": -100.0, "longitude": 75.0},
            {"id": "INV-3", "latitude": 15.0, "longitude": 250.0},
            {"id": "INV-4", "latitude": None, "longitude": 75.0},
            {"id": "INV-5", "latitude": "invalid", "longitude": 75.0},
        ]
        for rec in invalid_cases:
            res = classify_record_refactored(rec, self.bounds)
            self.assertNotEqual(res.status, "OUTSIDE")
            self.assertEqual(res.status, "REJECTED")

    # 12. Extracted is_inside_geofence responsibility tested directly
    def test_extracted_is_inside_geofence_directly(self) -> None:
        """Test the extracted is_inside_geofence function independently."""
        # Inside
        self.assertTrue(is_inside_geofence(15.0, 75.0, self.bounds))
        # Exact corners
        self.assertTrue(is_inside_geofence(10.0, 70.0, self.bounds))
        self.assertTrue(is_inside_geofence(20.0, 80.0, self.bounds))
        self.assertTrue(is_inside_geofence(10.0, 80.0, self.bounds))
        self.assertTrue(is_inside_geofence(20.0, 70.0, self.bounds))
        # Outside
        self.assertFalse(is_inside_geofence(21.0, 75.0, self.bounds))
        self.assertFalse(is_inside_geofence(9.9, 75.0, self.bounds))
        self.assertFalse(is_inside_geofence(15.0, 69.9, self.bounds))
        self.assertFalse(is_inside_geofence(15.0, 80.1, self.bounds))

    # 13. Record identity preserved
    def test_record_identity_preserved(self) -> None:
        """Verify that record IDs are strictly preserved in the classification results."""
        records = [
            {"id": "TRUCK-42", "latitude": 15.0, "longitude": 75.0},
            {"id": "VESSEL-09", "latitude": 21.0, "longitude": 75.0},
            {"id": "DRONE-99", "latitude": 100.0, "longitude": 75.0},
        ]
        results = classify_all_refactored(records, self.bounds)
        self.assertEqual(results[0].id, "TRUCK-42")
        self.assertEqual(results[1].id, "VESSEL-09")
        self.assertEqual(results[2].id, "DRONE-99")

    # 14. Valid zero coordinates accepted
    def test_valid_zero_coordinates_accepted(self) -> None:
        """Verify that 0.0 is treated as a valid numeric coordinate, not missing or falsy."""
        equator_meridian_bounds = GeofenceBounds(min_lat=-5.0, max_lat=5.0, min_lon=-5.0, max_lon=5.0)
        zero_record = {"id": "NULL-ISLAND", "latitude": 0.0, "longitude": 0.0}
        res = classify_record_refactored(zero_record, equator_meridian_bounds)
        self.assertEqual(res.status, "INSIDE")

    # 15. Custom geofence bounds parameterization
    def test_custom_bounds_parameterization(self) -> None:
        """Verify that geofence bounds can be configured with custom rectangular ranges."""
        arctic_bounds = GeofenceBounds(min_lat=60.0, max_lat=80.0, min_lon=-30.0, max_lon=10.0)
        point_in = {"id": "ARCTIC-IN", "latitude": 70.0, "longitude": -10.0}
        point_out = {"id": "ARCTIC-OUT", "latitude": 50.0, "longitude": -10.0}

        self.assertEqual(classify_record_refactored(point_in, arctic_bounds).status, "INSIDE")
        self.assertEqual(classify_record_refactored(point_out, arctic_bounds).status, "OUTSIDE")

    # 15. Deliberate wrong-result failure demonstration
    def test_deliberate_wrong_result_failure_caught(self) -> None:
        """Demonstrate that an intentional wrong expectation causes an AssertionError."""
        record_c = {"id": "C", "latitude": 21.0, "longitude": 75.0}
        actual_result = classify_record_refactored(record_c, self.bounds)

        # Record C is actually OUTSIDE. Asserting INSIDE must raise AssertionError.
        deliberate_wrong_expected = "INSIDE"

        with self.assertRaises(AssertionError) as ctx:
            self.assertEqual(
                actual_result.status,
                deliberate_wrong_expected,
                "Deliberate test experiment: Record C should be OUTSIDE, not INSIDE.",
            )
        self.assertIn("OUTSIDE", str(ctx.exception))
        self.assertIn("INSIDE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
