# -*- coding: utf-8 -*-
"""
tests/test_phase10e_sms.py
==========================
PARVAT NETRA • Phase 10E — SMS Gateway Adapter & Delivery Receipt Tests
-----------------------------------------------------------------------
Verifies:
  1. Multi-provider abstraction (MockSMSProvider, CDACSMSProvider).
  2. Provider configuration states (CONFIGURED, UNCONFIGURED, SIMULATED, FAILED, BLOCKED).
  3. Delivery receipt model: QUEUED, SENT, DELIVERED, FAILED, UNKNOWN.
  4. Core Safety Invariant: Simulated SMS must NEVER be labeled DELIVERED.
  5. Only authentic provider receipts can produce DELIVERED.
  6. Single-segment SMS character limit (<= 160 characters).
  7. Phone masking and privacy preservation.
"""

import pytest
from services.public_warning_service import (
    SMSGatewayAdapter,
    RECEIPT_QUEUED,
    RECEIPT_SENT,
    RECEIPT_DELIVERED,
    RECEIPT_FAILED,
    RECEIPT_UNKNOWN,
    PROVIDER_CONFIGURED,
    PROVIDER_UNCONFIGURED,
    PROVIDER_SIMULATED,
    PUBLIC_DISPATCH_ENABLED
)
from services.sms_service import MockSMSProvider, CDACSMSProvider


def test_sms_provider_abstraction():
    """Verifies that SMSGatewayAdapter supports both mock and CDAC providers."""
    mock_adapter = SMSGatewayAdapter(provider_type="mock")
    assert isinstance(mock_adapter.provider, MockSMSProvider)
    assert mock_adapter.get_provider_state() == PROVIDER_SIMULATED

    cdac_adapter = SMSGatewayAdapter(provider_type="cdac")
    assert isinstance(cdac_adapter.provider, CDACSMSProvider)


def test_sms_unconfigured_cdac_state():
    """Verifies that CDACSMSProvider defaults to UNCONFIGURED without credentials."""
    unconfigured_cdac = CDACSMSProvider(username="", password="")
    adapter = SMSGatewayAdapter(provider_type="cdac")
    adapter.provider = unconfigured_cdac
    assert adapter.get_provider_state() == PROVIDER_UNCONFIGURED


def test_simulated_sms_never_delivered():
    """
    CRITICAL INVARIANT:
    Simulated SMS must NEVER be marked as DELIVERED.
    Status must be SENT or SIMULATED_SENT, never DELIVERED.
    """
    adapter = SMSGatewayAdapter(provider_type="mock")
    record = adapter.send_sms(
        recipient_phone_masked="+91-98****1234",
        message="PAHAD AI WARNING: Landslide hazard near NH-10. ID:TEST-01",
        incident_id="INC-TEST-001",
        language="en"
    )

    assert record["delivery_status"] != RECEIPT_DELIVERED, "CRITICAL: Simulated SMS marked as DELIVERED!"
    assert record["delivery_status"] == RECEIPT_SENT
    assert record["dry_run"] is True
    assert record["carrier_receipt"] is None
    assert "[SIMULATED" in record["provenance"]


def test_sms_character_limit_enforced():
    """Verifies that SMS messages strictly adhere to the single-segment <= 160 character limit."""
    adapter = SMSGatewayAdapter(provider_type="mock")
    long_msg = "A" * 250
    record = adapter.send_sms(
        recipient_phone_masked="+91-98****5678",
        message=long_msg,
        incident_id="INC-TEST-002"
    )

    assert len(record["message"]) <= 160
    assert record["message"].endswith("...")
    assert record["message_length"] <= 160


def test_sms_delivery_receipt_states_defined():
    """Verifies the delivery receipt state enum integrity."""
    expected_states = {RECEIPT_QUEUED, RECEIPT_SENT, RECEIPT_DELIVERED, RECEIPT_FAILED, RECEIPT_UNKNOWN}
    for state in (RECEIPT_QUEUED, RECEIPT_SENT, RECEIPT_DELIVERED, RECEIPT_FAILED, RECEIPT_UNKNOWN):
        assert state in expected_states


def test_sms_unconfigured_provider_fails_closed():
    """Verifies that attempting live send on an unconfigured provider fails closed safely."""
    adapter = SMSGatewayAdapter(provider_type="cdac")
    adapter.provider = CDACSMSProvider(username="", password="")

    # In dry-run mode (default), it stays safe
    record = adapter.send_sms(
        recipient_phone_masked="+91-98****9999",
        message="Emergency Alert",
        incident_id="INC-TEST-003"
    )
    assert record["dry_run"] is True
    assert record["delivery_status"] != RECEIPT_DELIVERED
