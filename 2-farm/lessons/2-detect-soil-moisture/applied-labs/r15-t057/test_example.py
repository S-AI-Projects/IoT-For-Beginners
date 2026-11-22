import unittest
from example import simulate_hysteresis, compare_configurations


class TestMoistureHysteresis(unittest.TestCase):
    def test_contract_sequence_and_boundary_retention(self):
        # Contract: starting off, [700, 250, 400, 650] -> [off, on, on, off]
        res = simulate_hysteresis([700, 250, 400, 650])
        self.assertEqual(res["states"], ["off", "on", "on", "off"])
        self.assertEqual(res["rejected"], [])

        # 300 and 600 retain the previous state
        boundary_res = simulate_hysteresis([300, 600, 299, 300, 600, 601])
        self.assertEqual(boundary_res["states"], ["off", "off", "on", "on", "on", "off"])

    def test_out_of_range_and_invalid_readings_rejected(self):
        res = simulate_hysteresis([-1, 0, 1023, 1024, "500", True])
        self.assertEqual(res["states"], ["on", "off"])
        self.assertEqual(len(res["rejected"]), 4)

    def test_configuration_comparison_tradeoff(self):
        noisy = [650, 280, 450, 550, 290, 520, 620, 350]
        runs = compare_configurations(noisy)
        self.assertEqual(len(runs), 3)
        by_name = {r["config"]: r for r in runs}
        # Narrow band switches more frequently than wide band
        self.assertGreaterEqual(
            by_name["narrow_band_400_500"]["transitions"],
            by_name["wide_band_200_700"]["transitions"],
        )


if __name__ == "__main__":
    unittest.main()
