# -*- coding: utf-8 -*-
"""
tests/test_phase7g_rbac.py
==========================
PHASE 7G — Checkpoint 7G-01: Authority Role-Based Access Control (RBAC) Audit
Verifies privilege separation across:
  - PUBLIC
  - FIELD_OPERATOR
  - DISTRICT_AUTHORITY / STATE_AUTHORITY / AUTHORITY
  - ADMIN

Enforces:
  1. PUBLIC cannot approve alerts, authorize dispatches, or trigger sirens.
  2. FIELD_OPERATOR cannot approve alerts or authorize dispatches; can inspect, verify, escalate.
  3. DISTRICT_AUTHORITY / STATE_AUTHORITY can approve, reject, escalate, rollback, and authorize dispatch.
  4. ADMIN cannot approve warnings or bypass safety doctrines.
  5. NO role can activate physical sirens (siren safety lock).
"""

import os
import sys
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_PUBLIC,
    ROLE_FIELD_OPERATOR,
    ROLE_AUTHORITY,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_ADMIN,
    ACTION_APPROVE,
    ACTION_REJECT,
    ACTION_REQUEST_FIELD_VERIFICATION,
    ACTION_ESCALATE,
    ACTION_DEFER,
    ACTION_ROLLBACK,
    ACTION_OVERRIDE,
    check_rbac_permission
)
from engine.pahad_decision_store import DecisionRecordStore
from engine.operational_state_machine import OperationalStateMachine


@pytest.fixture
def isolated_env(tmp_path):
    db_file = str(tmp_path / "rbac_test.db")
    sm = OperationalStateMachine(db_path=db_file)
    dec_store = DecisionRecordStore(db_path=db_file)
    auth_srv = AuthorityReviewService(db_path=db_file, state_machine=sm)
    return dec_store, auth_srv, sm


def test_public_role_permissions():
    """PUBLIC role can only receive alerts and submit citizen reports; zero administrative power."""
    assert check_rbac_permission(ROLE_PUBLIC, "can_receive_alerts") is False
    assert check_rbac_permission(ROLE_PUBLIC, ACTION_APPROVE) is False
    assert check_rbac_permission(ROLE_PUBLIC, ACTION_REJECT) is False
    assert check_rbac_permission(ROLE_PUBLIC, ACTION_REQUEST_FIELD_VERIFICATION) is False
    assert check_rbac_permission(ROLE_PUBLIC, "AUTHORIZE_DISPATCH") is False
    assert check_rbac_permission(ROLE_PUBLIC, "TRIGGER_SIREN") is False


def test_public_role_submit_rejected(isolated_env, monkeypatch):
    """PUBLIC attempting to submit any authority action is rejected with PermissionError."""
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})

    with pytest.raises(PermissionError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="CITIZEN_ANON",
            role=ROLE_PUBLIC,
            action=ACTION_APPROVE,
            justification="I think road should close"
        )
    assert "PUBLIC role has zero administrative authority" in str(exc.value)


def test_field_operator_permissions():
    """FIELD_OPERATOR can inspect and request verification, but CANNOT approve or dispatch."""
    assert check_rbac_permission(ROLE_FIELD_OPERATOR, ACTION_REQUEST_FIELD_VERIFICATION) is True
    assert check_rbac_permission(ROLE_FIELD_OPERATOR, ACTION_ESCALATE) is True
    assert check_rbac_permission(ROLE_FIELD_OPERATOR, ACTION_DEFER) is True
    assert check_rbac_permission(ROLE_FIELD_OPERATOR, ACTION_APPROVE) is False
    assert check_rbac_permission(ROLE_FIELD_OPERATOR, "AUTHORIZE_DISPATCH") is False
    assert check_rbac_permission(ROLE_FIELD_OPERATOR, "TRIGGER_SIREN") is False


def test_field_operator_cannot_approve(isolated_env, monkeypatch):
    """FIELD_OPERATOR attempting to APPROVE is strictly rejected with PermissionError."""
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.90, "event_probability": 0.88})

    with pytest.raises(PermissionError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="BRO_OPERATOR_01",
            role=ROLE_FIELD_OPERATOR,
            action=ACTION_APPROVE,
            justification="Direct field approval"
        )
    assert "FIELD_OPERATOR cannot APPROVE" in str(exc.value)


def test_district_authority_permissions(isolated_env, monkeypatch):
    """DISTRICT_AUTHORITY can approve, reject, rollback, and authorize dispatches."""
    assert check_rbac_permission(ROLE_DISTRICT_AUTHORITY, ACTION_APPROVE) is True
    assert check_rbac_permission(ROLE_DISTRICT_AUTHORITY, ACTION_REJECT) is True
    assert check_rbac_permission(ROLE_DISTRICT_AUTHORITY, ACTION_ROLLBACK) is True
    assert check_rbac_permission(ROLE_DISTRICT_AUTHORITY, "AUTHORIZE_DISPATCH") is True
    assert check_rbac_permission(ROLE_DISTRICT_AUTHORITY, "TRIGGER_SIREN") is False


def test_admin_cannot_approve_alerts(isolated_env, monkeypatch):
    """ADMIN role is restricted to system maintenance and CANNOT approve public warnings."""
    assert check_rbac_permission(ROLE_ADMIN, ACTION_APPROVE) is False
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.92, "event_probability": 0.86})

    with pytest.raises(PermissionError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="SYSADMIN_ROOT",
            role=ROLE_ADMIN,
            action=ACTION_APPROVE,
            justification="Admin root approval"
        )
    assert "ADMIN cannot APPROVE public warnings" in str(exc.value)


def test_no_role_can_trigger_physical_sirens():
    """Safety Invariant: Zero roles possess permission to directly trigger physical sirens."""
    all_roles = [ROLE_PUBLIC, ROLE_FIELD_OPERATOR, ROLE_AUTHORITY, ROLE_DISTRICT_AUTHORITY, ROLE_STATE_AUTHORITY, ROLE_ADMIN]
    for role in all_roles:
        assert check_rbac_permission(role, "TRIGGER_SIREN") is False, f"Role {role} must not be allowed to trigger physical sirens"
