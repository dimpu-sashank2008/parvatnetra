# -*- coding: utf-8 -*-
"""
tests/test_field_shadow.py
==========================
Unit tests for FIELD_SHADOW_ACTIVE operational runtime, hazard assessment,
and acoustic siren / public alert suppression safety rules.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.field_shadow_service import FieldShadowService


@pytest.fixture
def temp_shadow_service(tmp_path):
    db_file = str(tmp_path / "test_shadow.db")
    return FieldShadowService(db_path=db_file)


def test_field_shadow_evaluates_nominal_slope(temp_shadow_service):
    res = temp_shadow_service.evaluate_corridor_risk(
        corridor_id="CORR-NH10-SIKKIM-KM48",
        telemetry={
            "pore_pressure_kpa": 8.0,
            "rain_24h_mm": 12.0,
            "tilt_deflection_deg": 0.02
        }
    )
    assert res["operational_mode"] == "FIELD_SHADOW_ACTIVE"
    assert res["safety_gate"] == "PUBLIC_SIREN_DISPATCH_LOCKED"
    assert res["siren_disposition"] == "SUPPRESSED_FIELD_SHADOW_TRIAL"
    assert res["fos"] > 1.3
    assert res["alert_level"] in ["GREEN_NORMAL", "YELLOW_WATCH"]
    assert "NH-717A" in res["bypass_route"]


def test_field_shadow_evaluates_critical_slope_with_siren_suppression(temp_shadow_service):
    res = temp_shadow_service.evaluate_corridor_risk(
        corridor_id="CORR-NH10-SIKKIM-KM48",
        telemetry={
            "pore_pressure_kpa": 65.0,
            "rain_24h_mm": 140.0,
            "tilt_deflection_deg": 1.25
        }
    )
    # Hazard is critical
    assert res["alert_level"] == "RED_CRITICAL"
    assert res["fos"] < 1.05
    assert res["cri"] >= 75.0

    # NON-NEGOTIABLE SAFETY GATE: Siren MUST be suppressed in shadow mode
    assert res["siren_disposition"] == "SUPPRESSED_FIELD_SHADOW_TRIAL"
    assert res["safety_gate"] == "PUBLIC_SIREN_DISPATCH_LOCKED"


def test_shadow_audit_logs_persisted(temp_shadow_service):
    # Run two evaluations
    temp_shadow_service.evaluate_corridor_risk("CORR-TUPUL-MANIPUR-RLY")
    temp_shadow_service.evaluate_corridor_risk("CORR-MELTHUM-MIZORAM")

    logs = temp_shadow_service.get_shadow_audit_logs()
    assert len(logs) == 2
    corridor_ids = {l["corridor_id"] for l in logs}
    assert "CORR-TUPUL-MANIPUR-RLY" in corridor_ids
    assert "CORR-MELTHUM-MIZORAM" in corridor_ids

    # Query filtered by corridor
    tupul_logs = temp_shadow_service.get_shadow_audit_logs(corridor_id="CORR-TUPUL-MANIPUR-RLY")
    assert len(tupul_logs) == 1
    assert tupul_logs[0]["corridor_id"] == "CORR-TUPUL-MANIPUR-RLY"


def test_shadow_status_reporting(temp_shadow_service):
    temp_shadow_service.evaluate_corridor_risk("CORR-NH10-SIKKIM-KM48")
    status = temp_shadow_service.get_shadow_status()
    assert status["mode"] == "FIELD_SHADOW_ACTIVE"
    assert status["public_siren_dispatch"] == "SUPPRESSED"
    assert status["cap_alerts_dispatch"] == "SUPPRESSED"
    assert status["total_evaluations_logged"] == 1
