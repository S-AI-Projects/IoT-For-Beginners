#!/usr/bin/env python3
"""Unit tests for Bounding-box Intersection over Union (IoU) simulation.

Task R15-T027: Bounding-box Intersection over Union (IoU)
Context: 5-retail/lessons/1-train-stock-detector
"""

import math
import os
import subprocess
import sys
import unittest

from example import (
    box_area,
    compute_iou_details,
    intersection_over_union,
    validate_box,
)


class TestBoundingBoxIoU(unittest.TestCase):
    """Test suite for IoU calculations, validations, boundary cases, and CLI scenarios."""

    def test_mandatory_worked_fixture(self):
        """Verify the exact mandatory worked fixture: Box A [0,0,2,2], Box B [1,1,3,3]."""
        box_a = [0, 0, 2, 2]
        box_b = [1, 1, 3, 3]

        details = compute_iou_details(box_a, box_b)
        self.assertEqual(details["area_a"], 4.0)
        self.assertEqual(details["area_b"], 4.0)
        self.assertEqual(details["intersection_area"], 1.0)
        self.assertEqual(details["union_area"], 7.0)

        actual_iou = intersection_over_union(box_a, box_b)
        self.assertAlmostEqual(actual_iou, 1.0 / 7.0, places=9)

    def test_identical_boxes(self):
        """Identical bounding boxes must produce an IoU of exactly 1.0."""
        box = [10.0, 20.0, 50.0, 80.0]
        actual_iou = intersection_over_union(box, box)
        self.assertEqual(actual_iou, 1.0)

    def test_disjoint_boxes(self):
        """Non-overlapping, disjoint bounding boxes must produce an IoU of 0.0."""
        box_a = [0, 0, 10, 10]
        box_b = [20, 20, 30, 30]
        actual_iou = intersection_over_union(box_a, box_b)
        self.assertEqual(actual_iou, 0.0)

    def test_containment(self):
        """When one box completely contains another, intersection equals smaller box area."""
        box_outer = [0.0, 0.0, 4.0, 4.0]  # area = 16
        box_inner = [1.0, 1.0, 3.0, 3.0]  # area = 4
        # Intersection = 4, Union = 16 + 4 - 4 = 16, IoU = 4/16 = 0.25
        actual_iou = intersection_over_union(box_outer, box_inner)
        self.assertEqual(actual_iou, 0.25)

        # Commutative check
        self.assertEqual(intersection_over_union(box_inner, box_outer), 0.25)

    def test_partial_overlap(self):
        """Verify standard rectangular partial overlap."""
        box_a = [0, 0, 10, 10]  # area = 100
        box_b = [5, 0, 15, 10]  # area = 100
        # Intersection: x in [5, 10], y in [0, 10] => area = 5 * 10 = 50
        # Union = 100 + 100 - 50 = 150, IoU = 50/150 = 1/3
        actual_iou = intersection_over_union(box_a, box_b)
        self.assertAlmostEqual(actual_iou, 1.0 / 3.0, places=9)

    def test_edge_touching_boxes_horizontal(self):
        """Boxes that share a vertical edge boundary must have 0.0 intersection and 0.0 IoU."""
        box_a = [0, 0, 2, 2]
        box_b = [2, 0, 4, 2]  # touching along x = 2
        actual_iou = intersection_over_union(box_a, box_b)
        self.assertEqual(actual_iou, 0.0)

    def test_edge_touching_boxes_vertical(self):
        """Boxes that share a horizontal edge boundary must have 0.0 intersection and 0.0 IoU."""
        box_a = [0, 0, 2, 2]
        box_b = [0, 2, 2, 4]  # touching along y = 2
        actual_iou = intersection_over_union(box_a, box_b)
        self.assertEqual(actual_iou, 0.0)

    def test_corner_touching_boxes(self):
        """Boxes touching only at a single vertex point must have 0.0 IoU."""
        box_a = [0, 0, 2, 2]
        box_b = [2, 2, 4, 4]  # touching at (2, 2)
        actual_iou = intersection_over_union(box_a, box_b)
        self.assertEqual(actual_iou, 0.0)

    def test_zero_area_boxes_behavior(self):
        """Zero-width and zero-height boxes must be permitted and yield 0.0 intersection."""
        # Zero-width box
        box_zero_w = [2, 0, 2, 5]  # width = 0, height = 5, area = 0
        box_normal = [0, 0, 4, 5]  # area = 20
        self.assertEqual(intersection_over_union(box_zero_w, box_normal), 0.0)

        # Zero-height box
        box_zero_h = [0, 3, 4, 3]  # width = 4, height = 0, area = 0
        self.assertEqual(intersection_over_union(box_zero_h, box_normal), 0.0)

        # Single point box
        box_point = [2, 2, 2, 2]
        self.assertEqual(intersection_over_union(box_point, box_normal), 0.0)

    def test_zero_union_area_returns_zero(self):
        """When both boxes have zero area, union area is 0.0 and IoU must return 0.0."""
        box_a = [1, 1, 1, 1]
        box_b = [2, 2, 2, 2]
        self.assertEqual(intersection_over_union(box_a, box_b), 0.0)

        # Identical zero-area boxes
        self.assertEqual(intersection_over_union(box_a, box_a), 0.0)

    def test_inverted_x_coordinates_rejected(self):
        """Boxes where x_min > x_max must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            validate_box([5, 0, 2, 2])
        self.assertIn("inverted x coordinates", str(ctx.exception))

    def test_inverted_y_coordinates_rejected(self):
        """Boxes where y_min > y_max must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            validate_box([0, 5, 2, 2])
        self.assertIn("inverted y coordinates", str(ctx.exception))

    def test_wrong_coordinate_count_rejected(self):
        """Boxes with fewer or more than 4 coordinates must raise ValueError."""
        with self.assertRaises(ValueError):
            validate_box([0, 0, 2])
        with self.assertRaises(ValueError):
            validate_box([0, 0, 2, 2, 5])
        with self.assertRaises(ValueError):
            validate_box([])

    def test_non_sequence_box_rejected(self):
        """Non-sequence inputs must raise TypeError."""
        with self.assertRaises(TypeError):
            validate_box("0,0,2,2")  # string
        with self.assertRaises(TypeError):
            validate_box({"x_min": 0, "y_min": 0, "x_max": 2, "y_max": 2})

    def test_non_numeric_coordinates_rejected(self):
        """Non-numeric coordinate types (e.g. strings, None) must raise TypeError."""
        with self.assertRaises(TypeError):
            validate_box([0, 0, "2", 2])
        with self.assertRaises(TypeError):
            validate_box([None, 0, 2, 2])
        with self.assertRaises(TypeError):
            validate_box([0, [1], 2, 2])

    def test_boolean_coordinates_rejected(self):
        """Booleans must be explicitly rejected despite being int subclasses in Python."""
        with self.assertRaises(TypeError) as ctx:
            validate_box([True, 0, 2, 2])
        self.assertIn("boolean", str(ctx.exception))

        with self.assertRaises(TypeError) as ctx:
            validate_box([0, False, 2, 2])
        self.assertIn("boolean", str(ctx.exception))

    def test_nan_and_infinity_rejected(self):
        """NaN and positive/negative infinity coordinates must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            validate_box([0, 0, float("nan"), 2])
        self.assertIn("finite number", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_box([0, 0, float("inf"), 2])
        self.assertIn("finite number", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_box([float("-inf"), 0, 2, 2])
        self.assertIn("finite number", str(ctx.exception))

    def test_cli_failure_scenario_subprocess(self):
        """Run the deliberate 'failure' CLI scenario in a fresh process and verify non-zero exit."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "failure"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertNotEqual(
            proc.returncode,
            0,
            f"Expected failure scenario to exit non-zero, got {proc.returncode}.",
        )
        self.assertIn("INTENTIONAL FAILURE", proc.stderr + proc.stdout)

    def test_cli_normal_scenario_subprocess(self):
        """Run the default / 'normal' CLI scenario in a fresh process and verify exit 0."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "normal"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(
            proc.returncode,
            0,
            f"Expected normal scenario to exit 0, got {proc.returncode}. Output:\n{proc.stdout}\n{proc.stderr}",
        )
        self.assertIn("MANDATORY WORKED FIXTURE", proc.stdout)
        self.assertIn("0.142857", proc.stdout)

    def test_cli_boundary_scenario_subprocess(self):
        """Run the 'boundary' CLI scenario in a fresh process and verify exit 0."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "boundary"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(
            proc.returncode,
            0,
            f"Expected boundary scenario to exit 0, got {proc.returncode}. Output:\n{proc.stdout}\n{proc.stderr}",
        )
        self.assertIn("TOUCHING BOXES", proc.stdout)
        self.assertIn("ZERO-WIDTH BOX", proc.stdout)


if __name__ == "__main__":
    unittest.main()
