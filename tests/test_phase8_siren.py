# -*- coding: utf-8 -*-
"""
tests/test_phase8_siren.py
==========================
Tests for Checkpoint 8-25:
Siren Architecture Test, HMAC-SHA256 Cryptographic Signing,
Nonce Replay Rejection, Expiry Protection, and Permanent DRY_RUN Isolation.
"""

import time
import pytest
from services.eoc_service import EOC_SERVICE


def test_siren_command_generation_and_fields():
    """Verify cryptographically signed siren command contains all 7 required security fields."""
    cmd = EOC_SERVICE.generate_signed_siren_command(
        incident_id="INC-SIREN-TEST-001",
        target="SIREN_RELAY_KM48",
        authorization="DM_PAKYONG_TOKEN_99",
        expiry_seconds=60
    )

    required_fields = ["incident_id", "timestamp", "target", "authorization", "signature", "expiry", "nonce"]
    for f in required_fields:
        assert f in cmd, f"Field {f} missing from siren command payload"

    assert cmd["siren_hardware_state"] == "DRY_RUN"
    assert cmd["badge"] == "[SIREN_DRY_RUN]"
    assert len(cmd["signature"]) == 64  # SHA-256 HMAC


def test_siren_verification_and_replay_protection():
    """Verify siren command verifies on first attempt but strictly fails on replay."""
    cmd = EOC_SERVICE.generate_signed_siren_command(
        incident_id="INC-SIREN-TEST-002",
        target="SIREN_RELAY_KM48",
        authorization="DM_PAKYONG_TOKEN_99",
        expiry_seconds=120
    )

    # First attempt: must succeed in dry-run
    ok, msg = EOC_SERVICE.verify_and_execute_siren_command(cmd)
    assert ok is True
    assert "verified and simulated" in msg

    # Second attempt with same nonce (Replay): must be rejected
    ok_replay, msg_replay = EOC_SERVICE.verify_and_execute_siren_command(cmd)
    assert ok_replay is False
    assert "Replay attack detected" in msg_replay


def test_siren_command_expiry():
    """Verify that an expired siren trigger token is rejected."""
    cmd = EOC_SERVICE.generate_signed_siren_command(
        incident_id="INC-SIREN-TEST-003",
        target="SIREN_RELAY_KM48",
        authorization="DM_PAKYONG_TOKEN_99",
        expiry_seconds=-10  # Expired 10 seconds ago
    )
    ok, msg = EOC_SERVICE.verify_and_execute_siren_command(cmd)
    assert ok is False
    assert "expired" in msg.lower()


def test_siren_command_signature_tampering():
    """Verify that tampering with any field invalidates the signature."""
    cmd = EOC_SERVICE.generate_signed_siren_command(
        incident_id="INC-SIREN-TEST-004",
        target="SIREN_RELAY_KM48",
        authorization="DM_PAKYONG_TOKEN_99",
        expiry_seconds=120
    )
    cmd["target"] = "SIREN_RELAY_GANGTOK"  # Tampered target
    ok, msg = EOC_SERVICE.verify_and_execute_siren_command(cmd)
    assert ok is False
    assert "Invalid cryptographic signature" in msg
