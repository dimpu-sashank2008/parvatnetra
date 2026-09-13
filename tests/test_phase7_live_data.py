# -*- coding: utf-8 -*-
"""
tests/test_phase7_live_data.py
==============================
Tests for Phase 7E Live Data Readiness & Connector Qualification.
Verifies all 8 data connectors report honest statuses without fabricating connectivity.
"""

import pytest
from scripts.validate_live_data import audit_all_connectors

def test_eight_connectors_audited():
    rep = audit_all_connectors()
    assert rep["total_connectors_audited"] == 8
    assert "public_unauthenticated_connectors" in rep
    assert "institutional_authenticated_connectors" in rep
    assert "infrastructure_connectors" in rep

def test_public_connectors_operational():
    rep = audit_all_connectors()
    public = rep["public_unauthenticated_connectors"]
    assert "open_meteo" in public
    assert public["open_meteo"]["status"] == "CONNECTED"
    assert public["open_meteo"]["auth_required"] is False

    assert "usgs_seismology" in public
    assert public["usgs_seismology"]["status"] == "CONNECTED"
    assert public["usgs_seismology"]["auth_required"] is False

def test_auth_gated_connectors_require_credentials():
    rep = audit_all_connectors()
    inst = rep["institutional_authenticated_connectors"]
    # IMD should be AUTH_REQUIRED without valid credentials
    assert inst["imd_weather"]["status"] == "AUTH_REQUIRED"
    assert inst["imd_weather"]["provenance"] == "[HISTORICAL/SIMULATED]"

    # NCS should indicate fallback to USGS
    assert inst["ncs_seismology"]["fallback"] == "USGS"
    assert inst["ncs_seismology"]["operational"] is True

    # CDSE / Sentinel-1
    assert inst["copernicus_cdse"]["status"] == "AUTH_REQUIRED"

    # ISRO Bhoonidhi
    assert inst["isro_bhoonidhi"]["status"] == "REGISTRATION_REQUIRED"

def test_infrastructure_connectors_ready():
    rep = audit_all_connectors()
    infra = rep["infrastructure_connectors"]
    assert "neon_postgres" in infra
    assert infra["neon_postgres"]["status"] in {"CONFIGURED", "UNAVAILABLE"}

    assert "iot_device_gateway" in infra
    assert infra["iot_device_gateway"]["status"] == "STANDBY_READY_FOR_DEVICES"

def test_overall_verdict_honest():
    rep = audit_all_connectors()
    summary = rep["summary"]
    assert summary["public_live_count"] == 2
    assert summary["auth_required_count"] == 4
    assert summary["zero_auth_fallback_available"] is True
    assert summary["overall_status"] == "SOFTWARE_READY_EXTERNAL_CREDENTIALS_PENDING"
