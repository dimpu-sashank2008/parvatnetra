# -*- coding: utf-8 -*-
"""
tests/test_phase11j_smoke.py
============================
Phase 11J: Deployment Hardening & Production Release Smoke Tests.
Verifies clean application startup, routing sanity, and response
contracts for all primary operational endpoints.
"""

import pytest
from app import app
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_01_root_dashboard(client):
    """Verify root page / loads successfully (HTTP 200)."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"PARVAT NETRA" in res.data or b"html" in res.data.lower()


def test_02_health_endpoints(client):
    """Verify /health returns 200 and /api/health returns valid status structure."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "UP"
    assert "version" in data

    api_res = client.get("/api/health")
    # 200 when PostGIS is connected, 503 when disconnected (standalone fallback)
    assert api_res.status_code in (200, 503)
    api_data = api_res.get_json()
    assert "status" in api_data
    assert "database" in api_data
    assert "service" in api_data


def test_03_pahad_live_inference(client):
    """Verify /api/pahad/live-inference executes inference with provenance."""
    res = client.post("/api/pahad/live-inference", json={
        "sector_id": "SK-NH10-KM48",
        "latitude": 27.33,
        "longitude": 88.61,
        "horizon_hours": 24
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "inference" in data
    inf = data["inference"]
    assert "cri" in inf or "risk_score" in inf
    assert "model_status" in inf


def test_04_pahad_forecast(client):
    """Verify /api/pahad/forecast returns multi-horizon forecast."""
    res = client.get("/api/pahad/forecast?sector_id=SK-NH10-KM48&lat=27.33&lon=88.61")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "forecast" in data


def test_05_pahad_data_status(client):
    """Verify /api/pahad/data-status returns data streams and model status."""
    res = client.get("/api/pahad/data-status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "data_streams" in data
    assert "event_model" in data


def test_06_pahad_highest_risk_corridor(client):
    """Verify /api/pahad/highest-risk-corridor identifies authoritative critical corridor."""
    res = client.get("/api/pahad/highest-risk-corridor")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "highest_risk_corridor" in data
    assert "id" in data["highest_risk_corridor"]
    assert "cri" in data["highest_risk_corridor"]


def test_07_eoc_incidents(client):
    """Verify /api/eoc/incidents returns incident list."""
    res = client.get("/api/eoc/incidents")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "incidents" in data


def test_08_eoc_command_brief(client):
    """Verify /api/eoc/command-brief returns executive briefing."""
    res = client.get("/api/eoc/command-brief")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "brief" in data


def test_09_eoc_sitrep(client):
    """Verify /api/eoc/sitrep/<id> generates structured SITREP for an incident."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="HIGH",
        model_probability=0.81,
        FoS=0.98,
        rainfall=175.0
    )
    res = client.get(f"/api/eoc/sitrep/{inc.incident_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["incident_id"] == inc.incident_id
    assert "sections" in data


def test_10_authority_siren_access(client):
    """Verify /api/authority/siren-access returns siren configuration and safety interlock."""
    res = client.get("/api/authority/siren-access")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "siren_access" in data
    # Confirm safety interlocks are fail-closed
    siren = data["siren_access"]
    assert siren.get("physical_siren_interlock") == "LOCKED"
    assert siren.get("human_authorization_required") is True
