import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
from engine.geospatial_registry import GEOSPATIAL_REGISTRY
from engine.pahad_fusion import PahadFusionEngine


class TestProvenance(unittest.TestCase):
    """Tests data provenance protocol and strict badge integrity."""

    ALLOWED_BADGES = {"[LIVE]", "[CACHED]", "[HISTORICAL]", "[SIMULATED]", "[DEMO]", "[UNAVAILABLE]"}

    def test_geospatial_registry_provenance_badges(self):
        """Ensure all registered GIS datasets carry valid, standardized provenance badges."""
        manifest = GEOSPATIAL_REGISTRY.export_manifest()
        datasets = manifest.get("datasets", [])
        self.assertGreaterEqual(len(datasets), 5)

        for ds in datasets:
            prov = ds.get("provenance")
            self.assertIn(
                prov,
                self.ALLOWED_BADGES,
                f"Dataset {ds.get('dataset_id')} has invalid provenance badge: {prov}",
            )

    def test_insar_never_labeled_live_without_direct_satellite_feed(self):
        """InSAR satellite deformation in local prototype must be [SIMULATED] or [CACHED], NEVER [LIVE]."""
        ds = GEOSPATIAL_REGISTRY.get_dataset("SENTINEL1_SAR_LOS")
        self.assertIsNotNone(ds)
        self.assertNotEqual(
            ds.provenance,
            "[LIVE]",
            "Sentinel-1 SAR synthetic LOS displacement cannot be labeled as [LIVE]",
        )
        self.assertIn(ds.provenance, ["[SIMULATED]", "[CACHED]"])

    def test_fusion_prediction_provenance_structure(self):
        """Verify fusion engine output outputs detailed provenance for all evidence modalities."""
        engine = PahadFusionEngine()
        result = engine.fuse(sector_id="S_PROV_TEST")

        provenance_list = result.get("data_provenance", [])
        self.assertIsInstance(provenance_list, list)
        self.assertGreaterEqual(len(provenance_list), 4)

        sources = {p.get("source", "") for p in provenance_list}
        self.assertTrue(any("IMD" in s for s in sources), f"IMD missing in {sources}")
        self.assertTrue(any("GSI" in s for s in sources), f"GSI missing in {sources}")
        self.assertTrue(any("Sentinel" in s or "Copernicus" in s for s in sources), f"Satellite missing in {sources}")
        self.assertTrue(any("Historical" in s or "Archive" in s for s in sources), f"Historical missing in {sources}")

        for p in provenance_list:
            self.assertIn("status", p)
            status_badge = f"[{p['status']}]" if not p['status'].startswith("[") else p['status']
            self.assertIn(
                status_badge,
                self.ALLOWED_BADGES,
                f"Provenance record has unapproved status: {p['status']}",
            )


if __name__ == "__main__":
    unittest.main()
