# -*- coding: utf-8 -*-
"""
tests/test_pahad_seismic_integration.py
=======================================
Integration tests for Seismic Intelligence flowing into PAHAD AI.
Verifies:
- Seismic events populating Dimension 4 (Seismic) of PAHAD unified feature vector
- PGA proxy calculations and modifier points added to CRI
- 2-of-3 Signal Confirmation Safety Rule (seismic alone cannot force false RED alarm)
- Provenance honesty and graceful degradation
"""

import unittest
import os

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_inputs import build_pahad_feature_vector
from engine.pahad_models import evaluate_pahad_fused_risk
from services.seismic_service import SEISMIC_SERVICE


class TestPahadSeismicIntegration(unittest.TestCase):

    def test_seismic_feature_vector_ingestion(self):
        """Verify SEISMIC_SERVICE outputs correctly populate Dimension 4 of PAHAD feature vector."""
        vector = build_pahad_feature_vector("SK-NH10-KM48")
        self.assertIn("raw_contract", vector)
        self.assertIn("seismic", vector["raw_contract"])
        seis = vector["raw_contract"]["seismic"]
        
        # Verify mandatory fields in Seismic Dimension
        self.assertIn("recent_event_id", seis)
        self.assertIn("magnitude", seis)
        self.assertIn("distance_km", seis)
        self.assertIn("shaking_proxy_g", seis)
        self.assertIn("trigger_level", seis)
        self.assertIn("risk_adjustment", seis)
        self.assertIn("provenance", seis)
        
        # Verify numerical features
        self.assertIn("features", vector)
        self.assertIn("seismic_magnitude", vector["features"])
        self.assertIn("seismic_shaking_proxy_g", vector["features"])

    def test_seismic_shaking_proxy_elevates_cri(self):
        """Verify that high PGA shaking proxy adds modifier points to final CRI."""
        # 1. Neutral seismic state (small distant event)
        neutral_res = evaluate_pahad_fused_risk(
            sector_id="SK-NH10-KM48",
            overrides={"seismic_risk_adjustment": 0.0, "seismic_shaking_proxy_g": 0.005}
        )
        
        # 2. Strong local shaking (M5.5 at 25km, high PGA)
        elevated_res = evaluate_pahad_fused_risk(
            sector_id="SK-NH10-KM48",
            overrides={"seismic_risk_adjustment": 0.30, "seismic_shaking_proxy_g": 0.22}
        )
        
        self.assertGreater(elevated_res["cri"], neutral_res["cri"])
        self.assertEqual(elevated_res["seismic_trigger"]["trigger_level"], "VERY_HIGH")
        self.assertEqual(elevated_res["seismic_trigger"]["risk_adjustment"], 0.30)

    def test_2_of_3_signal_safety_rule_with_seismic(self):
        """
        Verify that even with an elevated seismic modifier, if Physical FoS is stable (> 1.2)
        and Rainfall is within threshold, the 2-of-3 safety rule prevents a false RED alarm.
        """
        res = evaluate_pahad_fused_risk(
            sector_id="SK-NH10-KM48",
            overrides={
                "cohesion_kpa": 45.0,
                "friction_deg": 38.0,
                "slope_deg": 22.0,
                "pore_water_pressure_kpa": 2.0,
                "rainfall_24h_mm": 5.0,
                "rainfall_current_mmh": 0.2,
                "seismic_risk_adjustment": 0.30,
                "seismic_shaking_proxy_g": 0.22
            }
        )
        
        # Physical is stable (FoS > 1.0)
        self.assertFalse(res["signal_agreement"]["physical"], "Physical FoS must be safe")
        # Rainfall is within threshold
        self.assertFalse(res["signal_agreement"]["rainfall"], "Rainfall must be within threshold")
        # Therefore, signal count < 2, and risk band cannot be forced to EXTREME/RED
        self.assertLess(res["signal_agreement"]["count"], 2)
        self.assertNotEqual(res["risk_band"], "EXTREME", "Cannot declare EXTREME alarm without 2-of-3 signal convergence")

    def test_provenance_honesty_in_seismic_payload(self):
        """Verify seismic provenance badge contains only valid system states."""
        vector = build_pahad_feature_vector("SK-NH10-KM48")
        prov = vector["raw_contract"]["seismic"]["provenance"]
        self.assertTrue(
            any(tag in prov for tag in ["LIVE", "CACHED", "SIMULATED", "DEMO", "DEGRADED"]),
            f"Provenance '{prov}' must contain an honest system badge"
        )


if __name__ == "__main__":
    unittest.main()
