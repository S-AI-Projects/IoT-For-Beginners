import unittest
from example import classify_coordinates


class TestGeofenceOfflineAdapter(unittest.TestCase):
    def test_interior_boundary_and_outside_points(self):
        records = [
            {"id": "interior", "lat": 15, "lon": 75},
            {"id": "boundary", "lat": 10, "lon": 70},
            {"id": "outside", "lat": 21, "lon": 75},
        ]
        results = classify_coordinates(records)

        self.assertTrue(results[0]["inside"])
        self.assertTrue(results[1]["inside"])
        self.assertFalse(results[2]["inside"])

    def test_rejects_invalid_latitude_100(self):
        with self.assertRaises(ValueError):
            classify_coordinates([{"id": "bad-lat", "lat": 100, "lon": 75}])

        with self.assertRaises(ValueError):
            classify_coordinates([{"id": "bad-lon", "lat": 15, "lon": 200}])

    def test_callable_adapter_interface(self):
        # Verify external dependency can be swapped via the callable interface
        always_outside_stub = lambda lat, lon: False
        results = classify_coordinates([{"id": "stubbed", "lat": 15, "lon": 75}], adapter=always_outside_stub)
        self.assertFalse(results[0]["inside"])


if __name__ == "__main__":
    unittest.main()
