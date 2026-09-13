# -*- coding: utf-8 -*-
"""
tests/test_phase10j_demo_send.py
================================
PARVAT NETRA • Phase 10J — Interactive Demo Send REST API Tests
---------------------------------------------------------------
Verifies:
  1. POST /api/notifications/demo/send-test for Email destinations.
  2. POST /api/notifications/demo/send-test for SMS destinations.
  3. Automatic channel detection (Email vs Phone).
  4. Mandatory [PARVAT NETRA TEST ALERT] safety banner.
  5. Strict validation rejection of malformed addresses.
  6. Tamper-evident audit logging for every demo send.
"""

import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_demo_send_email_success(client):
    """Verifies successful test email dispatch via demo send endpoint."""
    payload = {
        "recipient": "evaluator@sih.gov.in",
        "channel": "EMAIL",
        "recipient_name": "SIH Evaluator",
        "language": "en",
        "alert_type": "TEST_ALERT",
        "corridor": "NH-10 (Sikkim Lifeline KM 48)"
    }
    res = client.post("/api/notifications/demo/send-test", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    body = res.get_json()

    assert body["success"] is True
    assert body["channel"] == "EMAIL"
    assert body["status"] in ("SIMULATED", "SENT")
    assert "provider_reference" in body
    assert body["provider"] == "DEMO_EMAIL_GATEWAY"
    assert "evaluator@sih.gov.in" in body["recipient_masked"] or "e*******r@sih.gov.in" in body["recipient_masked"]
    assert "[PARVAT NETRA TEST ALERT]" in body["test_banner"]


def test_demo_send_sms_success(client):
    """Verifies successful test SMS dispatch via demo send endpoint."""
    payload = {
        "recipient": "+919832011234",
        "channel": "SMS",
        "language": "ne",
        "alert_type": "HIGH_RISK_ADVISORY",
        "corridor": "NH-10 Km 48"
    }
    res = client.post("/api/notifications/demo/send-test", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    body = res.get_json()

    assert body["success"] is True
    assert body["channel"] == "SMS"
    assert body["status"] == "SIMULATED"
    assert "+91-XXXXX-1234" in body["recipient_masked"]
    assert "[PARVAT NETRA TEST ALERT]" in body["message_preview"]


def test_demo_send_auto_channel_detection(client):
    """Verifies auto channel detection differentiates between email and phone."""
    # Email auto-detect
    res_eml = client.post("/api/notifications/demo/send-test", data=json.dumps({
        "recipient": "officer@assam.gov.in",
        "channel": "AUTO"
    }), content_type="application/json")
    assert res_eml.status_code == 200
    assert res_eml.get_json()["channel"] == "EMAIL"

    # Phone auto-detect
    res_sms = client.post("/api/notifications/demo/send-test", data=json.dumps({
        "recipient": "+919832055678",
        "channel": "AUTO"
    }), content_type="application/json")
    assert res_sms.status_code == 200
    assert res_sms.get_json()["channel"] == "SMS"


def test_demo_send_invalid_inputs(client):
    """Verifies rejection of invalid recipient inputs with clear reasons."""
    # Empty recipient
    res_empty = client.post("/api/notifications/demo/send-test", data=json.dumps({
        "recipient": ""
    }), content_type="application/json")
    assert res_empty.status_code == 400

    # Bad email
    res_bad_email = client.post("/api/notifications/demo/send-test", data=json.dumps({
        "recipient": "not-an-email",
        "channel": "EMAIL"
    }), content_type="application/json")
    assert res_bad_email.status_code == 400
    assert "invalid email format" in res_bad_email.get_json()["error"].lower()

    # Bad phone number (too short)
    res_bad_phone = client.post("/api/notifications/demo/send-test", data=json.dumps({
        "recipient": "123",
        "channel": "SMS"
    }), content_type="application/json")
    assert res_bad_phone.status_code == 400
    assert "at least 10 digits" in res_bad_phone.get_json()["error"].lower()


def test_demo_journal_logging(client):
    """Verifies every demo dispatch is queryable via /api/notifications/demo/journal."""
    # Dispatch an alert
    client.post("/api/notifications/demo/send-test", data=json.dumps({
        "recipient": "journal_test@sih.gov.in",
        "channel": "EMAIL"
    }), content_type="application/json")

    res = client.get("/api/notifications/demo/journal?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert len(data["journal"]) > 0

    latest = data["journal"][-1]
    assert "message_id" in latest
    assert "audit_hash" in latest
    assert "channel" in latest
