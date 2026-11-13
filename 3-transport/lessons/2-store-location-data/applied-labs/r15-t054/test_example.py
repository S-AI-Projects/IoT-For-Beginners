import unittest
from example import evaluate_geofence_with_trace


class TestGeofenceInvariantAndTrace(unittest.TestCase):
    def test_classification_and_state_trace_invariant(self):
        records = [
            {"id": "interior", "lat": 15, "lon": 75},
            {"id": "boundary", "lat": 10, "lon": 70},
            {"id": "outside", "lat": 21, "lon": 75},
        ]
        output = evaluate_geofence_with_trace(records)
        results = output["results"]
        trace = output["state_trace"]

        # Expected membership classifications
        self.assertTrue(results[0]["inside"])
        self.assertTrue(results[1]["inside"])
        self.assertFalse(results[2]["inside"])

        # Invariant linking intermediate state trace to final output
        self.assertEqual(len(trace), len(results))
        for state_entry, final_entry in zip(trace, results):
            self.assertEqual(state_entry["id"], final_entry["id"])
            expected_inside = state_entry["lat_in_bounds"] and state_entry["lon_in_bounds"]
            self.assertEqual(state_entry["computed_inside"], expected_inside)
            self.assertEqual(final_entry["inside"], state_entry["computed_inside"])

    def test_rejects_invalid_latitude_100(self):
        with self.assertRaises(ValueError):
            evaluate_geofence_with_trace([{"id": "bad-lat", "lat": 100, "lon": 75}])

        with self.assertRaises(ValueError):
            evaluate_geofence_with_trace([{"id": "bad-lon", "lat": 15, "lon": -181}])


if __name__ == "__main__":
    unittest.main()
