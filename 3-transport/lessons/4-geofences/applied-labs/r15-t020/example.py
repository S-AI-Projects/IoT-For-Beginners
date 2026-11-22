"""
Geofence Membership — Scenario Assessment (R15-T020)

Lesson reference: 3-transport/lessons/4-geofences/README.md
Concept: In commercial vehicle tracking and logistics, geofences trigger alerts when assets
cross spatial perimeters. This lab implements an inclusive rectangular teaching geofence
and addresses three scenario-based applied assessment questions.

Important Model Note:
This rectangular bounding box is an introductory planar teaching model. It does NOT
implement spherical distance formulas (e.g. Haversine) or geodesics on Earth's ellipsoid.

Geofence Boundaries:
- Latitude: [10.0, 20.0] (inclusive)
- Longitude: [70.0, 80.0] (inclusive)

Valid Geographic Coordinate Constraints:
- -90.0 <= latitude <= 90.0
- -180.0 <= longitude <= 180.0
"""

from typing import Tuple


class RectangularTeachingGeofence:
    def __init__(
        self,
        min_lat: float = 10.0,
        max_lat: float = 20.0,
        min_lon: float = 70.0,
        max_lon: float = 80.0,
        inclusive: bool = True,
    ):
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.inclusive = inclusive

    def validate_coordinates(self, lat: float, lon: float):
        """Ensures coordinate values represent valid geographic points on Earth."""
        if isinstance(lat, bool) or isinstance(lon, bool) or not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise TypeError("Latitude and Longitude must be numeric values")
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Invalid latitude {lat}: must be between -90 and 90 degrees")
        if not (-180.0 <= lon <= 180.0):
            raise ValueError(f"Invalid longitude {lon}: must be between -180 and 180 degrees")

    def contains(self, lat: float, lon: float) -> bool:
        """
        Classifies coordinate record.
        Returns True if inside or on boundary (under inclusive policy), False if outside.
        Raises ValueError if coordinate is geographically invalid.
        """
        self.validate_coordinates(lat, lon)

        if self.inclusive:
            lat_inside = self.min_lat <= lat <= self.max_lat
            lon_inside = self.min_lon <= lon <= self.max_lon
        else:
            lat_inside = self.min_lat < lat < self.max_lat
            lon_inside = self.min_lon < lon < self.max_lon

        return lat_inside and lon_inside


# --- Applied Scenario Questions ---
def answer_question_1_predict_output(lat: float = 20.0, lon: float = 80.0) -> Tuple[bool, str]:
    """
    Question 1: Predict an output for coordinate (20.0, 80.0).
    Rationale: Under an inclusive rectangular boundary policy [10, 20] x [70, 80],
    both the maximum latitude (20.0) and maximum longitude (80.0) are classified as INSIDE.
    """
    geofence = RectangularTeachingGeofence()
    is_inside = geofence.contains(lat, lon)
    rationale = f"Coordinate ({lat}, {lon}) lies on the upper corner boundary; evaluated as {'INSIDE' if is_inside else 'OUTSIDE'}."
    return is_inside, rationale


def answer_question_2_diagnose_failure(lat: float = 100.0, lon: float = 75.0) -> Tuple[bool, str]:
    """
    Question 2: Diagnose why coordinate (100, 75) causes an execution failure.
    Rationale: Earth's coordinate reference system defines latitude between -90 and +90 degrees.
    A latitude of 100 exceeds polar limits and represents sensor corruption or invalid input.
    """
    geofence = RectangularTeachingGeofence()
    try:
        geofence.contains(lat, lon)
        return False, "Failed to reject invalid latitude"
    except ValueError as e:
        return True, f"Correctly diagnosed rejection: {e}"


def answer_question_3_choose_boundary_policy(boundary_point: Tuple[float, float] = (10.0, 70.0)) -> Tuple[str, str]:
    """
    Question 3: Choose and justify boundary policy (inclusive vs exclusive) for depot tracking.
    Rationale: In asset tracking, GPS drift along depot fences can cause rapid state oscillations
    ('border chattering'). An inclusive policy classifies perimeter fences as INSIDE to avoid
    premature departure alerts.
    """
    inc_fence = RectangularTeachingGeofence(inclusive=True)
    exc_fence = RectangularTeachingGeofence(inclusive=False)

    lat, lon = boundary_point
    inc_res = inc_fence.contains(lat, lon)
    exc_res = exc_fence.contains(lat, lon)

    choice = "INCLUSIVE"
    rationale = (
        f"Point ({lat}, {lon}) is {inc_res} with inclusive policy and {exc_res} with exclusive policy. "
        "Inclusive policy prevents false exit alerts caused by GPS jitter on perimeter boundaries."
    )
    return choice, rationale


def run_demo():
    geofence = RectangularTeachingGeofence()
    test_points = [
        (15.0, 75.0),  # interior point
        (10.0, 70.0),  # boundary point
        (21.0, 75.0),  # outside point
    ]
    print("Classifying local coordinate records:")
    for lat, lon in test_points:
        inside = geofence.contains(lat, lon)
        print(f"  Point ({lat}, {lon}) -> {'INSIDE' if inside else 'OUTSIDE'}")

    try:
        geofence.contains(100.0, 75.0)
    except ValueError as e:
        print(f"  Point (100.0, 75.0) -> REJECTED ({e})")

    q1_res, q1_rat = answer_question_1_predict_output()
    print(f"\nQ1 Predict Output: {q1_res} -> {q1_rat}")
    q2_res, q2_rat = answer_question_2_diagnose_failure()
    print(f"Q2 Diagnose Failure: {q2_res} -> {q2_rat}")
    q3_res, q3_rat = answer_question_3_choose_boundary_policy()
    print(f"Q3 Boundary Policy: {q3_res} -> {q3_rat}")


if __name__ == "__main__":
    run_demo()
