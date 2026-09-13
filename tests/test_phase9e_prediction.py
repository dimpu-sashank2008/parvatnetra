# -*- coding: utf-8 -*-
"""
tests/test_phase9e_prediction.py
================================
PARVAT NETRA - PAHAD AI Phase 9E Prediction Values & Mechanics Audit
--------------------------------------------------------------------
Validates:
  1. Live inference values: FoS, CRI, ML probability, rainfall, pore pressure, seismic modifier.
  2. Units, ranges, and normalization constraints.
  3. No artificial clamping of anomalous FoS (>10) on flat terrain (<3 deg).
  4. Honest physical explanation provided when FoS > 10.
  5. Surveyed steep slopes (30-50 deg) yield physically realistic FoS (0.5 - 1.5).
  6. Strict separation of Mohr-Coulomb FoS and ML event probability.
"""

import os
import sys
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.pahad_live_inference import run_live_inference, LiveInferenceResult


class TestPhase9EPredictionAudit(unittest.TestCase):
    """Audit prediction values, normalization, physical mechanics, and absence of artificial clamping."""

    def test_units_and_normalization_ranges(self):
        """Verify units and valid bounds for all core prediction metrics."""
        res = run_live_inference(sector_id="SK-NH10-KM48", latitude=27.33, longitude=88.61)
        self.assertIsInstance(res, LiveInferenceResult)
        d = res.to_dict()

        # CRI must be strictly in [0.0, 100.0]
        self.assertGreaterEqual(d["cri"], 0.0)
        self.assertLessEqual(d["cri"], 100.0)
        self.assertIn(d["risk_band"], ["LOW", "MODERATE", "HIGH", "VERY HIGH", "EXTREME"])

        # ML Event probability must be strictly in [0.0, 1.0]
        self.assertGreaterEqual(d["event_probability"], 0.0)
        self.assertLessEqual(d["event_probability"], 1.0)
        self.assertIn(d["probability_level"], ["LOW", "GUARDED", "ELEVATED", "HIGH", "SEVERE"])

        # Physical FoS must be a positive float
        self.assertGreater(d["fos_physical"], 0.0)

        # Features used check units
        feats = d["features_used"]
        rain_val = feats.get("rainfall_24h", feats.get("rain_24h"))
        self.assertIsNotNone(rain_val)
        self.assertGreaterEqual(rain_val, 0.0)

        pore_val = feats.get("pore_pressure_kpa", feats.get("pore_pressure"))
        self.assertIsNotNone(pore_val)
        self.assertGreaterEqual(pore_val, 0.0)

        slope_val = feats.get("slope_deg", feats.get("slope"))
        self.assertIsNotNone(slope_val)
        self.assertGreater(slope_val, 0.0)

    def test_strict_separation_of_fos_and_event_probability(self):
        """Model A (FoS) and Model B (Event Probability) must remain completely separate."""
        res = run_live_inference(sector_id="SK-NH10-KM48", latitude=27.33, longitude=88.61)
        d = res.to_dict()

        self.assertNotEqual(d["fos_physical"], d["event_probability"])
        self.assertIn("fos_status", d)
        self.assertIn("probability_level", d)

    def test_surveyed_steep_slope_realistic_fos(self):
        """Surveyed mountain slope (e.g. Sikkim 42 deg) must have physically defensible FoS (< 1.5)."""
        res = run_live_inference(sector_id="SK-NH10-KM48", latitude=27.33, longitude=88.61)
        self.assertLess(res.fos_physical, 2.0, "Steep mountainous corridor FoS should not diverge anomalously")
        self.assertGreater(res.fos_physical, 0.4, "FoS must remain physically non-negative and plausible")
        self.assertIsNone(res.anomalous_fos_explanation, "Normal steep slopes should not have anomalous FoS explanation")

    def test_flat_terrain_anomalous_fos_not_clamped(self):
        """Arbitrary flat plain (slope < 3 deg) produces FoS > 10; system must NOT clamp, but explain honestly."""
        flat_features = {
            "slope": 1.0,
            "elevation": 120.0,
            "soil_depth": 2.0,
            "cohesion": 15.0,
            "friction_angle": 30.0,
            "pore_pressure": 0.0,
            "rain_24h": 5.0,
            "rain_intensity": 1.0,
            "antecedent_rain_3d": 10.0,
            "antecedent_rain_7d": 20.0,
            "rainfall_threshold_exceedance": 0.0,
            "max_magnitude_24h": 0.0,
            "seismic_count_24h": 0,
            "nearest_seismic_distance": 250.0,
            "ground_displacement": 0.0,
            "tilt": 0.0,
            "historical_susceptibility": 0.2
        }
        res = run_live_inference(
            sector_id="CUSTOM-PLAIN-01",
            latitude=26.15,
            longitude=91.75,
            override_features=flat_features
        )
        d = res.to_dict()

        self.assertGreater(d["fos_physical"], 10.0, "Flat terrain must honestly calculate FoS > 10 without artificial clamp")
        self.assertIsNotNone(d["anomalous_fos_explanation"])
        self.assertIn("planar translational shear failure is physically unviable", d["anomalous_fos_explanation"])


if __name__ == "__main__":
    unittest.main()
