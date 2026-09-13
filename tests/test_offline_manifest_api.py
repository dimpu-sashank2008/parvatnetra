# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Offline Geospatial Manifest API Test Suite
Phase 3.2: Offline-First Web, Map Resilience & Data Synchronization
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app


class TestOfflineManifestApi(unittest.TestCase):
    """Validates the GET /api/geospatial/offline-manifest endpoint against Phase 3.2 specs."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_endpoint_response_envelope(self):
        """Verify endpoint returns HTTP 200 with complete envelope metadata."""
        res = self.client.get("/api/geospatial/offline-manifest")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertIn("manifest_version", data)
        self.assertIn("manifest_generated_at", data)
        self.assertIn("datasets", data)
        self.assertIsInstance(data["datasets"], list)
        self.assertGreaterEqual(len(data["datasets"]), 7)

    def test_02_mandatory_dataset_fields_compliance(self):
        """Verify every dataset entry contains all Section 10 mandatory fields."""
        res = self.client.get("/api/geospatial/offline-manifest")
        data = res.get_json()
        datasets = data.get("datasets", [])

        mandatory_fields = [
            "dataset_id",
            "name",
            "version",
            "size",
            "created_at",
            "updated_at",
            "coverage",
            "resolution",
            "download_available",
            "installed",
            "checksum",
            "source",
            "provenance"
        ]

        for ds in datasets:
            ds_id = ds.get("dataset_id")
            for field in mandatory_fields:
                self.assertIn(
                    field,
                    ds,
                    f"Dataset {ds_id} is missing mandatory field '{field}'"
                )

    def test_03_prebundled_core_package_registration(self):
        """Verify 'ner-core-v1' is registered and declared as installed with provenance CACHED."""
        res = self.client.get("/api/geospatial/offline-manifest")
        data = res.get_json()
        datasets = data.get("datasets", [])

        core_pkg = next((d for d in datasets if d.get("dataset_id") == "ner-core-v1"), None)
        self.assertIsNotNone(core_pkg, "ner-core-v1 dataset must be present in offline manifest")
        self.assertEqual(core_pkg.get("version"), "1.0")
        self.assertTrue(core_pkg.get("installed"))
        self.assertIn(core_pkg.get("provenance"), ("CACHED", "[CACHED]"))
        self.assertIsNotNone(core_pkg.get("checksum"))
        self.assertTrue(
            "NER" in core_pkg.get("coverage", "") or "North-Eastern" in core_pkg.get("coverage", ""),
            f"Expected NER coverage, got: {core_pkg.get('coverage')}"
        )

    def test_04_provenance_and_data_integrity(self):
        """Verify provenance values conform to official protocol (HISTORICAL, CACHED, LIVE, SIMULATED)."""
        res = self.client.get("/api/geospatial/offline-manifest")
        data = res.get_json()
        datasets = data.get("datasets", [])

        valid_provenances = {
            "HISTORICAL", "CACHED", "LIVE", "SIMULATED", "DEMO",
            "[HISTORICAL]", "[CACHED]", "[LIVE]", "[SIMULATED]", "[DEMO]"
        }
        for ds in datasets:
            prov = ds.get("provenance")
            self.assertIn(
                prov,
                valid_provenances,
                f"Dataset {ds.get('dataset_id')} has invalid provenance: {prov}"
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
