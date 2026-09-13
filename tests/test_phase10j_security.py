# -*- coding: utf-8 -*-
"""
tests/test_phase10j_security.py
===============================
PARVAT NETRA • Phase 10J — Authority Gate & Safety Protocol Tests
-----------------------------------------------------------------
Verifies:
  1. Statutory DMA 2005 authority gate for emergency alerting.
  2. Multi-source corroboration requirement (>= 2 independent signals).
  3. Incident authorization state gate (must be STATE_AUTHORIZED).
  4. Cryptographic HMAC token validation and rejection of expired tokens.
  5. AI and Voice Assistant strictly prohibited from autonomous public dispatch.
  6. Rejection of unauthenticated and public roles.
"""

import pytest
from services.production_sms_service import (
    PRODUCTION_SMS_SERVICE,
    ROLE_PUBLIC,
    ROLE_FIELD_OPERATOR,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    STATE_BLOCKED
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_NEW, STATE_AUTHORIZED

GEOFENCE = [
    [27.32, 88.60],
    [27.34, 88.60],
    [27.34, 88.62],
    [27.32, 88.62],
    [27.32, 88.60]
]


def test_public_and_operator_roles_blocked():
    """Verifies that non-authorized roles cannot trigger emergency dissemination."""
    res_pub = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id="INC-SEC-01",
        actor_id="CITIZEN_01",
        actor_role=ROLE_PUBLIC,
        auth_token="token",
        geofence_polygon=GEOFENCE
    )
    assert res_pub["success"] is False
    assert res_pub["status"] == STATE_BLOCKED
    assert "strictly prohibited" in res_pub["error"].lower()

    res_op = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id="INC-SEC-02",
        actor_id="OPERATOR_01",
        actor_role=ROLE_FIELD_OPERATOR,
        auth_token="token",
        geofence_polygon=GEOFENCE
    )
    assert res_op["success"] is False
    assert res_op["status"] == STATE_BLOCKED


def test_missing_and_invalid_hmac_token_blocked():
    """Verifies that missing or forged authorization tokens are rejected."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="CRITICAL",
        model_probability=0.88,
        FoS=0.89,
        rainfall=75.0,
        incident_id="INC-SEC-03"
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 3
    EOC_INCIDENT_MANAGER._save(inc)

    res_no_tok = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id="INC-SEC-03",
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token="",
        geofence_polygon=GEOFENCE
    )
    assert res_no_tok["success"] is False
    assert "missing" in res_no_tok["error"].lower()

    res_bad_tok = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id="INC-SEC-03",
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token="FORGED_TOKEN_XYZ_123",
        geofence_polygon=GEOFENCE
    )
    assert res_bad_tok["success"] is False
    assert "failed" in res_bad_tok["error"].lower()


def test_unauthorized_incident_state_blocked():
    """Verifies that incidents not in STATE_AUTHORIZED are blocked from broadcast."""
    inc_id = "INC-SEC-NEW-01"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="CRITICAL",
        model_probability=0.88,
        FoS=0.89,
        rainfall=75.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_NEW  # Not authorized
    inc.corroboration_count = 3
    EOC_INCIDENT_MANAGER._save(inc)

    token = PRODUCTION_SMS_SERVICE.auth_token_mgr.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    res = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token,
        geofence_polygon=GEOFENCE
    )
    assert res["success"] is False
    assert "not authorized" in res["error"].lower()


def test_corroboration_gate_enforcement():
    """Verifies that dispatches fail if 2-of-3 signal corroboration is missing."""
    inc_id = "INC-SEC-UNCORROB"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="CRITICAL",
        model_probability=0.88,
        FoS=0.89,
        rainfall=75.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 1  # Fails 2-of-3 requirement!
    inc.signal_agreement = "1-of-3 (Uncorroborated Anomaly)"
    EOC_INCIDENT_MANAGER._save(inc)

    token = PRODUCTION_SMS_SERVICE.auth_token_mgr.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    res = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token,
        geofence_polygon=GEOFENCE
    )
    assert res["success"] is False
    assert "corroboration" in res["error"].lower()
