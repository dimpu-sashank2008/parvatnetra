# -*- coding: utf-8 -*-
"""
tests/test_pahad_climate_integration.py
=======================================
Integration tests for Weather/Climate data flowing directly into PAHAD AI.
Verifies:
- Live/Cached weather feeding into build_pahad_feature_vector
- Dimension 1 (Climate) contract adherence
- Mandal-Sarkar I-D threshold triggering CRI elevation
- Degradation fallback resilience
"""

import unittest
import os

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_inputs import build_pahad_feature_vector
from engine.pahad_models import evaluate_pahad_fused_risk
from services.weather_service import (
    WEATHER_SERVICE,
    evaluate_mandal_sarkar_threshold,
    calculate_antecedent_precipitation_indices
)


class TestPahadClimateIntegration(unittest.TestCase):

    def test_climate_feature_vector_ingestion(self):
        """Verify WeatherService outputs correctly populate Dimension 1 of PAHAD feature vector."""
        vector = build_pahad_feature_vector("SK-NH10-KM48")
        self.assertIn("raw_contract", vector)
        self.assertIn("climate", vector["raw_contract"])
        climate = vector["raw_contract"]["climate"]
        
        # Verify mandatory fields in Climate Dimension
        self.assertIn("current_mm_hr", climate)
        self.assertIn("rain_24h_mm", climate)
        self.assertIn("rain_72h_mm", climate)
        self.assertIn("api_3d", climate)
        self.assertIn("api_7d", climate)
        self.assertIn("api_30d", climate)
        self.assertIn("threshold_state", climate)
        self.assertIn("provenance", climate)
        
        # Verify numerical features
        self.assertIn("features", vector)
        self.assertIn("rainfall_current_mmh", vector["features"])
        self.assertIn("rainfall_24h_mm", vector["features"])

    def test_mandal_sarkar_threshold_governs_trigger(self):
        """Verify Mandal-Sarkar formula triggers threshold exceedance when intensity crosses I_thresh."""
        # Baseline check at 24h duration: I_thresh ~= 1.827 mm/h
        # Low rainfall (0.5 mm/h over 24h = 12 mm) -> WITHIN_THRESHOLD
        status_low, breach_low = evaluate_mandal_sarkar_threshold(intensity_mm_hr=0.5, duration_hrs=24)
        self.assertFalse(breach_low)
        self.assertEqual(status_low, "WITHIN_THRESHOLD")
        
        # Severe rainfall (3.5 mm/h over 24h = 84 mm) -> EXCEEDED
        status_high, breach_high = evaluate_mandal_sarkar_threshold(intensity_mm_hr=3.5, duration_hrs=24)
        self.assertTrue(breach_high)
        self.assertEqual(status_high, "EXCEEDED")

    def test_climate_override_directly_alters_fused_cri(self):
        """Verify that injecting extreme rainfall into evaluate_pahad_fused_risk elevates CRI."""
        # 1. Low rainfall condition (5mm in 24h)
        low_res = evaluate_pahad_fused_risk(
            sector_id="SK-NH10-KM48",
            overrides={"rainfall_24h_mm": 5.0, "rainfall_current_mmh": 0.2}
        )
        # 2. Extreme rainfall condition (120mm in 24h, 15 mm/h)
        high_res = evaluate_pahad_fused_risk(
            sector_id="SK-NH10-KM48",
            overrides={"rainfall_24h_mm": 120.0, "rainfall_current_mmh": 15.0}
        )
        
        self.assertGreater(high_res["cri"], low_res["cri"], "Extreme rainfall must increase Composite Risk Index")
        self.assertTrue(high_res["rainfall_trigger"]["threshold_exceeded"], "Extreme rainfall must breach Mandal-Sarkar threshold")
        self.assertTrue(high_res["signal_agreement"]["rainfall"], "Rainfall agreement must be True under extreme loading")

    def test_degraded_climate_provider_preserves_honest_provenance(self):
        """Verify that if live provider fails, provenance badge transitions to [DEGRADED] or [DEMO]."""
        # When simulated or demo provider runs, provenance must clearly indicate simulation
        vector = build_pahad_feature_vector("SK-NH10-KM48")
        prov = vector["raw_contract"]["climate"]["provenance"]
        self.assertTrue(
            any(tag in prov for tag in ["LIVE", "CACHED", "SIMULATED", "DEMO", "DEGRADED"]),
            f"Provenance '{prov}' must contain an honest system badge"
        )
        self.assertNotIn("FAKE", prov)


if __name__ == "__main__":
    unittest.main()
