# -*- coding: utf-8 -*-
"""
tests/test_phase10i_delivery_receipts.py
========================================
PARVAT NETRA • Phase 10I — Asynchronous Delivery Receipts & Webhook Tests
-------------------------------------------------------------------------
Verifies:
  1. Delivery receipt data model tracking:
     incident_id, recipient_ref, provider, queued_at, sent_at, delivered_at, status, provider_reference, failure_reason.
  2. Invariant: Initial / simulated dispatch is never marked DELIVERED.
  3. Processing of authentic carrier DLR webhook callbacks (/api/sms/dlr).
  4. Successful DLR callback transitions record to DELIVERED with timestamp.
  5. Failed DLR callback transitions record to FAILED with failure reason.
"""

import pytest
from services.production_sms_service import (
    DeliveryReceiptTracker,
    STATE_QUEUED,
    STATE_SENT,
    STATE_DELIVERED,
    STATE_FAILED
)


def test_delivery_receipt_initial_record():
    """Verifies that an initial SMS record tracks all required attributes."""
    tracker = DeliveryReceiptTracker()
    record = {
        "dispatch_id": "DISP-TEST-001",
        "incident_id": "INC-DLR-01",
        "recipient_ref": "CITIZEN-01",
        "phone_masked": "+91-XXXXX-1234",
        "phone_hash": "hash123",
        "provider": "CDAC_MOBILE_SEVA",
        "queued_at": "2026-09-13T10:00:00Z",
        "sent_at": "2026-09-13T10:00:01Z",
        "delivered_at": None,
        "status": STATE_SENT,
        "provider_reference": None,
        "failure_reason": None,
        "dry_run": True
    }

    tracker.record_initial(record)
    retrieved = tracker.get_receipt("DISP-TEST-001")

    assert retrieved is not None
    assert retrieved["dispatch_id"] == "DISP-TEST-001"
    assert retrieved["status"] != STATE_DELIVERED
    assert retrieved["delivered_at"] is None


def test_carrier_dlr_webhook_confirms_delivered():
    """
    CRITICAL INVARIANT:
    Only authentic provider callback transitions status to DELIVERED.
    """
    tracker = DeliveryReceiptTracker()
    record = {
        "dispatch_id": "DISP-TEST-002",
        "incident_id": "INC-DLR-02",
        "recipient_ref": "CITIZEN-02",
        "phone_masked": "+91-XXXXX-5678",
        "phone_hash": "hash5678",
        "provider": "CDAC_MOBILE_SEVA",
        "queued_at": "2026-09-13T10:05:00Z",
        "sent_at": "2026-09-13T10:05:01Z",
        "delivered_at": None,
        "status": STATE_SENT,
        "provider_reference": None,
        "failure_reason": None,
        "dry_run": False
    }
    tracker.record_initial(record)

    # Carrier delivers SMS and sends DLR webhook callback
    ok, msg = tracker.update_from_webhook(
        dispatch_id="DISP-TEST-002",
        provider_reference="CDAC-MSG-889911",
        carrier_status="DELIVRD"
    )

    assert ok is True
    updated = tracker.get_receipt("DISP-TEST-002")
    assert updated["status"] == STATE_DELIVERED
    assert updated["delivered_at"] is not None
    assert updated["provider_reference"] == "CDAC-MSG-889911"


def test_carrier_dlr_webhook_reports_failure():
    """Verifies that failed carrier delivery transitions record to FAILED with reason."""
    tracker = DeliveryReceiptTracker()
    record = {
        "dispatch_id": "DISP-TEST-003",
        "incident_id": "INC-DLR-03",
        "recipient_ref": "CITIZEN-03",
        "phone_masked": "+91-XXXXX-9999",
        "phone_hash": "hash9999",
        "provider": "CDAC_MOBILE_SEVA",
        "queued_at": "2026-09-13T10:10:00Z",
        "sent_at": "2026-09-13T10:10:01Z",
        "delivered_at": None,
        "status": STATE_SENT,
        "provider_reference": None,
        "failure_reason": None,
        "dry_run": False
    }
    tracker.record_initial(record)

    # Carrier reports failure (e.g. absent subscriber / out of coverage)
    ok, msg = tracker.update_from_webhook(
        dispatch_id="DISP-TEST-003",
        provider_reference="CDAC-MSG-889922",
        carrier_status="UNDELIV",
        failure_reason="Subscriber handset switched off / unreachable in mountain gorge"
    )

    assert ok is True
    updated = tracker.get_receipt("DISP-TEST-003")
    assert updated["status"] == STATE_FAILED
    assert updated["delivered_at"] is None
    assert "mountain gorge" in updated["failure_reason"]
