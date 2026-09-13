# -*- coding: utf-8 -*-
"""
tests/test_phase10e_authority.py
================================
PARVAT NETRA • Phase 10E — Authority Security & RBAC Enforcement Tests
----------------------------------------------------------------------
Verifies:
  1. Statutory DMA 2005 authority RBAC controls.
  2. Strict rejection of PUBLIC and FIELD_OPERATOR roles.
  3. Rejection of unauthenticated or missing actor credentials.
  4. Rejection of expired or malformed authorization tokens.
  5. Enforcement of 2-of-3 multi-source sensor/geotechnical corroboration.
  6. Enforcement of incident status (must be AUTHORIZED).
  7. Jurisdiction validation (District Magistrate jurisdiction match).
"""

import pytest
from services.public_warning_service import (
    PUBLIC_WARNING_SERVICE,
    AUTHORIZATION_TOKEN_MANAGER,
    ROLE_PUBLIC,
    ROLE_FIELD_OPERATOR,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY
)
from engine.eoc_incident_manager import (
    EOC_INCIDENT_MANAGER,
    STATE_NEW,
    STATE_AUTHORIZED
)


class MockIncident:
    """Mock incident object for unit test isolation."""
    def __init__(self, incident_id: str, status: str, corroboration_count: int, district: str = "Pakyong"):
        self.incident_id = incident_id
        self.incident_status = status
        self.corroboration_count = corroboration_count
        self.district = district
        self.sector_id = "SK-NH10-KM48"
        self.severity = "WARNING"


def test_reject_public_role():
    """Verifies that PUBLIC users cannot authorize or trigger emergency dissemination."""
    inc = MockIncident("INC-AUTH-01", STATE_AUTHORIZED, 2)
    ok, reason = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="CITIZEN_001",
        actor_role=ROLE_PUBLIC,
        incident_id="INC-AUTH-01",
        auth_token="AUTH-v1.dummy.sig",
        incident_obj=inc
    )
    assert ok is False
    assert "strictly prohibited" in reason.lower()


def test_reject_field_operator_role():
    """Verifies that FIELD_OPERATOR cannot authorize public emergency dissemination."""
    inc = MockIncident("INC-AUTH-02", STATE_AUTHORIZED, 2)
    ok, reason = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="BRO_CREW_01",
        actor_role=ROLE_FIELD_OPERATOR,
        incident_id="INC-AUTH-02",
        auth_token="AUTH-v1.dummy.sig",
        incident_obj=inc
    )
    assert ok is False
    assert "strictly prohibited" in reason.lower()


def test_reject_unauthenticated():
    """Verifies that requests without actor_id or role fail."""
    inc = MockIncident("INC-AUTH-03", STATE_AUTHORIZED, 2)
    ok, reason = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="",
        actor_role="",
        incident_id="INC-AUTH-03",
        auth_token="AUTH-v1.dummy.sig",
        incident_obj=inc
    )
    assert ok is False
    assert "unauthenticated" in reason.lower()


def test_reject_missing_or_expired_token():
    """Verifies that missing or expired authorization token fails."""
    inc = MockIncident("INC-AUTH-04", STATE_AUTHORIZED, 2)
    ok, reason = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="DM_OFFICER",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        incident_id="INC-AUTH-04",
        auth_token="",
        incident_obj=inc
    )
    assert ok is False
    assert "missing" in reason.lower()

    # Expired token test
    ok_exp, reason_exp = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="DM_OFFICER",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        incident_id="INC-AUTH-04",
        auth_token="AUTH-v1.EXPIRED.SIG",
        incident_obj=inc
    )
    assert ok_exp is False
    assert "expired" in reason_exp.lower() or "validation failed" in reason_exp.lower()


def test_reject_insufficient_corroboration():
    """Verifies that alert is blocked if 2-of-3 corroboration is not met."""
    token = AUTHORIZATION_TOKEN_MANAGER.issue_token("DM_OFFICER", ROLE_DISTRICT_AUTHORITY, "INC-AUTH-05")
    inc_uncorroborated = MockIncident("INC-AUTH-05", STATE_AUTHORIZED, corroboration_count=1)

    ok, reason = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="DM_OFFICER",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        incident_id="INC-AUTH-05",
        auth_token=token,
        incident_obj=inc_uncorroborated
    )
    assert ok is False
    assert "corroboration" in reason.lower()


def test_reject_unauthorized_incident_status():
    """Verifies that incidents not in STATE_AUTHORIZED cannot be disseminated."""
    token = AUTHORIZATION_TOKEN_MANAGER.issue_token("DM_OFFICER", ROLE_DISTRICT_AUTHORITY, "INC-AUTH-06")
    inc_new = MockIncident("INC-AUTH-06", STATE_NEW, corroboration_count=2)

    ok, reason = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="DM_OFFICER",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        incident_id="INC-AUTH-06",
        auth_token=token,
        incident_obj=inc_new
    )
    assert ok is False
    assert "not authorized" in reason.lower()


def test_reject_jurisdiction_mismatch():
    """Verifies that District Magistrate outside incident jurisdiction is rejected."""
    token = AUTHORIZATION_TOKEN_MANAGER.issue_token("DM_NAMCHI", ROLE_DISTRICT_AUTHORITY, "INC-AUTH-07")
    inc_pakyong = MockIncident("INC-AUTH-07", STATE_AUTHORIZED, 2, district="Pakyong")

    ok, reason = PUBLIC_WARNING_SERVICE.validate_authority_and_corroboration(
        actor_id="DM_NAMCHI",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        incident_id="INC-AUTH-07",
        auth_token=token,
        jurisdiction="Namchi District",
        incident_obj=inc_pakyong
    )
    assert ok is False
    assert "jurisdiction mismatch" in reason.lower()
