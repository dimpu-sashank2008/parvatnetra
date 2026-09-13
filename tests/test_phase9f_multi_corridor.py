# -*- coding: utf-8 -*-
"""
tests/test_phase9f_multi_corridor.py
====================================
Phase 9F Multi-Corridor Audit:
  CP05 — Corridor Isolation (Zero cross-corridor state bleed)
  CP07 — Risk-Band Consistency across Canonical NER Corridors
  CP10 — Multi-corridor API Verification
"""

import os
import sys
import unittest
import json

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.canonical_registry import CANONICAL_REGISTRY
from engine.pahad_live_inference import run_live_inference
from app import app as flask_app


class TestPhase9FMultiCorridor(unittest.TestCase):
    """Corridor isolation, risk band consistency, and multi-corridor API audit."""

    def setUp(self):
        self.client = flask_app.test_client()
        self.audit_corridors = [
            ("ML-SONAPUR-01", "Meghalaya", "East Jaintia Hills", 25.105, 92.362),
            ("SK-NH10-KM48", "Sikkim", "Pakyong", 27.330, 88.610),
            ("MN-TUPUL-RLY", "Manipur", "Noney", 24.755, 93.578),
            ("AR-TAWANG-SELA", "Arunachal Pradesh", "Tawang", 27.580, 91.850),
            ("MZ-MELTHUM-QRY", "Mizoram", "Aizawl", 23.895, 92.960),
            ("NL-DZUKOU-KOH", "Nagaland", "Kohima", 25.582, 94.120)
        ]

    def test_cp05_corridor_isolation_sequential_invariance(self):
        """CP05: Sequential inference across corridors maintains strict isolation with zero state bleed."""
        results = {}

        for cid, state, dist, lat, lon in self.audit_corridors:
            loc = CANONICAL_REGISTRY.get_location(cid)
            self.assertIsNotNone(loc, f"Location {cid} must exist")
            self.assertEqual(loc.state, state)
            self.assertEqual(loc.district, dist)

            res = run_live_inference(sector_id=cid, latitude=lat, longitude=lon, forecast_horizon_hours=24)
            d = res.to_dict()

            # Ensure response metadata strictly matches the requested corridor
            self.assertEqual(d["sector_id"], cid)
            self.assertAlmostEqual(d["latitude"], lat, places=3)
            self.assertAlmostEqual(d["longitude"], lon, places=3)
            results[cid] = d

        # Verify all coordinates are distinct
        all_coords = [(results[c]["latitude"], results[c]["longitude"]) for c in results]
        self.assertEqual(len(all_coords), len(set(all_coords)), "Each corridor must have a unique coordinate signature")

        # Verify that switching back to the first corridor reproduces the exact same result (deterministic isolation)
        first_cid, _, _, first_lat, first_lon = self.audit_corridors[0]
        retest_res = run_live_inference(sector_id=first_cid, latitude=first_lat, longitude=first_lon, forecast_horizon_hours=24)
        retest_d = retest_res.to_dict()

        self.assertEqual(retest_d["sector_id"], results[first_cid]["sector_id"])
        self.assertEqual(retest_d["fos_physical"], results[first_cid]["fos_physical"])
        self.assertEqual(retest_d["cri"], results[first_cid]["cri"])

    def test_cp07_risk_band_consistency(self):
        """CP07: Risk bands strictly align with CRI numerical thresholds."""
        for cid, _, _, lat, lon in self.audit_corridors:
            res = run_live_inference(sector_id=cid, latitude=lat, longitude=lon, forecast_horizon_hours=24)
            cri = res.cri
            band = res.risk_band

            if cri >= 80.0:
                self.assertEqual(band, "EXTREME", f"CRI {cri} must be EXTREME")
            elif cri >= 60.0:
                self.assertEqual(band, "VERY_HIGH", f"CRI {cri} must be VERY_HIGH")
            elif cri >= 40.0:
                self.assertEqual(band, "HIGH", f"CRI {cri} must be HIGH")
            elif cri >= 20.0:
                self.assertEqual(band, "MODERATE", f"CRI {cri} must be MODERATE")
            else:
                self.assertEqual(band, "LOW", f"CRI {cri} must be LOW")

    def test_cp10_api_location_risk_multi_corridor(self):
        """CP10: /api/pahad/location-risk serves accurate, isolated payloads for all audit corridors."""
        for cid, state, dist, _, _ in self.audit_corridors:
            payload = {"location_id": cid, "horizon_hours": 24}
            resp = self.client.post(
                "/api/pahad/location-risk",
                data=json.dumps(payload),
                content_type="application/json"
            )
            self.assertEqual(resp.status_code, 200, f"Failed for {cid}")
            data = resp.get_json()

            self.assertEqual(data["status"], "SUCCESS")
            inf = data["inference"]
            self.assertEqual(inf["sector_id"], cid)
            self.assertIn("cri", inf)
            self.assertIn("fos_physical", inf)
            self.assertIn("risk_band", inf)
            self.assertIn("top_drivers", inf)
            self.assertIn("explanation", inf)

            loc_meta = data["location"]
            self.assertEqual(loc_meta["id"], cid)
            self.assertEqual(loc_meta["state"], state)


if __name__ == "__main__":
    unittest.main()
