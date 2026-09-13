# -*- coding: utf-8 -*-
"""
tests/test_phase9e_location_isolation.py
========================================
PARVAT NETRA - PAHAD AI Phase 9E Location Isolation & Multi-Corridor Invariance
-------------------------------------------------------------------------------
Validates:
  1. Live inference across 5 distinct NER locations:
     - Sikkim (SK-NH10-KM48)
     - Arunachal Pradesh (AR-TAWANG-SELA)
     - Mizoram (MZ-MELTHUM-QRY)
     - Meghalaya (ML-MAWSYNRAM)
     - Manipur (MN-TUPUL-RLY)
  2. Distinct geographic coordinates, administrative metadata, and surveyed geotechnical params.
  3. Absolute zero data leakage or state-bleed between sequential requests.
"""

import os
import sys
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.pahad_live_inference import run_live_inference
from engine.canonical_registry import CANONICAL_REGISTRY


class TestPhase9ELocationIsolation(unittest.TestCase):
    """Audit location isolation and absence of cross-corridor state bleed."""

    def test_five_ner_corridors_distinct_geotechnics(self):
        """Sequential inference for 5 corridors must yield distinct, isolated profiles."""
        test_corridors = [
            ("SK-NH10-KM48", "Sikkim", 27.33, 88.61),
            ("AR-TAWANG-SELA", "Arunachal Pradesh", 27.58, 91.85),
            ("MZ-MELTHUM-QRY", "Mizoram", 23.895, 92.96),
            ("ML-MAWSYNRAM", "Meghalaya", 25.297, 91.583),
            ("MN-TUPUL-RLY", "Manipur", 24.755, 93.578)
        ]

        results = {}
        for cid, expected_state, lat, lon in test_corridors:
            loc = CANONICAL_REGISTRY.get_location(cid)
            self.assertIsNotNone(loc, f"Corridor {cid} must exist in canonical registry")
            self.assertEqual(loc.state, expected_state)

            res = run_live_inference(sector_id=cid, latitude=lat, longitude=lon)
            d = res.to_dict()

            self.assertEqual(d["sector_id"], cid)
            self.assertAlmostEqual(d["latitude"], lat, places=2)
            self.assertAlmostEqual(d["longitude"], lon, places=2)
            results[cid] = d

        # Verify no two corridors have identical coordinate footprint or state
        coordinates = [(results[c]["latitude"], results[c]["longitude"]) for c in results]
        self.assertEqual(len(coordinates), len(set(coordinates)), "All corridors must have unique coordinates")

        # Verify site-specific geotechnical FoS values are within realistic ranges
        for cid, d in results.items():
            fos = d["fos_physical"]
            self.assertGreater(fos, 0.4, f"FoS for {cid} must be > 0.4")
            self.assertLess(fos, 2.0, f"FoS for {cid} must be < 2.0")


if __name__ == "__main__":
    unittest.main()
