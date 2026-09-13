# -*- coding: utf-8 -*-
"""
tests/test_incident_management.py
=================================
Unit tests for disaster incident entity management, tactical prioritization,
and incident state transitions.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.incident_manager import (
    IncidentManager,
    INCIDENT_OPEN,
    INCIDENT_RESPONDING,
    INCIDENT_STABILIZING,
    INCIDENT_RESOLVED,
    INCIDENT_CLOSED
)


@pytest.fixture
def temp_incidents(tmp_path):
    db_file = str(tmp_path / "test_incidents.db")
    return IncidentManager(db_path=db_file)


def test_create_incident_with_priority_and_bypass(temp_incidents):
    inc = temp_incidents.create_incident(
        decision_id="DEC-TEST-01",
        alert_id="ALERT-TEST-01",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        geofence_id="GEO-TEST-01",
        cri_score=88.0,
        population_at_risk=3200
    )
    assert inc["incident_id"].startswith("INC-")
    assert inc["status"] == INCIDENT_OPEN
    assert inc["priority_score"] > 5000.0  # High tactical priority
    assert "NH-717A" in inc["route_bypass"]


def test_incident_lifecycle_progression(temp_incidents):
    inc = temp_incidents.create_incident(
        decision_id="DEC-TEST-02",
        alert_id="ALERT-TEST-02",
        corridor_id="CORR-TUPUL-MANIPUR-RLY"
    )
    inc_id = inc["incident_id"]

    # OPEN -> RESPONDING
    updated1 = temp_incidents.update_incident_status(inc_id, INCIDENT_RESPONDING, "BRO teams mobilized")
    assert updated1["status"] == INCIDENT_RESPONDING

    # RESPONDING -> STABILIZING
    updated2 = temp_incidents.update_incident_status(inc_id, INCIDENT_STABILIZING, "Rock bolts installed")
    assert updated2["status"] == INCIDENT_STABILIZING

    # STABILIZING -> RESOLVED
    updated3 = temp_incidents.update_incident_status(inc_id, INCIDENT_RESOLVED, "Slope stable")
    assert updated3["status"] == INCIDENT_RESOLVED
    assert updated3["resolved_at"] is not None

    # RESOLVED -> CLOSED
    updated4 = temp_incidents.update_incident_status(inc_id, INCIDENT_CLOSED, "Incident closed")
    assert updated4["status"] == INCIDENT_CLOSED


def test_invalid_incident_status_raises_error(temp_incidents):
    inc = temp_incidents.create_incident(
        decision_id="DEC-TEST-03",
        alert_id="ALERT-TEST-03"
    )
    with pytest.raises(ValueError) as excinfo:
        temp_incidents.update_incident_status(inc["incident_id"], "INVALID_STATUS")
    assert "Invalid incident status" in str(excinfo.value)


def test_incident_ranking_by_priority(temp_incidents):
    # Low priority
    temp_incidents.create_incident(
        decision_id="DEC-LOW", alert_id="ALERT-LOW",
        corridor_id="CORR-DIMA-HASAO-ASSAM",
        cri_score=40.0, population_at_risk=200
    )
    # High priority
    temp_incidents.create_incident(
        decision_id="DEC-HIGH", alert_id="ALERT-HIGH",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        cri_score=92.0, population_at_risk=5000
    )

    ranked = temp_incidents.list_incidents()
    assert len(ranked) == 2
    assert ranked[0]["priority_score"] > ranked[1]["priority_score"]
    assert ranked[0]["corridor_id"] == "CORR-NH10-SIKKIM-KM48"
