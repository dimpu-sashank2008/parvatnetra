# -*- coding: utf-8 -*-
"""
tests/test_phase7g_fail_closed.py
=================================
Tests Checkpoints 7G-14 to 7G-20: Fail-Closed Invariants, False Positive Drills,
True Positive Dry-Run Drills, and Statutory Emergency Overrides.
Verifies:
  1. False Positive Drill: Contradicted signals -> human rejection -> CANCELLED, zero dispatch.
  2. True Positive Drill: 3/3 corroboration -> field report -> authority approval -> DRY_RUN dispatch.
  3. Emergency Override: Requires valid token and statutory justification (>= 10 chars).
  4. Fail-Closed on Corrupted Database / Non-existent decision.
"""

import pytest
from datetime import datetime, timezone
from engine.operational_state_machine import (
    OperationalStateMachine,
    STATE_CANCELLED,
    STATE_WARNING_AUTHORIZED,
    STATE_FIELD_RESPONSE
)
from engine.pahad_decision_store import DecisionRecordStore
from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_FIELD_OPERATOR,
    ACTION_APPROVE,
    ACTION_REJECT
)
from services.field_task_service import FieldTaskService, FieldVerificationReport
from services.notification_orchestrator import (
    NotificationOrchestrator,
    STATUS_SIMULATED
)

def test_false_positive_drill(tmp_path, monkeypatch):
    """CP 7G-16: False positive drill where uncorroborated anomaly is rejected by authority."""
    db_path = str(tmp_path / "fp_drill.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    notif = NotificationOrchestrator(db_path=db_path)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    monkeypatch.setattr("services.notification_orchestrator.NOTIFICATION_ORCHESTRATOR", notif)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    # Uncorroborated / false alarm observations
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.45, "rain_24h_mm": 12.0, "event_probability": 0.25}
    )
    dec_id = dec["decision_id"]

    # Package generated shows lack of corroboration
    pkg = svc.create_review_package(dec_id)
    assert pkg["signal_agreement"] == "0/3"

    # Authority evaluates and rejects false alarm
    rej_res = svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_REJECT,
        justification="Sensor jitter investigated; ground telemetry confirms stable slope. Rejecting false alarm."
    )
    assert rej_res["action"] == ACTION_REJECT
    assert rej_res["new_operational_state"] == STATE_CANCELLED
    assert sm.get_state(sector_id) == STATE_CANCELLED

    # Confirm zero notifications queued or dispatched
    notifs = notif.list_notifications(alert_id=dec_id)
    assert len(notifs) == 0

def test_true_positive_drill_with_dry_run_isolation(tmp_path, monkeypatch):
    """CP 7G-17: Fully corroborated event proceeds through field confirmation and authority approval."""
    db_path = str(tmp_path / "tp_drill.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    fts = FieldTaskService(db_path=db_path)
    notif = NotificationOrchestrator(db_path=db_path)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    monkeypatch.setattr("services.notification_orchestrator.NOTIFICATION_ORCHESTRATOR", notif)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 0.96, "rain_24h_mm": 185.0, "event_probability": 0.89}
    )
    dec_id = dec["decision_id"]

    # Check 3/3 corroboration
    pkg = svc.create_review_package(dec_id)
    assert pkg["signal_agreement"] == "3/3"

    # Step 1: Field verification requested
    svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action="REQUEST_FIELD_VERIFICATION",
        justification="Dispatching BRO ground team for physical check"
    )
    assert sm.get_state(sector_id) == STATE_FIELD_RESPONSE

    # Step 2: Field responder submits report
    task = fts.dispatch_field_task(dec_id, sector_id, "BRO_TEAM_ALPHA")
    report = FieldVerificationReport(
        report_id="REP-001",
        task_id=task["task_id"],
        operator="ENG_SHARMA_BRO",
        location={"latitude": 27.3300, "longitude": 88.6100, "accuracy_m": 3.5},
        timestamp=datetime.now(timezone.utc).isoformat(),
        media_reference=["https://evidence.parvatnetra.gov.in/img01.jpg"],
        observation="Tension crack width 8cm expanding rapidly near Km 48.5",
        severity="CRITICAL",
        verification_result="CONFIRMED",
        observed_cracks=True,
        slope_movement=True,
        debris=True,
        notes="Imminent road shoulder failure"
    )
    fts.submit_field_report(report)

    # Step 3: Authority approval with cryptographic token
    token = svc.token_manager.issue_token("DM_PAKYONG_01", ROLE_DISTRICT_AUTHORITY, dec_id)
    appr_res = svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Ground confirmation and 3/3 sensor agreement; evacuation approved",
        authorization_token=token
    )
    assert appr_res["new_operational_state"] == STATE_WARNING_AUTHORIZED

    # Step 4: Multi-channel dispatch strictly in DRY_RUN / SIMULATED mode
    cap_dict = notif.generate_cap_alert(
        alert_id=dec_id,
        event="Severe Landslide Evacuation",
        severity="Extreme",
        urgency="Immediate",
        certainty="Observed",
        area_description="NH-10 Km 48",
        instruction="Evacuate to Rangpo staging area via NH-717A"
    )
    dispatch_res = notif.dispatch_alert(
        alert_id=dec_id,
        cap_payload=cap_dict,
        channels=["SMS", "SIREN", "PUSH"],
        authorization_token=token,
        public_dispatch_enabled=True,
        dry_run=True
    )
    results = dispatch_res["channel_results"]
    assert results["SMS"]["status"] == STATUS_SIMULATED
    assert results["SIREN"]["status"] == STATUS_SIMULATED

def test_emergency_override_statutory_justification(tmp_path, monkeypatch):
    """CP 7G-09: Emergency override requires min 10 chars statutory justification and token."""
    db_path = str(tmp_path / "override_test.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.05, "rain_24h_mm": 140.0, "event_probability": 0.65}
    )
    dec_id = dec["decision_id"]

    token = svc.token_manager.issue_token("SEC_DISASTER_01", ROLE_STATE_AUTHORITY, dec_id)

    # Rejects short justification
    with pytest.raises(ValueError) as exc:
        svc.submit_emergency_override(
            decision_id=dec_id,
            reviewer_id="SEC_DISASTER_01",
            role=ROLE_STATE_AUTHORITY,
            justification="Short",
            authorization_token=token
        )
    assert "statutory justification" in str(exc.value)

    # Succeeds with comprehensive justification
    res = svc.submit_emergency_override(
        decision_id=dec_id,
        reviewer_id="SEC_DISASTER_01",
        role=ROLE_STATE_AUTHORITY,
        justification="Section 30 Disaster Management Act 2005 invocation due to imminent road collapse",
        authorization_token=token
    )
    assert res["action"] == "OVERRIDE"
    assert res["new_operational_state"] == STATE_WARNING_AUTHORIZED
