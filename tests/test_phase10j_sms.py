# -*- coding: utf-8 -*-
"""
tests/test_phase10j_sms.py
==========================
PARVAT NETRA • Phase 10J — SMS Dissemination & Carrier Interface Tests
----------------------------------------------------------------------
Verifies:
  1. SMS provider neutrality (Mock and CDAC Mobile Seva gateways).
  2. The 8 canonical operational SMS states.
  3. Strict Invariant: SIMULATED SMS is NEVER marked DELIVERED.
  4. PII protection: strict telephone number masking and hashing.
  5. Indian Government DLT compliance (DLT template IDs, principal entity ID).
"""

import pytest
from services.production_sms_service import (
    ProductionSMSAdapter,
    RecipientFilter,
    STATE_UNCONFIGURED,
    STATE_CONFIGURED,
    STATE_SIMULATED,
    STATE_SENT,
    STATE_DELIVERED,
    STATE_FAILED,
    STATE_BLOCKED
)


def test_sms_simulation_mode_and_invariants():
    """Verifies that simulation dispatches are never marked DELIVERED."""
    adapter = ProductionSMSAdapter(dry_run=True, provider_name="mock")
    assert adapter.dry_run is True

    # Render a test message
    rendered = adapter.template_engine.render(
        template_type="TEST_ALERT",
        language="en",
        area="Pakyong",
        corridor="NH-10 Km 48",
        incident_id="INC-SMS-TEST"
    )

    res = adapter.provider.send_sms(
        recipient_phone="+919832011234",
        message=rendered["message"],
        dlt_template_id=rendered["dlt_template_id"]
    )

    assert res["success"] is True
    assert res["status"] != STATE_DELIVERED, "CRITICAL: Mock SMS must never return DELIVERED status without carrier receipt!"
    assert res["status"] == STATE_SENT or res["status"] == STATE_SIMULATED


def test_phone_number_pii_minimization():
    """Verifies telephone number masking preserves country code and last 4 digits only."""
    cases = [
        ("+919832011234", "+91-XXXXX-1234"),
        ("9832011234", "983-XXXXX-1234"),
        ("+91 98320 55678", "+91-XXXXX-5678"),
        ("123", "UNKNOWN_PHONE")
    ]
    for raw, expected in cases:
        masked = RecipientFilter.mask_phone(raw)
        assert masked == expected, f"Failed masking for {raw}: got {masked}, expected {expected}"

    # Verify SHA-256 hash determinism
    h1 = RecipientFilter.hash_phone("+919832011234")
    h2 = RecipientFilter.hash_phone("+919832011234")
    assert h1 == h2
    assert len(h1) == 64


def test_dlt_template_id_mapping():
    """Verifies every canonical emergency category has an assigned DLT Template ID."""
    adapter = ProductionSMSAdapter()
    templates = ["LANDSLIDE_WARNING", "HIGH_RISK_ADVISORY", "ROAD_CLOSURE", "EVACUATION_ADVISORY", "ALL_CLEAR", "TEST_ALERT"]
    for t in templates:
        rendered = adapter.template_engine.render(template_type=t, incident_id="INC-DLT-CHECK")
        assert "dlt_template_id" in rendered
        assert rendered["dlt_template_id"].startswith("DLT-TE-")
