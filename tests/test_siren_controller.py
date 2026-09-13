# -*- coding: utf-8 -*-
"""
tests/test_siren_controller.py
==============================
Unit tests for Service-Layer Siren Controller & Relay Driver (Phase 6A).
Validates:
  - Strict DRY_RUN default invariant (physical_actuation=False by default)
  - Controller lifecycle: arm(), disarm(), deactivate(), status()
  - Diagnostic test mode execution without physical audible output
  - Token authorization verification for physical output actuation
  - Suppression of activations while controller is DISARMED
  - Audit event logging
"""

import pytest
from services.siren_controller import (
    SirenController,
    SIREN_AUTH_SECRET
)


@pytest.fixture
def siren():
    # Default dry run with physical test disallowed
    return SirenController(
        gateway_id="GW-TEST-01",
        hardware_enabled=False,
        dry_run=True,
        allow_physical_test=False,
        auth_secret="TEST_SAFETY_SECRET_123"
    )


def test_default_dry_run_invariants(siren):
    status = siren.status()
    assert status["dry_run"] is True
    assert status["hardware_enabled"] is False
    assert status["allow_physical_test"] is False
    assert status["is_armed"] is True
    assert "DRY_RUN" in status["safety_mode"]


def test_arm_and_disarm_states(siren):
    siren.disarm(operator="Test Officer")
    assert siren.status()["is_armed"] is False
    assert siren.status()["current_state"] == "DISARMED"

    siren.arm(operator="Test Officer")
    assert siren.status()["is_armed"] is True
    assert siren.status()["current_state"] == "ARMED"


def test_test_mode_physical_suppression(siren):
    event = siren.test(duration_sec=3, operator="Field Tech")
    assert event["event_type"] == "SIREN_TEST_EVENT"
    assert event["dry_run"] is True
    assert event["physical_actuation"] is False
    assert event["physical_output"] is False
    assert event["status"] == "TEST_COMPLETED_SAFE"
    assert "suppressed" in event["message"].lower()


def test_activation_while_disarmed_blocked(siren):
    siren.disarm()
    res = siren.activate(level="WARNING", reason="Heavy rainfall")
    assert res["status"] == "BLOCKED_DISARMED"
    assert res["physical_output"] is False


def test_activate_simulated_in_dry_run(siren):
    res = siren.activate(level="CRITICAL", reason="Slope displacement > 15 mm/day")
    assert res["severity"] == "CRITICAL"
    assert res["status"] == "SOUNDING_SIMULATED"
    assert res["dry_run"] is True
    assert res["physical_actuation"] is False


def test_auth_token_verification():
    secret = "SUPER_SECURE_TEST_KEY"
    ctrl = SirenController(auth_secret=secret)

    # Valid exact secret
    assert ctrl.verify_auth_token(secret, action="ACTIVATE") is True

    # Empty token fails
    assert ctrl.verify_auth_token(None, action="ACTIVATE") is False
    assert ctrl.verify_auth_token("", action="ACTIVATE") is False

    # Wrong token fails
    assert ctrl.verify_auth_token("WRONG_KEY", action="ACTIVATE") is False


def test_invalid_level_raises_error(siren):
    with pytest.raises(ValueError):
        siren.activate(level="MEGA_EMERGENCY_9000")


def test_audit_event_log(siren):
    siren.test(duration_sec=2)
    siren.activate(level="WARNING")
    siren.activate(level="CRITICAL")

    log = siren.get_event_log(limit=10)
    assert len(log) == 3
    # Reverse chronological order: latest is first
    assert log[0]["severity"] == "CRITICAL"
    assert log[1]["severity"] == "WARNING"
    assert log[2]["severity"] == "TEST"
