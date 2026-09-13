"""
PHASE 7F — CP 7F-08 & 7F-09: Provenance Normalization & Terrain Authority Tests
Verifies that all provenance values conform to the normalized vocabulary,
simulated seismic events are honestly tagged SIMULATED, and terrain feature authority
resolves the 0.0 placeholder vs 39.0 corridor registry baseline honestly.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_live_inference import run_live_inference
from services.seismic_service import SeismicService
from services.dem_service import DEMService


class TestProvenanceAndTerrainAuthority(unittest.TestCase):
    """CP 7F-08 & 7F-09: Provenance normalization & terrain authority resolution."""

    SECTOR = "CORR-NH10-SIKKIM-KM48"
    LAT = 27.2056
    LON = 88.4986

    VALID_PROVENANCES = {
        "LIVE", "CACHED", "DERIVED", "MODELLED", "SIMULATED", "HIL",
        "MISSING", "AUTH_REQUIRED", "UNAVAILABLE"
    }

    def test_01_all_feature_provenance_badges_normalized(self):
        """All feature provenance entries in snapshot must use valid normalized vocabulary."""
        res = run_live_inference(self.SECTOR, self.LAT, self.LON)
        for fp in res.feature_provenance:
            prov = fp["provenance"]
            self.assertIn(prov, self.VALID_PROVENANCES,
                          f"Feature {fp['feature']} has non-standard provenance: '{prov}'")

    def test_02_simulated_seismic_is_tagged_simulated(self):
        """SIM-EQ-NER-01 scenario earthquake must be tagged SIMULATED, never plain CACHED."""
        svc = SeismicService()
        ev = svc.get_latest_event()
        if ev and str(ev.get("event_id", "")).startswith("SIM-"):
            # Provenance must be SIMULATED
            self.assertEqual(ev.get("provenance"), "SIMULATED",
                             f"Simulated event {ev.get('event_id')} must have provenance=SIMULATED")

        # Also verify in live inference snapshot
        res = run_live_inference(self.SECTOR, self.LAT, self.LON)
        seismic_prov = next((fp for fp in res.feature_provenance if fp["feature"] == "seismic"), None)
        if seismic_prov and "SIM" in seismic_prov.get("source", ""):
            self.assertEqual(seismic_prov["provenance"], "SIMULATED",
                             "Simulated scenario earthquake in feature_provenance must be SIMULATED")

    def test_03_terrain_authority_resolves_placeholder_to_modelled(self):
        """DEM slope 0.0 placeholder must resolve to Corridor Registry slope stamped MODELLED."""
        res = run_live_inference(self.SECTOR, self.LAT, self.LON)
        d = res.to_dict()

        # Slope should be a realistic steep mountain value (>30 deg)
        slope_used = d["features_used"].get("slope_deg")
        self.assertIsNotNone(slope_used)
        self.assertGreater(float(slope_used), 30.0,
                           f"Mountain slope at KM48 must be steep (>30 deg), got: {slope_used}")

        # Provenance for slope_deg must be MODELLED (derived from corridor baseline, not raw live DEM)
        slope_prov = next((fp for fp in res.feature_provenance if fp["feature"] == "slope_deg"), None)
        self.assertIsNotNone(slope_prov)
        self.assertEqual(slope_prov["provenance"], "MODELLED")
        self.assertIn("Corridor Registry", slope_prov["source"])

    def test_04_dem_point_query_identified_as_historical(self):
        """Raw DEM metadata must specify [HISTORICAL], never [LIVE]."""
        svc = DEMService()
        meta = svc.get_metadata()
        self.assertEqual(meta.get("provenance"), "[HISTORICAL]")


if __name__ == "__main__":
    unittest.main()
