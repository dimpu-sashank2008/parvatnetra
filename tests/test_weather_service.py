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
    evaluate_mandal_sarkar_threshold,
    classify_visibility
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

    def test_classify_visibility_thresholds(self):
        # Extreme dense fog (< 200m)
        r_extreme = classify_visibility(150.0)
        self.assertEqual(r_extreme["classification"], "DENSE_FREEZING_FOG")
        self.assertEqual(r_extreme["color"], "#EF4444")
        self.assertIn("Halt", r_extreme["speed_limit"])

        # Dense fog (< 500m)
        r_dense = classify_visibility(350.0)
        self.assertEqual(r_dense["classification"], "DENSE_FOG")
        self.assertEqual(r_dense["color"], "#F59E0B")
        self.assertIn("25", r_dense["speed_limit"])

        # Moderate fog (< 1500m)
        r_mod = classify_visibility(1200.0)
        self.assertEqual(r_mod["classification"], "MODERATE_FOG")
        self.assertEqual(r_mod["color"], "#FBBF24")
        self.assertIn("40", r_mod["speed_limit"])

        # Mist / Haze (< 4000m)
        r_mist = classify_visibility(3000.0)
        self.assertEqual(r_mist["classification"], "MIST_HAZE")
        self.assertEqual(r_mist["color"], "#38BDF8")

        # Clear (>= 4000m)
        r_clear = classify_visibility(8500.0)
        self.assertEqual(r_clear["classification"], "CLEAR")
        self.assertEqual(r_clear["color"], "#10B981")

        # None / Default
        r_none = classify_visibility(None)
        self.assertEqual(r_none["classification"], "CLEAR")
        self.assertEqual(r_none["visibility_m"], 10000.0)

    def test_weather_atmosphere_visibility_integration(self):
        w = self.service.get_weather_for_sector("SK-NH10-KM48")
        atm = w.get("atmosphere", {})
        self.assertIn("visibility_m", atm)
        self.assertIn("visibility_km", atm)
        self.assertIn("fog_classification", atm)
        self.assertIn("fog_label", atm)
        self.assertIn("driving_advisory", atm)
        self.assertIn("visibility_color", atm)
        self.assertGreater(atm["visibility_m"], 0)

    def test_climate_map_visibility_fields(self):
        cmap = self.service.get_climate_map()
        for sec in cmap.get("sectors", []):
            self.assertIn("visibility_m", sec)
            self.assertIn("visibility_km", sec)
            self.assertIn("fog_classification", sec)
            self.assertIn("fog_label", sec)
            self.assertIn("driving_advisory", sec)
            self.assertIn("visibility_color", sec)


if __name__ == "__main__":
    unittest.main()
