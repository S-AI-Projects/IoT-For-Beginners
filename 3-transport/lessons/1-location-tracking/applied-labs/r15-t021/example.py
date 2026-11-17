"""Geofence Membership Example (Task R15-T021).

Demonstrates inclusive rectangular boundary containment checks in Python.

IMPORTANT CONCEPT:
This is a rectangular coordinate-boundary containment model using axis-aligned
intervals in decimal degrees. It is NOT a spherical-distance model (such as Haversine,
great-circle distance, or geodesic calculations).
"""

import math
from typing import Union

# Geofence boundary limits (inclusive)
GEO_MIN_LAT = 10.0
GEO_MAX_LAT = 20.0
GEO_MIN_LON = 70.0
GEO_MAX_LON = 80.0

# Earth geographic coordinate valid limits (in decimal degrees)
EARTH_MIN_LAT = -90.0
EARTH_MAX_LAT = 90.0
EARTH_MIN_LON = -180.0
EARTH_MAX_LON = 180.0


def validate_coordinates(
    latitude: Union[int, float], longitude: Union[int, float]
) -> None:
    """Validate latitude and longitude values against Earth coordinate limits.

    Coordinates must be numeric and within valid Earth ranges:
      - Latitude: [-90.0, 90.0]
      - Longitude: [-180.0, 180.0]

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.

    Raises:
        TypeError: If latitude or longitude is not numeric (or is a boolean).
        ValueError: If latitude or longitude is outside valid ranges, NaN, or infinite.
    """
    # Reject non-numeric types and booleans (which subclass int in Python)
    if not isinstance(latitude, (int, float)) or isinstance(latitude, bool):
        raise TypeError(
            f"Latitude must be a numeric value (int or float), got {type(latitude).__name__}."
        )
    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
        raise TypeError(
            f"Longitude must be a numeric value (int or float), got {type(longitude).__name__}."
        )

    # Reject non-finite floats
    if math.isnan(latitude) or math.isinf(latitude):
        raise ValueError(f"Latitude must be a finite number, got {latitude}.")
    if math.isnan(longitude) or math.isinf(longitude):
        raise ValueError(f"Longitude must be a finite number, got {longitude}.")

    # Validate coordinate boundaries
    if not (EARTH_MIN_LAT <= latitude <= EARTH_MAX_LAT):
        raise ValueError(
            f"Invalid latitude {latitude}: must be between {EARTH_MIN_LAT} and {EARTH_MAX_LAT} degrees."
        )
    if not (EARTH_MIN_LON <= longitude <= EARTH_MAX_LON):
        raise ValueError(
            f"Invalid longitude {longitude}: must be between {EARTH_MIN_LON} and {EARTH_MAX_LON} degrees."
        )


def is_inside_geofence(
    latitude: Union[int, float], longitude: Union[int, float]
) -> bool:
    """Determine whether a (latitude, longitude) coordinate lies inside the geofence.

    Boundaries are inclusive:
      - Latitude between 10.0 and 20.0
      - Longitude between 70.0 and 80.0

    Note: This is a planar axis-aligned coordinate-boundary containment check,
    NOT a spherical-distance model.

    Args:
        latitude: Latitude coordinate in decimal degrees (-90 to 90).
        longitude: Longitude coordinate in decimal degrees (-180 to 180).

    Returns:
        True if the coordinate is within or on the boundary of the geofence, False otherwise.

    Raises:
        TypeError: If coordinates are not numeric.
        ValueError: If coordinates are outside valid Earth ranges.
    """
    validate_coordinates(latitude, longitude)
    return (GEO_MIN_LAT <= latitude <= GEO_MAX_LAT) and (
        GEO_MIN_LON <= longitude <= GEO_MAX_LON
    )


def main() -> None:
    """Run sample evaluations demonstrating geofence containment and coordinate rejection."""
    print("=" * 70)
    print("Task R15-T021: Rectangular Geofence Membership Example")
    print(
        f"Geofence Boundaries (Inclusive): Latitude [{GEO_MIN_LAT}, {GEO_MAX_LAT}], "
        f"Longitude [{GEO_MIN_LON}, {GEO_MAX_LON}]"
    )
    print("Model: Planar Coordinate Boundary Containment (NOT a spherical-distance model)")
    print("=" * 70)
    print()

    sample_coordinates = [
        (15.0, 75.0, "Required inside case (interior)"),
        (10.0, 70.0, "Required boundary case (SW corner, inclusive)"),
        (20.0, 80.0, "Boundary case (NE corner, inclusive)"),
        (21.0, 75.0, "Required outside case (latitude > 20)"),
        (15.0, 85.0, "Outside case (longitude > 80)"),
        (100.0, 75.0, "Required invalid case (latitude 100 > 90)"),
        (-95.0, 75.0, "Invalid case (latitude -95 < -90)"),
        (15.0, 185.0, "Invalid case (longitude 185 > 180)"),
        (15.0, -185.0, "Invalid case (longitude -185 < -180)"),
    ]

    print(f"{'Latitude':<10} {'Longitude':<10} {'Result':<12} {'Description'}")
    print("-" * 70)

    for lat, lon, desc in sample_coordinates:
        try:
            inside = is_inside_geofence(lat, lon)
            status = "INSIDE" if inside else "OUTSIDE"
            print(f"{lat:<10.1f} {lon:<10.1f} {status:<12} {desc}")
        except (ValueError, TypeError) as exc:
            print(f"{lat:<10.1f} {lon:<10.1f} {'REJECTED':<12} {desc} -> {exc}")

    print("-" * 70)
    print("Sample execution completed successfully.")


if __name__ == "__main__":
    main()
