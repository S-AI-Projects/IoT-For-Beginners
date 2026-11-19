"""Applied Lab R15-T026: Geofence Membership — Refactor the Teaching Example.

Demonstrates local rectangular geofence membership classification, coordinate
validation, and refactoring by extracting boundary evaluation into a single
named responsibility: is_inside_geofence(latitude, longitude, bounds).

Lesson Context:
In Lesson 3 ("Visualize location data"), GPS location coordinates are plotted on
maps using GeoJSON format.
- Coordinate order convention:
  * GeoJSON specification (RFC 7946) requires [longitude, latitude].
  * Local Python fixtures and algorithms in this lab explicitly use (latitude, longitude).
- Geofence Model:
  * Inclusive axis-aligned planar bounding box in decimal degrees.
  * Not a spherical-distance model (Haversine/geodesic) or live cloud service.
"""

from dataclasses import asdict, dataclass
import math
import sys
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class GeofenceBounds:
    """Inclusive bounding box for rectangular geofence in decimal degrees."""

    min_lat: float = 10.0
    max_lat: float = 20.0
    min_lon: float = 70.0
    max_lon: float = 80.0


@dataclass
class ClassificationResult:
    """Result of classifying a coordinate record against a geofence."""

    id: str
    latitude: Any
    longitude: Any
    status: str  # "INSIDE", "OUTSIDE", or "REJECTED"
    reason: Optional[str] = None


def get_required_fixture() -> List[Dict[str, Any]]:
    """Return the four required fixture records in (latitude, longitude) order.

    Record A: (15, 75)   -> Expected: INSIDE
    Record B: (10, 70)   -> Expected: INSIDE (Inclusive boundary)
    Record C: (21, 75)   -> Expected: OUTSIDE
    Record D: (100, 75)  -> Expected: REJECTED (Latitude > 90)
    """
    return [
        {"id": "A", "latitude": 15, "longitude": 75},
        {"id": "B", "latitude": 10, "longitude": 70},
        {"id": "C", "latitude": 21, "longitude": 75},
        {"id": "D", "latitude": 100, "longitude": 75},
    ]


# -----------------------------------------------------------------------------
# Baseline Implementation (Reference Monolith)
# -----------------------------------------------------------------------------


def classify_record_baseline(
    record: Dict[str, Any],
    bounds: Optional[GeofenceBounds] = None,
) -> ClassificationResult:
    """Baseline monolithic classifier validating and evaluating geofence membership."""
    if bounds is None:
        bounds = GeofenceBounds()

    rec_id = str(record.get("id", "UNKNOWN"))
    raw_lat = record.get("latitude")
    raw_lon = record.get("longitude")

    # Validate latitude
    if raw_lat is None:
        return ClassificationResult(
            id=rec_id, latitude=raw_lat, longitude=raw_lon, status="REJECTED", reason="Missing latitude field."
        )
    if isinstance(raw_lat, bool) or not isinstance(raw_lat, (int, float)):
        return ClassificationResult(
            id=rec_id,
            latitude=raw_lat,
            longitude=raw_lon,
            status="REJECTED",
            reason=f"Latitude must be a numeric value, got {type(raw_lat).__name__}.",
        )
    if math.isnan(raw_lat) or math.isinf(raw_lat):
        return ClassificationResult(
            id=rec_id, latitude=raw_lat, longitude=raw_lon, status="REJECTED", reason="Latitude must be finite."
        )
    if not (-90.0 <= raw_lat <= 90.0):
        return ClassificationResult(
            id=rec_id,
            latitude=raw_lat,
            longitude=raw_lon,
            status="REJECTED",
            reason=f"Latitude {raw_lat} out of valid range [-90, 90].",
        )

    # Validate longitude
    if raw_lon is None:
        return ClassificationResult(
            id=rec_id, latitude=raw_lat, longitude=raw_lon, status="REJECTED", reason="Missing longitude field."
        )
    if isinstance(raw_lon, bool) or not isinstance(raw_lon, (int, float)):
        return ClassificationResult(
            id=rec_id,
            latitude=raw_lat,
            longitude=raw_lon,
            status="REJECTED",
            reason=f"Longitude must be a numeric value, got {type(raw_lon).__name__}.",
        )
    if math.isnan(raw_lon) or math.isinf(raw_lon):
        return ClassificationResult(
            id=rec_id, latitude=raw_lat, longitude=raw_lon, status="REJECTED", reason="Longitude must be finite."
        )
    if not (-180.0 <= raw_lon <= 180.0):
        return ClassificationResult(
            id=rec_id,
            latitude=raw_lat,
            longitude=raw_lon,
            status="REJECTED",
            reason=f"Longitude {raw_lon} out of valid range [-180, 180].",
        )

    # Monolithic inline membership check
    lat_in = bounds.min_lat <= raw_lat <= bounds.max_lat
    lon_in = bounds.min_lon <= raw_lon <= bounds.max_lon

    if lat_in and lon_in:
        return ClassificationResult(
            id=rec_id, latitude=raw_lat, longitude=raw_lon, status="INSIDE", reason="Coordinate is within geofence."
        )
    else:
        return ClassificationResult(
            id=rec_id, latitude=raw_lat, longitude=raw_lon, status="OUTSIDE", reason="Coordinate is outside geofence."
        )


