#!/usr/bin/env python3
"""Bounding-box Intersection over Union (IoU) simulation.

Task R15-T027: Bounding-box Intersection over Union (IoU)
Context: 5-retail/lessons/1-train-stock-detector

Coordinate convention:
  [x_min, y_min, x_max, y_max]
  - x_min, y_min: left and top edges.
  - x_max, y_max: right and bottom edges.
  - x increases to the right; y increases downward.
  - Coordinates are numeric pixel-like values; no image is loaded or processed.

Educational Scope & Limitations:
  This script is a local geometry simulation operating on numeric coordinates.
  It does not load or process real images, train or run neural network detectors,
  generate predictions, or interact with Azure Custom Vision or any cloud service.
"""

from __future__ import annotations

import argparse
import math
import sys
from typing import Any, Dict, Sequence, Tuple


def validate_box(box: Any, box_name: str = "box") -> Tuple[float, float, float, float]:
    """Validate a bounding box represented as [x_min, y_min, x_max, y_max].

    Requirements:
      - Must be a sequence (list or tuple) containing exactly 4 coordinates.
      - Reject booleans, non-numeric values, NaN, and positive/negative infinity.
      - Reject inverted boxes where x_min > x_max or y_min > y_max.
      - Do not silently reorder invalid coordinates.
      - Permit zero-width and zero-height boxes (x_min == x_max or y_min == y_max).

    Returns:
      Tuple of 4 floats: (x_min, y_min, x_max, y_max).

    Raises:
      TypeError: If the box is not a list/tuple, contains booleans, or non-numeric items.
      ValueError: If coordinate count != 4, values are non-finite, or coordinates are inverted.
    """
    if not isinstance(box, (list, tuple)):
        raise TypeError(
            f"{box_name} must be a list or tuple of 4 coordinates, got {type(box).__name__}."
        )

    if len(box) != 4:
        raise ValueError(
            f"{box_name} must contain exactly 4 coordinates [x_min, y_min, x_max, y_max], got {len(box)}."
        )

    coords = []
    for idx, val in enumerate(box):
        if isinstance(val, bool):
            raise TypeError(
                f"{box_name}[{idx}] must be a real number, got boolean {val!r}."
            )
        if not isinstance(val, (int, float)):
            raise TypeError(
                f"{box_name}[{idx}] must be an int or float, got {type(val).__name__} ({val!r})."
            )
        if math.isnan(val) or math.isinf(val):
            raise ValueError(
                f"{box_name}[{idx}] must be a finite number, got {val!r}."
            )
        coords.append(float(val))

    x_min, y_min, x_max, y_max = coords
    if x_min > x_max:
        raise ValueError(
            f"{box_name} has inverted x coordinates: x_min ({x_min}) > x_max ({x_max})."
        )
    if y_min > y_max:
        raise ValueError(
            f"{box_name} has inverted y coordinates: y_min ({y_min}) > y_max ({y_max})."
        )

    return (x_min, y_min, x_max, y_max)


def box_area(box: Tuple[float, float, float, float]) -> float:
    """Calculate the area of a validated bounding box."""
    x_min, y_min, x_max, y_max = box
    width = x_max - x_min
    height = y_max - y_min
    return width * height


def compute_iou_details(
    box_a: Sequence[Any], box_b: Sequence[Any]
) -> Dict[str, Any]:
    """Compute detailed intermediate calculations for Intersection over Union (IoU)."""
    val_a = validate_box(box_a, "box_a")
    val_b = validate_box(box_b, "box_b")

    area_a = box_area(val_a)
    area_b = box_area(val_b)

    # Intersection edges
    inter_x_min = max(val_a[0], val_b[0])
    inter_y_min = max(val_a[1], val_b[1])
    inter_x_max = min(val_a[2], val_b[2])
    inter_y_max = min(val_a[3], val_b[3])

    inter_w = max(0.0, inter_x_max - inter_x_min)
    inter_h = max(0.0, inter_y_max - inter_y_min)
    intersection_area = inter_w * inter_h

    union_area = area_a + area_b - intersection_area
    iou = (intersection_area / union_area) if union_area > 0.0 else 0.0

    return {
        "box_a": list(val_a),
        "box_b": list(val_b),
        "area_a": area_a,
        "area_b": area_b,
        "inter_box": [inter_x_min, inter_y_min, inter_x_max, inter_y_max],
        "inter_width": inter_w,
        "inter_height": inter_h,
        "intersection_area": intersection_area,
        "union_area": union_area,
        "iou": iou,
    }


def intersection_over_union(box_a: Sequence[Any], box_b: Sequence[Any]) -> float:
    """Calculate axis-aligned bounding-box Intersection over Union (IoU).

    Args:
      box_a: First bounding box [x_min, y_min, x_max, y_max].
      box_b: Second bounding box [x_min, y_min, x_max, y_max].

    Returns:
      float: IoU value in range [0.0, 1.0]. If union area is zero, returns 0.0.
    """
    return compute_iou_details(box_a, box_b)["iou"]


