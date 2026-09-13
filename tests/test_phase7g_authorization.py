# -*- coding: utf-8 -*-
"""
tests/test_phase7g_authorization.py
===================================
PHASE 7G — Checkpoint 7G-03 & 7G-04: Authority Review Contract & Approval Validation
Verifies:
  1. Complete 18-field Authority Review Contract.
  2. Missing decision metadata blocks authorization.
  3. Valid authority approval with cryptographic token succeeds.
  4. Invalid authority role is rejected.
  5. Missing authorization token is rejected.
  6. Malformed authorization token is rejected.
  7. Expired authorization token is rejected.
  8. Replayed / duplicate authorization token is rejected.
  9. Already RESOLVED alert cannot be approved.
 10. Already CANCELLED alert cannot be approved.
"""

import os
import sys
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_FIELD_OPERATOR,
    ROLE_ADMIN,
    ACTION_APPROVE,
    ACTION_REJECT
)
from engine.pahad_decision_store import DecisionRecordStore
from engine.operational_state_machine import (
    OperationalStateMachine,
    STATE_WARNING_AUTHORIZED,
    STATE_RESOLVED,
    STATE_CANCELLED
)


@pytest.fixture
def auth_env(tmp_path):
    db_file = str(tmp_path / "auth_val_test.db")
    sm = OperationalStateMachine(db_path=db_file)
    dec_store = DecisionRecordStore(db_path=db_file)
    auth_srv = AuthorityReviewService(db_path=db_file, state_machine=sm)
    return dec_store, auth_srv, sm


def test_18_field_authority_review_contract(auth_env, monkeypatch):
    """CP 7G-03: Authority review payload contains all 18 mandatory contract fields."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record(
        sector_id="SK-NH10-KM48",
        observations={"fos": 1.02, "event_probability": 0.82, "rain_24h_mm": 160.0}
    )

    pkg = auth_srv.create_review_package(decision_id=dec["decision_id"])

    required_fields = [
        "alert_id", "sector_id", "created_at", "severity", "risk_score",
        "model_probability", "FoS", "rainfall", "signal_agreement",
        "evidence_summary", "field_verification_status", "recommended_action",
        "reviewer_id", "reviewer_role", "decision", "decision_timestamp",
        "authorization_reference", "audit_hash"
    ]

    for field in required_fields:
        assert field in pkg, f"Missing required contract field '{field}' in authority review package"


def test_missing_decision_metadata_blocks_authorization(auth_env, monkeypatch):
    """CP 7G-03: Attempting authorization with incomplete decision metadata must fail."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})
    # Corrupt the record to simulate missing critical metadata
    conn = dec_store._get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE pahad_decisions SET fos = NULL, probability = NULL WHERE decision_id = ?", (dec["decision_id"],))
    conn.commit()
    conn.close()

    token = auth_srv.token_manager.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, dec["decision_id"])

    with pytest.raises(ValueError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="DM_PAKYONG",
            role=ROLE_DISTRICT_AUTHORITY,
            action=ACTION_APPROVE,
            justification="Approving incomplete record",
            authorization_token=token
        )
    assert "missing required geotechnical/risk metadata" in str(exc.value)


def test_valid_authority_approval(auth_env, monkeypatch):
    """CP 7G-04: Valid district authority with valid signed token succeeds."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.98, "event_probability": 0.85})
    token = auth_srv.token_manager.issue_token("DM_PAKYONG_01", ROLE_DISTRICT_AUTHORITY, dec["decision_id"])

    res = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Verified BRO geotechnical sensor readings. Approved closure.",
        authorization_token=token
    )
    assert res["action"] == ACTION_APPROVE
    assert res["new_operational_state"] == STATE_WARNING_AUTHORIZED
    assert res["authorization_reference"] == token
    assert res["audit_hash"] is not None


def test_invalid_authority_role_rejected(auth_env, monkeypatch):
    """CP 7G-04: Wrong role attempting approval is rejected with PermissionError."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})

    with pytest.raises(PermissionError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="TECH_01",
            role=ROLE_FIELD_OPERATOR,
            action=ACTION_APPROVE,
            justification="Field operator attempt"
        )
    assert "FIELD_OPERATOR cannot APPROVE" in str(exc.value)


def test_missing_token_rejected(auth_env, monkeypatch):
    """CP 7G-04: Missing authorization token on approval is rejected."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})

    with pytest.raises(ValueError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="DM_PAKYONG",
            role=ROLE_DISTRICT_AUTHORITY,
            action=ACTION_APPROVE,
            justification="Approve without token",
            authorization_token=None
        )
    assert "Missing authorization token" in str(exc.value)


def test_malformed_token_rejected(auth_env, monkeypatch):
    """CP 7G-04: Malformed authorization token is rejected."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})

    with pytest.raises(ValueError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="DM_PAKYONG",
            role=ROLE_DISTRICT_AUTHORITY,
            action=ACTION_APPROVE,
            justification="Approve with garbage",
            authorization_token="AUTH-v1.garbage_format"
        )
    assert "Malformed authorization token" in str(exc.value)


def test_expired_authorization_rejected(auth_env, monkeypatch):
    """CP 7G-04: Expired authorization token is strictly rejected."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})
    # Issue already expired token (ttl=-60)
    expired_token = auth_srv.token_manager.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, dec["decision_id"], ttl_seconds=-60)

    with pytest.raises(ValueError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="DM_PAKYONG",
            role=ROLE_DISTRICT_AUTHORITY,
            action=ACTION_APPROVE,
            justification="Approve with expired token",
            authorization_token=expired_token
        )
    assert "Expired authorization token" in str(exc.value)


def test_replayed_token_rejected(auth_env, monkeypatch):
    """CP 7G-04: Replayed / duplicate token use is strictly rejected."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})
    token = auth_srv.token_manager.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, dec["decision_id"])

    # First use: succeeds
    auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Legitimate first approval",
        authorization_token=token
    )

    # Second use (replay attempt): must fail
    with pytest.raises(ValueError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="DM_PAKYONG",
            role=ROLE_DISTRICT_AUTHORITY,
            action=ACTION_APPROVE,
            justification="Replay attack attempt",
            authorization_token=token
        )
    assert "replay detected" in str(exc.value).lower()


def test_already_resolved_alert_approval_rejected(auth_env, monkeypatch):
    """CP 7G-04: Cannot approve an alert that is already RESOLVED."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})
    token = auth_srv.token_manager.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, dec["decision_id"])

    # Force entity state to RESOLVED in state machine
    sm._current_states["SK-NH10-KM48"] = STATE_RESOLVED

    with pytest.raises(ValueError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="DM_PAKYONG",
            role=ROLE_DISTRICT_AUTHORITY,
            action=ACTION_APPROVE,
            justification="Attempt approval on resolved incident",
            authorization_token=token
        )
    assert "terminal state 'RESOLVED'" in str(exc.value)


def test_already_cancelled_alert_approval_rejected(auth_env, monkeypatch):
    """CP 7G-04: Cannot approve an alert that is already CANCELLED."""
    dec_store, auth_srv, sm = auth_env
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.95, "event_probability": 0.85})
    token = auth_srv.token_manager.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, dec["decision_id"])

    # Force entity state to CANCELLED in state machine
    sm._current_states["SK-NH10-KM48"] = STATE_CANCELLED

    with pytest.raises(ValueError) as exc:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="DM_PAKYONG",
            role=ROLE_DISTRICT_AUTHORITY,
            action=ACTION_APPROVE,
            justification="Attempt approval on cancelled incident",
            authorization_token=token
        )
    assert "terminal state 'CANCELLED'" in str(exc.value)
