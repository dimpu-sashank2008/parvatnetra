# -*- coding: utf-8 -*-
"""
tests/test_phase7_authority_workflow.py
=======================================
Tests for Phase 7G Authority Workflow & Human-in-the-Loop Validation.
Enforces the safety invariant: AI recommendation != Public Emergency Alert.
"""

import os
import sys
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_FIELD_OPERATOR,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ACTION_APPROVE,
    ACTION_REJECT,
    ACTION_REQUEST_FIELD_VERIFICATION,
    ACTION_ESCALATE
)
from engine.pahad_decision_store import DecisionRecordStore
from engine.operational_state_machine import OperationalStateMachine

@pytest.fixture
def isolated_env(tmp_path):
    db_file = str(tmp_path / "phase7_auth.db")
    sm = OperationalStateMachine(db_path=db_file)
    dec_store = DecisionRecordStore(db_path=db_file)
    auth_srv = AuthorityReviewService(db_path=db_file, state_machine=sm)
    return dec_store, auth_srv, sm

def test_ai_recommendation_does_not_auto_dispatch(isolated_env, monkeypatch):
    """Safety Invariant: High risk AI recommendation NEVER automatically triggers PUBLIC_DISPATCH."""
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    sector_id = "SK-NH10-KM48"
    # AI records critical condition
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 0.85, "event_probability": 0.95, "rain_24h_mm": 220.0}
    )
    assert dec["risk"] == "CRITICAL"
    assert dec["recommended_action"] in {"READY_FOR_AUTHORITY_REVIEW", "RED_ALERT_CORRIDOR_CLOSURE"}

    # Verify state machine is NOT in PUBLIC_DISPATCH
    current_state = sm.get_state(sector_id)
    assert current_state != "PUBLIC_DISPATCH"
    assert current_state in {"MONITORING", "SIGNAL_ANOMALY", "CONFIRMATION_PENDING", "STATE_AUTHORITY_REVIEW", "AUTHORITY_REVIEW"}

def test_two_stage_human_signoff(isolated_env, monkeypatch):
    """Validates two-stage review: Field verification followed by District Authority authorization."""
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    sector_id = "SK-NH10-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 0.95, "event_probability": 0.89}
    )

    # Stage 1: Field Operator verifies situation and requests field verification
    res_stage1 = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="BRO_OFFICER_LEPCHA",
        role=ROLE_FIELD_OPERATOR,
        action=ACTION_REQUEST_FIELD_VERIFICATION,
        justification="Verified tension cracks on shoulder at KM48. QRT dispatched."
    )
    assert res_stage1["action"] == ACTION_REQUEST_FIELD_VERIFICATION
    assert res_stage1["new_operational_state"] == "FIELD_RESPONSE"

    # Stage 2: District Magistrate reviews findings and issues formal authorization
    res_stage2 = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Confirmed slope failure imminent. Evacuating traffic to NH-717A.",
        authorization_token="PAKYONG-DM-ORDER-2026-99"
    )
    assert res_stage2["action"] == ACTION_APPROVE
    assert res_stage2["new_operational_state"] == "WARNING_AUTHORIZED"

def test_unauthorized_role_approval_rejected(isolated_env, monkeypatch):
    """Field operator attempting to approve public warning directly is rejected with PermissionError."""
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.92, "event_probability": 0.91})
    with pytest.raises(PermissionError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="FIELD_TECH_01",
            role=ROLE_FIELD_OPERATOR,
            action=ACTION_APPROVE,
            justification="Approve directly"
        )
    assert "cannot APPROVE" in str(exc.value)

def test_escalation_workflow(isolated_env, monkeypatch):
    """Field operator can escalate complex incident to District Authority."""
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 1.05, "event_probability": 0.74})
    res = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="BRO_OFFICER_01",
        role=ROLE_FIELD_OPERATOR,
        action=ACTION_ESCALATE,
        justification="Multi-kilometer fissure detected; requires District Magistrate inter-agency coordination."
    )
    assert res["action"] == ACTION_ESCALATE
    assert res["new_operational_state"] == "AUTHORITY_REVIEW"

def test_emergency_cancellation_and_rollback(isolated_env, monkeypatch):
    """Authority can dismiss a warning as false positive, rolling back to CANCELLED state."""
    dec_store, auth_srv, sm = isolated_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 1.12, "event_probability": 0.71})
    res = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_REJECT,
        justification="On-site inspection confirmed reading caused by construction blasting nearby, slope face is intact."
    )
    assert res["action"] == ACTION_REJECT
    assert res["new_operational_state"] == "CANCELLED"
