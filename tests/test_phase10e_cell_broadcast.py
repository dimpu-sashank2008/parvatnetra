# -*- coding: utf-8 -*-
"""
tests/test_phase10e_cell_broadcast.py
=====================================
PARVAT NETRA • Phase 10E — Cell Broadcast Adapter Tests (3GPP ATIS PWS)
-----------------------------------------------------------------------
Verifies:
  1. Provider-neutral Cell Broadcast adapter input/output schemas.
  2. Input: incident_id, geofence, severity, urgency, language, message, expiry.
  3. Output: provider_status, broadcast_status, correlation_id.
  4. Core Safety Invariant: CELL_BROADCAST = TEST/DRY_RUN (Zero live RF emissions).
  5. Validation of geofence polygon before cell site mapping.
  6. Rejection of invalid / empty / open polygons.
"""

import pytest
from services.public_warning_service import (
    CellBroadcastAdapter,
    CHANNEL_CELL_BROADCAST
)

CANONICAL_GEOFENCE = [
    [27.3300, 88.6100],
    [27.3350, 88.6100],
    [27.3350, 88.6150],
    [27.3300, 88.6150],
    [27.3300, 88.6100]
]


def test_cell_broadcast_output_schema():
    """Verifies that Cell Broadcast adapter produces all mandatory fields."""
    adapter = CellBroadcastAdapter()
    result = adapter.broadcast(
        incident_id="INC-CB-001",
        geofence_polygon=CANONICAL_GEOFENCE,
        severity="Severe",
        urgency="Immediate",
        language="en",
        message="PAHAD AI Landslide Evacuation Warning",
        expiry_iso="2026-12-31T23:59:59Z"
    )

    assert result["channel"] == CHANNEL_CELL_BROADCAST
    assert result["provider_status"] == "TEST/DRY_RUN"
    assert result["broadcast_status"] == "SIMULATED"
    assert result["correlation_id"].startswith("CB-")
    assert result["dry_run"] is True
    assert result["rf_actuation"] is False
    assert result["provenance"] == "[CELL_BROADCAST_DRY_RUN]"
    assert result["polygon_vertices"] == 5
    assert result["estimated_cell_sites"] > 0


def test_cell_broadcast_rejects_empty_geofence():
    """Verifies that empty geofence polygon is rejected."""
    adapter = CellBroadcastAdapter()
    result = adapter.broadcast(
        incident_id="INC-CB-002",
        geofence_polygon=[],
        severity="Severe",
        urgency="Immediate",
        language="en",
        message="Test alert",
        expiry_iso="2026-12-31T23:59:59Z"
    )

    assert result["broadcast_status"] == "FAILED_INVALID_GEOFENCE"
    assert result["correlation_id"] is None
    assert "empty" in result["error"].lower()


def test_cell_broadcast_rejects_insufficient_vertices():
    """Verifies that polygons with fewer than 3 vertices are rejected."""
    adapter = CellBroadcastAdapter()
    result = adapter.broadcast(
        incident_id="INC-CB-003",
        geofence_polygon=[[27.33, 88.61], [27.34, 88.61]],
        severity="Moderate",
        urgency="Future",
        language="en",
        message="Test alert",
        expiry_iso="2026-12-31T23:59:59Z"
    )

    assert result["broadcast_status"] == "FAILED_INVALID_GEOFENCE"
    assert "at least 3 vertices" in result["error"].lower()


def test_cell_broadcast_safety_flag():
    """Asserts that adapter default dry_run is True and cannot emit RF silently."""
    adapter = CellBroadcastAdapter()
    assert adapter.dry_run is True
