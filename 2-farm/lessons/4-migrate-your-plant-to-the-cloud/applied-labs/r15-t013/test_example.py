"""
Unit tests for Tensor-Shape Contract & Image Batch Normalization (R15-T013)

Tests verify:
1. Batch [[[0,255],[128,64]]] stays shape (1,2,2)
2. 0 -> 0.0 and 255 -> 1.0
3. Negative or >255 pixels are rejected
4. Direct vs independent implementation cross-validation on identical inputs
5. Deliberate wrong assertion failure test
"""

import unittest
from example import (
    get_shape,
    validate_and_normalize_direct,
    reference_independent_normalize,
    run_demo,
)


class TestTensorShapeContract(unittest.TestCase):
    def test_required_batch_normalization_and_shape(self):
        batch = [[[0, 255], [128, 64]]]
        shape, normalized = validate_and_normalize_direct(batch)

        # 1. Shape remains (1, 2, 2)
        self.assertEqual(shape, (1, 2, 2))
        self.assertEqual(len(normalized), 1)
        self.assertEqual(len(normalized[0]), 2)
        self.assertEqual(len(normalized[0][0]), 2)

        # 2. Pixel mapping checks: 0 -> 0.0, 255 -> 1.0
        self.assertAlmostEqual(normalized[0][0][0], 0.0)
        self.assertAlmostEqual(normalized[0][0][1], 1.0)
        self.assertAlmostEqual(normalized[0][1][0], 128 / 255.0)
        self.assertAlmostEqual(normalized[0][1][1], 64 / 255.0)

    def test_negative_pixel_rejected(self):
        batch = [[[0, -1], [128, 64]]]
        with self.assertRaises(ValueError) as ctx:
            validate_and_normalize_direct(batch)
        self.assertIn("out of range", str(ctx.exception))

    def test_pixel_greater_than_255_rejected(self):
        batch = [[[0, 256], [128, 64]]]
        with self.assertRaises(ValueError) as ctx:
            validate_and_normalize_direct(batch)
        self.assertIn("out of range", str(ctx.exception))

    def test_non_numeric_pixel_rejected(self):
        batch = [[[0, "255"], [128, 64]]]
        with self.assertRaises(TypeError):
            validate_and_normalize_direct(batch)

    def test_inconsistent_ragged_shape_rejected(self):
        ragged = [[[0, 255], [128]]]  # row 1 has 2 elements, row 2 has 1 element
        with self.assertRaises(ValueError):
            validate_and_normalize_direct(ragged)

    def test_compare_two_approaches_equivalence(self):
        """Compares direct implementation with independent reference calculation."""
        inputs = [
            [[[0, 255], [128, 64]]],
            [[[10, 20, 30], [40, 50, 60]], [[70, 80, 90], [100, 110, 120]]],
        ]
        for batch in inputs:
            shape1, norm1 = validate_and_normalize_direct(batch)
            shape2, norm2 = reference_independent_normalize(batch)
            self.assertEqual(shape1, shape2)
            # Compare rounded values
            for s1, s2 in zip(norm1, norm2):
                for r1, r2 in zip(s1, s2):
                    for p1, p2 in zip(r1, r2):
                        self.assertAlmostEqual(p1, p2, places=5)

    def test_run_demo(self):
        shape, norm = run_demo()
        self.assertEqual(shape, (1, 2, 2))
        self.assertEqual(len(norm), 1)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        batch = [[[0, 255], [128, 64]]]
        shape, _ = validate_and_normalize_direct(batch)
        with self.assertRaises(AssertionError):
            self.assertEqual(shape, (2, 2, 2))  # Expected (1, 2, 2)


if __name__ == "__main__":
    unittest.main()
