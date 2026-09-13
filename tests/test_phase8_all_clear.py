# -*- coding: utf-8 -*-
"""
tests/test_phase8_all_clear.py
==============================
Tests for Checkpoint 8-19 & 8-20:
Controlled All-Clear Protocol, Triple-Gate Verification,
and False Alarm / Withdrawal Retraction.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_AUTHORIZED, STATE_RESOLVED, STATE_CANCELLED
from services.eoc_service import EOC_SERVICE


def test_all_clear_triple_gate_success():
    """Verify All-Clear succeeds when physical stabilization, field confirmation, and authority approval are met."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=75.0,
        risk_band="HIGH",
        model_probability=0.78,
        FoS=1.02,
        rainfall=160.0
    )
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_AUTHORIZED, "DISTRICT_AUTHORITY", "DM_01", force=True)

    res = EOC_SERVICE.authorize_all_clear(
        incident_id=inc.incident_id,
        approver_role="DISTRICT_AUTHORITY",
        approver_id="DM_PAKYONG",
        field_clearance_confirmed=True,
        current_fos=1.35,
        current_rain_mm=8.0,
        justification="Rain ceased. BRO slope stabilization complete. Debris removed."
    )

    assert res["status"] == "ALL_CLEAR_AUTHORIZED"
    assert res["incident_status"] == STATE_RESOLVED
    assert res["payload"]["current_fos"] == 1.35


def test_ai_risk_decrease_alone_cannot_issue_all_clear():
    """Verify that an AI risk decrease alone CANNOT issue an All-Clear without field confirmation."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=35.0,
        risk_band="LOW",
        model_probability=0.15,
        FoS=1.45,
        rainfall=5.0
    )
    # Attempt All-Clear without field ground confirmation
    res = EOC_SERVICE.authorize_all_clear(
        incident_id=inc.incident_id,
        approver_role="DISTRICT_AUTHORITY",
        approver_id="DM_PAKYONG",
        field_clearance_confirmed=False,  # NOT CONFIRMED
        current_fos=1.45,
        current_rain_mm=5.0
    )

    assert res["status"] == "REJECTED"
    assert res["authorized"] is False
    assert "Field inspection confirmation is mandatory" in res["error"]


def test_all_clear_rejected_if_slope_physics_unstable():
    """Verify All-Clear is rejected if physical FoS is still below 1.25 or rain exceeds 50mm."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=60.0,
        risk_band="MEDIUM",
        model_probability=0.60,
        FoS=1.10,
        rainfall=65.0
    )
    # FoS 1.10 is too low
    res = EOC_SERVICE.authorize_all_clear(
        incident_id=inc.incident_id,
        approver_role="DISTRICT_AUTHORITY",
        approver_id="DM_PAKYONG",
        field_clearance_confirmed=True,
        current_fos=1.10,
        current_rain_mm=20.0
    )
    assert res["status"] == "REJECTED"
    assert "FoS=" in res["error"]


def test_false_alarm_withdrawal_and_retraction():
    """Verify false alarm withdrawal creates audit trail and generates retraction broadcast."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=75.0,
        risk_band="HIGH",
        model_probability=0.76,
        FoS=1.02,
        rainfall=155.0
    )
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_AUTHORIZED, "DISTRICT_AUTHORITY", "DM_01", force=True)

    withd_res = EOC_SERVICE.initiate_false_alarm_withdrawal(
        incident_id=inc.incident_id,
        approver_role="DISTRICT_AUTHORITY",
        approver_id="DM_PAKYONG",
        contradictory_evidence="BRO on-site inclinometer confirmed zero displacement. Sensor line short resolved."
    )

    assert withd_res["status"] == "WITHDRAWN"
    assert withd_res["incident_status"] == STATE_CANCELLED
    assert "[RETRACTION]" in withd_res["retraction_broadcast"]
