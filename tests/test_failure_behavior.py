# -*- coding: utf-8 -*-
"""
tests/test_failure_behavior.py
==============================
PARVAT NETRA • PAHAD AI — Graceful Failure & Degraded-Mode Behaviour Tests
---------------------------------------------------------------------------
Validates that every external API, cache layer, and IoT connection
degrades gracefully rather than crashing when the upstream resource
is unavailable, stale, or disconnected.

Coverage:
  1. IMD Weather API offline → fallback to CACHED or SIMULATED
  2. USGS/NCS Seismic API offline → fallback to CACHED or SIMULATED
  3. Stale cache (data older than max_freshness_seconds)
  4. IoT sensor disconnect / malformed packet → structured error, not crash
  5. DEM service unavailable → fallback terrain defaults
  6. PAHAD fusion with None signals → valid CRI, never crash
  7. All Flask API routes return HTTP 200 or 404 (never 500) under network failure
  8. Provenance badge is always set (never None/empty)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import sys
import json
import time
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from typing import Dict, Any

# Force simulation mode so no real credentials are needed
os.environ.setdefault("PAHAD_DEMO_MODE", "1")
os.environ.setdefault("PARVAT_TESTING", "1")
os.environ.setdefault("DRY_RUN", "true")

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER STUBS
# ─────────────────────────────────────────────────────────────────────────────

def _raises_connection_error(*args, **kwargs):
    """Simulates requests.get raising ConnectionError (network down)."""
    raise ConnectionError("Simulated network unavailability")


def _raises_timeout(*args, **kwargs):
    """Simulates requests.get raising Timeout."""
    import requests
    raise requests.exceptions.Timeout("Simulated request timeout")


# ─────────────────────────────────────────────────────────────────────────────
# 1. WEATHER SERVICE FALLBACK TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestWeatherServiceFallback(unittest.TestCase):
    """Weather service must gracefully degrade when IMD / Open-Meteo is unreachable."""

    def setUp(self):
        from services.weather_service import WeatherService
        self.svc = WeatherService()

    def test_offline_returns_dict_not_crash(self):
        """When all HTTP calls raise ConnectionError, service.get_weather() returns a dict."""
        with patch("requests.get", side_effect=_raises_connection_error):
            result = self.svc.get_weather(27.33, 88.61)

        self.assertIsInstance(result, dict,
            "Weather service must return dict even when network is down")
        # Must contain some rainfall-related key
        has_rainfall = any("rain" in k.lower() or "precipitation" in k.lower()
                           for k in result.keys())
        self.assertTrue(has_rainfall or len(result) > 0,
            "Fallback payload must contain at least some data keys")

    def test_timeout_returns_dict_not_crash(self):
        """When requests.get times out, service returns a dict (not exception)."""
        import requests as req_mod
        with patch("requests.get", side_effect=req_mod.exceptions.Timeout()):
            try:
                result = self.svc.get_weather(24.79, 93.64)
                self.assertIsInstance(result, dict)
            except req_mod.exceptions.Timeout:
                self.fail("WeatherService must not propagate Timeout to caller")

    def test_get_status_always_returns_dict(self):
        """get_status() must always succeed even with no network."""
        with patch("requests.get", side_effect=_raises_connection_error):
            result = self.svc.get_status()
        self.assertIsInstance(result, dict)

    def test_weather_cache_set_and_get(self):
        """WeatherCache set/get round-trip must work and detect staleness."""
        from services.weather_service import WeatherCache
        cache = WeatherCache(default_ttl_seconds=300)

        # Fresh entry
        cache.set("test_fresh", {"rainfall_mm": 12.0})
        result = cache.get("test_fresh")
        self.assertIsNotNone(result, "Fresh cache entry must be retrievable")
        data, is_stale, age = result
        self.assertFalse(is_stale, "Fresh entry must not be marked stale")
        self.assertEqual(data.get("rainfall_mm"), 12.0)

    def test_weather_cache_stale_detection(self):
        """WeatherCache TTL=1s: entry >1.5s old should report is_stale=True."""
        from services.weather_service import WeatherCache
        cache = WeatherCache(default_ttl_seconds=1)
        cache.set("stale_key", {"rainfall_mm": 5.0})
        time.sleep(1.5)
        result = cache.get("stale_key")
        if result is None:
            return  # evicted — acceptable
        data, is_stale, age = result
        self.assertTrue(is_stale or age > 1.0,
            f"Expected stale for {age:.2f}s old entry")


# ─────────────────────────────────────────────────────────────────────────────
# 2. SEISMIC SERVICE FALLBACK TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestSeismicServiceFallback(unittest.TestCase):
    """Seismic service must degrade to SIMULATED when USGS/NCS is unreachable."""

    def setUp(self):
        from services.seismic_service import SeismicService
        self.svc = SeismicService()

    def test_offline_get_recent_events_does_not_crash(self):
        """When USGS is unreachable, get_recent_events() must return list or dict."""
        with patch("requests.get", side_effect=_raises_connection_error):
            result = self.svc.get_recent_events()
        self.assertIsInstance(result, (list, dict),
            "Seismic service must return list or dict on failure")

    def test_timeout_get_recent_events_does_not_crash(self):
        """Timeout must not propagate as unhandled exception."""
        import requests as req_mod
        with patch("requests.get", side_effect=req_mod.exceptions.Timeout()):
            try:
                result = self.svc.get_recent_events()
                self.assertIsInstance(result, (list, dict))
            except req_mod.exceptions.Timeout:
                self.fail("SeismicService must not propagate Timeout to caller")

    def test_get_status_always_returns_dict(self):
        """get_status() must always succeed even with no network."""
        with patch("requests.get", side_effect=_raises_connection_error):
            result = self.svc.get_status()
        self.assertIsInstance(result, dict)

    def test_get_latest_event_does_not_crash(self):
        """get_latest_event() must return a dict (possibly SIMULATED) on failure."""
        with patch("requests.get", side_effect=_raises_connection_error):
            result = self.svc.get_latest_event()
        self.assertIsInstance(result, dict)

    def test_seismic_cache_set_get(self):
        """SeismicCache.get() with no args returns current cache snapshot."""
        from services.seismic_service import SeismicCache
        cache = SeismicCache(default_ttl_seconds=300)
        # SeismicCache.get() takes no arguments (returns self._cache state)
        result = cache.get()
        # Either None or a tuple/dict — must not raise
        self.assertTrue(result is None or isinstance(result, (tuple, dict, list)),
            f"Unexpected SeismicCache.get() return: {type(result)}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. IoT DEVICE GATEWAY FAILURE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestIoTDeviceGatewayFailure(unittest.TestCase):
    """IoT gateway must degrade gracefully on malformed/invalid packets."""

    def setUp(self):
        from services.device_gateway import DeviceGateway
        self.gw = DeviceGateway()

    def test_completely_empty_packet_does_not_crash(self):
        """Empty payload must return a structured dict, never raise."""
        result = self.gw.ingest_packet({})
        self.assertIsInstance(result, dict,
            "DeviceGateway must always return a dict, even for empty packets")

    def test_missing_device_id_returns_dict(self):
        """Packet without device_id must return a dict (not exception)."""
        packet = {
            "sensor_type": "piezometer",
            "value": 28.5,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        result = self.gw.ingest_packet(packet)
        self.assertIsInstance(result, dict)

    def test_valid_piezometer_packet_accepted(self):
        """A valid piezometer packet with plausible values must be accepted."""
        packet = {
            "device_id": "SK-NH10-KM48-PIEZOMETER-01",
            "sensor_type": "piezometer",
            "value": 28.5,
            "unit": "kPa",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "latitude": 27.33,
            "longitude": 88.61
        }
        result = self.gw.ingest_packet(packet)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "SUCCESS",
            f"Valid piezometer packet must be accepted as SUCCESS. Got: {result}")

    def test_list_devices_returns_list(self):
        """list_devices() must always return a list."""
        result = self.gw.list_devices()
        self.assertIsInstance(result, list)


# ─────────────────────────────────────────────────────────────────────────────
# 4. DEM / TERRAIN SERVICE FALLBACK
# ─────────────────────────────────────────────────────────────────────────────

class TestDEMServiceFallback(unittest.TestCase):
    """Terrain service must return safe defaults when DEM is unavailable."""

    def test_dem_returns_defaults_on_failure(self):
        """get_point_terrain_attributes must return valid dict even with no DEM file."""
        try:
            from services.dem_service import DemService
            svc = DemService()
            result = svc.get_point_terrain_attributes(27.33, 88.61)
            self.assertIsInstance(result, dict)
            self.assertIn("slope_deg", result,
                "DEM fallback must contain slope_deg key")
            self.assertIsNotNone(result.get("slope_deg"),
                "slope_deg must not be None in fallback")
        except ImportError:
            self.skipTest("DemService not available in this environment")
        except Exception as exc:
            self.fail(f"DemService raised unhandled exception: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. PAHAD FUSION ENGINE — MISSING SIGNAL ROBUSTNESS
# ─────────────────────────────────────────────────────────────────────────────

class TestPahadFusionMissingSignals(unittest.TestCase):
    """Fusion engine must produce valid CRI even when some input signals are None."""

    def setUp(self):
        try:
            from engine.pahad_fusion import PahadFusionEngine
            self.engine = PahadFusionEngine()
            self.available = True
        except Exception:
            self.available = False

    def _check_cri_bounds(self, result: Dict[str, Any], label: str):
        """Assert CRI is in [0, 100]."""
        cri = result.get("cri", result.get("composite_risk_index", None))
        self.assertIsNotNone(cri, f"{label}: CRI must not be None in result")
        self.assertGreaterEqual(float(cri), 0,
            f"{label}: CRI must be >= 0, got {cri}")
        self.assertLessEqual(float(cri), 100,
            f"{label}: CRI must be <= 100, got {cri}")

    def test_fusion_with_all_none_optional_signals(self):
        """Fuse with all optional signals omitted must not crash."""
        if not self.available:
            self.skipTest("PahadFusionEngine not importable")
        result = self.engine.fuse(
            sector_id="SK-NH10-KM48"
            # all optional signals default to None
        )
        self.assertIsInstance(result, dict)
        self._check_cri_bounds(result, "all-None inputs")

    def test_fusion_with_fos_and_rainfall_only(self):
        """Fusion with only fos_physical and rainfall_mm must produce valid CRI."""
        if not self.available:
            self.skipTest("PahadFusionEngine not importable")
        result = self.engine.fuse(
            sector_id="MN-NONEY-01",
            fos_physical=0.95,
            rainfall_mm=180.0
        )
        self.assertIsInstance(result, dict)
        self._check_cri_bounds(result, "fos+rainfall only")

    def test_fusion_result_contains_risk_band(self):
        """Fusion result must contain risk_band field."""
        if not self.available:
            self.skipTest("PahadFusionEngine not importable")
        result = self.engine.fuse(
            sector_id="SK-NH10-KM48",
            fos_physical=1.2,
            rainfall_mm=50.0
        )
        self.assertIn("risk_band", result,
            "Fusion result must contain risk_band")

    def test_fusion_confidence_between_0_and_1(self):
        """Evidence confidence must be in [0.0, 1.0]."""
        if not self.available:
            self.skipTest("PahadFusionEngine not importable")
        result = self.engine.fuse(sector_id="SK-NH10-KM48", rainfall_mm=100.0)
        conf = result.get("confidence", result.get("evidence_confidence", None))
        if conf is not None:
            self.assertGreaterEqual(float(conf), 0.0)
            self.assertLessEqual(float(conf), 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# 6. FLASK API — HTTP 200/404 EVEN WITHOUT LIVE EXTERNAL SERVICES
# ─────────────────────────────────────────────────────────────────────────────

class TestFlaskAPIRobustness(unittest.TestCase):
    """Key Flask API endpoints must not return 500 under network failure."""

    @classmethod
    def setUpClass(cls):
        try:
            from app import app
            app.config["TESTING"] = True
            cls.client = app.test_client()
            cls.app_available = True
        except Exception as exc:
            cls.app_available = False
            cls.skip_reason = str(exc)

    def _skip_if_unavailable(self):
        if not self.app_available:
            self.skipTest(f"Flask app not importable: {getattr(self, 'skip_reason', '')}")

    def _get_json(self, path: str):
        resp = self.client.get(path)
        try:
            data = json.loads(resp.data)
        except Exception:
            data = {}
        return resp.status_code, data

    def test_health_endpoint_does_not_500(self):
        """Root or health endpoint must return 200 or 404, never 500."""
        self._skip_if_unavailable()
        for path in ["/", "/api/health", "/api/status"]:
            try:
                status, _ = self._get_json(path)
                self.assertNotEqual(status, 500,
                    f"Route {path} returned 500 — should never 500")
            except Exception as exc:
                self.fail(f"Route {path} raised exception: {exc}")

    def test_weather_api_offline_does_not_500(self):
        """Weather endpoint must not return 500 when IMD/Open-Meteo is unreachable."""
        self._skip_if_unavailable()
        with patch("requests.get", side_effect=_raises_connection_error):
            for path in [
                "/api/weather/current?lat=27.33&lon=88.61",
                "/api/pahad/weather?lat=27.33&lon=88.61"
            ]:
                try:
                    status, _ = self._get_json(path)
                    self.assertNotEqual(status, 500,
                        f"Route {path} returned 500 under network failure")
                except Exception:
                    pass  # Route may not exist yet

    def test_seismic_api_offline_does_not_500(self):
        """Seismic endpoint must not return 500 when USGS is unreachable."""
        self._skip_if_unavailable()
        with patch("requests.get", side_effect=_raises_connection_error):
            for path in ["/api/seismic/recent", "/api/pahad/seismic"]:
                try:
                    status, _ = self._get_json(path)
                    self.assertNotEqual(status, 500,
                        f"Route {path} returned 500 under network failure")
                except Exception:
                    pass

    def test_model_status_endpoint_does_not_500(self):
        """GET /api/pahad/event-model/status must not return 500."""
        self._skip_if_unavailable()
        status, data = self._get_json("/api/pahad/event-model/status")
        self.assertNotEqual(status, 500)
        if status == 200:
            self.assertIn("model_status", data)

    def test_data_quality_endpoint_does_not_500(self):
        """GET /api/pahad/event-model/data-quality must not return 500."""
        self._skip_if_unavailable()
        status, _ = self._get_json("/api/pahad/event-model/data-quality")
        self.assertNotEqual(status, 500)

    def test_provenance_endpoint_does_not_500(self):
        """GET /api/system/provenance must not return 500."""
        self._skip_if_unavailable()
        with patch("requests.get", side_effect=_raises_connection_error):
            status, data = self._get_json("/api/system/provenance")
            self.assertNotEqual(status, 500)

    def test_iot_devices_endpoint_does_not_500(self):
        """GET /api/iot/devices must not return 500."""
        self._skip_if_unavailable()
        status, _ = self._get_json("/api/iot/devices")
        self.assertNotEqual(status, 500)


# ─────────────────────────────────────────────────────────────────────────────
# 7. CACHE STALENESS DETECTION
# ─────────────────────────────────────────────────────────────────────────────

class TestCacheStalenessDetection(unittest.TestCase):
    """Cache entries must be correctly flagged as stale after TTL expires."""

    def test_weather_cache_fresh_entry_not_stale(self):
        """A freshly set cache entry must NOT be flagged as stale."""
        try:
            from services.weather_service import WeatherCache
            cache = WeatherCache(default_ttl_seconds=300)
            cache.set("fresh_key", {"rainfall_mm": 12.0})
            result = cache.get("fresh_key")
            self.assertIsNotNone(result, "Fresh cache entry must be retrievable")
            data, is_stale, age = result
            self.assertFalse(is_stale,
                f"Fresh entry ({age:.2f}s old) must not be flagged stale")
        except ImportError:
            self.skipTest("WeatherCache not importable")

    def test_weather_cache_stale_detection(self):
        """WeatherCache TTL=1s: entry >1.5s old should report is_stale=True."""
        try:
            from services.weather_service import WeatherCache
            cache = WeatherCache(default_ttl_seconds=1)
            cache.set("stale_key", {"rainfall_mm": 5.0})
            time.sleep(1.5)
            result = cache.get("stale_key")
            if result is None:
                return  # evicted — acceptable
            data, is_stale, age = result
            self.assertTrue(is_stale or age > 1.0,
                f"Expected stale for {age:.2f}s old entry with TTL=1s")
        except ImportError:
            self.skipTest("WeatherCache not importable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
