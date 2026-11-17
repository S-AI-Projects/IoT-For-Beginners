"""Unit tests for Geofence Membership Example (Task R15-T021).

Verifies inclusive rectangular geofence membership and coordinate validation
using Python's standard library unittest framework.
"""

import os
import sys
import unittest

# Ensure the module directory is accessible for direct execution or discovery
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import is_inside_geofence, validate_coordinates  # noqa: E402


class TestGeofenceMembership(unittest.TestCase):
    """Test suite for rectangular geofence membership and boundary conditions."""

    # 1. Normal inside coordinate
    def test_normal_inside_coordinate(self) -> None:
        """Test points clearly inside the geofence."""
        # Required sample point: (15, 75) -> inside
        self.assertTrue(
            is_inside_geofence(15.0, 75.0),
            "Coordinate (15, 75) should be inside the geofence.",
        )
        self.assertTrue(
            is_inside_geofence(12.5, 72.5),
            "Interior coordinate (12.5, 72.5) should be inside the geofence.",
        )
        self.assertTrue(
            is_inside_geofence(18.0, 78.0),
            "Interior coordinate (18.0, 78.0) should be inside the geofence.",
        )

    # 2. Required inclusive boundary coordinate
    def test_inclusive_boundary_coordinates(self) -> None:
        """Test that points on boundaries and corners are treated as inside (inclusive)."""
        # Required sample point: (10, 70) -> inside (SW corner)
        self.assertTrue(
            is_inside_geofence(10.0, 70.0),
            "Corner coordinate (10, 70) should be inside (inclusive boundary).",
        )
        # Remaining three corners
        self.assertTrue(
            is_inside_geofence(20.0, 80.0),
            "Corner coordinate (20, 80) should be inside (NE corner).",
        )
        self.assertTrue(
            is_inside_geofence(10.0, 80.0),
            "Corner coordinate (10, 80) should be inside (SE corner).",
        )
        self.assertTrue(
            is_inside_geofence(20.0, 70.0),
            "Corner coordinate (20, 70) should be inside (NW corner).",
        )
        # Edges
        self.assertTrue(
            is_inside_geofence(15.0, 70.0),
            "West edge coordinate (15, 70) should be inside.",
        )
        self.assertTrue(
            is_inside_geofence(15.0, 80.0),
            "East edge coordinate (15, 80) should be inside.",
        )
        self.assertTrue(
            is_inside_geofence(10.0, 75.0),
            "South edge coordinate (10, 75) should be inside.",
        )
        self.assertTrue(
            is_inside_geofence(20.0, 75.0),
            "North edge coordinate (20, 75) should be inside.",
        )

    # 3. Outside coordinate
    def test_outside_coordinates(self) -> None:
        """Test points located outside the geofence."""
        # Required sample point: (21, 75) -> outside
        self.assertFalse(
            is_inside_geofence(21.0, 75.0),
            "Coordinate (21, 75) is north of latitude 20 and should be outside.",
        )
        # Points just outside each edge
        self.assertFalse(
            is_inside_geofence(9.9999, 75.0),
            "Coordinate south of latitude 10 should be outside.",
        )
        self.assertFalse(
            is_inside_geofence(20.0001, 75.0),
            "Coordinate north of latitude 20 should be outside.",
        )
        self.assertFalse(
            is_inside_geofence(15.0, 69.9999),
            "Coordinate west of longitude 70 should be outside.",
        )
        self.assertFalse(
            is_inside_geofence(15.0, 80.0001),
            "Coordinate east of longitude 80 should be outside.",
        )
        # Completely distant valid coordinate
        self.assertFalse(
            is_inside_geofence(0.0, 0.0),
            "Null Island (0, 0) should be outside.",
        )

    # 4. Invalid latitude 100
    def test_invalid_latitude_100(self) -> None:
        """Test that latitude 100 is rejected with a ValueError."""
        with self.assertRaises(ValueError) as context:
            is_inside_geofence(100.0, 75.0)
        self.assertIn("latitude", str(context.exception).lower())

    # 5. Invalid latitude below -90
    def test_invalid_latitude_below_minus_90(self) -> None:
        """Test that latitudes less than -90 are rejected with a ValueError."""
        with self.assertRaises(ValueError):
            is_inside_geofence(-90.1, 75.0)
        with self.assertRaises(ValueError):
            is_inside_geofence(-150.0, 75.0)

    # 6. Invalid longitude above 180
    def test_invalid_longitude_above_180(self) -> None:
        """Test that longitudes greater than 180 are rejected with a ValueError."""
        with self.assertRaises(ValueError) as context:
            is_inside_geofence(15.0, 180.1)
        self.assertIn("longitude", str(context.exception).lower())
        with self.assertRaises(ValueError):
            is_inside_geofence(15.0, 200.0)

    # 7. Invalid longitude below -180
    def test_invalid_longitude_below_minus_180(self) -> None:
        """Test that longitudes less than -180 are rejected with a ValueError."""
        with self.assertRaises(ValueError):
            is_inside_geofence(15.0, -180.1)
        with self.assertRaises(ValueError):
            is_inside_geofence(15.0, -250.0)

    # 8. Any other useful validation cases
    def test_valid_earth_extreme_coordinates(self) -> None:
        """Test that extreme valid Earth coordinates do not raise ValueError."""
        # Poles and antimeridian extremes should validate without error
        try:
            validate_coordinates(90.0, 180.0)
            validate_coordinates(-90.0, -180.0)
            validate_coordinates(0.0, 0.0)
        except (ValueError, TypeError) as exc:
            self.fail(f"Valid extreme coordinates raised unexpected error: {exc}")

    def test_non_numeric_and_special_values(self) -> None:
        """Test rejection of non-numeric types, booleans, NaN, and Inf."""
        # Non-numeric string inputs
        with self.assertRaises(TypeError):
            is_inside_geofence("15.0", 75.0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            is_inside_geofence(15.0, "75.0")  # type: ignore[arg-type]

        # None values
        with self.assertRaises(TypeError):
            is_inside_geofence(None, 75.0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            is_inside_geofence(15.0, None)  # type: ignore[arg-type]

        # Boolean values (subclass of int in Python, should be rejected)
        with self.assertRaises(TypeError):
            is_inside_geofence(True, 75.0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            is_inside_geofence(15.0, False)  # type: ignore[arg-type]

        # NaN and Infinity
        with self.assertRaises(ValueError):
            is_inside_geofence(float("nan"), 75.0)
        with self.assertRaises(ValueError):
            is_inside_geofence(15.0, float("nan"))
        with self.assertRaises(ValueError):
            is_inside_geofence(float("inf"), 75.0)
        with self.assertRaises(ValueError):
            is_inside_geofence(15.0, float("-inf"))


if __name__ == "__main__":
    unittest.main()
