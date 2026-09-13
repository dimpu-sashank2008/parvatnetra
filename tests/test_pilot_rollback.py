# -*- coding: utf-8 -*-
"""
tests/test_pilot_rollback.py
============================
Authoritative test suite for PARVAT NETRA / PAHAD AI Pilot Emergency Rollback.
Validates immediate de-escalation, alert revocation, siren de-activation, state reset,
and audit trail retention under emergency conditions.
"""

import pytest
from engine.pilot_profile import PilotProfileManager, PilotProfile, PilotMode, SafetyPolicy

@pytest.fixture
def manager_with_active_state():
    profile = PilotProfile(
        corridor="SK-NH10-KM48",
        mode=PilotMode.SUPERVISED_PILOT,
        safety_policy=SafetyPolicy(
            public_dispatch_enabled=False,
            siren_hardware_enabled=True  # Temporarily enabled for test
        )
    )
    return PilotProfileManager(profile)

def test_rollback_requires_valid_authority_token(manager_with_active_state):
    """Verify rollback cannot be triggered anonymously or with invalid tokens."""
    res = manager_with_active_state.execute_emergency_rollback(
        corridor="SK-NH10-KM48",
        operator_id="op-1",
        reason="Test rollback",
        authority_token=""  # Missing
    )
    assert res["success"] is False
    assert "Emergency rollback requires a valid authority token" in res["error"]

def test_rollback_execution_deescalates_all_controls(manager_with_active_state):
    """Verify rollback immediately revokes dispatch, disables siren, and resets corridor."""
    manager = manager_with_active_state

    res = manager.execute_emergency_rollback(
        corridor="SK-NH10-KM48",
        operator_id="magistrate-pakyong-01",
        reason="Field inspection confirmed false positive tension crack reading.",
        authority_token="AUTH-TOKEN-REVOKE-9999"
    )

    assert res["success"] is True
    assert res["rollback_id"].startswith("RB-")
    assert res["public_dispatch"] == "DISABLED"
    assert res["siren_mode"] == "DRY_RUN"
    assert "PUBLIC_DISPATCH_FORCED_DISABLED" in res["actions_taken"]
    assert "SIREN_HARDWARE_DEACTIVATED_DRY_RUN" in res["actions_taken"]
    assert "ACTIVE_ALERTS_CANCELLED" in res["actions_taken"]
    assert "CORRIDOR_STATE_RESET_TO_MONITORING" in res["actions_taken"]

    # Verify policy state
    profile = manager.get_profile()
    assert profile.safety_policy.public_dispatch_enabled is False
    assert profile.safety_policy.siren_hardware_enabled is False

def test_rollback_event_logged_in_audit_history(manager_with_active_state):
    """Verify rollback is permanently logged with timestamp and sanitized authority token."""
    manager = manager_with_active_state

    manager.execute_emergency_rollback(
        corridor="SK-NH10-KM48",
        operator_id="commander-swastik",
        reason="Road reopened; slope stabilized.",
        authority_token="AUTH-SEC-8888"
    )

    rollbacks = manager._rollback_events
    assert len(rollbacks) >= 1
    last_rb = rollbacks[-1]
    assert last_rb["operator_id"] == "commander-swastik"
    assert "Road reopened" in last_rb["reason"]
    assert last_rb["authority_token"] == "AUT***"  # Sanitized
    assert "T" in last_rb["timestamp"]  # ISO timestamp
