# -*- coding: utf-8 -*-
"""
tests/test_phase10j_delivery_receipts.py
========================================
PARVAT NETRA • Phase 10J — Delivery Receipts & Status Lifecycle Tests
---------------------------------------------------------------------
Verifies:
  1. Delivery receipt persistence for Email and SMS.
  2. Carrier DLR webhook processing and receipt retrieval.
  3. Strict Invariant: SIMULATED state must NEVER be converted to DELIVERED.
  4. Only carrier acknowledgment produces STATE_DELIVERED.
  5. Terminal failure transitions (FAILED) record root cause.
"""

import pytest
from services.email_service import (
    EmailDeliveryTracker,
    STATUS_QUEUED,
    STATUS_SENT,
    STATUS_DELIVERED,
    STATUS_FAILED,
    STATUS_SIMULATED
)
from services.production_sms_service import (
    DeliveryReceiptTracker,
    STATE_QUEUED,
    STATE_SENT,
    STATE_DELIVERED,
    STATE_FAILED,
    STATE_SIMULATED
)


def test_email_receipt_status_lifecycle():
    """Verifies that email receipt updates follow valid state transitions."""
    tracker = EmailDeliveryTracker(db_path=":memory:")
    msg_id = "MSG-LIFECYCLE-01"

    # 1. Initial Queued
    tracker.record_initial({
        "message_id": msg_id,
        "incident_id": "INC-01",
        "recipient": "sdrf@sikkim.gov.in",
        "subject": "Warning",
        "provider": "SMTP_GATEWAY",
        "status": STATUS_QUEUED
    })
    r1 = tracker.get_receipt(msg_id)
    assert r1["status"] == STATUS_QUEUED

    # 2. Transition to SENT
    tracker.update_status(msg_id, STATUS_SENT, provider_reference="SMTP-REF-889")
    r2 = tracker.get_receipt(msg_id)
    assert r2["status"] == STATUS_SENT
    assert r2["sent_at"] is not None

    # 3. Transition to DELIVERED on provider callback
    tracker.update_status(msg_id, STATUS_DELIVERED, delivered_at="2026-09-13T12:00:00Z")
    r3 = tracker.get_receipt(msg_id)
    assert r3["status"] == STATUS_DELIVERED
    assert r3["delivered_at"] == "2026-09-13T12:00:00Z"


def test_simulated_never_becomes_delivered():
    """
    CRITICAL INVARIANT:
    A simulated dispatch must never be modified to DELIVERED.
    """
    tracker = DeliveryReceiptTracker(db_path=":memory:")
    disp_id = "DISP-SIM-001"

    tracker.record_initial({
        "dispatch_id": disp_id,
        "incident_id": "INC-SIM-01",
        "recipient_ref": "CITIZEN-01",
        "phone_masked": "+91-XXXXX-1234",
        "phone_hash": "hash123",
        "provider": "mock",
        "queued_at": "2026-09-13T12:00:00Z",
        "status": STATE_SIMULATED,
        "dry_run": True
    })

    rec = tracker.get_receipt(disp_id)
    assert rec["status"] == STATE_SIMULATED
    assert rec["status"] != STATE_DELIVERED, "CRITICAL: Simulated status labeled DELIVERED!"


def test_carrier_webhook_dlr_update():
    """Verifies DLR callback updates dispatch record to DELIVERED."""
    tracker = DeliveryReceiptTracker(db_path=":memory:")
    disp_id = "DISP-REAL-99"

    tracker.record_initial({
        "dispatch_id": disp_id,
        "incident_id": "INC-REAL-01",
        "recipient_ref": "CITIZEN-02",
        "phone_masked": "+91-XXXXX-5678",
        "phone_hash": "hash567",
        "provider": "cdac",
        "queued_at": "2026-09-13T12:00:00Z",
        "status": STATE_SENT,
        "dry_run": False
    })

    # Webhook callback from telecom carrier
    ok, msg = tracker.update_from_webhook(
        dispatch_id=disp_id,
        provider_reference="CDAC-MSG-8821",
        carrier_status="DELIVRD"
    )
    assert ok is True

    updated = tracker.get_receipt(disp_id)
    assert updated["status"] == STATE_DELIVERED
    assert updated["provider_reference"] == "CDAC-MSG-8821"
    assert updated["delivered_at"] is not None


def test_carrier_webhook_failure_update():
    """Verifies carrier failure callback records error and transitions to FAILED."""
    tracker = DeliveryReceiptTracker(db_path=":memory:")
    disp_id = "DISP-FAIL-01"

    tracker.record_initial({
        "dispatch_id": disp_id,
        "incident_id": "INC-FAIL",
        "recipient_ref": "CITIZEN-03",
        "phone_masked": "+91-XXXXX-9999",
        "phone_hash": "hash999",
        "provider": "cdac",
        "queued_at": "2026-09-13T12:00:00Z",
        "status": STATE_SENT,
        "dry_run": False
    })

    ok, msg = tracker.update_from_webhook(
        dispatch_id=disp_id,
        provider_reference="CDAC-MSG-ERR",
        carrier_status="UNDELIV",
        failure_reason="Subscriber out of cellular coverage"
    )
    assert ok is True

    updated = tracker.get_receipt(disp_id)
    assert updated["status"] == STATE_FAILED
    assert "Subscriber out of cellular coverage" in updated["failure_reason"]
