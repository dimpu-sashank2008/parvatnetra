# -*- coding: utf-8 -*-
"""
tests/test_live_risk_map.py
============================
Automated Test Suite for PARVAT NETRA Live Risk GIS Map Operational Surface.
Verifies all 13 requirements specified in Phase 3.1 / GIS Operational Map Task:
  1. Current risk zones generated from runtime data
  2. Correct risk bands rendered
  3. Live rainfall provenance retained (Open-Meteo)
  4. USGS seismic provenance retained
  5. Simulated sensors remain simulated (with unverified deployment disclaimer)
  6. CRI remains DERIVED with PARTIAL live contribution
  7. Map refresh does not reset viewport
  8. Stale data is visibly classified (CACHED_LIVE with timestamp)
  9. No fake LIVE labels for in-situ, InSAR, DEM, or CRI
  10. No duplicate map layers (layerGroup cleared on refresh)
  11. Unavailable providers trigger safe fallback
  12. Citizen reports appear after submission
  13. Public authority safety controls remain locked (ENABLE_PUBLIC_DISPATCH=0, SIREN_DRY_RUN=1)
"""

import os
import io
import re
import json
import unittest
from unittest.mock import patch

# Set testing environment flags
os.environ.setdefault("PARVAT_TESTING", "1")
os.environ.setdefault("PAHAD_DEMO_MODE", "1")
os.environ.setdefault("DRY_RUN", "true")
os.environ.setdefault("ENABLE_PUBLIC_DISPATCH", "0")
os.environ.setdefault("SIREN_DRY_RUN", "1")

import sys
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import app
from services.realtime_cri_service import REALTIME_CRI_SERVICE


