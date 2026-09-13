# -*- coding: utf-8 -*-
"""
tests/test_phase9f_scientific_integrity.py
==========================================
Phase 9F Multi-Corridor Scientific Integrity Audit:
  CP01 — Canonical Corridor Audit (all 26 canonical locations valid, no duplicates)
  CP02 — Live Inference Pipeline Audit
  CP04 — CRI Monotonicity and Consistency
  CP06 — Highest-Risk Default Corridor Selection
"""

import os
import sys
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.canonical_registry import CANONICAL_REGISTRY
from engine.pahad_live_inference import run_live_inference
from engine.pahad_fusion import PahadFusionEngine
from app import app as flask_app


class TestPhase9FScientificIntegrity(unittest.TestCase):
    """Scientific integrity audit tests for Phase 9F."""

    def setUp(self):
        self.client = flask_app.test_client()

    def test_cp01_canonical_registry_completeness(self):
        """CP01: Exactly 26 canonical locations across NER, valid coordinates and surveyed geology."""
        locations = CANONICAL_REGISTRY.list_locations()
        self.assertEqual(len(locations), 26, "Must have exactly 26 canonical locations")

        ids = [loc.id for loc in locations]
        self.assertEqual(len(ids), len(set(ids)), "All 26 location IDs must be unique (zero duplicates)")

        # Verify NER state coverage
        states = set(loc.state for loc in locations)
        expected_states = {
            "Sikkim", "Arunachal Pradesh", "Assam", "Manipur",
            "Meghalaya", "Mizoram", "Nagaland", "Tripura", "West Bengal"
        }
        self.assertTrue(expected_states.issubset(states), f"All NER states + border corridor must be covered. Got: {states}")

        for loc in locations:
            self.assertTrue(20.0 <= loc.lat <= 30.0, f"Lat out of NER bounds for {loc.id}: {loc.lat}")
            self.assertTrue(88.0 <= loc.lon <= 98.0, f"Lon out of NER bounds for {loc.id}: {loc.lon}")
            self.assertTrue(30.0 <= loc.slope_deg <= 60.0, f"Surveyed slope out of realistic bounds for {loc.id}: {loc.slope_deg}")
            self.assertTrue(100.0 <= loc.elevation_m <= 5000.0, f"Surveyed elevation out of realistic bounds for {loc.id}: {loc.elevation_m}")
            self.assertTrue(len(loc.highway) > 0, f"Highway name missing for {loc.id}")

    def test_cp02_live_inference_bounds_across_corridors(self):
        """CP02: Real live inference across representative corridors yields strictly bounded outputs."""
        sample_corridors = [
            "ML-SONAPUR-01", "SK-NH10-KM48", "MN-TUPUL-RLY",
            "AR-TAWANG-SELA", "MZ-MELTHUM-QRY", "NL-DZUKOU-KOH"
        ]
        for cid in sample_corridors:
            loc = CANONICAL_REGISTRY.get_location(cid)
            self.assertIsNotNone(loc)
            res = run_live_inference(sector_id=cid, latitude=loc.lat, longitude=loc.lon, forecast_horizon_hours=24)
            d = res.to_dict()

            # Boundedness checks
            self.assertTrue(0.0 <= d["cri"] <= 100.0, f"CRI must be in [0, 100] for {cid}, got {d['cri']}")
            self.assertTrue(0.4 <= d["fos_physical"] <= 3.0, f"FoS must be physically realistic for steep slope {cid}, got {d['fos_physical']}")
            self.assertTrue(0.0 <= d["event_probability"] <= 1.0, f"Event probability must be in [0, 1] for {cid}, got {d['event_probability']}")
            self.assertIn(d["risk_band"], ["LOW", "MODERATE", "HIGH", "VERY_HIGH", "EXTREME"])
            self.assertIn(d["data_quality_level"], ["HIGH DATA COMPLETENESS", "PARTIAL DATA", "DEGRADED DATA"])

    def test_cp04_cri_monotonicity(self):
        """CP04: CRI responds monotonically to lower FoS, higher rainfall, and higher probability."""
        fusion = PahadFusionEngine()

        # Baseline
        base = fusion.fuse(
            sector_id="TEST-CORR",
            fos_physical=1.5,
            rainfall_mm=10.0,
            event_probability_24h=0.10
        )
        base_cri = base["cri"]

        # 1. Lower FoS (slope closer to failure) -> CRI must increase or stay same
        unstable = fusion.fuse(
            sector_id="TEST-CORR",
            fos_physical=0.85,
            rainfall_mm=10.0,
            event_probability_24h=0.10
        )
        self.assertGreaterEqual(unstable["cri"], base_cri, "Lower FoS must result in higher or equal CRI")

        # 2. Extreme rainfall -> CRI must increase
        deluge = fusion.fuse(
            sector_id="TEST-CORR",
            fos_physical=1.5,
            rainfall_mm=180.0,
            event_probability_24h=0.10
        )
        self.assertGreater(deluge["cri"], base_cri, "High rainfall loading must increase CRI")

        # 3. High ML event probability -> CRI must be consistent
        ml_spike = fusion.fuse(
            sector_id="TEST-CORR",
            fos_physical=1.5,
            rainfall_mm=10.0,
            event_probability_24h=0.85
        )
        self.assertGreaterEqual(ml_spike["cri"], base_cri, "Elevated ML probability must maintain or elevate CRI")

    def test_cp06_highest_risk_corridor_endpoint(self):
        """CP06: /api/pahad/highest-risk-corridor evaluates all 26 corridors and selects highest CRI deterministically."""
        resp = self.client.get("/api/pahad/highest-risk-corridor")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["total_corridors_evaluated"], 26)
        top = data["highest_risk_corridor"]
        self.assertIsNotNone(top)
        self.assertIn("id", top)
        self.assertIn("cri", top)
        self.assertIn("fos", top)

        # Ranked list must be in descending order of CRI
        ranked = data["ranked_corridors"]
        self.assertEqual(len(ranked), 26)
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(
                ranked[i]["cri"], ranked[i + 1]["cri"],
                f"Ranked corridors must be sorted by CRI descending: {ranked[i]['id']} ({ranked[i]['cri']}) vs {ranked[i+1]['id']} ({ranked[i+1]['cri']})"
            )


if __name__ == "__main__":
    unittest.main()
