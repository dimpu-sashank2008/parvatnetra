# -*- coding: utf-8 -*-
"""
tests/test_phase7_e2e_drill.py
==============================
Full End-to-End Operational Lifecycle Drill for Checkpoint 11.
Lifecycle Tested:
  NORMAL
  -> RAINFALL INCREASE
  -> PHYSICAL/EO/SEISMIC EVIDENCE
  -> PAHAD INFERENCE
  -> 2-OF-3 CORROBORATION
  -> AUTHORITY REVIEW PACKAGE
  -> TWO-STAGE SIGN-OFF (Field -> District Authority)
  -> CAP PREPARATION
  -> EMERGENCY ROLLBACK
  -> RECOVERY TO MONITORING
"""

import os
import sys
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from engine.operational_state_machine import OperationalStateMachine
from engine.pahad_decision_store import DecisionRecordStore
from services.authority_review_service import (
    AuthorityReviewService,
    ROLE_FIELD_OPERATOR,
    ROLE_DISTRICT_AUTHORITY,
    ACTION_REQUEST_FIELD_VERIFICATION,
    ACTION_APPROVE,
    ACTION_REJECT
)


def test_full_end_to_end_operational_lifecycle(tmp_path, monkeypatch):
    # 1. Setup isolated stores
    db_file = str(tmp_path / "e2e_drill.db")
    sm = OperationalStateMachine(db_path=db_file)
    dec_store = DecisionRecordStore(db_path=db_file)
    monkeypatch.setattr("services.authority_review_service.PAHAD_DECISION_STORE", dec_store)
    auth_srv = AuthorityReviewService(db_path=db_file, state_machine=sm)
    sector_id = "SK-NH10-KM48"

    # Step 1: NORMAL
    assert sm.get_state(sector_id) == "MONITORING"

    # Step 2 & 3: RAINFALL INCREASE & GEOTECHNICAL TELEMETRY
    # Simulated extreme monsoon conditions + pore pressure rise + low FoS
    telemetry = {
        "fos": 0.88,
        "event_probability": 0.92,
        "rain_24h_mm": 210.0,
        "pore_pressure_kpa": 65.0,
        "tilt_deg": 3.2,
        "seismic_score": 0.4
    }

    # Step 4: PAHAD INFERENCE & Step 5: CORROBORATION
    dec = dec_store.evaluate_and_record(sector_id=sector_id, observations=telemetry)
    assert dec["risk"] == "CRITICAL"
    assert dec["signals"]["is_corroborated"] is True  # 2-of-3 confirmed
    assert dec["recommended_action"] in {"READY_FOR_AUTHORITY_REVIEW", "RED_ALERT_CORRIDOR_CLOSURE"}

    # Invariant: State machine does NOT automatically jump to PUBLIC_DISPATCH
    assert sm.get_state(sector_id) != "PUBLIC_DISPATCH"

    # Step 6: AUTHORITY REVIEW PACKAGE CREATED
    pkg = auth_srv.create_review_package(decision_id=dec["decision_id"], corridor_id="CORR-NH10-SIKKIM-KM48")
    assert pkg["decision_id"] == dec["decision_id"]
    assert pkg["risk_assessment"]["risk_level"] == "CRITICAL"
    assert pkg["corroboration_confirmed"] is True
    assert "NH-717A" in pkg["route_consequences"]

    # Step 7: STAGE 1 VERIFICATION (Field Operator)
    res_stage1 = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="BRO_QRT_OFFICER",
        role=ROLE_FIELD_OPERATOR,
        action=ACTION_REQUEST_FIELD_VERIFICATION,
        justification="Verified 40mm tension crack at KM48 road shoulder. Deployed warning cones."
    )
    assert res_stage1["action"] == ACTION_REQUEST_FIELD_VERIFICATION
    assert res_stage1["new_operational_state"] == "FIELD_RESPONSE"
    assert sm.get_state(sector_id) == "FIELD_RESPONSE"

    # Step 8: STAGE 2 AUTHORIZATION (District Magistrate)
    res_stage2 = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_APPROVE,
        justification="Imminent slope collapse confirmed by BRO ground inspection. NH-10 closed at KM48.",
        authorization_token="ORDER-DM-PAKYONG-2026-KM48"
    )
    assert res_stage2["action"] == ACTION_APPROVE
    assert res_stage2["new_operational_state"] == "WARNING_AUTHORIZED"
    assert sm.get_state(sector_id) == "WARNING_AUTHORIZED"

    # Step 9: CAP PREPARATION
    from engine.pahad_cap import CAPAlertGenerator
    cap_gen = CAPAlertGenerator()
    cap_payload = {
        "identifier": f"CAP-{dec['decision_id']}",
        "sender": "DM_PAKYONG_EOC",
        "sent": "2026-09-10T22:30:00+05:30",
        "status": "Actual",
        "msgType": "Alert",
        "scope": "Public",
        "headline": "CRITICAL LANDSLIDE WARNING: NH-10 KM48 CLOSED",
        "description": "Severe hillslope movement detected. Traffic diverted to NH-717A.",
        "instruction": "Do not enter Pakyong-Rangpo sector. Use designated bypass routes.",
        "severity": "Extreme",
        "urgency": "Immediate",
        "certainty": "Observed",
        "areaDesc": "NH-10 Km 48 Pakyong District Sikkim",
        "polygon": "27.33,88.61 27.34,88.62 27.32,88.63 27.33,88.61"
    }
    cap_xml = cap_gen.build_cap_xml(cap_payload)
    assert "<alert" in cap_xml
    assert "CRITICAL LANDSLIDE WARNING" in cap_xml

    # Step 10: EMERGENCY ROLLBACK / CANCELLATION (Post-incident resolution or false trigger debrief)
    res_rollback = auth_srv.submit_review_action(
        decision_id=dec["decision_id"],
        reviewer_id="DM_PAKYONG",
        role=ROLE_DISTRICT_AUTHORITY,
        action=ACTION_REJECT,
        justification="Debris cleared by BRO Project Swastik; geotechnical inclinometer stabilizes. Reopening corridor."
    )
    assert res_rollback["action"] == ACTION_REJECT
    assert res_rollback["new_operational_state"] == "CANCELLED"
    assert sm.get_state(sector_id) == "CANCELLED"

    # Step 11: RECOVERY TO MONITORING
    sm.transition(sector_id, "MONITORING", "SYSTEM", "Cycle reset for continuous surveillance")
    assert sm.get_state(sector_id) == "MONITORING"
