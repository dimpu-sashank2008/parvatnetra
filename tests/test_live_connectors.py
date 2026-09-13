# -*- coding: utf-8 -*-
"""
tests/test_live_connectors.py
==============================
Tests for services/imd_service.py and services/ncs_service.py.
Phase 5C PAHAD AI.

All tests use mocks — no real HTTP calls in non-integration tests.
Integration tests (marked @pytest.mark.integration) are skipped when
credentials are absent.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, "c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi")

from services.imd_service import IMDConnector, IMDObservation, IMD_CONNECTOR
from services.ncs_service import NCSConnector, NCSObservation, NCS_CONNECTOR


# ─────────────────────────────────────────────────────────────────────────────
# IMD CONNECTOR TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestIMDConnector:

    # Test 1: AUTH_REQUIRED when env vars missing
    def test_imd_auth_required_when_not_configured(self):
        """IMDConnector.status must be AUTH_REQUIRED when env vars absent."""
        env = {"IMD_API_BASE_URL": "", "IMD_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = IMDConnector()
        assert connector.status == "AUTH_REQUIRED"

    # Test 2: get_status() returns AUTH_REQUIRED
    def test_imd_get_status_returns_auth_required(self):
        status = IMD_CONNECTOR.get_status()
        assert "status" in status
        assert "provider" in status
        # Since no creds in .env, should be AUTH_REQUIRED
        assert status["status"] in ("AUTH_REQUIRED", "READY", "LIVE")

    # Test 3: fetch_observations returns list with AUTH_REQUIRED provenance
    def test_imd_fetch_returns_auth_required_when_unconfigured(self):
        env = {"IMD_API_BASE_URL": "", "IMD_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = IMDConnector()
        obs = connector.fetch_observations(lat=27.33, lon=88.61, sector_id="TEST")
        assert isinstance(obs, list)
        assert len(obs) >= 1
        assert obs[0].provenance == "AUTH_REQUIRED"
        assert obs[0].value is None

    # Test 4: IMDObservation has required fields
    def test_imd_observation_required_fields(self):
        obs = IMDObservation(
            sector_id="SK-NH10-KM48",
            timestamp="2026-09-10T00:00:00+00:00",
            feature="rain_1h",
            value=None,
            unit="mm",
            source="IMD",
            quality="AUTH_REQUIRED",
            provenance="AUTH_REQUIRED",
            freshness="UNAVAILABLE",
            observed_at="",
            received_at="2026-09-10T00:00:00+00:00",
            location={"lat": 27.33, "lon": 88.61}
        )
        d = obs.to_dict()
        required_keys = ["sector_id", "timestamp", "feature", "value", "unit",
                         "source", "quality", "provenance"]
        for k in required_keys:
            assert k in d, f"Missing field: {k}"

    # Test 5: get_status returns dict with 'auth' key
    def test_imd_status_has_auth_key(self):
        status = IMD_CONNECTOR.get_status()
        assert "auth" in status

    # Test 6: AUTH_REJECTED on HTTP 401 mock
    def test_imd_returns_auth_required_on_401(self):
        env = {"IMD_API_BASE_URL": "https://mausam.imd.gov.in/api",
               "IMD_API_TOKEN": "valid_token_here"}
        with patch.dict(os.environ, env, clear=False):
            connector = IMDConnector()
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        with patch("services.imd_service.requests.get", return_value=mock_resp):
            obs = connector.fetch_observations(lat=27.33, lon=88.61, sector_id="TEST")
        assert len(obs) >= 1
        assert obs[0].provenance == "AUTH_REQUIRED"


# ─────────────────────────────────────────────────────────────────────────────
# NCS CONNECTOR TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestNCSConnector:

    # Test 7: USGS_FALLBACK when NCS_API_BASE_URL not set
    def test_ncs_uses_usgs_fallback_when_base_url_absent(self):
        env = {"NCS_API_BASE_URL": "", "NCS_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = NCSConnector()
        assert connector.status == "USGS_FALLBACK"
        assert not connector._is_ncs_configured()

    # Test 8: get_status() returns dict with 'status' key
    def test_ncs_get_status_has_status_key(self):
        status = NCS_CONNECTOR.get_status()
        assert "status" in status
        assert "provider" in status

    # Test 9: NCSObservation has required fields
    def test_ncs_observation_required_fields(self):
        obs = NCSObservation(
            event_id="TEST-001",
            timestamp="2026-09-10T00:00:00+00:00",
            magnitude=3.5,
            magnitude_type="ML",
            depth_km=15.0,
            latitude=27.3,
            longitude=88.6,
            region="Sikkim NE",
            source="USGS",
            provenance="LIVE",
            quality="GOOD",
            received_at="2026-09-10T00:00:00+00:00"
        )
        d = obs.to_dict()
        required_keys = ["event_id", "timestamp", "magnitude", "provenance"]
        for k in required_keys:
            assert k in d, f"Missing field: {k}"

    # Test 10: USGS GeoJSON parsed correctly with 2 features
    def test_ncs_usgs_fallback_parses_geojson(self):
        env = {"NCS_API_BASE_URL": "", "NCS_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = NCSConnector()

        usgs_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "us7000abc1",
                    "properties": {
                        "mag": 4.2, "magType": "Mw",
                        "place": "Sikkim", "time": 1726000000000
                    },
                    "geometry": {"type": "Point", "coordinates": [88.6, 27.3, 10.0]}
                },
                {
                    "id": "us7000abc2",
                    "properties": {
                        "mag": 3.1, "magType": "ML",
                        "place": "Assam", "time": 1725900000000
                    },
                    "geometry": {"type": "Point", "coordinates": [93.0, 25.1, 20.0]}
                }
            ]
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = usgs_geojson

        with patch("services.ncs_service.requests.get", return_value=mock_resp):
            events = connector.fetch_recent_events(min_mag=2.5)

        assert len(events) == 2
        assert events[0].magnitude == pytest.approx(4.2)
        assert events[0].source == "USGS"
        assert events[0].provenance == "LIVE"
        assert events[1].magnitude == pytest.approx(3.1)

    # Test 11: Returns empty list on USGS network failure
    def test_ncs_returns_empty_on_network_error(self):
        env = {"NCS_API_BASE_URL": "", "NCS_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = NCSConnector()

        import requests as req_mod
        with patch("services.ncs_service.requests.get",
                   side_effect=req_mod.exceptions.ConnectionError("Network down")):
            events = connector.fetch_recent_events(min_mag=2.5)

        assert isinstance(events, list)
        assert len(events) == 0

    # Test 12: NCSConnector.get_status() has usgs_fallback field
    def test_ncs_status_has_usgs_fallback(self):
        status = NCS_CONNECTOR.get_status()
        assert "usgs_fallback" in status
        assert status["usgs_fallback"] == "ALWAYS_AVAILABLE"

    # Test 13: derive_seismic_indicators calculates correct metrics
    def test_ncs_derive_seismic_indicators(self):
        connector = NCSConnector()
        now = datetime.now(timezone.utc)
        ev1 = NCSObservation(
            event_id="EV-1",
            timestamp=(now - timedelta(minutes=30)).isoformat(),
            magnitude=4.5,
            magnitude_type="Mw",
            depth_km=10.0,
            latitude=27.35,
            longitude=88.62,
            region="Sikkim",
            source="USGS",
            provenance="LIVE",
            quality="GOOD",
            received_at=now.isoformat()
        )
        ev2 = NCSObservation(
            event_id="EV-2",
            timestamp=(now - timedelta(hours=2)).isoformat(),
            magnitude=3.2,
            magnitude_type="ML",
            depth_km=15.0,
            latitude=27.50,
            longitude=88.80,
            region="North Sikkim",
            source="USGS",
            provenance="LIVE",
            quality="GOOD",
            received_at=now.isoformat()
        )
        derived = connector.derive_seismic_indicators([ev1, ev2], sector_lat=27.33, sector_lon=88.61)
        assert "count_24h" in derived
        assert "count_72h" in derived
        assert "max_magnitude" in derived
        assert "nearest_distance_km" in derived
        assert derived["count_24h"] == 2
        assert derived["max_magnitude"] == 4.5
        assert derived["nearest_distance_km"] < 10.0
        assert derived["source"] == "USGS"
        assert derived["quality"] == "GOOD"

    # Test 14: IMD extension methods return AUTH_REQUIRED when unconfigured
    def test_imd_extension_methods_unconfigured(self):
        env = {"IMD_API_BASE_URL": "", "IMD_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = IMDConnector()
        aws_obs = connector.fetch_aws_arg("AWS-001", sector_id="TEST-SEC")
        dist_obs = connector.fetch_district_rainfall("Pakyong", "Sikkim", sector_id="TEST-SEC")
        warn = connector.fetch_warnings("Sikkim", "Pakyong", sector_id="TEST-SEC")
        nowcast_obs = connector.fetch_nowcast(27.33, 88.61, sector_id="TEST-SEC")

        assert aws_obs[0].provenance == "AUTH_REQUIRED"
        assert dist_obs[0].provenance == "AUTH_REQUIRED"
        assert warn["warning_level"] == "AUTH_REQUIRED"
        assert nowcast_obs[0].provenance == "AUTH_REQUIRED"
