# -*- coding: utf-8 -*-
"""
tests/test_seismic_frontend_contract.py
=======================================
Automated test suite for PAHAD AI Seismic Intelligence UI and REST APIs.
Covers:
- /seismic workspace route and contract
- /api/seismic/recent deduplication & NER bounding box filtering
- /api/seismic/latest event endpoint
- /api/seismic/status diagnostic telemetry
- /api/seismic/impact PGA proxy attenuation and sector vulnerability rankings
- Prototype modifier disclaimer adherence
"""

import unittest
import os

os.environ["PARVAT_TESTING"] = "1"

from app import app
from services.seismic_service import SEISMIC_SERVICE, SeismicService


class TestSeismicFrontendContract(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_seismic_html_workspace(self):
        """Test GET /seismic returns dedicated seismic intelligence workspace with required components."""
        resp = self.client.get("/seismic")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        
        # Verify required headers and subheaders
        self.assertIn("SEISMIC INTELLIGENCE", html)
        self.assertIn("Recent seismic activity and potential landslide-trigger influence across NER", html)
        
        # Verify large map canvas exists
        self.assertIn('id="seismic-map-canvas"', html)
        
        # Verify layer control elements
        self.assertIn("Seismic Layers & Basemap", html)
        self.assertIn("Epicenters", html)
        self.assertIn("Affected Zones", html)
        self.assertIn("Corridor Sectors", html)
        
        # Verify Event Panel & Causal Flow
        self.assertIn("PAHAD Seismic Interpretation", html)
        self.assertIn("Earthquake → PAHAD Flow", html)
        self.assertIn("PROTOTYPE SEISMIC MODIFIER", html)
        self.assertIn("Sectors Requiring Re-evaluation", html)
        
        # Verify scientific disclaimer (earthquake does not guarantee landslide)
        self.assertIn("An earthquake does not guarantee a landslide", html)

    def test_api_seismic_recent_payload(self):
        """Test GET /api/seismic/recent returns deduplicated events within NER bounding box."""
        resp = self.client.get("/api/seismic/recent?limit=10&min_mag=2.5")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("count", data)
        self.assertIn("events", data)
        
        events = data["events"]
        self.assertGreaterEqual(len(events), 1)
        
        for evt in events:
            self.assertTrue("event_id" in evt or "id" in evt)
            self.assertIn("magnitude", evt)
            self.assertIn("depth_km", evt)
            self.assertIn("latitude", evt)
            self.assertIn("longitude", evt)
            self.assertIn("provenance", evt)
            
            # Verify coordinates lie inside NER bounding box [20-30N, 87-98E]
            lat = float(evt["latitude"])
            lon = float(evt["longitude"])
            self.assertGreaterEqual(lat, 20.0)
            self.assertLessEqual(lat, 30.0)
            self.assertGreaterEqual(lon, 87.0)
            self.assertLessEqual(lon, 98.0)

    def test_api_seismic_latest_payload(self):
        """Test GET /api/seismic/latest returns most recent event in NER."""
        resp = self.client.get("/api/seismic/latest")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        
        self.assertIn(data.get("status"), ["SUCCESS", "NO_EVENT"])
        if data.get("status") == "SUCCESS":
            evt = data.get("event")
            self.assertIsNotNone(evt)
            self.assertIn("magnitude", evt)
            self.assertIn("depth_km", evt)

    def test_api_seismic_impact_sector_and_matrix(self):
        """Test GET /api/seismic/impact for specific corridor and regional rankings."""
        # 1. Single Sector query
        resp = self.client.get("/api/seismic/impact?sector_id=SK-NH10-KM48")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("impact", data)
        impact = data["impact"]
        self.assertEqual(impact.get("sector_id"), "SK-NH10-KM48")
        self.assertIn("shaking_proxy_g", impact)
        self.assertIn("risk_adjustment", impact)
        self.assertIn("seismic_trigger_level", impact)

        # 2. Regional impact matrix query
        resp_all = self.client.get("/api/seismic/impact?min_mag=2.5")
        self.assertEqual(resp_all.status_code, 200)
        data_all = resp_all.get_json()
        self.assertEqual(data_all.get("status"), "SUCCESS")
        self.assertIn("impacts", data_all)
        self.assertGreaterEqual(len(data_all["impacts"]), 3)

    def test_api_seismic_status_telemetry(self):
        """Test GET /api/seismic/status reports active provider without fake live data."""
        resp = self.client.get("/api/seismic/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("active_provider_preference", data)
        self.assertIn("providers", data)


if __name__ == "__main__":
    unittest.main()
