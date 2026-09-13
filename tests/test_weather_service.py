# -*- coding: utf-8 -*-
"""
tests/test_weather_service.py
=============================
Unit & Integration Tests for PAHAD AI Weather & Climate Intelligence Service
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import time

from services.weather_service import (
    WeatherService,
    WeatherCache,
    IMDWeatherProvider,
    OpenMeteoWeatherProvider,
    DemoSimulatedWeatherProvider,
    calculate_antecedent_precipitation_indices,
    evaluate_mandal_sarkar_threshold
)


class TestWeatherService(unittest.TestCase):

    def setUp(self):
        self.service = WeatherService()
        self.service.cache.clear()

    def test_cache_ttl_and_stale_detection(self):
        cache = WeatherCache(default_ttl_seconds=1)
        test_payload = {"temp": 20.0, "rain": 5.0}
        cache.set("loc1", test_payload, ttl=1, source="Test")

        res = cache.get("loc1")
        self.assertIsNotNone(res)
        data, is_stale, age = res
        self.assertEqual(data["temp"], 20.0)
        self.assertFalse(is_stale)

        # Wait for TTL expiry
        time.sleep(1.1)
        res_expired = cache.get("loc1")
        self.assertIsNotNone(res_expired)
        _, is_stale_after, age_after = res_expired
        self.assertTrue(is_stale_after)
        self.assertGreaterEqual(age_after, 1.0)

    def test_imd_unconfigured_status(self):
        provider = IMDWeatherProvider()
        # In test environment, tokens are not configured
        with patch.dict(os.environ, {"IMD_API_BASE_URL": "", "IMD_API_TOKEN": ""}):
            self.assertFalse(provider._is_configured())
            status = provider.status()
            self.assertEqual(status["status"], "UNCONFIGURED")
            self.assertFalse(status["live_ready"])
            res = provider.fetch_weather(27.33, 88.61)
            self.assertIsNone(res)

    def test_demo_simulated_weather_generation(self):
        provider = DemoSimulatedWeatherProvider()
        res = provider.fetch_weather(lat=27.33, lon=88.61, sector_id="SK-NH10-KM48")
        self.assertIn("rain_24h_mm", res)
        self.assertIn("forecast", res)
        self.assertGreater(res["rain_24h_mm"], 0.0)
        self.assertIn(res["provenance"], ["SIMULATED", "DEMO"])

    def test_antecedent_precipitation_indices(self):
        # 24h rain = 50 mm, 72h rain = 120 mm
        api = calculate_antecedent_precipitation_indices(rain_24h=50.0, rain_72h=120.0, decay_k=0.84)
        self.assertIn("api_3d", api)
        self.assertIn("api_7d", api)
        self.assertIn("api_30d", api)
        self.assertGreater(api["api_3d"], 50.0)
        self.assertGreater(api["api_7d"], api["api_3d"])
        self.assertGreater(api["api_30d"], api["api_7d"])

    def test_mandal_sarkar_empirical_threshold(self):
        # High intensity storm (15 mm/hr) should breach Mandal-Sarkar 24h threshold
        res_high = evaluate_mandal_sarkar_threshold(intensity_mm_hr=15.0, duration_hours=24.0)
        self.assertTrue(res_high["threshold_exceeded"])
        self.assertIn(res_high["state"], ["CRITICAL_EXCEEDED", "ELEVATED_BREACH"])
        self.assertGreater(res_high["exceedance_ratio"], 1.0)

        # Gentle drizzle (0.1 mm/hr) should be within normal equilibrium
        res_low = evaluate_mandal_sarkar_threshold(intensity_mm_hr=0.1, duration_hours=24.0)
        self.assertFalse(res_low["threshold_exceeded"])
        self.assertEqual(res_low["state"], "NORMAL_EQUILIBRIUM")

    def test_normalized_weather_schema(self):
        w = self.service.get_weather_for_sector("SK-NH10-KM48")
        self.assertIn("timestamp", w)
        self.assertIn("location", w)
        self.assertIn("rainfall", w)
        self.assertIn("forecast", w)
        self.assertIn("atmosphere", w)
        self.assertIn("derived_pahad", w)
        self.assertIn("provenance", w)
        self.assertIn(w["provenance"], ["LIVE", "SIMULATED", "HISTORICAL", "DEMO", "DEGRADED", "CACHED"])

        # Check required fields
        self.assertIn("current_mm_hr", w["rainfall"])
        self.assertIn("rain_24h_mm", w["rainfall"])
        self.assertIn("api_3d", w["derived_pahad"])
        self.assertIn("rainfall_intensity_duration_state", w["derived_pahad"])

    def test_cache_fallback_when_offline(self):
        # Populate cache
        w1 = self.service.get_weather(lat=27.33, lon=88.61, sector_id="TEST-CACHE")
        self.assertIsNotNone(w1)

        # Second request should hit cache
        w2 = self.service.get_weather(lat=27.33, lon=88.61, sector_id="TEST-CACHE")
        self.assertEqual(w2["provenance"], "CACHED")
        self.assertIn("data_age_seconds", w2)

    def test_climate_map_generation(self):
        cmap = self.service.get_climate_map()
        self.assertEqual(cmap["status"], "SUCCESS")
        self.assertGreaterEqual(cmap["sector_count"], 4)
        first = cmap["sectors"][0]
        self.assertIn("sector_id", first)
        self.assertIn("rain_24h_mm", first)
        self.assertIn("provenance", first)


if __name__ == "__main__":
    unittest.main()
