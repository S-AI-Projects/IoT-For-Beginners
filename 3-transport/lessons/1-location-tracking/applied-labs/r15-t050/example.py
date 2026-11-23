"""Fictional GPS records classified with an inclusive rectangular geofence.

This is not a spherical-distance, polygon, GPS-hardware or network model.
"""
import math

RECTANGLE = {"lat_min": 10, "lat_max": 20, "lon_min": 70, "lon_max": 80}
POINTS = ((15, 75), (10, 70), (21, 75))


def classify(latitude, longitude, inclusive=True):
    """Validate lat/lon order; classify within the teaching rectangle."""
    for name, value, low, high in (("latitude", latitude, -90, 90),
                                   ("longitude", longitude, -180, 180)):
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError("invalid " + name)
    if type(inclusive) is not bool:
        raise ValueError("inclusive must be boolean")
    if inclusive:
        inside = (10 <= latitude <= 20 and 70 <= longitude <= 80)
    else:
        inside = (10 < latitude < 20 and 70 < longitude < 80)
    return "inside" if inside else "outside"


def answers():
    """Executable answers to three applied questions in README.md."""
    prediction = classify(15, 75)
    try:
        classify(100, 75)
    except ValueError as exc:
        diagnosis = "rejected: " + str(exc)
    else:
        diagnosis = "not rejected"
    boundary = classify(10, 70, inclusive=True)
    return {"predict": prediction, "diagnose": diagnosis, "boundary_policy": boundary}


def main():
    print("FICTIONAL local (latitude,longitude) geofence; inclusive rectangle")
    for lat, lon in POINTS:
        print("({},{}): {}".format(lat, lon, classify(lat, lon)))
    for name, answer in answers().items():
        print("{}: {}".format(name, answer))
    print("Not a spherical-distance model or live GPS observation.")


if __name__ == "__main__":
    main()
