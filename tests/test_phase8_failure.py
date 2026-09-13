# -*- coding: utf-8 -*-
"""
tests/test_phase8_failure.py
============================
Tests for Checkpoint 8-28:
Comprehensive Fail-Closed Verification Across Multi-Source Outages and Timeouts.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_NEW, STATE_AUTHORIZED, STATE_AUTHORITY_REVIEW
from services.eoc_service import EOC_SERVICE


def test_failure_drill_execution():
    """Verify all 6 core failure scenarios fail closed without unauthorized public broadcast."""
    drill_res = EOC_SERVICE.run_failure_drill()
    assert drill_res["drill_type"] == "EOC_FAIL_CLOSED_RESILIENCE_DRILL"
    assert drill_res["all_scenarios_failed_closed"] is True

    for scenario_name, outcome in drill_res["results"].items():
        assert outcome["passed"] is True, f"Scenario {scenario_name} failed closed check: {outcome['detail']}"


def test_escalation_engine_never_auto_approves():
    """Verify that timeout escalation bumps authority hierarchy but NEVER auto-authorizes alert."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=88.0,
        risk_band="CRITICAL",
        model_probability=0.90,
        FoS=0.91,
        rainfall=200.0,
        assigned_authority="DISTRICT_MAGISTRATE_PAKYONG"
    )
    # Simulate timeout expiration
    res = EOC_SERVICE.evaluate_escalation(inc.incident_id, timeout_seconds=0)

    assert res["escalated"] is True
    assert res["auto_dispatch_prevented"] is True
    assert res["incident_status"] == STATE_AUTHORITY_REVIEW

    # Crucial check: must NOT be in STATE_AUTHORIZED or STATE_DISPATCHED
    updated_inc = EOC_INCIDENT_MANAGER.get_incident(inc.incident_id)
    assert updated_inc.incident_status != STATE_AUTHORIZED
    assert updated_inc.incident_status != "DISPATCHED"
