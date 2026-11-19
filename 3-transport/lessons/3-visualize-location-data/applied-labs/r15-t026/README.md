# Applied Lab R15-T026: Geofence Membership — Refactor the Teaching Example

This applied lab demonstrates how to evaluate GPS location coordinates against an inclusive rectangular geofence, validate geographic inputs, and refactor monolithic classification logic by extracting a dedicated boundary-checking responsibility: `is_inside_geofence(latitude, longitude, bounds)`.

> ⚠️ **Educational Simulation Disclaimer**
>
> This lab is a **local Python simulation** using standard library components and in-memory sample records. It does **not** connect to real GPS hardware, Azure Maps services, Azure Storage, or cloud backends. The geofence model is an axis-aligned planar bounding box in decimal degrees, **not** a spherical-distance model (such as Haversine or geodesic formulas).

---

## Lesson Context: GPS Location Data & GeoJSON

In [Lesson 3: Visualize location data](../../README.md), IoT location coordinates captured from GPS sensors are visualized on web maps using GeoJSON layers.

### Critical Coordinate Convention Distinction

When working with spatial data across web mapping tools and Python code, coordinate ordering differences must be explicitly addressed:

- **GeoJSON Format (RFC 7946):** Specifies coordinates in **`[longitude, latitude]`** order (e.g. `[-122.26473, 47.73444]`), consistent with Cartesian `(x, y)` mathematics where longitude represents the horizontal x-axis and latitude represents the vertical y-axis.
- **Local Python Fixtures & Classical Navigation:** Geodesic and navigation conventions historically state coordinates as **`(latitude, longitude)`** (e.g. `(15, 75)`).

This applied lab explicitly operates on local Python records in **`(latitude, longitude)`** order to teach coordinate validation and planar boundary filtering before coordinates are formatted into GeoJSON structures for map rendering.

---

## Geofence Contract & Requirements

The lab enforces an inclusive rectangular bounding box defined in decimal degrees:

- **Minimum Latitude:** 10.0
- **Maximum Latitude:** 20.0
- **Minimum Longitude:** 70.0
- **Maximum Longitude:** 80.0

### Validation Rules

1. **Inclusive Boundaries:** Both minimum and maximum edges are inclusive (`10.0 <= latitude <= 20.0` and `70.0 <= longitude <= 80.0`).
2. **Valid Coordinate Ranges:**
   - Latitude must lie in `[-90.0, 90.0]`.
   - Longitude must lie in `[-180.0, 180.0]`.
3. **Strict Type Safety:**
   - Coordinates must be finite numeric values (`int` or `float`).
   - Booleans (which inherit from `int` in Python) are strictly rejected.
   - Strings (even numeric strings like `"15"`), `None`, and missing fields are rejected without silent type casting.
   - Non-finite numbers (`NaN`, `Infinity`, `-Infinity`) are rejected.
4. **Rejection vs. Outside:** Malformed or out-of-range coordinates are classified as `REJECTED`, never misclassified as `OUTSIDE`.
5. **Identity Preservation:** Each result retains the original input record `id`.

### Required Fixture

| Record | Latitude | Longitude | Expected Outcome | Classification Reason |
| :---: | :---: | :---: | :---: | :--- |
| **A** | 15 | 75 | **INSIDE** | Within latitude [10, 20] and longitude [70, 80] |
| **B** | 10 | 70 | **INSIDE** | Exactly on minimum boundary corner (inclusive) |
| **C** | 21 | 75 | **OUTSIDE** | Latitude 21 exceeds maximum boundary 20 |
| **D** | 100 | 75 | **REJECTED** | Latitude 100 exceeds valid geographic range [-90, 90] |

---

## Baseline vs. Refactored Architecture

This exercise demonstrates refactoring a monolithic implementation into clean, single-responsibility components while preserving exact behavioral equivalence.

### Baseline Monolith (`classify_record_baseline`)
The baseline implementation performs field extraction, type checking, range validation, and boundary evaluation within a single monolithic function. While functional, mixing validation concerns with geometric boundary logic impairs testability and reusability.

### Refactored Structure (`classify_record_refactored`)
The refactored design separates concerns into two distinct responsibilities:

1. **Validation Responsibility (`validate_coordinate_fields`):**
   Extracts and validates field presence, numeric types, finiteness, and geographic ranges `[-90, 90]` and `[-180, 180]`.
