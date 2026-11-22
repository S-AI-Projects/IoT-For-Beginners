"""
Unit tests for Classification Evaluation & Offline Adapter (R15-T015)

Tests verify:
1. y_true=[1,1,0,0], y_pred=[1,0,1,0] gives TP=1,FN=1,FP=1,TN=1, precision=recall=0.5
2. No positive predictions gives precision=0 under the documented zero-denominator policy
3. Offline service adapter operates deterministically
4. Error checking on length mismatch
5. Deliberate wrong assertion failure test
"""

import unittest
from example import (
    OfflineFruitDetectorAdapter,
    compute_metrics,
    run_demo,
)


class TestClassificationEvaluation(unittest.TestCase):
    def test_required_benchmark_fixture(self):
        """y_true=[1,1,0,0], y_pred=[1,0,1,0] -> TP=1,FN=1,FP=1,TN=1, precision=recall=0.5"""
        y_true = [1, 1, 0, 0]
        y_pred = [1, 0, 1, 0]
        res = compute_metrics(y_true, y_pred)

        self.assertEqual(res.tp, 1)
        self.assertEqual(res.fn, 1)
        self.assertEqual(res.fp, 1)
        self.assertEqual(res.tn, 1)
        self.assertAlmostEqual(res.precision, 0.5)
        self.assertAlmostEqual(res.recall, 0.5)

    def test_zero_denominator_no_positive_predictions(self):
        """No positive predictions gives precision=0 under the documented policy."""
        y_true = [1, 1, 0, 0]
        y_pred = [0, 0, 0, 0]
        res = compute_metrics(y_true, y_pred)

        self.assertEqual(res.tp, 0)
        self.assertEqual(res.fp, 0)
        self.assertEqual(res.precision, 0.0)
        self.assertEqual(res.recall, 0.0)

    def test_zero_denominator_no_positive_ground_truth(self):
        """No ground-truth positives gives recall=0 under the documented policy."""
        y_true = [0, 0, 0, 0]
        y_pred = [1, 0, 1, 0]
        res = compute_metrics(y_true, y_pred)

        self.assertEqual(res.tp, 0)
        self.assertEqual(res.fn, 0)
        self.assertEqual(res.recall, 0.0)
        self.assertAlmostEqual(res.precision, 0.0)

    def test_offline_adapter_service(self):
        canned = [1, 0, 1, 0]
        adapter = OfflineFruitDetectorAdapter(canned)
        samples = [{"image_id": i} for i in range(4)]
        preds = adapter.predict(samples)
        self.assertEqual(preds, canned)

        y_true = [1, 1, 0, 0]
        res = compute_metrics(y_true, preds)
        self.assertEqual(res.tp, 1)
        self.assertEqual(res.precision, 0.5)

    def test_length_mismatch_raises_error(self):
        with self.assertRaises(ValueError):
            compute_metrics([1, 0], [1])

    def test_run_demo(self):
        metrics = run_demo()
        self.assertEqual(metrics.tp, 1)
        self.assertEqual(metrics.precision, 0.5)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        res = compute_metrics([1, 1, 0, 0], [1, 0, 1, 0])
        with self.assertRaises(AssertionError):
            self.assertEqual(res.precision, 1.0)  # Precision is 0.5, expecting 1.0 must fail


if __name__ == "__main__":
    unittest.main()
