import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import check_invariant, evaluate  # noqa: E402


class Primary(unittest.TestCase):
    def test_primary_fixture(self):
        r, trace = evaluate([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual((r["tp"], r["fn"], r["fp"], r["tn"]), (1, 1, 1, 1))
        self.assertEqual(r["precision"], 0.5)
        self.assertEqual(r["recall"], 0.5)

    def test_state_trace(self):
        _, trace = evaluate([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(trace, [
            {"step": 1, "tp": 1, "fn": 0, "fp": 0, "tn": 0},
            {"step": 2, "tp": 1, "fn": 1, "fp": 0, "tn": 0},
            {"step": 3, "tp": 1, "fn": 1, "fp": 1, "tn": 0},
            {"step": 4, "tp": 1, "fn": 1, "fp": 1, "tn": 1},
        ])


class Invariant(unittest.TestCase):
    def test_invariant_on_several_inputs(self):
        cases = [([1, 1, 0, 0], [1, 0, 1, 0]), ([0, 0, 0], [0, 0, 0]),
                 ([1, 1, 1], [0, 0, 0]), ([1, 0, 1, 1, 0], [1, 0, 0, 1, 1]), ([], [])]
        for y_true, y_pred in cases:
            with self.subTest(y_true=y_true, y_pred=y_pred):
                r, trace = evaluate(y_true, y_pred)
                self.assertTrue(check_invariant(r, trace, len(y_true)))

    def test_invariant_detects_corrupted_state(self):
        r, trace = evaluate([1, 1, 0, 0], [1, 0, 1, 0])
        trace[-1]["tp"] += 1
        self.assertFalse(check_invariant(r, trace, 4))


class Boundary(unittest.TestCase):
    def test_no_positive_predictions_precision_zero(self):
        r, _ = evaluate([1, 1, 0], [0, 0, 0])
        self.assertEqual(r["precision"], 0.0)
        self.assertEqual(r["recall"], 0.0)

    def test_no_actual_positives_recall_zero(self):
        r, _ = evaluate([0, 0], [1, 0])
        self.assertEqual(r["recall"], 0.0)
        self.assertEqual(r["precision"], 0.0)

    def test_perfect(self):
        r, _ = evaluate([1, 0, 1], [1, 0, 1])
        self.assertEqual((r["precision"], r["recall"]), (1.0, 1.0))


class Invalid(unittest.TestCase):
    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            evaluate([1, 0], [1])

    def test_bad_label(self):
        with self.assertRaises(ValueError):
            evaluate([1, 2], [1, 0])


if __name__ == "__main__":
    unittest.main()
