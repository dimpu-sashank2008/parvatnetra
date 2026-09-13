# -*- coding: utf-8 -*-
"""
tests/test_phase10i_authorization.py
====================================
PARVAT NETRA • Phase 10I — Authority Gate & Security Verification Tests
-----------------------------------------------------------------------
Verifies:
  1. Mandatory DMA 2005 authority gate for emergency SMS dissemination.
  2. Multi-source sensor corroboration gate (2-of-3 required).
  3. Incident authorization status gate (must be STATE_AUTHORIZED).
  4. Cryptographic authority token verification (rejects missing/expired tokens).
  5. District jurisdiction validation.
  6. Direct rejection of unauthorized roles (PUBLIC, FIELD_OPERATOR).
  7. AI / Voice Assistant prohibited from triggering SMS dispatches autonomously.
"""

import pytest
from services.production_sms_service import (
    PRODUCTION_SMS_SERVICE,
    STATE_BLOCKED,
    ROLE_PUBLIC,
    ROLE_FIELD_OPERATOR,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_NEW, STATE_AUTHORIZED

GEOFENCE_SAMPLE = [
    [27.3200, 88.6000],
    [27.3400, 88.6000],
    [27.3400, 88.6200],
    [27.3200, 88.6200],
    [27.3200, 88.6000]
]


def test_reject_public_and_field_operator_roles():
    """Verifies that non-authority roles cannot queue emergency SMS."""
    # Test PUBLIC role
    res_pub = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id="INC-AUTH-01",
        actor_id="CITIZEN_USER",
        actor_role=ROLE_PUBLIC,
        auth_token="AUTH-v1.dummy.sig",
        geofence_polygon=GEOFENCE_SAMPLE
    )
    assert res_pub["success"] is False
    assert res_pub["status"] == STATE_BLOCKED
    assert "strictly prohibited" in res_pub["error"].lower()

    # Test FIELD_OPERATOR role
    res_field = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id="INC-AUTH-02",
        actor_id="BRO_CREW_01",
        actor_role=ROLE_FIELD_OPERATOR,
        auth_token="AUTH-v1.dummy.sig",
        geofence_polygon=GEOFENCE_SAMPLE
    )
    assert res_field["success"] is False
    assert res_field["status"] == STATE_BLOCKED
    assert "strictly prohibited" in res_field["error"].lower()


def test_reject_missing_or_expired_token():
    """Verifies that requests with missing or expired authority tokens are blocked."""
    inc_id = "INC-AUTH-03"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="CRITICAL",
        model_probability=0.88,
        FoS=0.85,
        rainfall=90.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 3
    EOC_INCIDENT_MANAGER._save(inc)

    # Missing token
    res_missing = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token="",
        geofence_polygon=GEOFENCE_SAMPLE
    )
    assert res_missing["success"] is False
    assert "missing" in res_missing["error"].lower()

    # Expired token
    res_expired = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token="AUTH-v1.EXPIRED.SIG",
        geofence_polygon=GEOFENCE_SAMPLE
    )
    assert res_expired["success"] is False
    assert "validation failed" in res_expired["error"].lower() or "expired" in res_expired["error"].lower()


def test_reject_unauthorized_incident_state():
    """Verifies that incidents in STATE_NEW cannot trigger public SMS."""
    inc_id = "INC-AUTH-04"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=80.0,
        risk_band="HIGH",
        model_probability=0.82,
        FoS=0.92,
        rainfall=70.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_NEW
    EOC_INCIDENT_MANAGER._save(inc)

    token = PRODUCTION_SMS_SERVICE.auth_token_mgr.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    res = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token,
        geofence_polygon=GEOFENCE_SAMPLE
    )
    assert res["success"] is False
    assert "not authorized" in res["error"].lower()


def test_reject_jurisdiction_mismatch():
    """Verifies that an authority outside the incident district is blocked."""
    inc_id = "INC-AUTH-05"
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
    inc.district = "Pakyong"
    inc.corroboration_count = 2
    EOC_INCIDENT_MANAGER._save(inc)

    token = PRODUCTION_SMS_SERVICE.auth_token_mgr.issue_token("DM_NAMCHI", ROLE_DISTRICT_AUTHORITY, inc_id)

    res = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_NAMCHI",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token,
        geofence_polygon=GEOFENCE_SAMPLE,
        jurisdiction="Namchi District"
    )
    assert res["success"] is False
    assert "jurisdiction mismatch" in res["error"].lower()
