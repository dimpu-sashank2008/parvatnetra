# -*- coding: utf-8 -*-
"""
tests/test_operational_state_machine.py
=======================================
Unit tests for the 11-state operational state machine, side states,
permitted transition validation, and append-only audit logging.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    STATE_SUPPRESSED,
    STATE_CANCELLED,
    STATE_EXPIRED
)


@pytest.fixture
def temp_sm(tmp_path):
    db_file = str(tmp_path / "test_sm.db")
    return OperationalStateMachine(db_path=db_file)


def test_initial_state_defaults_to_monitoring(temp_sm):
    assert temp_sm.get_state("ENTITY-01") == STATE_MONITORING


def test_canonical_operational_lifecycle(temp_sm):
    e = "ENTITY-CORR-01"

    # MONITORING -> ANOMALY_DETECTED
    temp_sm.transition(e, STATE_ANOMALY_DETECTED, "SENSOR_AGENT", "Pore pressure spike observed")
    assert temp_sm.get_state(e) == STATE_ANOMALY_DETECTED

    # ANOMALY_DETECTED -> PAHAD_EVALUATING
    temp_sm.transition(e, STATE_PAHAD_EVALUATING, "PAHAD_INFERENCE", "Computing FoS and event prob")
    assert temp_sm.get_state(e) == STATE_PAHAD_EVALUATING

    # PAHAD_EVALUATING -> CORROBORATION_PENDING
    temp_sm.transition(e, STATE_CORROBORATION_PENDING, "CORROBORATION_ENGINE", "Verifying independent signals")
    assert temp_sm.get_state(e) == STATE_CORROBORATION_PENDING

    # CORROBORATION_PENDING -> AUTHORITY_REVIEW
    temp_sm.transition(e, STATE_AUTHORITY_REVIEW, "AI_SUPERVISOR", "Corroborated 3 groups, elevated to DM")
    assert temp_sm.get_state(e) == STATE_AUTHORITY_REVIEW

    # AUTHORITY_REVIEW -> WARNING_AUTHORIZED
    temp_sm.transition(e, STATE_WARNING_AUTHORIZED, "DISTRICT_AUTHORITY:DM_01", "Approved public warning")
    assert temp_sm.get_state(e) == STATE_WARNING_AUTHORIZED

    # WARNING_AUTHORIZED -> PUBLIC_DISPATCH
    temp_sm.transition(e, STATE_PUBLIC_DISPATCH, "OPERATIONS_DESK", "Dispatching to siren and SMS", authorization="NDMA-AUTH-2026")
    assert temp_sm.get_state(e) == STATE_PUBLIC_DISPATCH

    # PUBLIC_DISPATCH -> FIELD_RESPONSE
    temp_sm.transition(e, STATE_FIELD_RESPONSE, "SDRF_COMMAND", "QRT convoy en route to road closure")
    assert temp_sm.get_state(e) == STATE_FIELD_RESPONSE

    # FIELD_RESPONSE -> ACKNOWLEDGED
    temp_sm.transition(e, STATE_ACKNOWLEDGED, "FIELD_LEAD", "Road blocked and traffic diverted")
    assert temp_sm.get_state(e) == STATE_ACKNOWLEDGED

    # ACKNOWLEDGED -> RESOLVED
    temp_sm.transition(e, STATE_RESOLVED, "BRO_ENGINEER", "Debris cleared, slope stabilized")
    assert temp_sm.get_state(e) == STATE_RESOLVED

    # RESOLVED -> CLOSED
    temp_sm.transition(e, STATE_CLOSED, "DM_OFFICER", "Corridor re-opened to normal traffic")
    assert temp_sm.get_state(e) == STATE_CLOSED


def test_public_dispatch_requires_authorization(temp_sm):
    e = "ENTITY-UNAUTH-01"
    temp_sm.transition(e, STATE_ANOMALY_DETECTED, "TEST", "Trigger")
    temp_sm.transition(e, STATE_PAHAD_EVALUATING, "TEST", "Eval")
    temp_sm.transition(e, STATE_CORROBORATION_PENDING, "TEST", "Corrob")
    temp_sm.transition(e, STATE_AUTHORITY_REVIEW, "TEST", "Review")
    temp_sm.transition(e, STATE_WARNING_AUTHORIZED, "TEST", "Auth")

    # Attempt transition without authorization token
    with pytest.raises(PermissionError) as excinfo:
        temp_sm.transition(e, STATE_PUBLIC_DISPATCH, "TEST_ACTOR", "Attempting public siren")
    assert "requires valid authority authorization token" in str(excinfo.value)


def test_illegal_state_transition_raises_error(temp_sm):
    e = "ENTITY-ILLEGAL-01"
    # Cannot jump directly from MONITORING to PUBLIC_DISPATCH
    with pytest.raises(ValueError) as excinfo:
        temp_sm.transition(e, STATE_PUBLIC_DISPATCH, "TEST_ACTOR", "Illegal leap")
    assert "Illegal operational transition" in str(excinfo.value)


def test_side_states_suppressed_cancelled_expired(temp_sm):
    # Suppressed from monitoring
    temp_sm.transition("ENT-SUPP", STATE_SUPPRESSED, "SYS", "Suppressed under shadow mode")
    assert temp_sm.get_state("ENT-SUPP") == STATE_SUPPRESSED

    # Cancelled from authority review
    temp_sm.transition("ENT-CANC", STATE_ANOMALY_DETECTED, "SYS", "Anomaly")
    temp_sm.transition("ENT-CANC", STATE_PAHAD_EVALUATING, "SYS", "Eval")
    temp_sm.transition("ENT-CANC", STATE_CORROBORATION_PENDING, "SYS", "Corrob")
    temp_sm.transition("ENT-CANC", STATE_AUTHORITY_REVIEW, "SYS", "Review")
    temp_sm.transition("ENT-CANC", STATE_CANCELLED, "DM_01", "False alarm due to livestock")
    assert temp_sm.get_state("ENT-CANC") == STATE_CANCELLED


def test_history_logging(temp_sm):
    e = "ENT-HIST"
    temp_sm.transition(e, STATE_ANOMALY_DETECTED, "ACTOR_A", "Step 1")
    temp_sm.transition(e, STATE_PAHAD_EVALUATING, "ACTOR_B", "Step 2")

    history = temp_sm.get_history(e)
    assert len(history) == 2
    assert history[0]["new_state"] == STATE_ANOMALY_DETECTED
    assert history[1]["new_state"] == STATE_PAHAD_EVALUATING
    assert history[0]["actor"] == "ACTOR_A"