def run_normal_scenario() -> None:
    """Run the mandatory worked fixture and demonstrate core properties."""
    print("=" * 80)
    print("Task R15-T027: Bounding-box Intersection over Union (IoU)")
    print("Scenario: normal (Mandatory Worked Fixture & Core Demonstrations)")
    print("=" * 80)
    print()
    print("Coordinate Convention: [x_min, y_min, x_max, y_max]")
    print("  - x_min, y_min: left and top edges")
    print("  - x_max, y_max: right and bottom edges")
    print("  - x increases rightward, y increases downward")
    print()

    # 1. Mandatory Worked Fixture
    box_a = [0, 0, 2, 2]
    box_b = [1, 1, 3, 3]
    details = compute_iou_details(box_a, box_b)

    expected_area_a = 4.0
    expected_area_b = 4.0
    expected_intersection = 1.0
    expected_union = 7.0
    expected_iou = 1.0 / 7.0

    print("1. MANDATORY WORKED FIXTURE:")
    print("-" * 80)
    print(f"  Input Box A:          {box_a}")
    print(f"  Input Box B:          {box_b}")
    print(f"  Area of Box A:        {details['area_a']:.1f} (Expected: {expected_area_a:.1f})")
    print(f"  Area of Box B:        {details['area_b']:.1f} (Expected: {expected_area_b:.1f})")
    print(
        f"  Intersection Box:     [{details['inter_box'][0]:.1f}, {details['inter_box'][1]:.1f}, "
        f"{details['inter_box'][2]:.1f}, {details['inter_box'][3]:.1f}] "
        f"(width={details['inter_width']:.1f}, height={details['inter_height']:.1f})"
    )
    print(
        f"  Intersection Area:    {details['intersection_area']:.1f} (Expected: {expected_intersection:.1f})"
    )
    print(
        f"  Union Area:           {details['union_area']:.1f} "
        f"(= Area A + Area B - Intersection = {expected_area_a:.1f} + {expected_area_b:.1f} - {expected_intersection:.1f} = {expected_union:.1f})"
    )
    print(f"  Actual IoU:           {details['iou']:.12f}")
    print(f"  Expected IoU (1/7):   {expected_iou:.12f}")

    diff = abs(details["iou"] - expected_iou)
    assert diff < 1e-9, f"Calculation mismatch: expected {expected_iou}, got {details['iou']}"
    print("  Verification:         PASSED (Exact match within floating-point tolerance)")
    print()

    # 2. Identical Boxes Demonstration
    box_same = [0, 0, 2, 2]
    iou_same = intersection_over_union(box_same, box_same)
    print("2. IDENTICAL BOXES DEMONSTRATION:")
    print("-" * 80)
    print(f"  Box A: {box_same}, Box B: {box_same}")
    print(f"  Actual IoU: {iou_same:.6f} (Expected: 1.000000)")
    assert iou_same == 1.0, f"Expected 1.0, got {iou_same}"
    print("  Verification: PASSED (Identical boxes have IoU = 1.0)")
    print()

    # 3. Disjoint Boxes Demonstration
    box_disjoint_a = [0, 0, 2, 2]
    box_disjoint_b = [4, 4, 6, 6]
    iou_disjoint = intersection_over_union(box_disjoint_a, box_disjoint_b)
    print("3. DISJOINT BOXES DEMONSTRATION:")
    print("-" * 80)
    print(f"  Box A: {box_disjoint_a}, Box B: {box_disjoint_b}")
    print(f"  Actual IoU: {iou_disjoint:.6f} (Expected: 0.000000)")
    assert iou_disjoint == 0.0, f"Expected 0.0, got {iou_disjoint}"
    print("  Verification: PASSED (Disjoint boxes have IoU = 0.0)")
    print()

    print("=" * 80)
    print("Educational Note: This simulation uses numeric coordinates only.")
    print("It does not load images or evaluate real machine learning models.")
    print("=" * 80)


