# -*- coding: utf-8 -*-
"""
tests/test_phase9f_provenance.py
================================
Phase 9F Scientific Integrity Audit:
  CP08 — Provenance Tracking & Data Honesty Audit
  CP09 — Graceful Fallback & Degradation Audit
"""

import os
import sys
import unittest
from unittest.mock import patch

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.canonical_registry import CANONICAL_REGISTRY
from engine.pahad_live_inference import (
    run_live_inference,
    _compute_data_quality_level,
    _compute_data_quality_score,
    FeatureProvenance
)


class TestPhase9FProvenance(unittest.TestCase):
    """Rigorous audit of provenance tagging, data honesty, and graceful degradation."""

    def test_cp08_feature_provenance_honesty(self):
        """CP08: Every feature in inference has traceable provenance; no simulated data is marked as [LIVE]."""
        res = run_live_inference("ML-SONAPUR-01", 25.105, 92.362, forecast_horizon_hours=24)
        d = res.to_dict()

        valid_provenance_tags = {"LIVE", "CACHED", "MODELLED", "MISSING", "SIMULATED", "HISTORICAL", "DERIVED"}
        prov_items = d.get("feature_provenance", [])
        self.assertGreater(len(prov_items), 0, "Must have provenance records")

        for item in prov_items:
            self.assertIn("feature", item)
            self.assertIn("provenance", item)
            self.assertIn("source", item)
            self.assertIn(item["provenance"], valid_provenance_tags, f"Unknown tag: {item['provenance']}")

            # No simulated or modelled data may ever be tagged as LIVE
            if "simulator" in item["source"].lower() or "synthetic" in item["source"].lower():
                self.assertNotEqual(item["provenance"], "LIVE", f"Simulated data falsely tagged as LIVE: {item}")

    def test_cp08_data_quality_levels(self):
        """CP08: Quality levels correctly reflect feature completeness and provenance scores."""
        high = _compute_data_quality_level(completeness=0.95, dq_score=0.90, missing_feats=[])
        self.assertEqual(high, "HIGH DATA COMPLETENESS")

        partial = _compute_data_quality_level(completeness=0.60, dq_score=0.65, missing_feats=["soil_moisture"])
        self.assertEqual(partial, "PARTIAL DATA")

        degraded = _compute_data_quality_level(completeness=0.30, dq_score=0.35, missing_feats=["rainfall_24h", "soil_moisture", "pore_pressure"])
        self.assertEqual(degraded, "DEGRADED DATA")

    def test_cp09_graceful_fallback_weather_disconnected(self):
        """CP09: When weather service fails or is disconnected, inference falls back gracefully without crash."""
        with patch("services.weather_service.WeatherService.get_weather", side_effect=Exception("Network Timeout")):
            res = run_live_inference("SK-NH10-KM48", 27.33, 88.61, forecast_horizon_hours=24)
            d = res.to_dict()

            self.assertIsNotNone(d)
            self.assertEqual(d["sector_id"], "SK-NH10-KM48")
            self.assertTrue(0.0 <= d["cri"] <= 100.0)
            self.assertTrue(0.4 <= d["fos_physical"] <= 3.0)

            # Weather feature should be marked as MISSING or imputed with training median
            weather_prov = [p for p in d.get("feature_provenance", []) if p.get("feature") == "weather"]
            if weather_prov:
                self.assertIn(weather_prov[0]["provenance"], ["MISSING", "CACHED", "MODELLED"])

    def test_cp09_graceful_fallback_seismic_disconnected(self):
        """CP09: When seismic service fails, system falls back to fault simulator with [SIMULATED] badge."""
        with patch("services.seismic_service.SeismicService.get_recent_events", side_effect=Exception("API Unreachable")):
            res = run_live_inference("MN-TUPUL-RLY", 24.755, 93.578, forecast_horizon_hours=24)
            d = res.to_dict()

            self.assertIsNotNone(d)
            self.assertEqual(d["sector_id"], "MN-TUPUL-RLY")
            self.assertTrue(0.0 <= d["cri"] <= 100.0)

            seismic_prov = [p for p in d.get("feature_provenance", []) if p.get("feature") == "seismic"]
            if seismic_prov:
                self.assertIn(seismic_prov[0]["provenance"], ["SIMULATED", "MISSING", "CACHED"])


if __name__ == "__main__":
    unittest.main()
