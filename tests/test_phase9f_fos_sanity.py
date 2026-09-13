# -*- coding: utf-8 -*-
"""
tests/test_phase9f_fos_sanity.py
================================
Phase 9F Scientific Integrity Audit:
  CP03 — FoS Scientific Sanity & Physical Mechanics Verification
  - Validates Mohr-Coulomb infinite slope limit equilibrium mechanics
  - Audits all 26 canonical corridors for absence of FoS <= 0, FoS > 3, FoS > 10
  - Verifies geotechnical sensitivity to slope gradient and pore pressure
  - Ensures anomalous FoS values (if any) provide scientific explanations without artificial clamping
"""

import os
import sys
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.canonical_registry import CANONICAL_REGISTRY
from engine.pahad_models import calculate_infinite_slope_fs
from engine.pahad_live_inference import run_live_inference


class TestPhase9FFoSSanity(unittest.TestCase):
    """Rigorous audit of Factor of Safety (FoS) calculations and geotechnical sanity."""

    def test_cp03_all_canonical_corridors_fos_in_realistic_bounds(self):
        """CP03: All 26 canonical corridors must produce 0.4 < FoS <= 2.5 without anomalies."""
        locations = CANONICAL_REGISTRY.list_locations()
        anomalies = []

        for loc in locations:
            res = run_live_inference(sector_id=loc.id, latitude=loc.lat, longitude=loc.lon, forecast_horizon_hours=24)
            fos = res.fos_physical

            if fos <= 0.0:
                anomalies.append(f"{loc.id}: FoS <= 0 ({fos})")
            elif fos > 3.0:
                anomalies.append(f"{loc.id}: FoS > 3.0 ({fos})")

            self.assertGreater(fos, 0.4, f"FoS must be greater than 0.4 for {loc.id}, got {fos}")
            self.assertLessEqual(fos, 2.5, f"FoS must be <= 2.5 for surveyed steep slope {loc.id}, got {fos}")

        self.assertEqual(len(anomalies), 0, f"No FoS anomalies allowed across canonical corridors: {anomalies}")

    def test_cp03_infinite_slope_mechanics(self):
        """Mohr-Coulomb limit equilibrium equation obeys physical invariants."""
        # Baseline slope calculation
        res_baseline = calculate_infinite_slope_fs(
            cohesion_kpa=15.0,
            friction_deg=28.0,
            slope_deg=35.0,
            soil_depth_m=3.0,
            water_table_ratio=0.3,
            soil_sat_weight=18.5
        )
        fos_base = res_baseline.factor_of_safety
        self.assertGreater(fos_base, 0.5)
        self.assertLess(fos_base, 2.5)

        # 1. Steeper slope must reduce FoS
        res_steep = calculate_infinite_slope_fs(
            cohesion_kpa=15.0,
            friction_deg=28.0,
            slope_deg=48.0,
            soil_depth_m=3.0,
            water_table_ratio=0.3,
            soil_sat_weight=18.5
        )
        self.assertLess(res_steep.factor_of_safety, fos_base, "Steeper slope must reduce FoS")

        # 2. Water table rise (higher pore pressure) must reduce FoS
        res_saturated = calculate_infinite_slope_fs(
            cohesion_kpa=15.0,
            friction_deg=28.0,
            slope_deg=35.0,
            soil_depth_m=3.0,
            water_table_ratio=0.9,
            soil_sat_weight=18.5
        )
        self.assertLess(res_saturated.factor_of_safety, fos_base, "Water table rise must reduce effective stress and FoS")

        # 3. Increased cohesion must increase FoS
        res_high_c = calculate_infinite_slope_fs(
            cohesion_kpa=30.0,
            friction_deg=28.0,
            slope_deg=35.0,
            soil_depth_m=3.0,
            water_table_ratio=0.3,
            soil_sat_weight=18.5
        )
        self.assertGreater(res_high_c.factor_of_safety, fos_base, "Higher soil cohesion must increase FoS")

    def test_cp03_explanation_for_unusual_terrain(self):
        """Very flat slopes (e.g. 5 deg) produce high FoS which must have scientific explanation without clamping."""
        res_flat = run_live_inference(
            sector_id="SYNTH-FLAT",
            latitude=26.0,
            longitude=91.0,
            override_features={"slope_deg": 5.0, "pore_pressure_kpa": 0.0}
        )
        # On a 5-degree slope, gravity shear stress is tiny, so FoS is naturally high
        self.assertGreater(res_flat.fos_physical, 3.0)
        # Explanation must clarify that high FoS is due to gentle slope mechanics, not clamped
        exp = res_flat.to_dict().get("anomalous_fos_explanation")
        self.assertTrue(
            exp is not None or "slope" in str(res_flat.explanation).lower(),
            "Gentle terrain FoS must be explained scientifically"
        )


if __name__ == "__main__":
    unittest.main()
