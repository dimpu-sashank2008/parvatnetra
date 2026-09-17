# -*- coding: utf-8 -*-
"""
tests/test_isro_bhuvan_service.py
=================================
Automated test suite for ISRO / NRSC Bhuvan Earth Observation Service & REST APIs.
Covers:
- Metadata registry and layer definitions
- Fallback transparent PNG generation
- Bhuvan WMS probe logic & reachability
- /api/isro/bhuvan-status endpoint
- /api/isro/layers endpoint
- /api/isro/wms-proxy tile caching & graceful degradation
- Index page UI integration for ISRO layers and Bhuvan basemap switcher
"""

import os
import unittest
from unittest.mock import patch, MagicMock

os.environ["PARVAT_TESTING"] = "1"

from app import app
from services.isro_bhuvan_service import (
    BHUVAN_LAYERS,
    get_layers_metadata,
    get_service_status,
    probe_bhuvan_wms,
    _transparent_tile,
    build_wms_request_url,
)


class TestISROBhuvanService(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_layer_registry_contains_required_layers(self):
        """Verify all required ISRO layers are registered with provenance."""
        self.assertIn("landslide_hazard", BHUVAN_LAYERS)
        self.assertIn("landslide_susceptibility", BHUVAN_LAYERS)
        self.assertIn("bhuvan_satellite", BHUVAN_LAYERS)

        for layer_id, cfg in BHUVAN_LAYERS.items():
            self.assertIn("display_name", cfg)
            self.assertIn("provenance", cfg)
            self.assertIn("wms_layer", cfg)
            self.assertTrue(cfg["provenance"].startswith("[ISRO/"))

    def test_transparent_tile_format(self):
        """Verify fallback transparent tile is valid PNG data."""
        tile = _transparent_tile()
        self.assertIsInstance(tile, bytes)
        self.assertTrue(len(tile) > 0)
        # PNG magic number: 0x89 50 4E 47 0D 0A 1A 0A
        self.assertEqual(tile[:8], b"\x89PNG\r\n\x1a\n")

    def test_build_wms_request_url(self):
        """Verify build_wms_request_url builds valid upstream query."""
        params = {
            "BBOX": "88.0,26.0,89.0,27.0",
            "WIDTH": "256",
            "HEIGHT": "256",
            "SRS": "EPSG:4326",
            "FORMAT": "image/png"
        }
        url = build_wms_request_url("landslide_hazard", params)
        self.assertIsNotNone(url)
        self.assertIn("SERVICE=WMS", url)
        self.assertIn("REQUEST=GetMap", url)
        self.assertIn("India_Landslide_Hazard", url)
        self.assertIn("88.0%2C26.0%2C89.0%2C27.0", url)

    def test_get_layers_metadata(self):
        """Verify get_layers_metadata returns properly structured records."""
        meta = get_layers_metadata()
        self.assertEqual(len(meta), len(BHUVAN_LAYERS))
        layer_ids = [m["layer_id"] for m in meta]
        self.assertIn("landslide_hazard", layer_ids)
        self.assertIn("bhuvan_satellite", layer_ids)
        for item in meta:
            self.assertIn("display_name", item)
            self.assertIn("provenance", item)
            self.assertIn("wms_proxy_url", item)

    @patch("requests.get")
    def test_probe_bhuvan_wms_online(self, mock_get):
        """Verify probe correctly handles a healthy Bhuvan response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<WMT_MS_Capabilities><Service><Name>OGC:WMS</Name></Service></WMT_MS_Capabilities>"
        mock_get.return_value = mock_resp

        status = probe_bhuvan_wms(force=True)
        self.assertTrue(status["online"])
        self.assertIsNone(status["error"])
        self.assertIsNotNone(status["latency_ms"])

    @patch("requests.get")
    def test_probe_bhuvan_wms_offline_graceful(self, mock_get):
        """Verify probe handles unreachable server gracefully without throwing."""
        mock_get.side_effect = Exception("Connection timeout to NRSC gateway")

        status = probe_bhuvan_wms(force=True)
        self.assertFalse(status["online"])
        self.assertIn("Connection timeout", status["error"])

    def test_api_isro_bhuvan_status(self):
        """Test GET /api/isro/bhuvan-status endpoint contract."""
        resp = self.client.get("/api/isro/bhuvan-status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("service", data)
        self.assertIn("provenance", data)
        self.assertEqual(data["provenance"], "[ISRO/NRSC]")
        self.assertIn("layers_available", data)

    def test_api_isro_layers(self):
        """Test GET /api/isro/layers endpoint contract."""
        resp = self.client.get("/api/isro/layers")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("layers", data)
        self.assertIn("count", data)
        self.assertGreaterEqual(data["count"], 3)
        self.assertEqual(data["provenance"], "[ISRO/NRSC]")

    def test_api_isro_wms_proxy_graceful(self):
        """Test /api/isro/wms-proxy returns 200 and image even if upstream fails."""
        resp = self.client.get("/api/isro/wms-proxy?layer=landslide_hazard&BBOX=88,26,89,27")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.content_type.startswith("image/"))
        self.assertTrue(len(resp.data) > 0)

    def test_api_isro_wms_proxy_missing_layer(self):
        """Test /api/isro/wms-proxy without layer parameter returns 400 with transparent PNG."""
        resp = self.client.get("/api/isro/wms-proxy")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content_type, "image/png")

    def test_index_html_has_isro_controls(self):
        """Verify index.html contains ISRO Earth Observation UI section and toggles."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Category and status pill
        self.assertIn("ISRO / NRSC EARTH OBS", html)
        self.assertIn('id="bhuvan-status-pill"', html)
        self.assertIn('id="bhuvan-status-bar"', html)

        # Layer toggles
        self.assertIn('id="lc-toggle-bhuvan-hazard"', html)
        self.assertIn('id="lc-toggle-bhuvan-suscept"', html)
        self.assertIn('id="lc-toggle-bhuvan-sat"', html)

        # Basemap button
        self.assertIn('id="mb-bhuvan"', html)
        self.assertIn("Bhuvan", html)

    def test_api_isro_thematic_zones(self):
        """Test GET /api/isro/thematic-zones returns valid GeoJSON for hazard and susceptibility."""
        # Hazard
        resp = self.client.get("/api/isro/thematic-zones?layer=landslide_hazard")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(data["provenance"], "[ISRO/NRSC]")
        self.assertGreaterEqual(len(data["features"]), 5)

        # Susceptibility
        resp2 = self.client.get("/api/isro/thematic-zones?layer=landslide_susceptibility")
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertEqual(data2["type"], "FeatureCollection")
        self.assertEqual(data2["provenance"], "[ISRO/NESAC]")
        self.assertGreaterEqual(len(data2["features"]), 5)


if __name__ == "__main__":
    unittest.main()
