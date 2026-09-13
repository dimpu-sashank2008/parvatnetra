# -*- coding: utf-8 -*-
"""
tests/test_phase7g_audit.py
===========================
Tests Checkpoint 7G-13: Cryptographically Chained Audit Log & Tamper-Detection.
Verifies:
  1. Immutable SHA-256 hash chaining across consecutive review events.
  2. Genesis hash initialization (64 zeros).
  3. Strict payload verification across entries.
  4. Detection of manual database modification/tampering.
"""

import sqlite3
import pytest
from engine.operational_state_machine import OperationalStateMachine
from engine.pahad_decision_store import DecisionRecordStore
from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ACTION_APPROVE,
    ACTION_REJECT,
    ACTION_ROLLBACK,
    ACTION_REQUEST_FIELD_VERIFICATION
)

def test_audit_chain_sequential_linking(tmp_path, monkeypatch):
    db_path = str(tmp_path / "audit_chain.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec1 = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.05, "rain_24h_mm": 155.0, "event_probability": 0.78}
    )
    dec1_id = dec1["decision_id"]

    # Action 1: Field verification request
    svc.submit_review_action(
        decision_id=dec1_id,
        reviewer_id="DIST_OFFICER_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_REQUEST_FIELD_VERIFICATION,
        justification="Ground verification requested at Km 48"
    )

    # Action 2: Approve after verification
    token = svc.token_manager.issue_token("DIST_OFFICER_01", ROLE_DISTRICT_AUTHORITY, dec1_id)
    svc.submit_review_action(
        decision_id=dec1_id,
        reviewer_id="DIST_OFFICER_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Verified by BRO team, approving evacuation",
        authorization_token=token
    )

    # Action 3: Rollback
    svc.submit_review_action(
        decision_id=dec1_id,
        reviewer_id="DIST_OFFICER_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_ROLLBACK,
        justification="Hazard mitigated"
    )

    entries = svc.get_audit_chain()
    assert len(entries) >= 3

    # Check genesis hash
    assert entries[0]["prev_hash"] == "0" * 64

    # Check hash links
    for i in range(1, len(entries)):
        assert entries[i]["prev_hash"] == entries[i - 1]["entry_hash"]

    # Verify whole chain
    valid, err = svc.verify_audit_chain()
    assert valid is True
    assert err is None

def test_tamper_detection_in_audit_chain(tmp_path, monkeypatch):
    db_path = str(tmp_path / "tamper_test.db")
    sm = OperationalStateMachine(db_path=db_path)
    dec_store = DecisionRecordStore(db_path=db_path)
    svc = AuthorityReviewService(db_path=db_path, state_machine=sm)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    sector_id = "CORR-NH10-SIKKIM-KM48"
    dec = dec_store.evaluate_and_record(
        sector_id=sector_id,
        observations={"fos": 1.02, "rain_24h_mm": 170.0, "event_probability": 0.85}
    )
    dec_id = dec["decision_id"]

    token = svc.token_manager.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, dec_id)
    svc.submit_review_action(
        decision_id=dec_id,
        reviewer_id="DM_PAKYONG",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Approved legitimate hazard",
        authorization_token=token
    )

    # Verify chain is valid initially
    valid, err = svc.verify_audit_chain()
    assert valid is True

    # Tamper with database row directly
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE authority_audit_chain SET reason = 'TAMPERED REASON' WHERE decision_id = ?", (dec_id,))
    conn.commit()
    conn.close()

    # Verify tamper detection detects corrupt entry
    valid, err = svc.verify_audit_chain()
    assert valid is False
    assert "Tampering detected" in err
