# -*- coding: utf-8 -*-
"""
tests/test_phase10i_security.py
===============================
PARVAT NETRA • Phase 10I — Security, RBAC & REST API Integration Tests
----------------------------------------------------------------------
Verifies:
  1. REST API endpoint contracts:
     - GET  /api/sms/status
     - POST /api/sms/queue-emergency
     - POST /api/sms/dlr
     - GET  /api/sms/delivery/<dispatch_id>
     - GET  /api/sms/sachet/<incident_id>
     - POST /api/sms/cell-broadcast
  2. No API keys or plain credentials leaked in REST responses.
  3. RBAC enforcement: 403 Forbidden for unprivileged callers.
  4. PII protection: Responses contain only masked phone numbers.
  5. SACHET / CAP 1.2 handoff and Cell Broadcast preview contracts.
"""

import json
import pytest
from app import app
from services.production_sms_service import (
    PRODUCTION_SMS_SERVICE,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_PUBLIC
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_AUTHORIZED

GEOFENCE = [
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


def test_api_sms_status(client):
    """Verifies that /api/sms/status reports configuration safely without leaking passwords."""
    res = client.get("/api/sms/status")
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert "configuration_state" in data
    assert "safety_mode" in data
    assert data["safety_mode"] == "TEST/DRY_RUN"
    assert "india_government_readiness" in data
    assert "CDAC_SMS_PASSWORD" not in str(data)
    assert "secret" not in str(data).lower()


def test_api_queue_emergency_authorized(client):
    """Verifies successful authorized emergency SMS queueing via REST endpoint."""
    inc_id = "INC-SEC-01"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=88.0,
        risk_band="CRITICAL",
        model_probability=0.91,
        FoS=0.84,
        rainfall=95.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 3
    EOC_INCIDENT_MANAGER._save(inc)

    token = PRODUCTION_SMS_SERVICE.auth_token_mgr.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    payload = {
        "incident_id": inc_id,
        "actor_id": "DM_PAKYONG",
        "actor_role": ROLE_DISTRICT_AUTHORITY,
        "auth_token": token,
        "geofence_polygon": GEOFENCE
    }

    res = client.post("/api/sms/queue-emergency", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    body = res.get_json()["data"]

    assert body["success"] is True
    assert body["dispatched_count"] > 0
    assert body["dry_run"] is True

    # Verify PII minimization in response
    for rec in body["recipients"]:
        assert "-XXXXX-" in rec["phone_masked"]
        assert "phone_hash" in rec
        assert "phone_raw" not in rec  # Raw phone must not be exposed


def test_api_queue_emergency_rejected_public(client):
    """Verifies that unauthorized public callers are rejected with 403 Forbidden."""
    payload = {
        "incident_id": "INC-SEC-02",
        "actor_id": "PUBLIC_CALLER",
        "actor_role": ROLE_PUBLIC,
        "auth_token": "token",
        "geofence_polygon": GEOFENCE
    }

    res = client.post("/api/sms/queue-emergency", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 403
    body = res.get_json()
    assert body["status"] == "rejected"


def test_api_dlr_webhook_flow(client):
    """Verifies DLR webhook ingestion and retrieval."""
    payload = {
        "dispatch_id": "DISP-API-TEST-99",
        "provider_reference": "CDAC-GW-12345",
        "carrier_status": "DELIVRD"
    }

    res = client.post("/api/sms/dlr", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    assert res.get_json()["status"] == "success"

    # Retrieve receipt
    res_get = client.get("/api/sms/delivery/DISP-API-TEST-99")
    assert res_get.status_code == 200
    rec = res_get.get_json()["data"]
    assert rec["status"] == "DELIVERED"
    assert rec["provider_reference"] == "CDAC-GW-12345"


def test_api_sachet_and_cell_broadcast_preview(client):
    """Verifies SACHET handoff and Cell Broadcast endpoints."""
    # SACHET handoff
    res_sachet = client.get("/api/sms/sachet/INC-SEC-01")
    assert res_sachet.status_code == 200
    s_data = res_sachet.get_json()["data"]
    assert s_data["sachet_status"] == "READY"
    assert "cap_xml" in s_data

    # Cell Broadcast preview
    cb_payload = {
        "geofence_polygon": GEOFENCE,
        "severity": "Extreme",
        "urgency": "Immediate",
        "message": "Evacuation advisory"
    }
    res_cb = client.post("/api/sms/cell-broadcast", data=json.dumps(cb_payload), content_type="application/json")
    assert res_cb.status_code == 200
    cb_data = res_cb.get_json()["data"]
    assert cb_data["provider_status"] == "TEST/DRY_RUN"
    assert cb_data["dry_run"] is True
