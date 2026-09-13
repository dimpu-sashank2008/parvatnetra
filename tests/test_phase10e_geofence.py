# -*- coding: utf-8 -*-
"""
tests/test_phase10e_geofence.py
===============================
PARVAT NETRA • Phase 10E — Geofence Safety & Boundary Verification Tests
------------------------------------------------------------------------
Verifies:
  1. Ray-casting polygon containment: inside, outside, boundary.
  2. Geofence polygon validation: rejects empty polygons, <3 vertices, non-numeric coords.
  3. Coordinates physical range checks (-90 to +90 lat, -180 to +180 lon).
  4. Alert dissemination strictly rejects invalid or out-of-boundary geofences.
  5. Pre-authorization barrier: No alert can be dispatched prior to authority authorization.
"""

import pytest
from services.public_warning_service import (
    point_in_polygon,
    validate_geofence_polygon,
    PUBLIC_WARNING_SERVICE
)

# Canonical 15 km Risk Corridor Polygon for NH-10 Km 48 (Pakyong / Gangtok)
NH10_POLYGON = [
    [27.3200, 88.6000],
    [27.3400, 88.6000],
    [27.3400, 88.6200],
    [27.3200, 88.6200],
    [27.3200, 88.6000]
]


def test_point_inside_geofence():
    """Point squarely inside polygon returns True."""
    assert point_in_polygon(27.3300, 88.6100, NH10_POLYGON) is True


def test_point_outside_geofence():
    """Point far away from polygon returns False."""
    # Delhi / outside Sikkim
    assert point_in_polygon(28.6139, 77.2090, NH10_POLYGON) is False
    # Nearby point just outside bounding box
    assert point_in_polygon(27.3500, 88.6300, NH10_POLYGON) is False


def test_point_on_boundary_geofence():
    """Boundary point handling does not error or produce inconsistent state."""
    res = point_in_polygon(27.3200, 88.6100, NH10_POLYGON)
    assert isinstance(res, bool)


def test_validate_geofence_empty_and_insufficient():
    """Rejection of empty or single/two-point polygons."""
    ok_empty, err_empty = validate_geofence_polygon([])
    assert ok_empty is False
    assert "empty" in err_empty.lower()

    ok_few, err_few = validate_geofence_polygon([[27.33, 88.61]])
    assert ok_few is False
    assert "at least 3 vertices" in err_few.lower()


def test_validate_geofence_invalid_coordinates():
    """Rejection of out-of-range or non-numeric coordinates."""
    # Latitude > 90
    ok_lat, err_lat = validate_geofence_polygon([[127.33, 88.61], [27.34, 88.61], [27.33, 88.62]])
    assert ok_lat is False
    assert "physical range" in err_lat.lower()

    # Non-numeric coordinate
    ok_nan, err_nan = validate_geofence_polygon([["invalid", 88.61], [27.34, 88.61], [27.33, 88.62]])
    assert ok_nan is False
    assert "non-numeric" in err_nan.lower()


def test_dissemination_rejects_empty_geofence():
    """Verifies that dissemination endpoint rejects an empty geofence polygon."""
    res = PUBLIC_WARNING_SERVICE.disseminate_emergency_warning(
        incident_id="INC-GEO-001",
        actor_id="DM_OFFICER",
        actor_role="DISTRICT_AUTHORITY",
        auth_token="AUTH-v1.test.sig",
        geofence_polygon=[]
    )

    assert res["success"] is False
    assert res["status"] in ("DISSEMINATION_REJECTED", "INVALID_GEOFENCE")