2. **Extracted Boundary Responsibility (`is_inside_geofence`):**
   ```python
   def is_inside_geofence(
       latitude: Union[int, float],
       longitude: Union[int, float],
       bounds: GeofenceBounds,
   ) -> bool:
       lat_ok = bounds.min_lat <= latitude <= bounds.max_lat
       lon_ok = bounds.min_lon <= longitude <= bounds.max_lon
       return lat_ok and lon_ok
   ```
   Pure geometric function that evaluates whether valid coordinates satisfy inclusive bounding box constraints.

### Equivalence Guarantee
The reference baseline function is maintained alongside the refactored code. The verification function `verify_equivalence()` asserts that for any dataset, both implementations produce identical `ClassificationResult` outputs for every record.

---

## Prerequisites

* **Python 3.x**
* **Python Standard Library only** (no third-party GIS or math packages required).

---

## Running the Example

Execute the teaching example from the repository root:

```bash
python3 3-transport/lessons/3-visualize-location-data/applied-labs/r15-t026/example.py
```

### Expected Output

```output
================================================================================
Task R15-T026: Geofence Membership — Refactor Teaching Example
Context: Lesson 3-3 GPS Location Data & GeoJSON Visualization
================================================================================

GEOFENCE DEFINITION:
--------------------------------------------------------------------------------
  Latitude Range:  [10.0, 20.0] (inclusive)
  Longitude Range: [70.0, 80.0] (inclusive)
  Note: Coordinate order is (latitude, longitude) in local Python code.
        In GeoJSON (RFC 7946), coordinates are formatted [longitude, latitude].

INPUT FIXTURE RECORDS:
--------------------------------------------------------------------------------
  Record A: Latitude = 15, Longitude = 75
  Record B: Latitude = 10, Longitude = 70
  Record C: Latitude = 21, Longitude = 75
  Record D: Latitude = 100, Longitude = 75

CLASSIFICATION RESULTS & EQUIVALENCE COMPARISON:
--------------------------------------------------------------------------------
Record   (Lat, Lon)         Baseline     Refactored   Match?   Reason
--------------------------------------------------------------------------------
A        (15, 75)           INSIDE       INSIDE       YES      Coordinate is within geofence.
B        (10, 70)           INSIDE       INSIDE       YES      Coordinate is within geofence.
C        (21, 75)           OUTSIDE      OUTSIDE      YES      Coordinate is outside geofence.
D        (100, 75)          REJECTED     REJECTED     YES      Latitude 100 out of valid range [-90, 90].

EQUIVALENCE PROOF:
--------------------------------------------------------------------------------
✓ Equivalence Check PASSED: Baseline and refactored implementations return identical results.

DEMONSTRATION: Intentional Failure Detection
--------------------------------------------------------------------------------
✓ Confirmed: Deliberately incorrect expected classification caught successfully:
  -> Deliberate check failed as expected: Record C is OUTSIDE, not INSIDE.

EDUCATIONAL DISCLAIMER:
--------------------------------------------------------------------------------
This simulation demonstrates local rectangular geofencing in decimal degrees.
It is NOT a spherical-distance model (Haversine/geodesic) and does NOT connect
to real GPS sensors, Azure Maps services, or cloud infrastructure.
================================================================================
```

---

## Running the Unit Tests

Execute test discovery using Python's standard `unittest` framework:

```bash
python3 -m unittest discover -s 3-transport/lessons/3-visualize-location-data/applied-labs/r15-t026 -p "test_*.py"
```

Run with verbose output:

```bash
python3 -m unittest discover -s 3-transport/lessons/3-visualize-location-data/applied-labs/r15-t026 -p "test_*.py" -v
```

### Expected Test Output

```output
Ran 17 tests in 0.002s

OK
```

---

## Limitations

1. **Planar Bounding Box:** Assumes a flat rectangular coordinate system in decimal degrees. Does not compute geodesic distances, Haversine arc lengths, or account for Earth curvature.
2. **No Hardware or Cloud Map Integration:** Does not communicate with physical GPS receivers (such as NMEA streams via UART/USB) or cloud mapping APIs (such as Azure Maps Web SDK).
3. **Simple Geometries:** Models axis-aligned rectangles; complex arbitrary polygons (such as convex hulls or GeoJSON MultiPolygons) require ray-casting or point-in-polygon (PIP) algorithms explored in advanced coursework.
