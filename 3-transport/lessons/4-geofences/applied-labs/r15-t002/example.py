"""Geofence membership — inclusive rectangular teaching geofence (R15-T002).

Standard library only. A SIMULATION: it does not use GPS hardware, maps,
or cloud geofencing APIs (such as Azure Maps).

IMPORTANT NOTE ON GEODESICS:
This implementation uses an inclusive planar bounding-box model with latitude
range [10, 20] and longitude range [70, 80]. It is an illustrative educational
fixture and is NOT a spherical-distance (Haversine/geodesic) or ellipsoidal model.

Rules:
  - Latitude must be in [-90, 90]; Longitude must be in [-180, 180].
  - Coordinates outside valid spherical range (e.g., latitude 100) are rejected with ValueError.
  - Geofence bounds:
      Latitude: [10, 20] inclusive
      Longitude: [70, 80] inclusive
  - Points with 10 <= lat <= 20 and 70 <= lon <= 80 are "inside".
  - Other valid points are "outside".
"""

# Geofence boundary definitions
LAT_MIN = 10.0
LAT_MAX = 20.0
LON_MIN = 70.0
LON_MAX = 80.0


def validate_coordinates(lat, lon):
    """Validates that lat and lon are numeric and within real-world spherical ranges."""
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        raise TypeError("Latitude must be a numeric value")
    if not isinstance(lon, (int, float)) or isinstance(lon, bool):
        raise TypeError("Longitude must be a numeric value")
    if lat < -90.0 or lat > 90.0:
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if lon < -180.0 or lon > 180.0:
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")


def classify_point(lat, lon):
    """Classifies a coordinate record as 'inside' or 'outside'.

    Raises ValueError if coordinates are outside valid spherical limits.
    """
    validate_coordinates(lat, lon)

    # Inclusive boundary check
    if LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX:
        return "inside"
    return "outside"


def classify_records(records):
    """Classifies a list of (lat, lon) coordinate tuples."""
    return [classify_point(lat, lon) for lat, lon in records]


if __name__ == "__main__":
    test_points = [(15, 75), (10, 70), (21, 75)]
    for pt in test_points:
        print(f"Point {pt}: {classify_point(*pt)}")
