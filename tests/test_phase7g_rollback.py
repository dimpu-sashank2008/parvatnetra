# -*- coding: utf-8 -*-
"""
tests/test_phase7g_rollback.py
==============================
Tests Checkpoint 7G-10: Warning Rollback and Alert Withdrawal.
Verifies that authorized warnings can be rolled back to CANCELLED state,
active notifications are withdrawn, and chained audit logs are recorded.
"""

import pytest
from engine.operational_state_machine import (
    OperationalStateMachine,
    STATE_WARNING_AUTHORIZED,
    STATE_CANCELLED,
    STATE_PUBLIC_DISPATCH
)
from engine.pahad_decision_store import DecisionRecordStore
from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_FIELD_OPERATOR,
    ACTION_APPROVE,
    ACTION_ROLLBACK
)
from services.notification_orchestrator import (
    NotificationOrchestrator,
    STATUS_CANCELLED,
    STATUS_WITHDRAWN,
    STATUS_SIMULATED
)

def test_authorized_warning_rollback_to_cancelled(tmp_path, monkeypatch):
    db_path = str(tmp_path / "rollback_test.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    notif = NotificationOrchestrator(db_path=db_path)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    monkeypatch.setattr("services.notification_orchestrator.NOTIFICATION_ORCHESTRATOR", notif)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.04, "rain_24h_mm": 160.0, "event_probability": 0.81}
    )
    dec_id = dec["decision_id"]

    # Approve warning
    token = svc.token_manager.issue_token("DM_PAKYONG_01", ROLE_DISTRICT_AUTHORITY, dec_id)
    appr_res = svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Initial ground risk assessment approved",
        authorization_token=token
    )
    assert appr_res["new_operational_state"] == STATE_WARNING_AUTHORIZED

    # Queue some notifications
    cap_dict = notif.generate_cap_alert(
        alert_id=dec_id,
        event="Landslide Hazard",
        severity="Severe",
        urgency="Expected",
        certainty="Likely",
        area_description="NH10 Km 48",
        instruction="Caution advised"
    )
    notif.dispatch_alert(
        alert_id=dec_id,
        cap_payload=cap_dict,
        channels=["SMS", "PUSH"],
        authorization_token=token,
        public_dispatch_enabled=True,
        dry_run=True
    )

    # Now execute ROLLBACK by District Authority
    roll_res = svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_ROLLBACK,
        justification="Ground inspection confirmed slope has restabilized; false alarm mitigated"
    )
    assert roll_res["action"] == ACTION_ROLLBACK
    assert roll_res["new_operational_state"] == STATE_CANCELLED
    assert sm.get_state(sector_id) == STATE_CANCELLED

    # Check notification withdrawal
    notif_list = notif.list_notifications(alert_id=dec_id)
    assert len(notif_list) > 0
    for n in notif_list:
        assert n["status"] in [STATUS_WITHDRAWN, STATUS_CANCELLED]

def test_field_operator_cannot_execute_rollback(tmp_path, monkeypatch):
    db_path = str(tmp_path / "rollback_perm.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.04, "rain_24h_mm": 160.0, "event_probability": 0.81}
    )
    dec_id = dec["decision_id"]

    token = svc.token_manager.issue_token("DM_PAKYONG_01", ROLE_DISTRICT_AUTHORITY, dec_id)
    svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Approved",
        authorization_token=token
    )

    with pytest.raises(PermissionError) as exc:
        svc.submit_review_action(
            decision_id=dec_id,
            reviewer_id="FIELD_OP_01",
            role=ROLE_FIELD_OPERATOR,
            action=ACTION_ROLLBACK,
            justification="Field op trying to rollback"
        )
    assert "cannot execute ROLLBACK" in str(exc.value)

def test_rollback_generates_audit_trail_entry(tmp_path, monkeypatch):
    db_path = str(tmp_path / "rollback_audit.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.04, "rain_24h_mm": 160.0, "event_probability": 0.81}
    )
    dec_id = dec["decision_id"]

    token = svc.token_manager.issue_token("SEC_DISASTER_01", ROLE_STATE_AUTHORITY, dec_id)
    svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="SEC_DISASTER_01",
        role=ROLE_STATE_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Approved by State",
        authorization_token=token
    )

    svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="SEC_DISASTER_01",
        role=ROLE_STATE_AUTHORITY,
        action=ACTION_ROLLBACK,
        justification="State Commissioner withdrawal after weather clearance"
    )

    audit_chain = svc.get_audit_chain(decision_id=dec_id)
    actions = [entry["action"] for entry in audit_chain]
    assert ACTION_APPROVE in actions
    assert ACTION_ROLLBACK in actions

    # Verify audit chain integrity
    valid, err = svc.verify_audit_chain()
    assert valid is True
    assert err is None
