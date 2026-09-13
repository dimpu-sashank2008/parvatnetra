# -*- coding: utf-8 -*-
"""
tests/test_pilot_readiness.py
=============================
Authoritative test suite for PARVAT NETRA / PAHAD AI Phase 6F Pilot Readiness Gate.
Validates the 16 critical dimensions (A-P), readiness scoring, blocker classifications,
and decision logic under SIH 26001 / NDMA guidelines.
"""

import pytest
from engine.pilot_profile import (
    PilotProfileManager,
    PilotMode,
    GateStatus,
    BlockerSeverity,
    PILOT_MANAGER
)

def test_readiness_dimensions_evaluated():
    """Verify all 16 dimensions (A through P) are present in the evaluation."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    audits = evaluation.dimension_audits

    expected_dimensions = [
        "A_DATA", "B_MODEL", "C_WEATHER", "D_SEISMIC",
        "E_SATELLITE_EO", "F_TERRAIN", "G_PHYSICAL_IOT", "H_EDGE_GATEWAY",
        "I_ALERTING", "J_MOBILE", "K_OFFLINE", "L_SECURITY",
        "M_HUMAN_OVERSIGHT", "N_OBSERVABILITY", "O_INCIDENT_RESPONSE", "P_OPERATIONAL_PROCEDURES"
    ]
    for dim in expected_dimensions:
        assert dim in audits, f"Missing dimension: {dim}"
        assert "status" in audits[dim]
        assert "requirement" in audits[dim]
        assert "evidence" in audits[dim]
        assert "blocker" in audits[dim]
        assert "remediation" in audits[dim]

def test_dimension_status_values():
    """Verify all dimension statuses belong to allowed enum values."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    allowed_statuses = {s.value for s in GateStatus}
    for dim, record in evaluation.dimension_audits.items():
        assert record["status"] in allowed_statuses, f"Invalid status '{record['status']}' in {dim}"

def test_data_gate_evaluated_pass():
    """Verify DATA gate passes with 17 canonical events and 0 leakage."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    data_audit = evaluation.dimension_audits["A_DATA"]
    assert data_audit["status"] == GateStatus.PASS.value
    assert "17 verified historical events" in data_audit["requirement"]

def test_physical_iot_gate_fails_honestly():
    """Verify PHYSICAL IoT gate honestly evaluates to FAIL because on-slope deployment is pending."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    iot_audit = evaluation.dimension_audits["G_PHYSICAL_IOT"]
    assert iot_audit["status"] == GateStatus.FAIL.value
    assert "PHYSICAL_DEPLOYMENT_PENDING" in iot_audit["evidence"]
    assert iot_audit["blocker"] == "P0"

def test_weather_and_seismic_partial():
    """Verify weather and seismic evaluate to PARTIAL due to unconfigured government tokens."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    weather_audit = evaluation.dimension_audits["C_WEATHER"]
    seismic_audit = evaluation.dimension_audits["D_SEISMIC"]

    assert weather_audit["status"] == GateStatus.PARTIAL.value
    assert "AUTH_REQUIRED" in weather_audit["evidence"]

    assert seismic_audit["status"] == GateStatus.PARTIAL.value
    assert "AUTH_REQUIRED" in seismic_audit["evidence"]

def test_mandatory_and_external_gates():
    """Verify separation of internal mandatory pilot gates vs external dependencies."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    assert evaluation.mandatory_gates_pass is True
    assert evaluation.external_gates_pass is False

def test_readiness_scores_bounds():
    """Verify all readiness sub-scores are mathematically bounded in [0.0, 1.0]."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    for score_name in [
        "software_readiness", "data_readiness", "model_readiness",
        "field_readiness", "institutional_readiness", "operational_readiness"
    ]:
        val = getattr(evaluation, score_name)
        assert 0.0 <= val <= 1.0, f"Score {score_name}={val} out of bounds"

    assert evaluation.software_readiness == 1.0
    assert evaluation.data_readiness == 1.0
    assert evaluation.model_readiness == 0.85  # Account for limited historical training volume
    assert evaluation.field_readiness == 0.30  # Bench ready, physical on-slope absent
    assert evaluation.operational_readiness >= 0.90

def test_final_verdict_value():
    """Verify the final decision is strictly one of the two allowed values."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    allowed_verdicts = {
        "READY_FOR_CONTROLLED_SUPERVISED_PILOT",
        "NOT_READY_FOR_CONTROLLED_SUPERVISED_PILOT"
    }
    assert evaluation.final_verdict in allowed_verdicts
    assert evaluation.final_verdict == "READY_FOR_CONTROLLED_SUPERVISED_PILOT"

def test_blockers_categorization():
    """Verify blockers are categorized with P0, P1, and P2 severities and valid schemas."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    blockers = evaluation.blockers
    assert len(blockers) >= 4

    p0_list = [b for b in blockers if b.severity == BlockerSeverity.P0]
    p1_list = [b for b in blockers if b.severity == BlockerSeverity.P1]
    p2_list = [b for b in blockers if b.severity == BlockerSeverity.P2]

    assert len(p0_list) >= 2  # Physical IoT + IMD auth
    assert len(p1_list) >= 2  # Model volume + NCS auth
    assert len(p2_list) >= 1  # Copernicus raw raster download

    for b in blockers:
        assert b.id.startswith("BLK-")
        assert len(b.owner) > 3
        assert len(b.required_action) > 5
        assert len(b.acceptance_condition) > 5

def test_readiness_serialization():
    """Verify evaluation serializes cleanly to JSON dictionary."""
    evaluation = PILOT_MANAGER.evaluate_readiness()
    d = evaluation.to_dict()
    assert d["final_verdict"] == "READY_FOR_CONTROLLED_SUPERVISED_PILOT"
    assert d["mandatory_gates_pass"] is True
    assert d["external_gates_pass"] is False
    assert d["p0_blockers_count"] >= 2
    assert d["software_readiness"] == 1.0
