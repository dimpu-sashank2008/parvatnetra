# -*- coding: utf-8 -*-
"""
tests/test_pilot_modes.py
=========================
Authoritative test suite for PARVAT NETRA / PAHAD AI Pilot Modes.
Verifies the 5 supported modes, transitions, safety policies, and anti-escalation locks.
"""

import pytest
from engine.pilot_profile import (
    PilotProfileManager,
    PilotProfile,
    PilotMode,
    SafetyPolicy
)

@pytest.fixture
def fresh_manager():
    """Provides a fresh isolated PilotProfileManager instance for test isolation."""
    profile = PilotProfile(
        pilot_id="TEST-PILOT-CORRIDOR-01",
        corridor="SK-NH10-KM48",
        mode=PilotMode.SHADOW,
        safety_policy=SafetyPolicy(
            public_dispatch_enabled=False,
            siren_hardware_enabled=False,
            auto_escalate_mode=False
        )
    )
    return PilotProfileManager(profile)

def test_all_pilot_modes_defined():
    """Verify all 5 required modes are defined and recognized."""
    expected_modes = {"DEVELOPMENT", "DEMO", "SHADOW", "SUPERVISED_PILOT", "OPERATIONAL"}
    actual_modes = {m.value for m in PilotMode}
    assert expected_modes == actual_modes

def test_default_public_dispatch_disabled(fresh_manager):
    """Verify by default PUBLIC_DISPATCH is strictly disabled."""
    profile = fresh_manager.get_profile()
    assert profile.safety_policy.public_dispatch_enabled is False
    assert profile.safety_policy.siren_hardware_enabled is False

def test_mode_transition_requires_authority_token(fresh_manager):
    """Verify transition without a valid authority token is rejected."""
    res = fresh_manager.set_mode(
        target_mode=PilotMode.SUPERVISED_PILOT,
        authority_token="",  # Empty token
        operator_id="op-test"
    )
    assert res["success"] is False
    assert "Authority token is required" in res["error"]
    assert fresh_manager.get_mode() == PilotMode.SHADOW

def test_mode_transition_invalid_mode_rejected(fresh_manager):
    """Verify attempting to set an unknown mode string is rejected."""
    res = fresh_manager.set_mode(
        target_mode="AUTONOMOUS_WARFARE",
        authority_token="AUTH-VALID-TOKEN-1234",
        operator_id="op-test"
    )
    assert res["success"] is False
    assert "Invalid pilot mode" in res["error"]

def test_operational_mode_blocked_when_external_gates_fail(fresh_manager):
    """Verify system strictly refuses escalation to OPERATIONAL when external gates fail."""
    res = fresh_manager.set_mode(
        target_mode=PilotMode.OPERATIONAL,
        authority_token="SUPER-USER-AUTH-TOKEN-9999",
        operator_id="director-sdma"
    )
    assert res["success"] is False
    assert "Cannot escalate to OPERATIONAL mode" in res["error"]
    assert res["external_gates_pass"] is False
    assert fresh_manager.get_mode() != PilotMode.OPERATIONAL

def test_transition_to_supervised_pilot(fresh_manager):
    """Verify authorized transition to SUPERVISED_PILOT keeps public dispatch disabled."""
    res = fresh_manager.set_mode(
        target_mode=PilotMode.SUPERVISED_PILOT,
        authority_token="AUTH-TOKEN-VALID-TOKEN-8888",
        operator_id="op-swastik-01",
        reason="Initiate monitored field trial"
    )
    assert res["success"] is True
    assert res["active_mode"] == PilotMode.SUPERVISED_PILOT.value
    assert res["public_dispatch_enabled"] is False  # Must remain disabled
    assert res["siren_hardware_enabled"] is False

def test_anti_auto_escalation_enforcement(fresh_manager):
    """Verify auto_escalate_mode cannot be toggled to bypass safety gates."""
    profile = fresh_manager.get_profile()
    profile.safety_policy.auto_escalate_mode = True

    # Transition attempts must clear auto_escalate_mode
    res = fresh_manager.set_mode(
        target_mode=PilotMode.SHADOW,
        authority_token="AUTH-TOKEN-TOKEN-12345",
        operator_id="op-01"
    )
    assert res["success"] is True
    assert fresh_manager.get_profile().safety_policy.auto_escalate_mode is False

def test_demo_mode_isolation(fresh_manager):
    """Verify switching to DEMO mode explicitly locks public dispatch and siren."""
    res = fresh_manager.set_mode(
        target_mode=PilotMode.DEMO,
        authority_token="AUTH-TOKEN-TOKEN-99999",
        operator_id="evaluator-01"
    )
    assert res["success"] is True
    profile = fresh_manager.get_profile()
    assert profile.mode == PilotMode.DEMO
    assert profile.safety_policy.public_dispatch_enabled is False
    assert profile.safety_policy.siren_hardware_enabled is False

def test_mode_transition_audit_history(fresh_manager):
    """Verify every mode transition is immutably recorded in history."""
    fresh_manager.set_mode(
        target_mode=PilotMode.SUPERVISED_PILOT,
        authority_token="AUTH-TOKEN-TOKEN-11111",
        operator_id="op-1",
        reason="Trial start"
    )
    fresh_manager.set_mode(
        target_mode=PilotMode.SHADOW,
        authority_token="AUTH-TOKEN-TOKEN-22222",
        operator_id="op-2",
        reason="Trial pause"
    )
    history = fresh_manager._mode_history
    assert len(history) >= 3  # Init + 2 transitions
    assert history[-1]["to_mode"] == "SHADOW"
    assert history[-2]["to_mode"] == "SUPERVISED_PILOT"
