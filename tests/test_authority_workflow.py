# -*- coding: utf-8 -*-
"""
tests/test_authority_workflow.py
================================
Unit tests for human-in-the-loop authority review workflows, role permissions,
and review action handling.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_FIELD_OPERATOR,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_ADMIN,
    ACTION_APPROVE,
    ACTION_REJECT,
    ACTION_REQUEST_FIELD_VERIFICATION,
    ACTION_ESCALATE,
    ACTION_DEFER
)
from engine.pahad_decision_store import DecisionRecordStore


@pytest.fixture
def temp_services(tmp_path):
    db_file = str(tmp_path / "test_auth.db")
    dec_store = DecisionRecordStore(db_path=db_file)
    auth_srv = AuthorityReviewService(db_path=db_file)
    return dec_store, auth_srv


def test_create_review_package(temp_services, monkeypatch):
    dec_store, auth_srv = temp_services
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    # Seed a decision
    dec = dec_store.evaluate_and_record(
        sector_id="SK-NH10-KM48",
        observations={
            "fos": 1.02,
            "event_probability": 0.82,
            "rain_24h_mm": 120.0,
            "pore_pressure_kpa": 55.0
        }
    )

    pkg = auth_srv.create_review_package(decision_id=dec["decision_id"], corridor_id="CORR-NH10-SIKKIM-KM48")
    assert pkg["decision_id"] == dec["decision_id"]
    assert pkg["risk_assessment"]["risk_level"] in ["CRITICAL", "HIGH"]
    assert pkg["corroboration_confirmed"] is True
    assert "NH-717A" in pkg["route_consequences"]


def test_field_operator_cannot_approve(temp_services, monkeypatch):
    dec_store, auth_srv = temp_services
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 1.05, "event_probability": 0.78})

    with pytest.raises(PermissionError) as excinfo:
        auth_srv.submit_review_action(
            decision_id=dec["decision_id"],
            reviewer_id="TECH_LEPCHA",
            role=ROLE_FIELD_OPERATOR,
            action=ACTION_APPROVE,
            justification="Looks bad to me"
        )
    assert "FIELD_OPERATOR cannot APPROVE public warnings" in str(excinfo.value)


def test_district_authority_approves_warning(temp_services, monkeypatch):
    dec_store, auth_srv = temp_services
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 0.98, "event_probability": 0.88, "rain_24h_mm": 110.0})

    res = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Verified BRO geotechnical sensor readings. Approved closure.",
        authorization_token="AUTH-DM-2026"
    )
    assert res["action"] == ACTION_APPROVE
    assert res["role"] == ROLE_DISTRICT_AUTHORITY
    assert res["new_operational_state"] == "WARNING_AUTHORIZED"


def test_authority_rejects_warning(temp_services, monkeypatch):
    dec_store, auth_srv = temp_services
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 1.15, "event_probability": 0.68})

    res = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG_01",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_REJECT,
        justification="False trigger caused by local water pipe rupture."
    )
    assert res["action"] == ACTION_REJECT
    assert res["new_operational_state"] == "CANCELLED"


def test_authority_requests_field_verification(temp_services, monkeypatch):
    dec_store, auth_srv = temp_services
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)

    dec = dec_store.evaluate_and_record("SK-NH10-KM48", {"fos": 1.20, "event_probability": 0.60})

    res = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="OPERATOR_01",
        role=ROLE_FIELD_OPERATOR,
        action=ACTION_REQUEST_FIELD_VERIFICATION,
        justification="Dispatch BRO QRT to inspect toe erosion before declaring closure"
    )
    assert res["action"] == ACTION_REQUEST_FIELD_VERIFICATION
    assert res["new_operational_state"] == "FIELD_RESPONSE"
