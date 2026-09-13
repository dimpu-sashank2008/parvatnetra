# -*- coding: utf-8 -*-
"""
tests/test_phase8_eoc.py
========================
Tests for Checkpoint 8-01 & 8-02:
EOC Operating Model, Command Dashboard, Roles, and Lifecycle Foundations.
"""

import os
import pytest
from engine.eoc_incident_manager import (
    EOC_INCIDENT_MANAGER,
    STATE_NEW,
    STATE_TRIAGED,
    STATE_AUTHORIZED,
    STATE_RESOLVED,
)
from services.eoc_service import EOC_SERVICE


def test_eoc_operating_roles():
    """Verify that all 6 required roles and documentation exist."""
    assert os.path.exists("docs/PHASE8_EOC_OPERATING_MODEL.md")
    with open("docs/PHASE8_EOC_OPERATING_MODEL.md", "r", encoding="utf-8") as f:
        content = f.read()
    required_roles = ["PUBLIC", "FIELD_OPERATOR", "EOC_OPERATOR", "DISTRICT_AUTHORITY", "STATE_AUTHORITY", "ADMIN"]
    for role in required_roles:
        assert role in content, f"Role {role} missing from operating model document"


def test_eoc_command_brief_generation():
    """Verify EOC executive command brief aggregates telemetry, model, and authority status."""
    brief = EOC_SERVICE.generate_command_brief()
    assert isinstance(brief, dict)
    assert "active_incident" in brief
    if brief.get("active_incident"):
        assert "cri" in brief
        assert "fos" in brief
        assert "ml_probability" in brief
        assert "signal_agreement" in brief
        assert "dispatch_status" in brief


def test_eoc_incident_queue_prioritization():
    """Verify prioritized incident queue sorting logic."""
    inc1 = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=92.0,
        risk_band="CRITICAL",
        model_probability=0.88,
        FoS=0.91,
        rainfall=210.0,
        population_at_risk=8000,
        road_criticality=98.0
    )
    inc2 = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=45.0,
        risk_band="MEDIUM",
        model_probability=0.35,
        FoS=1.28,
        rainfall=40.0,
        population_at_risk=1200,
        road_criticality=60.0
    )

    prio1 = EOC_INCIDENT_MANAGER.calculate_priority(inc1)
    prio2 = EOC_INCIDENT_MANAGER.calculate_priority(inc2)
    assert prio1 > prio2, f"Critical incident priority {prio1} should exceed medium incident {prio2}"

    incidents = EOC_INCIDENT_MANAGER.list_incidents(limit=10)
    assert len(incidents) >= 2
    # Verify descending sort
    assert incidents[0]["priority_score"] >= incidents[1]["priority_score"]


def test_eoc_display_projection():
    """Verify display projection fields (Checkpoint 8-04)."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=80.0,
        risk_band="HIGH",
        model_probability=0.78,
        FoS=1.04,
        rainfall=165.0
    )
    d = inc.to_dict()
    assert "display_projection" in d
    proj = d["display_projection"]
    assert "ai_prediction" in proj
    assert "signal_agreement" in proj
    assert "data_quality" in proj
    assert "provenance" in proj
    assert "authority_state" in proj


def test_eoc_rest_api_endpoints():
    """Verify Flask REST endpoints under /api/eoc."""
    from app import app
    client = app.test_client()

    # 1. GET /api/eoc/incidents
    res = client.get("/api/eoc/incidents")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "incidents" in data

    # 2. GET /api/eoc/command-brief
    brief_res = client.get("/api/eoc/command-brief")
    assert brief_res.status_code == 200
    brief_data = brief_res.get_json()
    assert brief_data["status"] == "SUCCESS"

    # 3. POST /api/eoc/drill/e2e
    e2e_res = client.post("/api/eoc/drill/e2e")
    assert e2e_res.status_code == 200
    e2e_data = e2e_res.get_json()
    assert e2e_data["status"] == "COMPLETED_SUCCESSFULLY"

    # 4. POST /api/eoc/drill/failure
    fail_res = client.post("/api/eoc/drill/failure")
    assert fail_res.status_code == 200
    fail_data = fail_res.get_json()
    assert fail_data["all_scenarios_failed_closed"] is True

