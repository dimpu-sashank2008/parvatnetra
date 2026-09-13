# -*- coding: utf-8 -*-
"""
tests/test_phase8_sms.py
========================
Tests for Checkpoint 8-10:
SMS Provider Abstraction, Allowed States, [SIMULATED SMS] Tagging,
and Zero Fake Delivery Claims.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_AUTHORIZED
from services.eoc_service import (
    EOC_SERVICE,
    SMS_STATE_CONFIGURED,
    SMS_STATE_UNCONFIGURED,
    SMS_STATE_SIMULATED,
    SMS_STATE_FAILED,
    SMS_STATE_BLOCKED,
)
from services.sms_service import SMS_SERVICE, SMS_TEMPLATES


def test_sms_provider_allowed_states():
    """Verify provider abstraction enforces the 5 defined operational states."""
    valid_states = {
        SMS_STATE_CONFIGURED,
        SMS_STATE_UNCONFIGURED,
        SMS_STATE_SIMULATED,
        SMS_STATE_FAILED,
        SMS_STATE_BLOCKED,
    }
    assert EOC_SERVICE._sms_provider_state in valid_states


def test_simulated_sms_badge_and_no_fake_delivered():
    """Verify test-mode SMS strictly displays [SIMULATED SMS] and never DELIVERED."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="CRITICAL",
        model_probability=0.88,
        FoS=0.95,
        rainfall=180.0
    )
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_AUTHORIZED, "DISTRICT_AUTHORITY", "DM_01", force=True)

    disp = EOC_SERVICE.dispatch_incident_notifications(
        incident_id=inc.incident_id,
        authorization_token="AUTH_TOKEN_TEST",
        channels=["SMS"],
        test_mode=True
    )
    sms_res = disp["channels"]["SMS"]

    assert sms_res["status"] == "SIMULATED"
    assert sms_res["status"] != "DELIVERED"
    assert sms_res["badge"] == "[SIMULATED SMS]"
    assert "[SIMULATED SMS]" in sms_res["template_sample"]


def test_sms_multilingual_length():
    """Verify SMS templates across Himalayan languages stay within 160-char SMS limit."""
    languages = ["en", "hi", "ne", "bh", "lp", "as"]
    for lang in languages:
        msg = SMS_SERVICE.format_sms_message(
            alert_id="PN-ALERT-TEST-001",
            level_name="CRITICAL",
            language=lang
        )
        assert len(msg) <= 160, f"Rendered SMS for {lang} exceeded 160 chars ({len(msg)} chars)"

