# -*- coding: utf-8 -*-
"""
tests/test_phase7g_state_machine.py
===================================
PHASE 7G — Checkpoint 7G-02: State Machine Lifecycle Audit
Verifies:
  1. The complete sequential lifecycle progression.
  2. Prevention of AI jumping directly to PUBLIC_DISPATCH or WARNING_AUTHORIZED.
  3. PUBLIC_DISPATCH strictly mandates valid authorization token.
  4. Permitted rejection transitions to CANCELLED.
  5. Two-way transition between AUTHORITY_REVIEW and FIELD_RESPONSE.
"""

import pytest
from engine.operational_state_machine import (
    OperationalStateMachine,
    STATE_MONITORING,
    STATE_ANOMALY_DETECTED,
    STATE_PAHAD_EVALUATING,
    STATE_CORROBORATION_PENDING,
    STATE_AUTHORITY_REVIEW,
    STATE_WARNING_AUTHORIZED,
    STATE_PUBLIC_DISPATCH,
    STATE_FIELD_RESPONSE,
    STATE_ACKNOWLEDGED,
    STATE_RESOLVED,
    STATE_CLOSED,
    STATE_CANCELLED
)


@pytest.fixture
def sm(tmp_path):
    db_file = str(tmp_path / "sm_test.db")
    return OperationalStateMachine(db_path=db_file)


def test_complete_lifecycle_progression(sm):
    """Verifies that an incident can progress through the full authorized lifecycle."""
    entity = "CORR-NH10-SIKKIM-KM48"

    assert sm.get_state(entity) == STATE_MONITORING

    sm.transition(entity, STATE_ANOMALY_DETECTED, "SENSOR_GATEWAY", "Pore pressure anomaly")
    assert sm.get_state(entity) == STATE_ANOMALY_DETECTED

    sm.transition(entity, STATE_PAHAD_EVALUATING, "PAHAD_PIPELINE", "FoS evaluation")
    assert sm.get_state(entity) == STATE_PAHAD_EVALUATING

    sm.transition(entity, STATE_CORROBORATION_PENDING, "PAHAD_PIPELINE", "Corroboration convergence")
    assert sm.get_state(entity) == STATE_CORROBORATION_PENDING

    sm.transition(entity, STATE_AUTHORITY_REVIEW, "CORROBORATION_ENGINE", "Elevated to authority")
    assert sm.get_state(entity) == STATE_AUTHORITY_REVIEW

    sm.transition(entity, STATE_WARNING_AUTHORIZED, "DISTRICT_AUTHORITY:DM_01", "Approved warning", authorization="AUTH-TOKEN-123")
    assert sm.get_state(entity) == STATE_WARNING_AUTHORIZED

    sm.transition(entity, STATE_PUBLIC_DISPATCH, "DISTRICT_AUTHORITY:DM_01", "Dispatched to sirens/SMS", authorization="AUTH-TOKEN-123")
    assert sm.get_state(entity) == STATE_PUBLIC_DISPATCH

    sm.transition(entity, STATE_FIELD_RESPONSE, "SDRF_COMMAND", "QRT staged at Rangpo")
    assert sm.get_state(entity) == STATE_FIELD_RESPONSE

    sm.transition(entity, STATE_ACKNOWLEDGED, "SDRF_OFFICER", "Closure barriers in place")
    assert sm.get_state(entity) == STATE_ACKNOWLEDGED

    sm.transition(entity, STATE_RESOLVED, "DISTRICT_AUTHORITY", "Slope stabilized")
    assert sm.get_state(entity) == STATE_RESOLVED

    sm.transition(entity, STATE_CLOSED, "CONTROL_ROOM", "Incident closed")
    assert sm.get_state(entity) == STATE_CLOSED


