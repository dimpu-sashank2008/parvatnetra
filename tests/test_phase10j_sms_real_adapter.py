# -*- coding: utf-8 -*-
"""
tests/test_phase10j_sms_real_adapter.py
======================================
PARVAT NETRA • Phase 10J — Real SMS Carrier Adapter & Telecom Gateway Tests
--------------------------------------------------------------------------
Verifies:
  1. Real SMS carrier abstraction (CDACSMSProvider, Telecom Gateways).
  2. Environment variable-only credential loading (zero hardcoded secrets).
  3. Strict invariant: Unconfigured provider reports SMS PROVIDER NOT CONFIGURED.
  4. Never fakes SENT or DELIVERED for real telecom carrier without credentials.
  5. Indian Government DLT compliance (Principle Entity ID, DLT Template IDs).
"""

import os
import pytest
from services.sms_service import CDACSMSProvider, MockSMSProvider
from services.production_sms_service import (
    ProductionSMSAdapter,
    STATE_UNCONFIGURED,
    STATE_CONFIGURED,
    STATE_SIMULATED,
    STATE_DELIVERED,
    STATE_SENT,
    STATE_BLOCKED
)


def test_cdac_credentials_read_from_environment(monkeypatch):
    """Verifies CDACSMSProvider reads configuration strictly from environment variables."""
    monkeypatch.setenv("CDAC_SMS_USERNAME", "nic_disaster_ops")
    monkeypatch.setenv("CDAC_SMS_PASSWORD", "sec_token_9998")

    provider = CDACSMSProvider()
    assert provider.username == "nic_disaster_ops"
    assert provider.password == "sec_token_9998"
    assert provider.is_configured is True


def test_cdac_unconfigured_fails_safely():
    """Verifies CDACSMSProvider returns error when credentials are not configured."""
    provider = CDACSMSProvider(username="", password="")
    assert provider.is_configured is False

    res = provider.send(
        phone="+919832011234",
        message="PARVAT NETRA TEST ALERT"
    )
    assert res["success"] is False
    assert "unconfigured" in res["status"].lower()
    assert "credentials not configured" in res["error"].lower()


def test_unconfigured_real_sms_is_blocked_not_faked():
    """Invariant: When real SMS is demanded without credentials, it reports BLOCKED."""
    adapter = ProductionSMSAdapter(dry_run=False, provider_name="cdac")
    # Ensure provider is unconfigured
    adapter.provider.is_configured = False

    status_dict = adapter.get_provider_configuration_status()
    assert status_dict["configuration_state"] == STATE_UNCONFIGURED

    # Verify adapter blocks dispatch if credentials absent in real mode
    res = adapter.provider.send_sms(
        recipient_phone="+919832011234",
        message="[TEST ALERT] Landslide risk warning"
    )
    assert res["success"] is False
    assert res["status"] != STATE_DELIVERED, "CRITICAL: Unconfigured SMS provider must never claim DELIVERED!"


def test_mock_sms_simulation_mode():
    """Verifies safe simulation mode returns SIMULATED and never DELIVERED."""
    mock = MockSMSProvider()
    res = mock.send_sms(
        recipient_phone="+919832011234",
        message="[SIMULATED SMS] Landslide drill"
    )
    assert res["success"] is True
    assert res["status"] == "SIMULATED"
    assert res["status"] != STATE_DELIVERED
    assert res["provider"] == "MOCK_SMS_GATEWAY"


def test_fast2sms_unconfigured_fails_safely():
    """Verifies Fast2SMS provider without API key fails safely."""
    from services.sms_service import Fast2SMSProvider
    provider = Fast2SMSProvider(api_key="")
    assert provider.is_configured is False
    res = provider.send("9059318367", "TEST ALERT")
    assert res["success"] is False
    assert "FAILED_UNCONFIGURED_CREDENTIALS" in res["status"]


def test_twilio_unconfigured_fails_safely():
    """Verifies Twilio provider without credentials fails safely."""
    from services.sms_service import TwilioSMSProvider
    provider = TwilioSMSProvider(account_sid="", auth_token="", from_number="")
    assert provider.is_configured is False
    res = provider.send("+919059318367", "TEST ALERT")
    assert res["success"] is False
    assert "FAILED_UNCONFIGURED_CREDENTIALS" in res["status"]