# -----------------------------------------------------------------------------
# Refactored Implementation (Extracted Responsibility)
# -----------------------------------------------------------------------------


def validate_coordinate_fields(
    record: Dict[str, Any],
) -> Tuple[bool, Optional[float], Optional[float], Optional[str]]:
    """Validate that record contains finite, valid numeric latitude and longitude.

    Returns:
        (is_valid, lat_float, lon_float, rejection_reason)
    """
    raw_lat = record.get("latitude")
    raw_lon = record.get("longitude")

    if raw_lat is None:
        return False, None, None, "Missing latitude field."
    if isinstance(raw_lat, bool) or not isinstance(raw_lat, (int, float)):
        return False, None, None, f"Latitude must be a numeric value, got {type(raw_lat).__name__}."
    if math.isnan(raw_lat) or math.isinf(raw_lat):
        return False, None, None, "Latitude must be finite."
    if not (-90.0 <= raw_lat <= 90.0):
        return False, None, None, f"Latitude {raw_lat} out of valid range [-90, 90]."

    if raw_lon is None:
        return False, None, None, "Missing longitude field."
    if isinstance(raw_lon, bool) or not isinstance(raw_lon, (int, float)):
        return False, None, None, f"Longitude must be a numeric value, got {type(raw_lon).__name__}."
    if math.isnan(raw_lon) or math.isinf(raw_lon):
        return False, None, None, "Longitude must be finite."
    if not (-180.0 <= raw_lon <= 180.0):
        return False, None, None, f"Longitude {raw_lon} out of valid range [-180, 180]."

    return True, float(raw_lat), float(raw_lon), None


def is_inside_geofence(
    latitude: Union[int, float],
    longitude: Union[int, float],
    bounds: GeofenceBounds,
) -> bool:
    """Determine whether a valid (latitude, longitude) coordinate lies inside the geofence.

    Extracted Responsibility:
      Pure geometric containment test against inclusive bounding box.
      Both minimum and maximum boundaries are inclusive (<=).
    """
    lat_ok = bounds.min_lat <= latitude <= bounds.max_lat
    lon_ok = bounds.min_lon <= longitude <= bounds.max_lon
    return lat_ok and lon_ok


def classify_record_refactored(
    record: Dict[str, Any],
    bounds: Optional[GeofenceBounds] = None,
) -> ClassificationResult:
    """Refactored classifier delegating boundary checking to is_inside_geofence."""
    if bounds is None:
        bounds = GeofenceBounds()

    rec_id = str(record.get("id", "UNKNOWN"))
    is_valid, lat, lon, reason = validate_coordinate_fields(record)

    if not is_valid:
        return ClassificationResult(
            id=rec_id,
            latitude=record.get("latitude"),
            longitude=record.get("longitude"),
            status="REJECTED",
            reason=reason,
        )

    # Delegate to the extracted boundary responsibility
    assert lat is not None and lon is not None
    inside = is_inside_geofence(lat, lon, bounds)

    if inside:
        return ClassificationResult(
            id=rec_id,
            latitude=lat,
            longitude=lon,
            status="INSIDE",
            reason="Coordinate is within geofence.",
        )
    else:
        return ClassificationResult(
            id=rec_id,
            latitude=lat,
            longitude=lon,
            status="OUTSIDE",
            reason="Coordinate is outside geofence.",
        )


def classify_all_baseline(
    records: List[Dict[str, Any]],
    bounds: Optional[GeofenceBounds] = None,
) -> List[ClassificationResult]:
    """Classify multiple records using baseline implementation."""
    return [classify_record_baseline(rec, bounds) for rec in records]


def classify_all_refactored(
    records: List[Dict[str, Any]],
    bounds: Optional[GeofenceBounds] = None,
) -> List[ClassificationResult]:
    """Classify multiple records using refactored implementation."""
    return [classify_record_refactored(rec, bounds) for rec in records]


