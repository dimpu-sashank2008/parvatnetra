# -*- coding: utf-8 -*-
"""
tests/test_climate_map_api.py
=============================
Automated test suite for PAHAD AI Climate Map UI and Backend REST APIs.
Covers:
- /climate-map workspace route
- /api/weather/climate-map regional precipitation matrix
- /api/weather/status provider diagnostics
- /api/weather/forecast multi-horizon forecast
- Provenance honesty and cache behavior
"""

import unittest
import os

# Set testing flag to prevent infinite background daemon loops during test imports
os.environ["PARVAT_TESTING"] = "1"

from app import app
from services.weather_service import WEATHER_SERVICE, WeatherCache


class TestClimateMapApi(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_climate_map_html_workspace(self):
        """Test GET /climate-map returns dedicated intelligence workspace with required UI components."""
        resp = self.client.get("/climate-map")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        
        # Verify required headers and subheaders
        self.assertIn("CLIMATE INTELLIGENCE", html)
        self.assertIn("Live environmental conditions influencing hillslope stability across NER", html)
        
        # Verify large map canvas exists
        self.assertIn('id="climate-map-canvas"', html)
        
        # Verify layer control elements (SVG icons, no emoji)
        self.assertIn("Map Layers & Basemap", html)
        self.assertIn("Current mm/h", html)
        self.assertIn("24h Rain", html)
        self.assertIn("72h Antecedent", html)
        self.assertIn("Forecast 48h", html)
        self.assertIn("CRI Scores", html)
        self.assertIn("I-D Breach", html)
        self.assertIn("FoS Contours", html)
        
        # Verify Status Panel & Causal Flow
        self.assertIn("Raw Environmental Observations", html)
        self.assertIn("PAHAD Climate Interpretation", html)
        self.assertIn("Rainfall Accumulation Timeline", html)
        self.assertIn("NER Regional Climate Matrix", html)

    def test_api_weather_climate_map_payload(self):
        """Test GET /api/weather/climate-map returns regional matrix across critical corridors."""
        resp = self.client.get("/api/weather/climate-map")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("timestamp", data)
        self.assertIn("provenance", data)
        self.assertIn("sectors", data)
        
        sectors = data["sectors"]
        self.assertGreaterEqual(len(sectors), 5)
        
        # Verify NH-10 Km 48 baseline sector
        nh10 = next((s for s in sectors if s.get("sector_id") == "SK-NH10-KM48"), None)
        self.assertIsNotNone(nh10, "SK-NH10-KM48 must be present in climate map")
        self.assertIn("current_intensity_mmh", nh10)
        self.assertIn("rain_24h_mm", nh10)
        self.assertIn("api_3d", nh10)
        self.assertIn("threshold_state", nh10)
        self.assertIn("provenance", nh10)

    def test_api_weather_status_payload(self):
        """Test GET /api/weather/status returns provider connectivity and cache telemetry."""
        resp = self.client.get("/api/weather/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        
        self.assertIn("active_provider_preference", data)
        self.assertIn("providers", data)
        self.assertIn("cache_ttl_seconds", data)

    def test_api_weather_forecast_payload(self):
        """Test GET /api/weather/forecast returns multi-horizon precipitation curve."""
        resp = self.client.get("/api/weather/forecast?sector_id=SK-NH10-KM48")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("sector_id"), "SK-NH10-KM48")
        self.assertIn("forecast", data)
        self.assertIn("derived_pahad", data)
        
        forecast = data["forecast"]
        self.assertIn("24h_mm", forecast)
        self.assertIn("48h_mm", forecast)
        self.assertIn("hourly_trend", forecast)

    def test_weather_cache_isolation_and_no_fake_live(self):
        """Verify WeatherCache marks stale data honestly and never claims fake [LIVE] on degraded cache."""
        cache = WeatherCache(default_ttl_seconds=1)
        cache.set("TEST_SEC", {"rain": 50.0}, ttl=1, source="TestProvider")
        
        res = cache.get("TEST_SEC")
        self.assertIsNotNone(res)
        data, is_stale, age = res
        self.assertFalse(is_stale)
        
        # Expired lookup returns stale flag
        import time
        time.sleep(1.1)
        res_stale = cache.get("TEST_SEC")
        self.assertIsNotNone(res_stale)
        _, is_stale_now, age_now = res_stale
        self.assertTrue(is_stale_now)
        self.assertGreaterEqual(age_now, 1.0)


if __name__ == "__main__":
    unittest.main()
