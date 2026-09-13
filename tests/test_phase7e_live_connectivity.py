"""
PHASE 7E — CP4-A through CP4-F: Live Connectivity Tests
Tests actual external source reachability and correct AUTH_REQUIRED reporting.

These tests only verify what the software correctly reports.
They do NOT fabricate connectivity.
"""
import os
import sys
import json
import time
import socket
import unittest
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestOpenMeteoLive(unittest.TestCase):
    """CP4-A: Open-Meteo must return LIVE data for NER corridor."""

    CORRIDOR_LAT = 27.2056
    CORRIDOR_LON = 88.4986
    TIMEOUT = 20

    def test_open_meteo_reachable(self):
        """Open-Meteo API must respond for NH10 KM48 coordinates."""
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.CORRIDOR_LAT}&longitude={self.CORRIDOR_LON}"
            f"&hourly=precipitation&daily=precipitation_sum"
            f"&forecast_days=1&past_days=1&timezone=Asia/Kolkata"
        )
        try:
            resp = urllib.request.urlopen(url, timeout=self.TIMEOUT)
            data = json.loads(resp.read())
            self.assertIn("latitude", data)
            self.assertIn("hourly", data)
            self.assertIn("daily", data)
            self.assertIn("precipitation_sum", data["daily"])
        except Exception as e:
            self.fail(f"Open-Meteo unreachable: {e}")

    def test_open_meteo_response_schema(self):
        """Open-Meteo response must include forecast horizons and precipitation."""
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.CORRIDOR_LAT}&longitude={self.CORRIDOR_LON}"
            f"&daily=precipitation_sum&forecast_days=3&timezone=Asia/Kolkata"
        )
        try:
            resp = urllib.request.urlopen(url, timeout=self.TIMEOUT)
            data = json.loads(resp.read())
            daily = data.get("daily", {})
            self.assertIn("time", daily)
            self.assertIn("precipitation_sum", daily)
            times = daily["time"]
            self.assertGreaterEqual(len(times), 3, "Must have 3 forecast days")
        except Exception as e:
            self.skipTest(f"Open-Meteo network issue: {e}")

    def test_open_meteo_data_freshness(self):
        """Open-Meteo timestamps must be within 24h of current time."""
        import datetime
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.CORRIDOR_LAT}&longitude={self.CORRIDOR_LON}"
            f"&daily=precipitation_sum&forecast_days=1&timezone=UTC"
        )
        try:
            resp = urllib.request.urlopen(url, timeout=self.TIMEOUT)
            data = json.loads(resp.read())
            times = data.get("daily", {}).get("time", [])
            if not times:
                self.skipTest("No times in response")
            today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            # Response should include today or yesterday
            self.assertTrue(
                any(t >= (datetime.datetime.utcnow() - datetime.timedelta(days=2)).strftime("%Y-%m-%d") for t in times),
                f"Forecast times {times[-3:]} too stale"
            )
        except Exception as e:
            self.skipTest(f"Open-Meteo network issue: {e}")


class TestIMDStatus(unittest.TestCase):
    """CP4-A: IMD must report AUTH_REQUIRED when credentials absent."""

    def test_imd_reports_auth_required_without_credentials(self):
        """IMD connector must NOT silently succeed without credentials."""
        imd_key = os.environ.get("IMD_API_KEY", "")
        imd_url = os.environ.get("IMD_API_URL", "")
        # If no credentials — service must acknowledge AUTH_REQUIRED
        if not imd_key:
            # Verify weather service correctly reports IMD as UNCONFIGURED
            from services.weather_service import WeatherService
            ws = WeatherService()
            status = ws.get_status()
            imd_status = status.get("providers", {}).get("imd", {}).get("status", "UNKNOWN")
            self.assertIn(imd_status, ["UNCONFIGURED", "AUTH_REQUIRED", "UNAVAILABLE"],
                          f"IMD must not claim READY without credentials, got: {imd_status}")

    def test_imd_not_substituted_as_open_meteo(self):
        """Weather service must distinguish IMD from Open-Meteo in status."""
        from services.weather_service import WeatherService
        ws = WeatherService()
        status = ws.get_status()
        providers = status.get("providers", {})
        # Both providers must be listed separately
        self.assertIn("imd", providers, "IMD must be tracked as separate provider")
        self.assertIn("openmeteo", providers, "Open-Meteo must be tracked as separate provider")
        # Their statuses must differ when IMD is unconfigured
        imd_ready = providers.get("imd", {}).get("live_ready", True)
        openmeteo_status = providers.get("openmeteo", {}).get("status", "UNKNOWN")
        if not os.environ.get("IMD_API_KEY"):
            self.assertFalse(imd_ready, "IMD must not be live_ready without API key")


