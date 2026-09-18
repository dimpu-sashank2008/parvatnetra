# -*- coding: utf-8 -*-
"""
tests/test_official_sitrep.py
=============================
Verifies official NDMA disaster situation report memo generation, 2-of-3 corroboration breakdown,
evacuation directives, asset mobilization, and REST API contract.
"""

import pytest
import json
from app import app as flask_app
from services.ai_sitrep import AI_SITREP_SERVICE

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c

def test_service_official_sitrep_glof():
    memo = AI_SITREP_SERVICE.generate_official_ndma_sitrep("glof")
    assert memo["status"] == "success"
    assert "NDMA/NER/EOC/2026/SITREP" in memo["memo_reference"]
    assert "LEVEL-3" in memo["disaster_level"]
    assert memo["geography"]["state"] == "Sikkim"
    assert "NH-717A" in memo["geography"]["designated_detour"]
    assert "signals_confirmed" in memo["triangulation_confirmation"]
    assert len(memo["emergency_directives"]) >= 4

def test_service_official_sitrep_remal():
    memo = AI_SITREP_SERVICE.generate_official_ndma_sitrep("remal")
    assert memo["status"] == "success"
    assert memo["geography"]["state"] == "Mizoram"
    assert "Cyclone Remal" in memo["incident_name"]

def test_api_sitrep_official_memo_endpoint(client):
    res = client.get("/api/sitrep/official-memo?scenario=glof")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert "multi_physics_evidence" in data
    assert "signal_1_radar" in data["multi_physics_evidence"]
    assert "signal_2_geotechnical" in data["multi_physics_evidence"]
    assert "signal_3_insar" in data["multi_physics_evidence"]
    assert "signal_4_edge_cv" in data["multi_physics_evidence"]

def test_api_hardware_bom_endpoint(client):
    res = client.get("/api/hardware/bom")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["total_cost_inr"] < 25000
    assert data["cost_savings_pct"] > 90.0
