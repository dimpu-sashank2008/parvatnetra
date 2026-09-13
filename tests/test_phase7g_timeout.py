# -*- coding: utf-8 -*-
"""
tests/test_phase7g_timeout.py
=============================
Tests Checkpoint 7G-08: Authority Review Timeout and Fail-Closed Invariants.
Ensures alerts sitting unreviewed in AUTHORITY_REVIEW never auto-dispatch.
"""

import pytest
from engine.operational_state_machine import OperationalStateMachine, STATE_AUTHORITY_REVIEW, STATE_EXPIRED, STATE_PUBLIC_DISPATCH, STATE_WARNING_AUTHORIZED
from engine.pahad_decision_store import DecisionRecordStore
from services.authority_review_service import AuthorityReviewService, ROLE_DISTRICT_AUTHORITY, ACTION_APPROVE

def test_timeout_fails_closed_to_expired(tmp_path, monkeypatch):
    db_path = str(tmp_path / "timeout_test.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    
    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.02, "rain_24h_mm": 165.0, "event_probability": 0.88}
    )
    dec_id = dec["decision_id"]
    
    # Place entity in AUTHORITY_REVIEW
    sm.transition(sector_id, "ANOMALY_DETECTED", "TEST", "Trigger")
    sm.transition(sector_id, "PAHAD_EVALUATING", "TEST", "Eval")
    sm.transition(sector_id, "CORROBORATION_PENDING", "TEST", "Corrob")
    sm.transition(sector_id, "AUTHORITY_REVIEW", "TEST", "Awaiting review")
    assert sm.get_state(sector_id) == STATE_AUTHORITY_REVIEW
    
    res = svc.handle_review_timeout(dec_id, timeout_seconds=900, action="EXPIRE")
    assert res["timed_out"] is True
    assert res["action_taken"] == "EXPIRED"
    assert res["new_state"] == STATE_EXPIRED
    assert res["public_dispatch_prevented"] is True
    assert sm.get_state(sector_id) == STATE_EXPIRED
    assert sm.get_state(sector_id) != STATE_PUBLIC_DISPATCH
    assert sm.get_state(sector_id) != STATE_WARNING_AUTHORIZED

def test_timeout_escalation_maintains_safety(tmp_path, monkeypatch):
    db_path = str(tmp_path / "timeout_esc.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    
    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.05, "rain_24h_mm": 155.0, "event_probability": 0.79}
    )
    dec_id = dec["decision_id"]
    
    sm.transition(sector_id, "ANOMALY_DETECTED", "TEST", "Trigger")
    sm.transition(sector_id, "PAHAD_EVALUATING", "TEST", "Eval")
    sm.transition(sector_id, "CORROBORATION_PENDING", "TEST", "Corrob")
    sm.transition(sector_id, "AUTHORITY_REVIEW", "TEST", "Awaiting review")
    
    res = svc.handle_review_timeout(dec_id, timeout_seconds=600, action="ESCALATE")
    assert res["timed_out"] is True
    assert res["action_taken"] == "ESCALATED"
    assert res["escalated_to"] == "STATE_AUTHORITY"
    assert res["public_dispatch_prevented"] is True
    assert sm.get_state(sector_id) == STATE_AUTHORITY_REVIEW
    assert sm.get_state(sector_id) != STATE_PUBLIC_DISPATCH

def test_already_resolved_alert_does_not_timeout(tmp_path, monkeypatch):
    db_path = str(tmp_path / "timeout_resolved.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    
    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.05, "rain_24h_mm": 155.0, "event_probability": 0.79}
    )
    dec_id = dec["decision_id"]
    
    token = svc.token_manager.issue_token("DIST_OFFICER_01", ROLE_DISTRICT_AUTHORITY, dec_id)
    svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DIST_OFFICER_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Legitimate ground hazard confirmed",
        authorization_token=token
    )
    
    res = svc.handle_review_timeout(dec_id, timeout_seconds=900, action="EXPIRE")
    assert res["timed_out"] is False
    assert "already resolved" in res["reason"]
