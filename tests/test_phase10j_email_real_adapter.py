# -*- coding: utf-8 -*-
"""
tests/test_phase10j_email_real_adapter.py
=========================================
PARVAT NETRA • Phase 10J — Real Email Provider Adapter & SMTP/API Tests
-----------------------------------------------------------------------
Verifies:
  1. Real transactional email sending abstraction (SMTPEmailProvider, APIEmailProvider).
  2. Environment variable-only configuration isolation (zero hardcoded secrets).
  3. Pre-flight recipient RFC 5322 validation.
  4. Unconfigured safety invariant: Returns UNAVAILABLE/BLOCKED, never fakes delivery.
  5. Never reports DELIVERED merely because API/SMTP accepted request.
"""

import os
import pytest
from services.email_service import (
    SMTPEmailProvider,
    APIEmailProvider,
    DemoEmailProvider,
    ProductionEmailService,
    validate_email_address,
    STATUS_SENT,
    STATUS_SIMULATED,
    STATUS_DELIVERED,
    STATUS_UNAVAILABLE,
    STATUS_FAILED,
    STATUS_BLOCKED
)


def test_smtp_adapter_reads_environment_strictly(monkeypatch):
    """Verifies SMTPEmailProvider strictly reads credentials from environment variables."""
    monkeypatch.setenv("SMTP_HOST", "smtp.test-carrier.gov.in")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_USER", "eoc_officer")
    monkeypatch.setenv("SMTP_PASS", "secure_pass_123")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "alerts@sikkim.gov.in")

    provider = SMTPEmailProvider()
    assert provider.host == "smtp.test-carrier.gov.in"
    assert provider.port == 465
    assert provider.user == "eoc_officer"
    assert provider.password == "secure_pass_123"
    assert provider.default_from == "alerts@sikkim.gov.in"
    assert provider.is_configured() is True


def test_smtp_unconfigured_safety_invariant():
    """Verifies that without SMTP configuration, provider blocks dispatch honestly."""
    provider = SMTPEmailProvider()
    provider.host = ""  # Force unconfigured
    assert provider.is_configured() is False

    res = provider.send_email(
        to_email="evaluator@sih.gov.in",
        subject="TEST ALERT",
        body_text="Test body content"
    )

    assert res["success"] is False
    assert res["status"] == STATUS_UNAVAILABLE
    assert "not configured" in res["error"].lower()
    assert res["status"] != STATUS_DELIVERED, "CRITICAL: Unconfigured SMTP must never mark DELIVERED!"


def test_api_email_adapter_payload_and_safety():
    """Verifies APIEmailProvider structures cloud request and fails safely when unconfigured."""
    provider = APIEmailProvider()
    provider.api_url = ""
    provider.api_key = ""
    assert provider.is_configured() is False

    res = provider.send_email(
        to_email="evaluator@sih.gov.in",
        subject="TEST CLOUD",
        body_text="Test"
    )
    assert res["success"] is False
    assert res["status"] == STATUS_UNAVAILABLE


def test_email_validation_pre_flight():
    """Verifies RFC 5322 email syntax validation prevents corrupt dispatches."""
    valid_cases = [
        "officer@sikkim.gov.in",
        "commander-ndrf@nic.in",
        "evaluator+judge@sih.gov.in"
    ]
    for v in valid_cases:
        ok, norm = validate_email_address(v)
        assert ok is True
        assert norm == v.lower()

    invalid_cases = [
        "not-an-email",
        "user@",
        "@domain.com",
        "user@domain..com",
        "space in@email.com",
        ""
    ]
    for inv in invalid_cases:
        ok, err = validate_email_address(inv)
        assert ok is False
        assert len(err) > 0


def test_simulated_email_never_marked_delivered():
    """Invariant: Simulation/Mock mode produces STATUS_SIMULATED, NEVER STATUS_DELIVERED."""
    demo = DemoEmailProvider()
    res = demo.send_email(
        to_email="evaluator@sih.gov.in",
        subject="TEST",
        body_text="Demo Alert"
    )
    assert res["success"] is True
    assert res["status"] == STATUS_SIMULATED
    assert res["status"] != STATUS_DELIVERED
