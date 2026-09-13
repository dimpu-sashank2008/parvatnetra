# -*- coding: utf-8 -*-
"""
tests/test_phase8_mobile_push.py
================================
Tests for Checkpoint 8-09:
Flutter Mobile Notification Payload Contract and Multi-Type Alert Support.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_AUTHORIZED
from services.eoc_service import EOC_SERVICE


def test_mobile_push_contract_fields():
    """Verify Flutter mobile push payload adheres to 7 required contract fields."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=86.0,
        risk_band="CRITICAL",
        model_probability=0.88,
        FoS=0.93,
        rainfall=175.0,
        recommended_action="EVACUATE",
        provenance="[SIMULATED]"
    )
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_AUTHORIZED, "DISTRICT_AUTHORITY", "DM_01", force=True)

    disp = EOC_SERVICE.dispatch_incident_notifications(
        incident_id=inc.incident_id,
        authorization_token="AUTH_TOKEN_TEST",
        channels=["MOBILE"],
        test_mode=True
    )
    mobile_res = disp["channels"]["MOBILE"]
    payload = mobile_res["payload_contract"]

    # Checkpoint 8-09 required fields: incident, severity, location, time, action, language, provenance
    assert "incident_id" in payload
    assert "severity" in payload
    assert "location" in payload
    assert "time" in payload
    assert "action" in payload
    assert "language" in payload
    assert "provenance" in payload

    assert payload["severity"] == "CRITICAL"
    assert payload["action"] == "EVACUATE"
    assert payload["provenance"] == "[SIMULATED]"


def test_mobile_alert_types_supported():
    """Verify supported mobile alert types (warning, watch, road closure, evacuation, all-clear, ack)."""
    supported_actions = [
        "EMERGENCY_WARNING",
        "WATCH",
        "ROAD_CLOSURE",
        "EVACUATION_ADVISORY",
        "ALL_CLEAR",
        "ACKNOWLEDGEMENT"
    ]
    for action in supported_actions:
        inc = EOC_INCIDENT_MANAGER.create_incident(
            sector_id="SK-NH10-KM48",
            risk_score=65.0,
            risk_band="HIGH",
            model_probability=0.70,
            FoS=1.05,
            rainfall=150.0,
            recommended_action=action
        )
        assert inc.recommended_action == action