def run_boundary_scenario() -> None:
    """Run edge-touching and zero-area boundary cases."""
    print("=" * 80)
    print("Task R15-T027: Bounding-box Intersection over Union (IoU)")
    print("Scenario: boundary (Edge-Touching & Zero-Area Bounding Boxes)")
    print("=" * 80)
    print()

    # 1. Edge-Touching Boxes (Horizontal)
    box1 = [0, 0, 2, 2]
    box2_h = [2, 0, 4, 2]
    details_h = compute_iou_details(box1, box2_h)
    print("1. HORIZONTALLY TOUCHING BOXES:")
    print("-" * 80)
    print(f"  Box A: {box1}")
    print(f"  Box B: {box2_h}")
    print(
        f"  Intersection width: max(0.0, min(2, 4) - max(0, 2)) = max(0.0, 2 - 2) = {details_h['inter_width']:.1f}"
    )
    print(f"  Intersection area:  {details_h['intersection_area']:.1f}")
    print(f"  Actual IoU:         {details_h['iou']:.6f} (Expected: 0.000000)")
    print(
        "  Explanation: Touching along an edge produces zero width (or height), so intersection area is 0."
    )
    assert details_h["iou"] == 0.0
    print("  Verification:       PASSED")
    print()

    # 2. Edge-Touching Boxes (Vertical)
    box2_v = [0, 2, 2, 4]
    details_v = compute_iou_details(box1, box2_v)
    print("2. VERTICALLY TOUCHING BOXES:")
    print("-" * 80)
    print(f"  Box A: {box1}")
    print(f"  Box B: {box2_v}")
    print(
        f"  Intersection height: max(0.0, min(2, 4) - max(0, 2)) = max(0.0, 2 - 2) = {details_v['inter_height']:.1f}"
    )
    print(f"  Intersection area:   {details_v['intersection_area']:.1f}")
    print(f"  Actual IoU:          {details_v['iou']:.6f} (Expected: 0.000000)")
    assert details_v["iou"] == 0.0
    print("  Verification:        PASSED")
    print()

    # 3. Corner-Touching Boxes
    box2_c = [2, 2, 4, 4]
    details_c = compute_iou_details(box1, box2_c)
    print("3. CORNER TOUCHING BOXES:")
    print("-" * 80)
    print(f"  Box A: {box1}")
    print(f"  Box B: {box2_c}")
    print(f"  Actual IoU: {details_c['iou']:.6f} (Expected: 0.000000)")
    assert details_c["iou"] == 0.0
    print("  Verification: PASSED")
    print()

    # 4. Zero-Area Box (Zero Width) Overlapping a Normal Box
    box_zero_w = [1, 0, 1, 2]  # x_min == x_max == 1
    details_zw = compute_iou_details(box_zero_w, box1)
    print("4. ZERO-WIDTH BOX WITH NORMAL BOX:")
    print("-" * 80)
    print(f"  Box A (Zero Width): {box_zero_w} (Area = {details_zw['area_a']:.1f})")
    print(f"  Box B (Normal):     {box1} (Area = {details_zw['area_b']:.1f})")
    print(f"  Intersection Area:  {details_zw['intersection_area']:.1f}")
    print(f"  Union Area:         {details_zw['union_area']:.1f}")
    print(f"  Actual IoU:         {details_zw['iou']:.6f} (Expected: 0.000000)")
    assert details_zw["iou"] == 0.0
    print("  Verification:       PASSED")
    print()

    # 5. Two Zero-Area Boxes (Zero Union Area)
    point1 = [1, 1, 1, 1]
    point2 = [2, 2, 2, 2]
    details_points = compute_iou_details(point1, point2)
    print("5. TWO ZERO-AREA BOXES (ZERO UNION AREA):")
    print("-" * 80)
    print(f"  Box A: {point1} (Area = {details_points['area_a']:.1f})")
    print(f"  Box B: {point2} (Area = {details_points['area_b']:.1f})")
    print(f"  Union Area: {details_points['union_area']:.1f}")
    print(f"  Actual IoU: {details_points['iou']:.6f} (Expected: 0.000000)")
    print(
        "  Explanation: When union area is 0.0, IoU is defined as 0.0 to prevent division by zero."
    )
    assert details_points["iou"] == 0.0
    print("  Verification: PASSED")
    print()


def run_failure_scenario() -> None:
    """Run deliberate incorrect assertion to demonstrate failure detection."""
    print("=" * 80)
    print("Task R15-T027: Bounding-box Intersection over Union (IoU)")
    print("Scenario: failure (Intentional Failure Demonstration)")
    print("=" * 80)
    print()
    print("Notice: This scenario intentionally asserts an incorrect expected IoU.")
    print("It demonstrates that verification checks properly fail with a non-zero exit code.")
    print()

    box_a = [0, 0, 2, 2]
    box_b = [1, 1, 3, 3]
    actual_iou = intersection_over_union(box_a, box_b)
    false_expected_iou = 0.999999

    print(f"Input Box A: {box_a}")
    print(f"Input Box B: {box_b}")
    print(f"Actual IoU:               {actual_iou:.6f}")
    print(f"False Expected Value:     {false_expected_iou:.6f}")
    print()
    print("Triggering deliberate assertion failure now...")

    # Deliberately fail the assertion
    assert (
        actual_iou == false_expected_iou
    ), f"INTENTIONAL FAILURE: Actual IoU ({actual_iou:.6f}) != Expected ({false_expected_iou:.6f})"


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Axis-aligned Bounding-Box Intersection over Union (IoU) Simulation."
    )
    parser.add_argument(
        "scenario",
        nargs="?",
        default="normal",
        choices=["normal", "boundary", "failure"],
        help="Scenario to run: 'normal' (default), 'boundary', or 'failure'.",
    )

    args = parser.parse_args()

    if args.scenario == "normal":
        run_normal_scenario()
    elif args.scenario == "boundary":
        run_boundary_scenario()
    elif args.scenario == "failure":
        run_failure_scenario()


if __name__ == "__main__":
    main()
