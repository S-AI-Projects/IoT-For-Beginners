import unittest
from example import validate_and_normalize_batch


class TestTensorShapeContract(unittest.TestCase):
    def test_valid_boundary_batch(self):
        # Smallest valid boundary batch: shape (1, 2, 2) with 0 and 255 boundaries
        batch = [[[0, 255], [128, 64]]]
        result = validate_and_normalize_batch(batch)

        self.assertEqual(result["shape"], [1, 2, 2])
        self.assertEqual(result["normalized"][0][0][0], 0.0)
        self.assertEqual(result["normalized"][0][0][1], 1.0)
        self.assertAlmostEqual(result["normalized"][0][1][0], 128 / 255.0, places=5)
        self.assertAlmostEqual(result["normalized"][0][1][1], 64 / 255.0, places=5)

    def test_rejects_negative_and_over_255_pixels(self):
        with self.assertRaises(ValueError):
            validate_and_normalize_batch([[[-1, 255], [128, 64]]])

        with self.assertRaises(ValueError):
            validate_and_normalize_batch([[[0, 256], [128, 64]]])

    def test_rejects_invalid_shape_and_non_numeric(self):
        # Ragged width
        with self.assertRaises(ValueError):
            validate_and_normalize_batch([[[0, 255], [128]]])

        # Boolean or string pixel
        with self.assertRaises(ValueError):
            validate_and_normalize_batch([[[True, 255], [128, 64]]])

        with self.assertRaises(ValueError):
            validate_and_normalize_batch([[["0", 255], [128, 64]]])


if __name__ == "__main__":
    unittest.main()
