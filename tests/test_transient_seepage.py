# -*- coding: utf-8 -*-
"""
tests/test_transient_seepage.py
===============================
Validates Geotechnical Transient Unsaturated Seepage & Dynamic Pore Pressure Engine:
1. van Genuchten (1980) SWCC saturation curve properties.
2. Infiltration wetting front descent under rainfall.
3. Matric suction dissipation and positive basal pore-water pressure accumulation.
4. Dynamic Factor of Safety FoS(t) degradation to failure under cloudburst deluge.
5. Stability retention under dry / gentle rainfall regimes.
"""

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.transient_seepage import (
    SoilHydraulicParams,
    van_genuchten_saturation,
    simulate_transient_seepage
)


class TestTransientSeepage(unittest.TestCase):

    def test_01_van_genuchten_swcc_curve(self):
        """Test SWCC effective saturation function properties."""
        params = SoilHydraulicParams()
        # Zero suction = fully saturated
        s_0 = van_genuchten_saturation(0.0, params.alpha_kpa, params.n_index, params.m_index)
        self.assertEqual(s_0, 1.0)

        # Increasing suction monotonically decreases saturation
        s_10 = van_genuchten_saturation(10.0, params.alpha_kpa, params.n_index, params.m_index)
        s_50 = van_genuchten_saturation(50.0, params.alpha_kpa, params.n_index, params.m_index)
        s_100 = van_genuchten_saturation(100.0, params.alpha_kpa, params.n_index, params.m_index)

        self.assertGreater(s_0, s_10)
        self.assertGreater(s_10, s_50)
        self.assertGreater(s_50, s_100)
        self.assertGreaterEqual(s_100, 0.0)

    def test_02_dry_regime_slope_remains_stable(self):
        """Verify dry slope with zero precipitation maintains stable FoS > 1.2."""
        dry_rain = [0.0] * 24
        res = simulate_transient_seepage(
            rainfall_hourly_mm=dry_rain,
            slope_angle_deg=35.0,
            slip_depth_m=4.0
        )
        self.assertEqual(res.status, "STABLE")
        self.assertGreater(res.min_factor_of_safety, 1.20)
        self.assertIsNone(res.time_to_failure_hours)

    def test_03_deluge_triggers_wetting_and_failure(self):
        """Verify 24h severe cloudburst deluge (210mm) on 42 deg slope causes collapse."""
        # Realistic monsoon deluge sequence with peak intensity 28 mm/h
        storm_rain = [
            2.0, 4.0, 6.0, 8.0, 14.0, 22.0, 28.0, 25.0, 20.0, 16.0,
            12.0, 10.0, 8.0, 6.0, 5.0, 4.0, 4.0, 3.0, 3.0, 2.0,
            2.0, 2.0, 1.0, 1.0
        ]
        self.assertGreater(sum(storm_rain), 200.0)

        res = simulate_transient_seepage(
            rainfall_hourly_mm=storm_rain,
            slope_angle_deg=42.0,
            slip_depth_m=2.0,
            initial_suction_kpa=25.0,
            initial_volumetric_moisture=0.36
        )

        self.assertEqual(res.status, "CRITICAL_COLLAPSE")
        self.assertLess(res.min_factor_of_safety, 1.0)
        self.assertIsNotNone(res.time_to_failure_hours)
        self.assertGreater(res.time_to_failure_hours, 4)

        # Wetting front reached slip depth
        self.assertAlmostEqual(res.max_wetting_depth_m, 2.0, places=1)
        # Positive pore water pressure developed
        self.assertGreater(res.max_pore_pressure_kpa, 0.0)

    def test_04_wetting_front_monotonic_during_rain(self):
        """Verify wetting front monotonically descends through soil column."""
        rain = [10.0] * 12
        res = simulate_transient_seepage(
            rainfall_hourly_mm=rain,
            slope_angle_deg=38.0,
            slip_depth_m=4.5
        )
        depths = [ep.wetting_front_depth_m for ep in res.epochs]
        for i in range(1, len(depths)):
            self.assertGreaterEqual(depths[i], depths[i - 1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
