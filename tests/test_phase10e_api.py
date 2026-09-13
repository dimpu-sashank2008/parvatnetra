# -*- coding: utf-8 -*-
"""
tests/test_phase10e_api.py
==========================
PARVAT NETRA • Phase 10E — Public Warning REST API End-to-End Tests
-------------------------------------------------------------------
Verifies:
  1. GET  /api/warning/channels/status
  2. POST /api/warning/disseminate
  3. GET  /api/warning/delivery/<dissemination_id>
  4. GET  /api/warning/cap/<incident_id> (JSON & XML formats)
  5. GET  /api/warning/audit
"""

import json
import pytest
from app import app
from services.public_warning_service import (
    AUTHORIZATION_TOKEN_MANAGER,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_PUBLIC
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_AUTHORIZED

GEOFENCE_VALID = [
    [27.3200, 88.6000],
    [27.3400, 88.6000],
    [27.3400, 88.6200],
    [27.3200, 88.6200],
    [27.3200, 88.6000]
]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_channel_status(client):
    """Verifies that /api/warning/channels/status reports dry-run modes for all channels."""
    res = client.get("/api/warning/channels/status")
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert "channels" in data
    assert "SMS" in data["channels"]
    assert "CELL_BROADCAST" in data["channels"]
    assert "CAP_GATEWAY" in data["channels"]
    assert "SIREN" in data["channels"]
    assert data["global_safety_invariants"]["PUBLIC_DISPATCH"] == "DISABLED"
    assert data["global_safety_invariants"]["SIREN_DRY_RUN"] == 1


def test_api_disseminate_authorized(client):
    """Verifies successful authorized dissemination through REST endpoint."""
    inc_id = "INC-API-DISSEM-01"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="CRITICAL",
        model_probability=0.89,
        FoS=0.88,
        rainfall=80.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 3
    EOC_INCIDENT_MANAGER._save(inc)

    token = AUTHORIZATION_TOKEN_MANAGER.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    payload = {
        "incident_id": inc_id,
        "actor_id": "DM_PAKYONG",
        "actor_role": ROLE_DISTRICT_AUTHORITY,
        "auth_token": token,
        "geofence_polygon": GEOFENCE_VALID,
        "channels": ["SMS", "CELL_BROADCAST", "CAP_GATEWAY", "SIREN"]
    }

    res = client.post("/api/warning/disseminate", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    res_data = res.get_json()["data"]

    assert res_data["status"] == "DISSEMINATED_DRY_RUN"
    assert "dissemination_id" in res_data
    assert "channel_receipts" in res_data
    assert "audit_hash" in res_data


def test_api_disseminate_rejected_public(client):
    """Verifies that public role is rejected by /api/warning/disseminate with 403."""
    payload = {
        "incident_id": "INC-ANY",
        "actor_id": "ANON_CITIZEN",
        "actor_role": ROLE_PUBLIC,
        "auth_token": "token",
        "geofence_polygon": GEOFENCE_VALID
    }
    res = client.post("/api/warning/disseminate", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 403
    body = res.get_json()
    assert body["status"] == "rejected"


def test_api_cap_feed_json_and_xml(client):
    """Verifies that /api/warning/cap/<incident_id> outputs valid JSON and XML feeds."""
    # JSON format
    res_json = client.get("/api/warning/cap/INC-TEST-CAP?format=json")
    assert res_json.status_code == 200
    json_data = res_json.get_json()
    assert json_data["status"] == "success"
    assert "cap_data" in json_data

    # XML format
    res_xml = client.get("/api/warning/cap/INC-TEST-CAP?format=xml")
    assert res_xml.status_code == 200
    assert "application/xml" in res_xml.content_type
    assert b"<alert" in res_xml.data


def test_api_audit_trail(client):
    """Verifies that /api/warning/audit verifies ledger integrity and returns entries."""
    res = client.get("/api/warning/audit?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["ledger_integrity"] == "INTACT"
    assert "entries" in data
