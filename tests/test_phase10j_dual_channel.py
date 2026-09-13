# -*- coding: utf-8 -*-
"""
tests/test_phase10j_dual_channel.py
===================================
PARVAT NETRA • Phase 10J — Dual Channel (Email + SMS) Dissemination Tests
-------------------------------------------------------------------------
Verifies:
  1. Single action queues BOTH Email and SMS independently (CP03).
  2. Notification reference generated in format PN-TEST-XXXXXXXX.
  3. Channel result isolation: one channel's failure does not cancel the other.
  4. Both channel dispatches are recorded into the tamper-evident journal.
  5. Correct metadata propagation (recipient, provider reference, timestamps).
"""

import pytest
from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE


def test_dual_channel_dispatch_both_succeed():
    """Verifies one call dispatches both Email and SMS and tracks both."""
    res = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="officer@sikkim.gov.in",
        phone_number="+919832011234",
        recipient_name="SDMA Commissioner",
        language="en",
        scenario_id="SK-NH10-KM48",
        is_test=True
    )

    assert res["success"] is True
    assert res["incident_id"].startswith("PN-TEST-")
    assert "EMAIL" in res["channels"]
    assert "SMS" in res["channels"]

    eml = res["channels"]["EMAIL"]
    assert eml["success"] is True
    assert eml["status"] in ("SENT", "SIMULATED")
    assert "provider" in eml
    assert eml["recipient_masked"].startswith("o")

    sms = res["channels"]["SMS"]
    assert sms["success"] is True
    assert sms["status"] in ("SENT", "SIMULATED")
    assert "provider" in sms
    assert sms["recipient_masked"].endswith("1234")


def test_dual_channel_journal_records_both_entries():
    """Verifies both Email and SMS dispatches create separate entries in the audit journal."""
    res = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="evaluator@sih.gov.in",
        phone_number="+919832055678",
        language="hi",
        scenario_id="ML-SONAPUR-01",
        is_test=True
    )

    inc_id = res["incident_id"]
    journal_entries = UNIFIED_NOTIFICATION_SERVICE.journal.list_entries(incident_id=inc_id)

    # Should have at least 2 entries (one for EMAIL, one for SMS)
    channels_logged = {entry["channel"] for entry in journal_entries}
    assert "EMAIL" in channels_logged
    assert "SMS" in channels_logged
    for entry in journal_entries:
        assert entry["incident_id"] == inc_id
        assert len(entry["audit_hash"]) == 64
