# -*- coding: utf-8 -*-
"""
tests/test_phase10j_failure.py
==============================
PARVAT NETRA • Phase 10J — Failure Isolation & Independent Channel Tests
------------------------------------------------------------------------
Verifies CP09, CP10, CP11:
  1. CP09: Email fails, SMS succeeds -> EMAIL = FAILED, SMS = SENT.
  2. CP10: SMS fails, Email succeeds -> SMS = FAILED / BLOCKED, EMAIL = SENT.
  3. CP11: Complete failure: both fail -> EMAIL = FAILED, SMS = FAILED.
     Shows: NOTIFICATION DELIVERY FAILED with exact reason. Never silently marks success.
"""

import pytest
from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE


def test_cp09_email_failure_sms_success():
    """CP09: When Email fails (e.g. invalid syntax) and SMS succeeds, SMS proceeds independently."""
    res = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="invalid-email-syntax@",  # Deliberate invalid email
        phone_number="+919832011234",          # Valid phone number
        scenario_id="ML-SONAPUR-01",
        is_test=True
    )

    assert "EMAIL" in res["channels"]
    assert "SMS" in res["channels"]

    # Email must be marked FAILED
    eml = res["channels"]["EMAIL"]
    assert eml["success"] is False
    assert eml["status"] == "FAILED"
    assert "Invalid email" in eml["error"]

    # SMS must be marked successful independently
    sms = res["channels"]["SMS"]
    assert sms["success"] is True
    assert sms["status"] in ("SENT", "SIMULATED")

    # Status summary reflects independent channels
    assert "EMAIL=FAILED" in res["status_summary"]
    assert "SMS=" in res["status_summary"]


def test_cp10_sms_failure_email_success():
    """CP10: When SMS fails (e.g. invalid number) and Email succeeds, Email proceeds independently."""
    res = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="judge@example.gov.in",  # Valid email
        phone_number="123",                   # Deliberate invalid short phone
        scenario_id="SK-NH10-KM48",
        is_test=True
    )

    assert "EMAIL" in res["channels"]
    assert "SMS" in res["channels"]

    # SMS must be marked FAILED
    sms = res["channels"]["SMS"]
    assert sms["success"] is False
    assert sms["status"] == "FAILED"
    assert "Invalid phone" in sms["error"]

    # Email must be marked successful independently
    eml = res["channels"]["EMAIL"]
    assert eml["success"] is True
    assert eml["status"] in ("SENT", "SIMULATED")

    # Status summary reflects independent channels
    assert "SMS=FAILED" in res["status_summary"]
    assert "EMAIL=" in res["status_summary"]


def test_cp11_complete_failure_both_channels():
    """CP11: When both channels fail, overall status is NOTIFICATION DELIVERY FAILED with reasons."""
    res = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="bad-email-format",  # Invalid email
        phone_number="999",               # Invalid phone
        scenario_id="MZ-HUNTHAR-01",
        is_test=True
    )

    assert res["success"] is False
    assert res["status_summary"] == "NOTIFICATION DELIVERY FAILED"
    assert "NOTIFICATION DELIVERY FAILED" in res["message"]
    assert res["channels"]["EMAIL"]["success"] is False
    assert res["channels"]["SMS"]["success"] is False
    assert res["channels"]["EMAIL"]["status"] == "FAILED"
    assert res["channels"]["SMS"]["status"] == "FAILED"


def test_empty_recipients_rejected():
    """Verifies that submitting with zero recipients fails immediately with helpful error."""
    res = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="",
        phone_number="",
        scenario_id="ML-SONAPUR-01",
        is_test=True
    )

    assert res["success"] is False
    assert "Recipient input required" in res["error"]
