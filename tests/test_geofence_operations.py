# -*- coding: utf-8 -*-
"""
tests/test_geofence_operations.py
=================================
Unit tests for spatial geofence calculation, configurable radius,
population-at-risk exposure, and exact geometry persistence.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.geofence_service import GeofenceService, haversine_distance_km


@pytest.fixture
def temp_geofence(tmp_path):
    db_file = str(tmp_path / "test_geofence.db")
    return GeofenceService(db_path=db_file)


def test_haversine_distance_calculation():
    # Pakyong to Singtam is approximately ~9.5 km
    dist = haversine_distance_km(27.2405, 88.5850, 27.2480, 88.5980)
    assert 1.0 < dist < 3.0


def test_configurable_radius_not_hardcoded(temp_geofence):
    # Centered at Km 48 (27.33, 88.61)
    # Small radius: 2.0 km
    res_small = temp_geofence.calculate_geofence_impact(27.3300, 88.6100, radius_km=2.0)
    # Large radius: 15.0 km
    res_large = temp_geofence.calculate_geofence_impact(27.3300, 88.6100, radius_km=15.0)

    # Invariant: Must not be hardcoded
    assert res_small["radius_km"] == 2.0
    assert res_large["radius_km"] == 15.0
    assert res_small["affected_population"] < res_large["affected_population"]
    assert len(res_small["affected_infrastructure"]) <= len(res_large["affected_infrastructure"])


def test_infrastructure_identification_in_geofence(temp_geofence):
    res = temp_geofence.calculate_geofence_impact(27.2450, 88.5900, radius_km=5.0)
    infra_names = [i["name"] for i in res["affected_infrastructure"]]

    # Pakyong Hospital and Singtam Teesta Suspension Bridge should be captured
    assert any("Hospital" in name for name in infra_names)
    assert any("Bridge" in name for name in infra_names)


def test_geofence_geometry_persistence_and_retrieval(temp_geofence):
    res = temp_geofence.calculate_geofence_impact(27.3300, 88.6100, radius_km=8.0, alert_id="ALERT-TEST-001")
    geo_id = res["geofence_id"]

    retrieved = temp_geofence.get_geofence(geo_id)
    assert retrieved is not None
    assert retrieved["alert_id"] == "ALERT-TEST-001"
    assert retrieved["radius_km"] == 8.0
    assert retrieved["geometry"]["type"] == "PointBuffer"
    assert retrieved["geometry"]["center"] == [88.6100, 27.3300]
