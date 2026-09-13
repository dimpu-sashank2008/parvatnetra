# -*- coding: utf-8 -*-
"""
tests/test_operational_audit.py
===============================
Unit tests for append-only operational audit logging, transition history,
authority review tracking, and tamper-proof decision records.
"""

import sys
import os
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.operational_state_machine import (
    OperationalStateMachine,
    STATE_MONITORING,
    STATE_ANOMALY_DETECTED,
    STATE_PAHAD_EVALUATING,
    STATE_CORROBORATION_PENDING,
    STATE_AUTHORITY_REVIEW,
    STATE_WARNING_AUTHORIZED,
    STATE_PUBLIC_DISPATCH,
    STATE_FIELD_RESPONSE,
    STATE_ACKNOWLEDGED,
    STATE_RESOLVED,
    STATE_CLOSED
)
from engine.pahad_decision_store import DecisionRecordStore
from services.authority_review_service import AuthorityReviewService, ROLE_DISTRICT_AUTHORITY, ACTION_APPROVE
from services.notification_orchestrator import NotificationOrchestrator


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_operational_audit.db")


def test_state_machine_append_only_transitions(temp_db):
    sm = OperationalStateMachine(db_path=temp_db)
    entity_id = "CORRIDOR-NH10-KM48"

    # Step through multiple operational states
    sm.transition(entity_id, STATE_ANOMALY_DETECTED, "TELEMETRY_PIPELINE", "Piezometer pore pressure spike > 65 kPa")
    sm.transition(entity_id, STATE_PAHAD_EVALUATING, "PAHAD_INFERENCE_ENGINE", "Initiating multimodal geotechnical evaluation")
    sm.transition(entity_id, STATE_CORROBORATION_PENDING, "CORROBORATION_AGENT", "Corroborating piezometric and rain signals")
    sm.transition(entity_id, STATE_AUTHORITY_REVIEW, "AI_SUPERVISOR", "Corroboration threshold satisfied")

    history = sm.get_history(entity_id)
    assert len(history) == 4

    # Verify chronological sequence and metadata
    assert history[0]["previous_state"] == STATE_MONITORING
    assert history[0]["new_state"] == STATE_ANOMALY_DETECTED
    assert history[0]["actor"] == "TELEMETRY_PIPELINE"
    assert "Piezometer pore pressure spike" in history[0]["reason"]

    assert history[1]["previous_state"] == STATE_ANOMALY_DETECTED
    assert history[1]["new_state"] == STATE_PAHAD_EVALUATING

    assert history[2]["previous_state"] == STATE_PAHAD_EVALUATING
    assert history[2]["new_state"] == STATE_CORROBORATION_PENDING

    assert history[3]["previous_state"] == STATE_CORROBORATION_PENDING
    assert history[3]["new_state"] == STATE_AUTHORITY_REVIEW
    assert history[3]["actor"] == "AI_SUPERVISOR"

    # Verify current state matches final transition
    assert sm.get_state(entity_id) == STATE_AUTHORITY_REVIEW


def test_authority_review_audit_log(temp_db, monkeypatch):
    sm = OperationalStateMachine(db_path=temp_db)
    dec_store = DecisionRecordStore(db_path=temp_db)
    ars = AuthorityReviewService(db_path=temp_db, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    # Seed decision record
    dec = dec_store.evaluate_and_record(
        sector_id="SK-NH10-KM48",
        observations={"fos": 1.02, "event_probability": 0.82, "rain_24h_mm": 120.0, "pore_pressure_kpa": 55.0}
    )
    decision_id = dec["decision_id"]

    # Submit an authority approval
    review = ars.submit_review_action(
        decision_id=decision_id,
        reviewer_id="DM-EAST-SIKKIM-01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Corridor landslide risk corroborated by IMD nowcast and site piezometer"
    )

    assert review["decision_id"] == decision_id
    assert review["role"] == ROLE_DISTRICT_AUTHORITY
    assert review["action"] == ACTION_APPROVE
    assert review["reviewer_id"] == "DM-EAST-SIKKIM-01"
    assert review["new_operational_state"] == STATE_WARNING_AUTHORIZED

    # Fetch audit history
    history = ars.list_reviews(decision_id=decision_id)
    assert len(history) == 1
    rec = history[0]
    assert rec["review_id"] == review["review_id"]
    assert rec["justification"] == "Corridor landslide risk corroborated by IMD nowcast and site piezometer"
    assert rec["timestamp"] is not None


def test_decision_store_immutable_audit(temp_db):
    store = DecisionRecordStore(db_path=temp_db)
    sector_id = "SK-NH10-KM48"

    observations = {
        "fos": 1.02,
        "event_probability": 0.82,
        "rain_24h_mm": 160.0,
        "pore_pressure_kpa": 72.0,
        "tilt_deg": 4.2,
        "provenance": "LIVE",
        "freshness_status": "FRESH"
    }

    res = store.evaluate_and_record(
        sector_id=sector_id,
        observations=observations,
        model_version="v3.1.0-gbdt",
        dataset_version="v3.1-real-ner"
    )

    decision_id = res["decision_id"]
    fetched = store.get_decision(decision_id)
    assert fetched is not None
    assert fetched["decision_id"] == decision_id
    assert fetched["sector_id"] == sector_id
    assert fetched["risk"] == "CRITICAL"
    assert fetched["fos"] == 1.02
    assert fetched["probability"] == 0.82
    assert fetched["confidence"] == 0.90
    assert fetched["model_version"] == "v3.1.0-gbdt"
    assert fetched["dataset_version"] == "v3.1-real-ner"
    assert fetched["input_provenance"] == "LIVE"
    assert fetched["freshness"] == "FRESH"
    assert fetched["safety_gate_result"] == "PASSED_CORROBORATED"
    assert fetched["is_ood"] == 0


def test_notification_delivery_and_acknowledgement_audit(temp_db):
    notif = NotificationOrchestrator(db_path=temp_db)

    cap_payload = notif.generate_cap_alert(
        alert_id="ALERT-AUDIT-01",
        event="Rapid Creep Anomaly",
        severity="Severe",
        urgency="Immediate",
        certainty="Observed",
        area_description="NH-10 Km 48 Gangtok corridor",
        instruction="Evacuate downslope settlement"
    )

    dispatched = notif.dispatch_alert(
        alert_id="ALERT-AUDIT-01",
        cap_payload=cap_payload,
        channels=["MOBILE", "WEB"]
    )

    mobile_nid = dispatched["channel_results"]["MOBILE"]["notification_id"]
    notif.record_acknowledgement(mobile_nid, acknowledged_by="DUTY_OFFICER_QRT")

    records = notif.list_notifications(alert_id="ALERT-AUDIT-01")
    assert len(records) == 2

    mobile_rec = next(r for r in records if r["notification_id"] == mobile_nid)
    assert mobile_rec["status"] == "DELIVERED"
    assert mobile_rec["acknowledged_by"] == "DUTY_OFFICER_QRT"
    assert mobile_rec["acknowledged_at"] is not None
