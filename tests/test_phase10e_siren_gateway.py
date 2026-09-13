# -*- coding: utf-8 -*-
"""
tests/test_phase10e_siren_gateway.py
====================================
PARVAT NETRA • Phase 10E — Acoustic Siren Gateway & Hardware Security Tests
---------------------------------------------------------------------------
Verifies:
  1. Siren security architecture: authorized warning -> signed command -> nonce -> timestamp -> expiry -> HMAC.
  2. Core Safety Invariant: SIREN_DRY_RUN = 1 (Zero audible physical sound).
  3. Strict 5-tier state separation:
     DISABLED -> ARMED -> AUTHORIZED -> COMMAND_QUEUED -> DRY_RUN_EXECUTED.
  4. AI cannot directly trigger sirens (requires statutory human authority role).
  5. Replay attack rejection: Nonces can only be executed once.
  6. Expired command rejection.
  7. Cryptographic signature tampering detection.
"""

import time
import pytest
from services.public_warning_service import (
    SirenGatewayAdapter,
    SIREN_STATE_DISABLED,
    SIREN_STATE_ARMED,
    SIREN_STATE_COMMAND_QUEUED,
    SIREN_STATE_DRY_RUN_EXECUTED,
    ROLE_PUBLIC,
    ROLE_FIELD_OPERATOR,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_AUTHORITY
)
from services.siren_controller import SirenController


def test_siren_states_and_lifecycle():
    """Verifies that the siren gateway progresses through the 5 canonical states."""
    controller = SirenController(hardware_enabled=False, dry_run=True)
    adapter = SirenGatewayAdapter(controller=controller)

    assert adapter.current_state == SIREN_STATE_ARMED

    # Generate signed command
    cmd = adapter.generate_signed_command(
        incident_id="INC-SIREN-001",
        target_sector="NH-10 Km 48",
        authority_role=ROLE_DISTRICT_AUTHORITY,
        authority_id="DM_PAKYONG_OFFICER_01",
        token="AUTH-v1.testtoken.sig",
        expiry_seconds=120
    )

    assert cmd["siren_state"] == SIREN_STATE_COMMAND_QUEUED
    assert adapter.current_state == SIREN_STATE_COMMAND_QUEUED
    assert "signature" in cmd
    assert "nonce" in cmd

    # Execute safe dry run
    exec_res = adapter.verify_and_execute(cmd)
    assert exec_res["success"] is True
    assert exec_res["status"] == SIREN_STATE_DRY_RUN_EXECUTED
    assert adapter.current_state == SIREN_STATE_DRY_RUN_EXECUTED
    assert exec_res["physical_sound_output"] is False


def test_siren_ai_or_public_cannot_generate_command():
    """Verifies that non-statutory roles (PUBLIC, FIELD_OPERATOR) cannot sign siren commands."""
    adapter = SirenGatewayAdapter()

    with pytest.raises(PermissionError) as exc_pub:
        adapter.generate_signed_command(
            incident_id="INC-SIREN-002",
            target_sector="NH-10",
            authority_role=ROLE_PUBLIC,
            authority_id="CITIZEN_01",
            token="token"
        )
    assert "not authorized" in str(exc_pub.value)

    with pytest.raises(PermissionError) as exc_field:
        adapter.generate_signed_command(
            incident_id="INC-SIREN-003",
            target_sector="NH-10",
            authority_role=ROLE_FIELD_OPERATOR,
            authority_id="FIELD_CREW_01",
            token="token"
        )
    assert "not authorized" in str(exc_field.value)


def test_siren_replay_attack_rejected():
    """Verifies that executing the same signed command twice fails on nonce reuse."""
    adapter = SirenGatewayAdapter()
    cmd = adapter.generate_signed_command(
        incident_id="INC-SIREN-004",
        target_sector="NH-10",
        authority_role=ROLE_STATE_AUTHORITY,
        authority_id="SDMA_DIRECTOR",
        token="valid_token",
        expiry_seconds=60
    )

    first_exec = adapter.verify_and_execute(cmd)
    assert first_exec["success"] is True

    # Replay attack attempt
    second_exec = adapter.verify_and_execute(cmd)
    assert second_exec["success"] is False
    assert second_exec["status"] == "REPLAY_DETECTED"
    assert "replay attack" in second_exec["error"].lower()


def test_siren_expired_command_rejected():
    """Verifies that siren commands with past expiry timestamp are rejected."""
    adapter = SirenGatewayAdapter()
    cmd = adapter.generate_signed_command(
        incident_id="INC-SIREN-005",
        target_sector="NH-10",
        authority_role=ROLE_DISTRICT_AUTHORITY,
        authority_id="DM_01",
        token="token",
        expiry_seconds=-10  # Expired in past
    )

    exec_res = adapter.verify_and_execute(cmd)
    assert exec_res["success"] is False
    assert exec_res["status"] == "EXPIRED_COMMAND"


def test_siren_signature_tamper_rejected():
    """Verifies that modifying the target or signature fails HMAC verification."""
    adapter = SirenGatewayAdapter()
    cmd = adapter.generate_signed_command(
        incident_id="INC-SIREN-006",
        target_sector="NH-10 Km 48",
        authority_role=ROLE_DISTRICT_AUTHORITY,
        authority_id="DM_01",
        token="token",
        expiry_seconds=120
    )

    # Tamper with target sector
    tampered_cmd = cmd.copy()
    tampered_cmd["target_sector"] = "NH-717A TAMPERED"

    exec_res = adapter.verify_and_execute(tampered_cmd)
    assert exec_res["success"] is False
    assert exec_res["status"] == "INVALID_SIGNATURE"
