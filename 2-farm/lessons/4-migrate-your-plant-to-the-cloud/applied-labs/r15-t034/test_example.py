import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import LocalAdapter, batch_shape, normalize_batch, run  # noqa: E402

FIXTURE = [[[0, 255], [128, 64]]]


class Normalize(unittest.TestCase):
    def test_shape_preserved(self):
        self.assertEqual(batch_shape(FIXTURE), (1, 2, 2))
        self.assertEqual(batch_shape(normalize_batch(FIXTURE)), (1, 2, 2))

    def test_endpoints(self):
        out = normalize_batch(FIXTURE)
        self.assertEqual(out[0][0][0], 0)
        self.assertEqual(out[0][0][1], 1)

    def test_middle_values(self):
        out = normalize_batch(FIXTURE)
        self.assertAlmostEqual(out[0][1][0], 128 / 255)
        self.assertAlmostEqual(out[0][1][1], 64 / 255)

    def test_all_outputs_in_range(self):
        for row in normalize_batch([[[0, 1, 254, 255]], [[10, 20, 30, 40]]])[0]:
            for v in row:
                self.assertTrue(0 <= v <= 1)

    def test_multi_image_batch_shape(self):
        batch = [[[0, 1, 2], [3, 4, 5]], [[6, 7, 8], [9, 10, 11]]]
        self.assertEqual(batch_shape(normalize_batch(batch)), (2, 2, 3))


class Rejections(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(ValueError):
            normalize_batch([[[0, -1]]])

    def test_above_255(self):
        with self.assertRaises(ValueError):
            normalize_batch([[[0, 256]]])

    def test_non_numbers(self):
        for bad in ["5", None, True, float("nan")]:
            with self.assertRaises(ValueError):
                normalize_batch([[[0, bad]]])

    def test_bad_shapes(self):
        for bad in [[], [[]], [[[]]], [[[0, 1], [2]]], [[[0]], [[0], [1]]], 5]:
            with self.assertRaises(ValueError):
                normalize_batch(bad)


class Adapter(unittest.TestCase):
    def test_adapter_deterministic(self):
        batch = [[[0, 0]], [[255, 255]]]
        self.assertEqual(run(batch, LocalAdapter()), ["dark", "bright"])
        self.assertEqual(run(batch, LocalAdapter()), run(batch, LocalAdapter()))

    def test_service_is_swappable_callable(self):
        calls = []

        def fake(normalized):
            calls.append(normalized)
            return ["x"]

        self.assertEqual(run(FIXTURE, fake), ["x"])
        self.assertEqual(batch_shape(calls[0]), (1, 2, 2))

    def test_service_not_called_on_invalid_input(self):
        def fail(_):
            raise AssertionError("service must not be called")

        with self.assertRaises(ValueError):
            run([[[300]]], fail)


if __name__ == "__main__":
    unittest.main()
