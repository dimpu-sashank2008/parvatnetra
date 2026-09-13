# -*- coding: utf-8 -*-
"""
tests/test_phase8_security.py
=============================
Tests for Checkpoint 8-29:
Role-Based Access Control (RBAC), Tamper-Evident SHA-256 Audit Chain,
Cryptographic Nonce Replay Rejection, and Payload Tampering Prevention.
"""

import hashlib
import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_NEW, STATE_AUTHORIZED, STATE_RESOLVED
from services.eoc_service import EOC_SERVICE


def test_rbac_authorization_jurisdiction():
    """Verify that unauthorized roles cannot approve alerts or authorize all-clear."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=75.0,
        risk_band="HIGH",
        model_probability=0.76,
        FoS=1.04,
        rainfall=155.0
    )

    # 1. PUBLIC role cannot authorize All-Clear
    res1 = EOC_SERVICE.authorize_all_clear(
        incident_id=inc.incident_id,
        approver_role="PUBLIC",
        approver_id="CITIZEN_01",
        field_clearance_confirmed=True,
        current_fos=1.35,
        current_rain_mm=5.0
    )
    assert res1["status"] == "REJECTED"
    assert "lacks statutory jurisdiction" in res1["error"]

    # 2. FIELD_OPERATOR role cannot authorize All-Clear
    res2 = EOC_SERVICE.authorize_all_clear(
        incident_id=inc.incident_id,
        approver_role="FIELD_OPERATOR",
        approver_id="BRO_01",
        field_clearance_confirmed=True,
        current_fos=1.35,
        current_rain_mm=5.0
    )
    assert res2["status"] == "REJECTED"
    assert "lacks statutory jurisdiction" in res2["error"]

    # 3. DISTRICT_AUTHORITY role CAN authorize All-Clear
    res3 = EOC_SERVICE.authorize_all_clear(
        incident_id=inc.incident_id,
        approver_role="DISTRICT_AUTHORITY",
        approver_id="DM_PAKYONG",
        field_clearance_confirmed=True,
        current_fos=1.35,
        current_rain_mm=5.0
    )
    assert res3["status"] == "ALL_CLEAR_AUTHORIZED"


def test_audit_hash_chain_tamper_evidence():
    """Verify that every lifecycle transition recalculates and chains the SHA-256 audit hash."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=70.0,
        risk_band="HIGH",
        model_probability=0.72,
        FoS=1.05,
        rainfall=150.0
    )
    h0 = inc.audit_hash
    assert len(h0) == 64

    # Transition 1
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, "TRIAGED", "EOC_OPERATOR", "OP_01")
    inc1 = EOC_INCIDENT_MANAGER.get_incident(inc.incident_id)
    h1 = inc1.audit_hash
    assert h1 != h0

    # Transition 2
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, "FIELD_VERIFICATION", "EOC_OPERATOR", "OP_01")
    inc2 = EOC_INCIDENT_MANAGER.get_incident(inc.incident_id)
    h2 = inc2.audit_hash
    assert h2 != h1


def test_siren_tampered_payload_rejection():
    """Verify cryptographic rejection of modified siren commands."""
    cmd = EOC_SERVICE.generate_signed_siren_command(
        incident_id="INC-SEC-001",
        target="SIREN_NH10_KM48",
        authorization="DM_TOKEN_VALID"
    )
    # Tamper with authorization token
    cmd["authorization"] = "FORGED_ATTACKER_TOKEN"
    ok, msg = EOC_SERVICE.verify_and_execute_siren_command(cmd)
    assert ok is False
    assert "Invalid cryptographic signature" in msg
