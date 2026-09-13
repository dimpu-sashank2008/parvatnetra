# -*- coding: utf-8 -*-
"""
tests/test_institutional_commissioning.py
=========================================
Phase 6B Test Suite: Institutional Data Commissioning
Tests for IMD, NCS, Satellite 4-tier pipeline, and /api/institutional/data-health.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.imd_service import IMDConnector, IMD_CONNECTOR, NER_IMD_STATIONS, get_station_for_coords
from services.ncs_service import NCSConnector, NCS_CONNECTOR
from services.satellite_service import SATELLITE_SERVICE, EO_PIPELINE_STAGES
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


class TestInstitutionalIMD:

    def test_imd_unconfigured_auth_required(self):
        env = {"IMD_API_BASE_URL": "", "IMD_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = IMDConnector()
            diag = connector.verify_connection()
            assert diag["status"] == "AUTH_REQUIRED"
            assert diag["auth_state"] == "AUTH_REQUIRED"
            assert diag["authenticated"] is False
            assert "error" in diag

    def test_imd_mock_successful_connection(self):
        env = {"IMD_API_BASE_URL": "https://api.imd.gov.in/v1", "IMD_API_TOKEN": "valid_token"}
        with patch.dict(os.environ, env, clear=False):
            connector = IMDConnector()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            with patch("requests.get", return_value=mock_resp):
                diag = connector.verify_connection()
                assert diag["status"] == "LIVE"
                assert diag["auth_state"] == "CONFIGURED"
                assert diag["authenticated"] is True
                assert diag["error"] is None

    def test_imd_station_mapping(self):
        st_id, st_info = get_station_for_coords(27.33, 88.61)
        assert st_id in NER_IMD_STATIONS
        assert st_info["state"] == "Sikkim"
        assert len(NER_IMD_STATIONS) >= 10

    def test_imd_get_status_contains_all_fields(self):
        status = IMD_CONNECTOR.get_status()
        required_keys = ["status", "provider", "auth", "auth_state", "endpoint", "stations_count"]
        for k in required_keys:
            assert k in status, f"Missing key '{k}' in get_status"


class TestInstitutionalNCS:

    def test_ncs_unconfigured_auth_required(self):
        env = {"NCS_API_BASE_URL": "", "NCS_API_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            connector = NCSConnector()
            diag = connector.verify_connection()
            assert diag["status"] == "AUTH_REQUIRED"
            assert diag["ncs_status"] == "AUTH_REQUIRED"
            assert diag["auth_state"] == "AUTH_REQUIRED"
            assert diag["fallback_provider"] == "USGS"
            assert diag["fallback_status"] == "ACTIVE"

    def test_ncs_get_status_has_auth_state_and_active_source(self):
        status = NCS_CONNECTOR.get_status()
        assert "ncs_status" in status
        assert "auth_state" in status
        assert "active_source" in status
        assert status["active_source"] in ("NCS", "USGS")

    def test_ncs_mock_successful_connection(self):
        env = {"NCS_API_BASE_URL": "https://seismo.gov.in/api", "NCS_API_TOKEN": "token"}
        with patch.dict(os.environ, env, clear=False):
            connector = NCSConnector()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            with patch("requests.get", return_value=mock_resp):
                diag = connector.verify_connection()
                assert diag["status"] == "LIVE"
                assert diag["ncs_status"] == "LIVE"
                assert diag["auth_state"] == "CONFIGURED"
                assert diag["authenticated"] is True


class TestInstitutionalEO:

    def test_eo_4_tier_pipeline_structure(self):
        assert "CATALOGUE_DISCOVERY" in EO_PIPELINE_STAGES
        assert "DOWNLOAD" in EO_PIPELINE_STAGES
        assert "PROCESSING" in EO_PIPELINE_STAGES
        assert "FEATURE_READY" in EO_PIPELINE_STAGES

    def test_eo_pipeline_status_reporting(self):
        status = SATELLITE_SERVICE.get_pipeline_status()
        assert status["overall_status"] == "CATALOGUE_DISCOVERY_ACTIVE"
        assert "missions" in status
        assert "Sentinel-1_SAR" in status["missions"]
        assert "Sentinel-2_MSI" in status["missions"]
        assert "NISAR_S_Band" in status["missions"]
        assert "Copernicus_GLO30_DEM" in status["missions"]
        assert "NDVI_Vegetation" in status["missions"]

    def test_eo_verify_access_when_unconfigured(self):
        env = {"COPERNICUS_CLIENT_ID": "", "COPERNICUS_CLIENT_SECRET": ""}
        with patch.dict(os.environ, env, clear=False):
            res = SATELLITE_SERVICE.verify_eo_access()
            assert res["status"] == "AUTH_REQUIRED"
            assert res["auth_state"] == "AUTH_REQUIRED"
            assert res["raw_download_available"] is False
            assert res["catalogue_discovery_available"] is True


class TestInstitutionalDataHealthAPI:

    def test_data_health_endpoint_contract(self, client):
        resp = client.get("/api/institutional/data-health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "SUCCESS"
        assert "modalities" in data
        mods = data["modalities"]

        # Verify all 6 modalities present
        for mod_name in ("imd", "ncs", "eo", "dem", "iot", "cwc"):
            assert mod_name in mods, f"Modality '{mod_name}' missing from data-health"
            mod_data = mods[mod_name]
            assert "status" in mod_data
            assert "freshness" in mod_data
            assert "auth_state" in mod_data
            assert "source" in mod_data
            assert "error" in mod_data

    def test_data_health_credentials_audit(self, client):
        resp = client.get("/api/institutional/data-health")
        data = resp.get_json()
        assert "credentials_audit" in data
        audit = data["credentials_audit"]
        assert "IMD_API_BASE_URL" in audit
        assert "NCS_API_BASE_URL" in audit
        assert "COPERNICUS_CLIENT_ID" in audit