def verify_equivalence(
    records: List[Dict[str, Any]],
    bounds: Optional[GeofenceBounds] = None,
) -> bool:
    """Assert that baseline and refactored classifiers return identical results.

    Raises:
        AssertionError: If any record produces a differing classification status.
    """
    baseline_results = classify_all_baseline(records, bounds)
    refactored_results = classify_all_refactored(records, bounds)

    if len(baseline_results) != len(refactored_results):
        raise AssertionError(
            f"Result count mismatch: baseline={len(baseline_results)}, refactored={len(refactored_results)}"
        )

    for b, r in zip(baseline_results, refactored_results):
        if b != r:
            differences = []
            if b.id != r.id:
                differences.append(f"id ({b.id} != {r.id})")
            if b.latitude != r.latitude:
                differences.append(f"latitude ({b.latitude} != {r.latitude})")
            if b.longitude != r.longitude:
                differences.append(f"longitude ({b.longitude} != {r.longitude})")
            if b.status != r.status:
                differences.append(f"status ({b.status} != {r.status})")
            if b.reason != r.reason:
                differences.append(f"reason ({b.reason!r} != {r.reason!r})")
            diff_str = ", ".join(differences) if differences else "attributes differ"
            raise AssertionError(
                f"Equivalence mismatch for record '{b.id}': {diff_str}. "
                f"Baseline: {b}, Refactored: {r}"
            )

    return True


def main() -> None:
    """Execute the teaching example and display baseline vs refactored equivalence."""
    print("=" * 80)
    print("Task R15-T026: Geofence Membership — Refactor Teaching Example")
    print("Context: Lesson 3-3 GPS Location Data & GeoJSON Visualization")
    print("=" * 80)
    print()

    bounds = GeofenceBounds(min_lat=10.0, max_lat=20.0, min_lon=70.0, max_lon=80.0)
    fixture = get_required_fixture()

    print("GEOFENCE DEFINITION:")
    print("-" * 80)
    print(f"  Latitude Range:  [{bounds.min_lat}, {bounds.max_lat}] (inclusive)")
    print(f"  Longitude Range: [{bounds.min_lon}, {bounds.max_lon}] (inclusive)")
    print("  Note: Coordinate order is (latitude, longitude) in local Python code.")
    print("        In GeoJSON (RFC 7946), coordinates are formatted [longitude, latitude].")
    print()

    print("INPUT FIXTURE RECORDS:")
    print("-" * 80)
    for rec in fixture:
        print(f"  Record {rec['id']}: Latitude = {rec['latitude']}, Longitude = {rec['longitude']}")
    print()

    # Run both baseline and refactored classifiers
    baseline_res = classify_all_baseline(fixture, bounds)
    refactored_res = classify_all_refactored(fixture, bounds)

    print("CLASSIFICATION RESULTS & EQUIVALENCE COMPARISON:")
    print("-" * 80)
    header = f"{'Record':<8} {'(Lat, Lon)':<18} {'Baseline':<12} {'Refactored':<12} {'Match?':<8} {'Reason'}"
    print(header)
    print("-" * 80)

    for b, r in zip(baseline_res, refactored_res):
        coord_str = f"({b.latitude}, {b.longitude})"
        match_str = "YES" if b.status == r.status else "NO"
        reason_str = r.reason or ""
        print(f"{b.id:<8} {coord_str:<18} {b.status:<12} {r.status:<12} {match_str:<8} {reason_str}")
    print()

    # Verify equivalence
    print("EQUIVALENCE PROOF:")
    print("-" * 80)
    try:
        verify_equivalence(fixture, bounds)
        print("✓ Equivalence Check PASSED: Baseline and refactored implementations return identical results.")
    except AssertionError as exc:
        print(f"✗ Equivalence Check FAILED: {exc}")
        sys.exit(1)
    print()

    print("DEMONSTRATION: Intentional Failure Detection")
    print("-" * 80)
    # Demonstrate deliberate wrong-result detection
    corrupted_records = [
        {"id": "C", "latitude": 21, "longitude": 75}  # Actual: OUTSIDE
    ]
    corrupted_expected = "INSIDE"  # Deliberately wrong assertion
    actual_status = classify_record_refactored(corrupted_records[0], bounds).status
    try:
        assert actual_status == corrupted_expected, (
            f"Deliberate check failed as expected: Record C is {actual_status}, not {corrupted_expected}."
        )
        print("✗ Corruption was NOT detected.")
    except AssertionError as exc:
        print(f"✓ Confirmed: Deliberately incorrect expected classification caught successfully:")
        print(f"  -> {exc}")
    print()

    print("EDUCATIONAL DISCLAIMER:")
    print("-" * 80)
    print("This simulation demonstrates local rectangular geofencing in decimal degrees.")
    print("It is NOT a spherical-distance model (Haversine/geodesic) and does NOT connect")
    print("to real GPS sensors, Azure Maps services, or cloud infrastructure.")
    print("=" * 80)


if __name__ == "__main__":
    main()
