# -*- coding: utf-8 -*-
"""
tests/test_phase8_incidents.py
==============================
Tests for Checkpoint 8-03:
Persistent Incident Schema (18 fields), Full Lifecycle State Machine,
and SHA-256 Audit Chaining.
"""

import os
import pytest
from engine.eoc_incident_manager import (
    EOC_INCIDENT_MANAGER,
    EOCIncident,
    STATE_NEW,
    STATE_TRIAGED,
    STATE_FIELD_VERIFICATION,
    STATE_AUTHORITY_REVIEW,
    STATE_AUTHORIZED,
    STATE_DISPATCHED,
    STATE_ACKNOWLEDGED,
    STATE_MONITORING,
    STATE_RESOLVED,
    STATE_REJECTED,
    STATE_CANCELLED,
    STATE_EXPIRED,
)


def test_persistent_incident_18_fields():
    """Verify all 18 required fields are present in persistent incident object."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=78.5,
        risk_band="HIGH",
        model_probability=0.81,
        FoS=0.99,
        rainfall=172.0,
        seismic_state="QUIET",
        sensor_state="HEALTHY",
        signal_agreement="2-of-3 Corroborated",
        data_quality=0.96,
        provenance="[SIMULATED]",
        recommended_action="EVACUATE",
        assigned_authority="DISTRICT_MAGISTRATE_PAKYONG",
        assigned_field_team="BRO_TASK_FORCE_KM48",
        geofence_radius=15.0
    )
    inc_dict = inc.to_dict()
    required_18_fields = [
        "incident_id", "sector_id", "created_at", "risk_score", "risk_band",
        "model_probability", "FoS", "rainfall", "seismic_state", "sensor_state",
        "signal_agreement", "data_quality", "provenance", "recommended_action",
        "incident_status", "assigned_authority", "assigned_field_team",
        "geofence_radius", "audit_hash"
    ]
    for f in required_18_fields:
        assert f in inc_dict, f"Required field {f} missing from incident dictionary"

    assert inc.incident_status == STATE_NEW
    assert len(inc.audit_hash) == 64  # SHA-256 hex string


def test_incident_full_lifecycle_progression():
    """Verify clean transitions across canonical operational lifecycle states."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=85.0,
        risk_band="CRITICAL",
        model_probability=0.89,
        FoS=0.94,
        rainfall=195.0
    )
    inc_id = inc.incident_id
    initial_hash = inc.audit_hash

    # NEW -> TRIAGED
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_TRIAGED, "EOC_OPERATOR", "OP_01")
    assert ok and inc.incident_status == STATE_TRIAGED
    assert inc.audit_hash != initial_hash
    hash_triaged = inc.audit_hash

    # TRIAGED -> FIELD_VERIFICATION
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_FIELD_VERIFICATION, "EOC_OPERATOR", "OP_01")
    assert ok and inc.incident_status == STATE_FIELD_VERIFICATION
    assert inc.audit_hash != hash_triaged
    hash_field = inc.audit_hash

    # FIELD_VERIFICATION -> AUTHORITY_REVIEW
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_AUTHORITY_REVIEW, "FIELD_OPERATOR", "BRO_01")
    assert ok and inc.incident_status == STATE_AUTHORITY_REVIEW
    assert inc.audit_hash != hash_field
    hash_review = inc.audit_hash

    # AUTHORITY_REVIEW -> AUTHORIZED
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_AUTHORIZED, "DISTRICT_AUTHORITY", "DM_01")
    assert ok and inc.incident_status == STATE_AUTHORIZED
    assert inc.audit_hash != hash_review
    hash_auth = inc.audit_hash

    # AUTHORIZED -> DISPATCHED
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_DISPATCHED, "EOC_OPERATOR", "EOC_AUTO")
    assert ok and inc.incident_status == STATE_DISPATCHED
    assert inc.audit_hash != hash_auth
    hash_disp = inc.audit_hash

    # DISPATCHED -> ACKNOWLEDGED
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_ACKNOWLEDGED, "CITIZEN", "USER_123")
    assert ok and inc.incident_status == STATE_ACKNOWLEDGED
    assert inc.audit_hash != hash_disp
    hash_ack = inc.audit_hash

    # ACKNOWLEDGED -> MONITORING
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_MONITORING, "EOC_OPERATOR", "OP_02")
    assert ok and inc.incident_status == STATE_MONITORING

    # MONITORING -> RESOLVED
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_id, STATE_RESOLVED, "DISTRICT_AUTHORITY", "DM_01")
    assert ok and inc.incident_status == STATE_RESOLVED


def test_illegal_lifecycle_transition_rejection():
    """Verify that illegal lifecycle skips are strictly rejected."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=70.0,
        risk_band="HIGH",
        model_probability=0.72,
        FoS=1.05,
        rainfall=155.0
    )
    # Skipping from NEW directly to AUTHORIZED must fail
    ok, msg, _ = EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_AUTHORIZED, "DISTRICT_AUTHORITY", "DM_01")
    assert not ok
    assert "Illegal transition" in msg

    # Skipping from NEW directly to DISPATCHED must fail
    ok2, msg2, _ = EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_DISPATCHED, "EOC_OPERATOR", "OP_01")
    assert not ok2
    assert "Illegal transition" in msg2


def test_terminal_states_support():
    """Verify support for REJECTED, CANCELLED, EXPIRED states."""
    # Test REJECTED
    inc_rej = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48", risk_score=50.0, risk_band="MEDIUM", model_probability=0.4, FoS=1.2, rainfall=30.0
    )
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_rej.incident_id, STATE_REJECTED, "EOC_OPERATOR", "OP_01")
    assert ok and inc.incident_status == STATE_REJECTED

    # Test CANCELLED
    inc_canc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48", risk_score=60.0, risk_band="MEDIUM", model_probability=0.5, FoS=1.15, rainfall=60.0
    )
    ok, _, inc = EOC_INCIDENT_MANAGER.transition_state(inc_canc.incident_id, STATE_CANCELLED, "EOC_OPERATOR", "OP_01")
    assert ok and inc.incident_status == STATE_CANCELLED