def test_ai_cannot_jump_directly_to_public_dispatch(sm):
    """Safety Invariant: AI evaluation cannot jump directly to PUBLIC_DISPATCH."""
    entity = "CORR-NH10-SIKKIM-KM48"
    sm.transition(entity, STATE_ANOMALY_DETECTED, "SENSOR", "Anomaly")
    sm.transition(entity, STATE_PAHAD_EVALUATING, "AI", "Evaluating")

    # Attempt illegal transition: PAHAD_EVALUATING -> PUBLIC_DISPATCH
    with pytest.raises(ValueError) as exc:
        sm.transition(entity, STATE_PUBLIC_DISPATCH, "AI_AUTOMATION", "Auto alert trigger")
    assert "Illegal operational transition" in str(exc.value)


def test_ai_cannot_jump_directly_to_warning_authorized(sm):
    """Safety Invariant: AI evaluation cannot jump directly to WARNING_AUTHORIZED without authority review."""
    entity = "CORR-NH10-SIKKIM-KM48"
    sm.transition(entity, STATE_ANOMALY_DETECTED, "SENSOR", "Anomaly")
    sm.transition(entity, STATE_PAHAD_EVALUATING, "AI", "Evaluating")
    sm.transition(entity, STATE_CORROBORATION_PENDING, "AI", "Corroboration")

    # Attempt illegal transition: CORROBORATION_PENDING -> WARNING_AUTHORIZED
    with pytest.raises(ValueError) as exc:
        sm.transition(entity, STATE_WARNING_AUTHORIZED, "AI_AUTOMATION", "Auto authorization")
    assert "Illegal operational transition" in str(exc.value)


def test_public_dispatch_requires_authorization_token(sm):
    """Transitioning to PUBLIC_DISPATCH strictly requires an authorization token."""
    entity = "CORR-NH10-SIKKIM-KM48"
    sm.transition(entity, STATE_ANOMALY_DETECTED, "SYS", "Anomaly")
    sm.transition(entity, STATE_PAHAD_EVALUATING, "SYS", "Eval")
    sm.transition(entity, STATE_CORROBORATION_PENDING, "SYS", "Corrob")
    sm.transition(entity, STATE_AUTHORITY_REVIEW, "SYS", "Review")
    sm.transition(entity, STATE_WARNING_AUTHORIZED, "DM_01", "Approved", authorization="AUTH-VALID-01")

    # Attempt transition without authorization token
    with pytest.raises(PermissionError) as exc:
        sm.transition(entity, STATE_PUBLIC_DISPATCH, "OPERATOR", "Dispatch without token", authorization=None)
    assert "requires valid authority authorization token" in str(exc.value)


def test_rejection_transitions_to_cancelled(sm):
    """Authority review rejection transitions entity to CANCELLED state."""
    entity = "CORR-NH10-SIKKIM-KM48"
    sm.transition(entity, STATE_ANOMALY_DETECTED, "SYS", "Anomaly")
    sm.transition(entity, STATE_PAHAD_EVALUATING, "SYS", "Eval")
    sm.transition(entity, STATE_CORROBORATION_PENDING, "SYS", "Corrob")
    sm.transition(entity, STATE_AUTHORITY_REVIEW, "SYS", "Review")

    sm.transition(entity, STATE_CANCELLED, "DISTRICT_AUTHORITY:DM_01", "False trigger from blasting")
    assert sm.get_state(entity) == STATE_CANCELLED


def test_field_verification_two_way_loop(sm):
    """Authority can request field verification, and field response returns to authority review."""
    entity = "CORR-NH10-SIKKIM-KM48"
    sm.transition(entity, STATE_ANOMALY_DETECTED, "SYS", "Anomaly")
    sm.transition(entity, STATE_PAHAD_EVALUATING, "SYS", "Eval")
    sm.transition(entity, STATE_CORROBORATION_PENDING, "SYS", "Corrob")
    sm.transition(entity, STATE_AUTHORITY_REVIEW, "SYS", "Review")

    # Authority requests ground inspection
    sm.transition(entity, STATE_FIELD_RESPONSE, "DISTRICT_AUTHORITY", "Dispatch BRO QRT")
    assert sm.get_state(entity) == STATE_FIELD_RESPONSE

    # Field response returns to review
    sm.transition(entity, STATE_AUTHORITY_REVIEW, "BRO_OFFICER", "Ground report submitted for review")
    assert sm.get_state(entity) == STATE_AUTHORITY_REVIEW
