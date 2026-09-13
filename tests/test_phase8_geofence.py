# -*- coding: utf-8 -*-
"""
tests/test_phase8_geofence.py
=============================
Tests for Checkpoint 8-06:
15 km Geodesic Public Safety Geofence, Affected Population Calculation,
and Zero Notification Before Authorization.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_NEW, STATE_AUTHORIZED
from services.eoc_service import EOC_SERVICE, haversine_distance_km


def test_haversine_calculation():
    """Verify accuracy of great-circle geodesic calculation."""
    # Distance between Gangtok (27.3389, 88.6065) and Singtam (27.2350, 88.4980) ~ 15.8 km
    dist = haversine_distance_km(27.3389, 88.6065, 27.2350, 88.4980)
    assert 14.0 <= dist <= 17.0


def test_15km_geofence_intersection():
    """Verify 15 km geofence correctly calculates affected settlements, roads, and polygon."""
    center_lat, center_lon = 27.3300, 88.6100  # NH-10 KM 48
    geo = EOC_SERVICE.calculate_15km_geofence(center_lat, center_lon, radius_km=15.0)

    assert geo["radius_km"] == 15.0
    assert geo["affected_population"] > 0
    assert len(geo["affected_villages"]) >= 2
    assert len(geo["affected_roads"]) >= 2
    # Verify polygon has at least 16 vertices
    assert len(geo["geofence_polygon"]) >= 16
    # Verify polygon starts and ends at same coordinate (closed ring)
    assert geo["geofence_polygon"][0] == geo["geofence_polygon"][-1]


def test_zero_notification_before_authorization():
    """Verify that no notifications can be dispatched when incident is in NEW or unauthorized state."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=82.0,
        risk_band="CRITICAL",
        model_probability=0.86,
        FoS=0.95,
        rainfall=185.0
    )
    assert inc.incident_status == STATE_NEW

    # Attempt dispatch without authorization
    disp_res = EOC_SERVICE.dispatch_incident_notifications(
        incident_id=inc.incident_id,
        authorization_token="NONE",
        test_mode=True
    )
    assert disp_res.get("status") == "BLOCKED"
    assert disp_res.get("authorized") is False
    assert "must be in AUTHORIZED state" in disp_res.get("error", "")
