# -*- coding: utf-8 -*-
"""
tests/test_phase10j_email.py
============================
PARVAT NETRA • Phase 10J — Email Provider & Delivery Layer Tests
----------------------------------------------------------------
Verifies:
  1. RFC 5322 email syntax validation (valid, invalid, edge cases).
  2. DemoEmailProvider dispatches safely with STATUS_SIMULATED.
  3. SMTPEmailProvider abstraction, configuration check, and unconfigured safety.
  4. APIEmailProvider abstraction.
  5. HTML + Text MIME multipart template rendering.
  6. Life-safety instructions preserved without truncation.
  7. Invariant: Never convert SIMULATED into DELIVERED.
"""

import pytest
from services.email_service import (
    validate_email_address,
    DemoEmailProvider,
    SMTPEmailProvider,
    APIEmailProvider,
    ProductionEmailService,
    EmailDeliveryTracker,
    STATUS_SIMULATED,
    STATUS_SENT,
    STATUS_DELIVERED,
    STATUS_FAILED,
    STATUS_UNAVAILABLE,
    VALID_EMAIL_STATES
)


def test_email_validation_rules():
    """Verifies that RFC 5322 validation accepts valid and rejects invalid addresses."""
    valid_addresses = [
        "commander@ndrf.gov.in",
        "sdrf.sikkim@nic.in",
        "officer-10@disaster.assam.gov.in",
        "alert+test@domain.org",
        "user123@example.co.in"
    ]
    for addr in valid_addresses:
        ok, res = validate_email_address(addr)
        assert ok is True, f"Expected '{addr}' to be valid, got: {res}"
        assert res == addr.lower()

    invalid_addresses = [
        "",
        "notanemail",
        "@nodomain.com",
        "user@",
        "user@.com",
        "user@domain",
        "user@domain..com",
        "user space@domain.com",
        None
    ]
    for bad in invalid_addresses:
        ok, reason = validate_email_address(bad)
        assert ok is False, f"Expected '{bad}' to be invalid"
        assert len(reason) > 0


def test_demo_email_provider_dispatch():
    """Verifies safe simulation mode of DemoEmailProvider."""
    provider = DemoEmailProvider()
    assert provider.is_configured() is True

    res = provider.send_email(
        to_email="evaluator@sih.gov.in",
        subject="TEST ALERT",
        body_text="Test message body text.",
        body_html="<p>Test HTML body</p>"
    )

    assert res["success"] is True
    assert res["status"] == STATUS_SIMULATED
    assert res["status"] != STATUS_DELIVERED, "CRITICAL: Demo email must never be marked DELIVERED!"
    assert res["provider"] == "DEMO_EMAIL_GATEWAY"
    assert "EML-DEMO-" in res["provider_reference"]
    assert len(provider.dispatched_history) == 1


def test_smtp_unconfigured_safety():
    """Verifies SMTPEmailProvider returns UNAVAILABLE when SMTP_HOST is not set."""
    provider = SMTPEmailProvider()
    provider.host = ""  # Force unconfigured
    assert provider.is_configured() is False

    res = provider.send_email(
        to_email="test@sih.gov.in",
        subject="Test Alert",
        body_text="Test"
    )
    assert res["success"] is False
    assert res["status"] == STATUS_UNAVAILABLE
    assert "not configured" in res["error"].lower()


def test_api_email_provider_unconfigured_safety():
    """Verifies APIEmailProvider returns UNAVAILABLE when API URL/key is missing."""
    provider = APIEmailProvider()
    provider.api_url = ""
    provider.api_key = ""
    assert provider.is_configured() is False

    res = provider.send_email(
        to_email="test@sih.gov.in",
        subject="Test",
        body_text="Test"
    )
    assert res["success"] is False
    assert res["status"] == STATUS_UNAVAILABLE


def test_template_rendering_and_action_preservation():
    """Verifies multipart email templates preserve life-safety actions."""
    svc = ProductionEmailService()
    action = "Evacuate immediately via BRO NH-717A bypass corridor"

    subj, text, html = svc.render_email_template(
        template_type="LANDSLIDE_WARNING",
        area="Dikchu",
        corridor="NH-10 Km 48",
        risk_level="EXTREME",
        action=action,
        incident_id="INC-EML-TEST-01",
        is_test=True
    )

    assert "[PARVAT NETRA TEST ALERT]" in subj
    assert "[PARVAT NETRA TEST ALERT]" in text
    assert "[PARVAT NETRA TEST ALERT]" in html
    assert action in text
    assert action in html
    assert "INC-EML-TEST-01" in text
    assert "INC-EML-TEST-01" in html


def test_email_delivery_tracker_lifecycle():
    """Verifies persistent tracking of email dispatches and receipt transitions."""
    tracker = EmailDeliveryTracker(db_path=":memory:")
    msg_id = "MSG-EML-TEST-99"

    tracker.record_initial({
        "message_id": msg_id,
        "incident_id": "INC-001",
        "recipient": "officer@sikkim.gov.in",
        "subject": "LANDSLIDE WARNING",
        "provider": "DEMO_GATEWAY",
        "status": STATUS_SIMULATED,
        "is_demo": True
    })

    receipt = tracker.get_receipt(msg_id)
    assert receipt is not None
    assert receipt["message_id"] == msg_id
    assert receipt["status"] == STATUS_SIMULATED
    assert receipt["recipient_masked"] == "o*****r@sikkim.gov.in"

    # Transition status
    tracker.update_status(
        message_id=msg_id,
        new_status=STATUS_SENT,
        provider_reference="REF-GATEWAY-123"
    )
    updated = tracker.get_receipt(msg_id)
    assert updated["status"] == STATUS_SENT
    assert updated["provider_reference"] == "REF-GATEWAY-123"