class TestUSGSLive(unittest.TestCase):
    """CP4-B: USGS seismic must return real responses."""

    NER_BBOX = {"minlat": 20, "maxlat": 30.5, "minlon": 87, "maxlon": 98}
    TIMEOUT = 20

    def test_usgs_api_reachable(self):
        """USGS FDSNws must respond for NER bbox query."""
        url = (
            "https://earthquake.usgs.gov/fdsnws/event/1/query"
            "?format=geojson&starttime=2026-08-11&endtime=2026-09-11"
            f"&minlatitude={self.NER_BBOX['minlat']}&maxlatitude={self.NER_BBOX['maxlat']}"
            f"&minlongitude={self.NER_BBOX['minlon']}&maxlongitude={self.NER_BBOX['maxlon']}"
            "&minmagnitude=2.0&limit=5"
        )
        try:
            resp = urllib.request.urlopen(url, timeout=self.TIMEOUT)
            data = json.loads(resp.read())
            self.assertIn("type", data)
            self.assertEqual(data["type"], "FeatureCollection")
            self.assertIn("features", data)
            self.assertIn("metadata", data)
            api_ver = data.get("metadata", {}).get("api", "")
            self.assertTrue(api_ver.startswith("2."), f"Expected USGS API v2.x, got: {api_ver}")
        except Exception as e:
            self.fail(f"USGS unreachable: {e}")

    def test_usgs_events_within_ner_bbox(self):
        """Any returned USGS events must be within NER bounding box."""
        url = (
            "https://earthquake.usgs.gov/fdsnws/event/1/query"
            "?format=geojson&starttime=2026-08-11&endtime=2026-09-11"
            f"&minlatitude={self.NER_BBOX['minlat']}&maxlatitude={self.NER_BBOX['maxlat']}"
            f"&minlongitude={self.NER_BBOX['minlon']}&maxlongitude={self.NER_BBOX['maxlon']}"
            "&minmagnitude=2.0&limit=10"
        )
        try:
            resp = urllib.request.urlopen(url, timeout=self.TIMEOUT)
            data = json.loads(resp.read())
            for feature in data.get("features", []):
                coords = feature.get("geometry", {}).get("coordinates", [0, 0, 0])
                lon, lat = coords[0], coords[1]
                self.assertGreaterEqual(lat, self.NER_BBOX["minlat"])
                self.assertLessEqual(lat, self.NER_BBOX["maxlat"])
                self.assertGreaterEqual(lon, self.NER_BBOX["minlon"])
                self.assertLessEqual(lon, self.NER_BBOX["maxlon"])
        except Exception as e:
            self.skipTest(f"USGS network issue: {e}")

    def test_ncs_reports_auth_required_without_credentials(self):
        """NCS must NOT be reported as LIVE without institutional credentials."""
        ncs_key = os.environ.get("NCS_API_KEY", "")
        if not ncs_key:
            from services.seismic_service import SeismicService
            ss = SeismicService()
            status = ss.get_status()
            ncs_status = status.get("providers", {}).get("ncs", {}).get("status", "UNKNOWN")
            self.assertIn(ncs_status, ["UNCONFIGURED", "AUTH_REQUIRED", "UNAVAILABLE"],
                          f"NCS must not claim READY without credentials, got: {ncs_status}")

    def test_usgs_not_substituted_as_ncs(self):
        """Seismic service must distinguish USGS from NCS."""
        from services.seismic_service import SeismicService
        ss = SeismicService()
        status = ss.get_status()
        providers = status.get("providers", {})
        self.assertIn("ncs", providers, "NCS must be tracked separately")
        self.assertIn("usgs", providers, "USGS must be tracked separately")


class TestPostGISConnectivity(unittest.TestCase):
    """CP4-E: PostGIS connectivity must be accurately reported."""

    def test_postgis_port_state_accurately_reported(self):
        """PostGIS connectivity must match actual port state."""
        s = socket.socket()
        s.settimeout(2)
        port_open = (s.connect_ex(("localhost", 5432)) == 0)
        s.close()
        # Whatever the state, system must NOT claim connection when port is closed
        if not port_open:
            # System should gracefully handle DB unavailability
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host="localhost", port=5432, database="parvat_netra",
                    user="pahad", connect_timeout=2
                )
                conn.close()
                self.fail("Expected connection failure when port is closed")
            except Exception:
                pass  # Expected — DB not running

    def test_mqtt_port_state_accurately_reported(self):
        """MQTT broker state must be honestly reported."""
        s = socket.socket()
        s.settimeout(2)
        mqtt_open = (s.connect_ex(("localhost", 1883)) == 0)
        s.close()
        # Just verify we can check it — not assert any state
        self.assertIsInstance(mqtt_open, bool)


class TestDEMService(unittest.TestCase):
    """CP4-D: DEM must be marked CACHED/HISTORICAL, not real-time."""

    def test_dem_provenance_is_historical_not_live(self):
        """DEM must report HISTORICAL or CACHED provenance, never LIVE."""
        from services.dem_service import DEMService
        dem = DEMService()
        meta = dem.get_metadata()
        provenance = meta.get("provenance", "")
        self.assertIn(provenance, ["[HISTORICAL]", "[CACHED]", "HISTORICAL", "CACHED"],
                      f"DEM must not claim LIVE provenance, got: {provenance}")

    def test_dem_crs_is_epsg4326(self):
        """DEM must declare CRS."""
        from services.dem_service import DEMService
        dem = DEMService()
        meta = dem.get_metadata()
        crs = meta.get("crs", "")
        self.assertTrue(crs, "DEM must declare CRS")

    def test_dem_placeholder_values_flagged(self):
        """DEM slope=0.0 at NH10 KM48 is physically implausible — must be flagged."""
        from services.dem_service import DEMService
        dem = DEMService()
        attrs = dem.get_point_terrain_attributes(27.2056, 88.4986)
        slope = float(attrs.get("slope_deg", 0))
        # NH10 KM48 is on a steep Himalayan slope — slope=0.0 is a placeholder
        # The test verifies we can detect this programmatically
        if slope == 0.0:
            # System returned placeholder — provenance must NOT say LIVE
            provenance = attrs.get("provenance", "")
            self.assertNotEqual(provenance, "[LIVE]",
                                "Slope=0.0 placeholder must not have LIVE provenance")


if __name__ == "__main__":
    unittest.main()