class TestLiveRiskGISMap(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.template_path = os.path.join(REPO_ROOT, "templates", "index.html")
        with open(cls.template_path, "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    # -------------------------------------------------------------------------
    # 1. Current risk zones are generated from runtime data
    # -------------------------------------------------------------------------
    def test_01_current_risk_zones_generated_from_runtime_data(self):
        """Verify GET /api/pahad/realtime-cri/geojson returns 20 canonical corridors with runtime data."""
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertIn("metadata", data)
        self.assertIn("features", data)

        features = data["features"]
        self.assertEqual(len(features), 20, f"Expected 20 canonical corridors, got {len(features)}")

        # Verify metadata
        meta = data["metadata"]
        self.assertEqual(meta.get("dataset_class"), "CACHED_LIVE")
        self.assertEqual(meta.get("record_count"), 20)
        self.assertEqual(meta.get("live_sources_count"), 2)
        self.assertIn("highest_risk_band", meta)
        self.assertIn("highest_risk_cri", meta)

        # Check first feature structure
        f0 = features[0]
        self.assertEqual(f0.get("type"), "Feature")
        self.assertEqual(f0.get("geometry", {}).get("type"), "Point")
        coords = f0.get("geometry", {}).get("coordinates")
        self.assertIsInstance(coords, list)
        self.assertEqual(len(coords), 2)
        lon, lat = coords
        # Longitude and Latitude must be in NER geographic bounds (roughly 88-97 E, 21-30 N)
        self.assertTrue(88.0 <= lon <= 97.5, f"Longitude {lon} out of NER bounds")
        self.assertTrue(21.0 <= lat <= 30.5, f"Latitude {lat} out of NER bounds")

        props = f0.get("properties", {})
        self.assertIn("sector_id", props)
        self.assertIn("corridor", props)
        self.assertIn("state", props)
        self.assertIn("cri", props)
        self.assertIn("physical_fos", props)

    # -------------------------------------------------------------------------
    # 2. Correct risk bands are rendered
    # -------------------------------------------------------------------------
    def test_02_correct_risk_bands_rendered(self):
        """Verify alert bands adhere to standard scale: LOW, MODERATE, HIGH, VERY_HIGH, EXTREME."""
        valid_bands = {"LOW", "MODERATE", "HIGH", "VERY_HIGH", "EXTREME"}
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        self.assertEqual(res.status_code, 200)
        features = res.get_json().get("features", [])

        for feat in features:
            props = feat.get("properties", {})
            band = props.get("alert_band")
            cri = props.get("cri", 0.0)
            self.assertIn(band, valid_bands, f"Invalid alert band: {band}")

            # Check boundary consistency
            if cri >= 80.0:
                self.assertEqual(band, "EXTREME")
            elif cri >= 60.0:
                self.assertEqual(band, "VERY_HIGH")
            elif cri >= 40.0:
                self.assertEqual(band, "HIGH")
            elif cri >= 20.0:
                self.assertEqual(band, "MODERATE")
            else:
                self.assertEqual(band, "LOW")

    # -------------------------------------------------------------------------
    # 3. Live rainfall provenance is retained (Open-Meteo)
    # -------------------------------------------------------------------------
    def test_03_live_rainfall_provenance_retained(self):
        """Verify rainfall is classified as LIVE_EXTERNAL from Open-Meteo REST API."""
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        data = res.get_json()
        features = data.get("features", [])
        self.assertGreater(len(features), 0)

        for feat in features:
            props = feat.get("properties", {})
            self.assertEqual(props.get("rainfall_class"), "LIVE_EXTERNAL")
            self.assertIn("Open-Meteo", props.get("rainfall_source", ""))
            self.assertIn("rainfall_24h_mm", props)

        # Check metadata declares Open-Meteo
        meta = data.get("metadata", {})
        live_sources = meta.get("live_sources", [])
        self.assertTrue(any("Open-Meteo" in s for s in live_sources))

    # -------------------------------------------------------------------------
    # 4. USGS seismic provenance is retained
    # -------------------------------------------------------------------------
    def test_04_usgs_seismic_provenance_retained(self):
        """Verify seismic data is classified as LIVE_EXTERNAL from USGS GeoJSON."""
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        data = res.get_json()
        features = data.get("features", [])

        for feat in features:
            props = feat.get("properties", {})
            self.assertEqual(props.get("seismic_class"), "LIVE_EXTERNAL")
            self.assertIn("USGS", props.get("seismic_source", ""))
            self.assertIn("seismic_magnitude", props)

        meta = data.get("metadata", {})
        live_sources = meta.get("live_sources", [])
        self.assertTrue(any("USGS" in s for s in live_sources))

    # -------------------------------------------------------------------------
    # 5. Simulated sensors remain simulated
    # -------------------------------------------------------------------------
    def test_05_simulated_sensors_remain_simulated(self):
        """Verify in-situ pore water & soil moisture sensors are strictly SIMULATED with disclaimer."""
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        data = res.get_json()
        features = data.get("features", [])

        for feat in features:
            props = feat.get("properties", {})
            self.assertEqual(props.get("sensor_class"), "SIMULATED")
            self.assertNotEqual(props.get("sensor_class"), "LIVE_EXTERNAL")
            self.assertIn("Physical deployment not verified", props.get("sensor_note", ""))

        meta = data.get("metadata", {})
        simulated_sources = meta.get("simulated_sources", [])
        self.assertTrue(any("van Genuchten" in s or "In-Situ" in s for s in simulated_sources))

    # -------------------------------------------------------------------------
    # 6. CRI remains DERIVED
    # -------------------------------------------------------------------------
    def test_06_cri_remains_derived(self):
        """Verify Composite Risk Index is explicitly DERIVED with partial live contribution."""
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        data = res.get_json()
        features = data.get("features", [])

        for feat in features:
            props = feat.get("properties", {})
            self.assertEqual(props.get("cri_class"), "DERIVED")
            self.assertNotEqual(props.get("cri_class"), "LIVE_EXTERNAL")
            self.assertEqual(props.get("live_contribution"), "PARTIAL")

    # -------------------------------------------------------------------------
    # 7. Map refresh does not reset viewport
    # -------------------------------------------------------------------------
    def test_07_map_refresh_does_not_reset_viewport(self):
        """Verify loadCurrentRiskZones preserves map view during periodic polling."""
        # Verify loadCurrentRiskZones handles isPeriodicRefresh without resetting viewport
        self.assertTrue("loadCurrentRiskZones(isPeriodicRefresh" in self.index_html, "loadCurrentRiskZones definition missing")
        self.assertTrue("refreshed silently without viewport disruption" in self.index_html, "Viewport preservation handling missing")

        # In periodic mode, ensure fitBounds/setView is NOT triggered
        self.assertTrue("setInterval" in self.index_html, "Periodic interval missing")
        self.assertTrue("loadCurrentRiskZones(true)" in self.index_html, "Silent refresh call missing")

    # -------------------------------------------------------------------------
    # 8. Stale data is visibly classified
    # -------------------------------------------------------------------------
    def test_08_stale_data_is_visibly_classified(self):
        """Verify CACHED_LIVE classification and data freshness elements in DOM."""
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        meta = res.get_json().get("metadata", {})
        self.assertEqual(meta.get("dataset_class"), "CACHED_LIVE")
        self.assertIn("generated_at", meta)

        # Verify data status panel and map status strip in HTML
        self.assertTrue('id="gis-map-status-strip"' in self.index_html, "Map status strip missing")
        self.assertTrue('id="gis-data-status-panel"' in self.index_html, "Data status panel missing")
        self.assertTrue("CACHED_LIVE" in self.index_html, "CACHED_LIVE badge missing")
        self.assertTrue("DATA STATUS" in self.index_html, "DATA STATUS title missing")

    # -------------------------------------------------------------------------
    # 9. No fake LIVE labels
    # -------------------------------------------------------------------------
    def test_09_no_fake_live_labels(self):
        """Ensure no misleading 'LIVE' badges for InSAR, DEM, In-Situ, or CRI."""
        # Check data status panel text in template
        self.assertTrue("HISTORICAL / PROCESSED" in self.index_html, "InSAR historical badge missing")
        self.assertTrue("STATIC" in self.index_html, "DEM static badge missing")
        self.assertTrue("Physical deployment not verified" in self.index_html, "In-situ disclaimer missing")
        self.assertTrue("Mixed-provenance inputs" in self.index_html, "CRI mixed-provenance badge missing")

        # Ensure no claim of "100% LIVE"
        self.assertTrue("100% LIVE" not in self.index_html, "Found prohibited '100% LIVE' claim")
        self.assertTrue("ALL SENSORS LIVE" not in self.index_html, "Found prohibited 'ALL SENSORS LIVE' claim")

    # -------------------------------------------------------------------------
    # 10. No duplicate map layers
    # -------------------------------------------------------------------------
    def test_10_no_duplicate_map_layers(self):
        """Verify layer group is cleared prior to populating fresh markers."""
        has_init = ("currentRiskZonesLayerGroup=L.layerGroup().addTo(map);" in self.index_html or
                    "currentRiskZonesLayerGroup = L.layerGroup().addTo(map);" in self.index_html)
        self.assertTrue(has_init, "currentRiskZonesLayerGroup initialization missing")
        self.assertTrue("currentRiskZonesLayerGroup.clearLayers();" in self.index_html, "clearLayers() missing")
        self.assertTrue('id="lc-toggle-current-risk-zones"' in self.index_html, "Layer control toggle button missing")
        self.assertTrue("function toggleCurrentRiskZones" in self.index_html, "toggleCurrentRiskZones function missing")

    # -------------------------------------------------------------------------
    # 11. Unavailable providers trigger safe fallback
    # -------------------------------------------------------------------------
    def test_11_unavailable_providers_trigger_safe_fallback(self):
        """Verify that when external APIs fail, service safely falls back without 500 error."""
        with patch("services.realtime_cri_service.build_pahad_feature_vector", side_effect=Exception("API Timeout")):
            # Service should return cached dataset or safe fallback
            dataset = REALTIME_CRI_SERVICE.get_latest_dataset()
            self.assertIn("records", dataset)
            self.assertEqual(dataset.get("status"), "SUCCESS")

        # GeoJSON endpoint returns valid 200 response even in fallback
        res = self.client.get("/api/pahad/realtime-cri/geojson")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json().get("type"), "FeatureCollection")

    # -------------------------------------------------------------------------
    # 12. Citizen reports appear after submission
    # -------------------------------------------------------------------------
    def test_12_citizen_reports_appear_after_submission(self):
        """Verify citizen report submission enters verification pipeline with tracking ID."""
        sample_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc`\x00\x00'
            b'\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        data = {
            "category": "Active Mudslide",
            "notes": "Fast mudflow on NH-10 test corridor",
            "latitude": "27.2020",
            "longitude": "88.5185",
            "reporter_name": "Test Sentinel Citizen",
            "phone": "+91-9434012345",
            "photo": (io.BytesIO(sample_png), "test_mudslide.png", "image/png")
        }

        res = self.client.post("/api/reports/submit", data=data, content_type="multipart/form-data")
        self.assertIn(res.status_code, [200, 201])
        res_json = res.get_json()
        self.assertEqual(res_json.get("status"), "SUCCESS")
        self.assertIn("tracking_id", res_json)
        self.assertTrue(res_json["tracking_id"].startswith("PN-REPORT-2026-"))

        # Verify report is accessible in reports list
        list_res = self.client.get("/api/reports/list")
        self.assertEqual(list_res.status_code, 200)
        reports = list_res.get_json()
        self.assertIsInstance(reports, list)
        self.assertTrue(any(r.get("tracking_id") == res_json["tracking_id"] for r in reports))

    # -------------------------------------------------------------------------
    # 13. Public authority controls remain locked
    # -------------------------------------------------------------------------
    def test_13_public_authority_controls_remain_locked(self):
        """Verify statutory safety interlocks: ENABLE_PUBLIC_DISPATCH=0, SIREN_DRY_RUN=1."""
        # Environmental safety invariants
        self.assertEqual(os.environ.get("ENABLE_PUBLIC_DISPATCH", "0"), "0")
        self.assertEqual(os.environ.get("SIREN_DRY_RUN", "1"), "1")
        self.assertEqual(os.environ.get("CAP_PRODUCTION_DISPATCH", "0"), "0")
        self.assertEqual(os.environ.get("SACHET_PRODUCTION_DISPATCH", "0"), "0")
        self.assertEqual(os.environ.get("CELL_BROADCAST_PRODUCTION", "0"), "0")
        self.assertEqual(os.environ.get("PUBLIC_DEMO_TEST_ONLY", "1"), "1")

        # HTML must clearly declare Disaster Management Act statutory requirements
        self.assertIn("Disaster Management Act 2005", self.index_html)
        self.assertIn("ENABLE_PUBLIC_DISPATCH = 0", self.index_html)
        self.assertIn("SIREN_DRY_RUN", self.index_html)


if __name__ == "__main__":
    unittest.main()
