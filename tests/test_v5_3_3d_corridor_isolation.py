# -*- coding: utf-8 -*-
"""
tests/test_v5_3_3d_corridor_isolation.py
=========================================
PARVAT NETRA • PAHAD AI — Phase V5.3 3D Corridor Isolation Test Suite
"""

import pytest
from app import app
from engine.corridor_registry import SEED_CORRIDORS


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_v5_3_corridor_registry_km48_matches_3d_config(client):
    """Verify that corridor registry KM48 definition matches 3D config exactly."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200
    config_corridor = res.get_json()["canonical_corridor"]

    km48_seed = next((c for c in SEED_CORRIDORS if c.corridor_id == "CORR-NH10-SIKKIM-KM48"), None)
    assert km48_seed is not None

    assert config_corridor["corridor_id"] == km48_seed.corridor_id
    assert config_corridor["state"] == km48_seed.state
    assert config_corridor["district"] == km48_seed.district
    assert config_corridor["road"] == km48_seed.road
    assert config_corridor["target_coordinates"]["elevation_m"] == km48_seed.elevation
    assert config_corridor["target_coordinates"]["slope_deg"] == km48_seed.slope


def test_v5_3_km48_coordinate_precision(client):
    """Verify that KM48 target coordinates are strictly isolated to Pakyong, Sikkim."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200
    coords = res.get_json()["canonical_corridor"]["target_coordinates"]

    assert coords["latitude"] == 27.3300
    assert coords["longitude"] == 88.6100

    # Ensure coordinates lie strictly within Sikkim geographic bounding box
    # Sikkim: Lat 27.0° to 28.1° N, Lon 88.0° to 88.9° E
    assert 27.0 <= coords["latitude"] <= 28.1
    assert 88.0 <= coords["longitude"] <= 88.9
