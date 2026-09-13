import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app


class TestOfflineManifest(unittest.TestCase):
    """Tests /api/geospatial/offline-manifest endpoint and layer bundle readiness."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_offline_manifest_endpoint_status(self):
        """Verify GET /api/geospatial/offline-manifest returns 200 with OPERATIONAL status."""
        res = self.client.get("/api/geospatial/offline-manifest")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertEqual(data.get("manifest_version"), "3.0.0")
        self.assertIn("manifest_generated_at", data)
        self.assertIn("datasets", data)
        self.assertIn("offline_capabilities", data)

    def test_offline_manifest_mandatory_layers_present(self):
        """Verify presence of all mandatory layers required for offline mountain operations."""
        res = self.client.get("/api/geospatial/offline-manifest")
        data = res.get_json()
        datasets = data.get("datasets", [])

        dataset_ids = {d.get("dataset_id") for d in datasets}
        required_ids = {
            "DEM_COPERNICUS_30M",              # DEM
            "NER_ADMIN_BOUNDARIES",             # Boundaries
            "BRO_PWD_MOUNTAIN_ROADS",           # Roads/highways
            "NER_EMERGENCY_SHELTERS",           # Shelters
            "GSI_LANDSLIDE_INVENTORY",          # Historical landslides
            "CRITICAL_SECTOR_RISK_SNAPSHOTS",   # Risk snapshots
            "SENTINEL1_SAR_LOS",                # Remote sensing InSAR
        }
        missing = required_ids - dataset_ids
        self.assertEqual(len(missing), 0, f"Mandatory offline layers missing: {missing}")

    def test_offline_capabilities_declaration(self):
        """Verify explicit offline storage and sync contract declaration."""
        res = self.client.get("/api/geospatial/offline-manifest")
        data = res.get_json()
        caps = data.get("offline_capabilities", {})

        self.assertTrue(caps.get("vector_tiles_cached"))
        self.assertTrue(caps.get("raster_dem_available"))
        self.assertTrue(caps.get("offline_sync_supported"))
        self.assertIn("SQLite", caps.get("storage_type", ""))


if __name__ == "__main__":
    unittest.main()
