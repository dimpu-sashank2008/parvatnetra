# -*- coding: utf-8 -*-
"""
tests/test_v5_3_gods_eye.py
===========================
PARVAT NETRA • PAHAD AI — Phase V5.3 God's Eye 3D GIS Configuration Test Suite
"""

import pytest
import os
import json
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_v5_3_gods_eye_config_endpoint_success(client):
    """Verify that GET /api/gods-eye/config returns 200 with phase V5.3 schema."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200
    data = res.get_json()

    assert data["status"] == "SUCCESS"
    assert data["phase"] == "V5.3"
    assert "provider_status" in data
    assert "active_provider" in data
    assert "provider_badge" in data
    assert "canonical_corridor" in data
    assert "flight_hierarchy" in data
    assert "telemetry_state" in data
    assert data["provenance"] == "[3D GIS / GEOSPATIAL PRESENTATION]"


def test_v5_3_canonical_corridor_km48_metadata(client):
    """Verify that canonical corridor is CORR-NH10-SIKKIM-KM48 with precise coordinates."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200
    corridor = res.get_json()["canonical_corridor"]

    assert corridor["corridor_id"] == "CORR-NH10-SIKKIM-KM48"
    assert corridor["state"] == "Sikkim"
    assert corridor["district"] == "Pakyong"
    assert corridor["road"] == "NH-10"
    assert corridor["kilometre_marker"] == "Km 48.200"
    assert corridor["target_coordinates"]["latitude"] == 27.3300
    assert corridor["target_coordinates"]["longitude"] == 88.6100
    assert corridor["target_coordinates"]["elevation_m"] == 680.0
    assert corridor["target_coordinates"]["slope_deg"] == 42.5
    assert corridor["fos"] == 1.04
    assert corridor["cri_score"] == 78.4


def test_v5_3_hierarchical_flight_steps(client):
    """Verify that hierarchical flight contains 5 sequential checkpoints from India to KM48."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200
    steps = res.get_json()["flight_hierarchy"]

    assert len(steps) == 5
    step_labels = [s["label"] for s in steps]
    assert step_labels == ["INDIA", "NER", "SIKKIM", "NH-10", "KM48"]

    # Verify descending heights
    heights = [s["height_m"] for s in steps]
    assert heights == [4500000, 1200000, 250000, 25000, 3500]


def test_v5_3_telemetry_state_factual_integrity(client):
    """Verify that telemetry state truthfully reports 0 physical sensors installed."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200
    state = res.get_json()["telemetry_state"]

    assert state["physical_sensors_installed"] == 0
    assert state["live_telemetry_records"] == 0
    assert state["sensor_provenance"] == "[PLANNED / BENCH TESTED / PHYSICAL TELEMETRY PENDING]"
    assert state["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"
