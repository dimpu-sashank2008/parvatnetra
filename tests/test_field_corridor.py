# -*- coding: utf-8 -*-
"""
tests/test_field_corridor.py
============================
Unit & integration tests for Himalayan corridor registry, lifecycle transitions,
and geometric metadata.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.corridor_registry import (
    CorridorRegistry,
    CorridorDefinition,
    STATUS_CANDIDATE,
    STATUS_SURVEYED,
    STATUS_APPROVED,
    STATUS_DEPLOYMENT_PENDING,
    STATUS_DEPLOYED,
    STATUS_VALIDATED
)


@pytest.fixture
def temp_registry(tmp_path):
    db_file = str(tmp_path / "test_corridors.db")
    return CorridorRegistry(db_path=db_file)


def test_seed_corridors_loaded(temp_registry):
    corridors = temp_registry.list_corridors()
    assert len(corridors) == 5

    corr_ids = {c.corridor_id for c in corridors}
    assert "CORR-NH10-SIKKIM-KM48" in corr_ids
    assert "CORR-TUPUL-MANIPUR-RLY" in corr_ids
    assert "CORR-MELTHUM-MIZORAM" in corr_ids
    assert "CORR-NH717A-PEDONG-RISSI" in corr_ids
    assert "CORR-DIMA-HASAO-ASSAM" in corr_ids


def test_get_corridor_details(temp_registry):
    c = temp_registry.get_corridor("CORR-NH10-SIKKIM-KM48")
    assert c is not None
    assert c.state == "Sikkim"
    assert c.district == "Pakyong"
    assert c.slope == 42.5
    assert c.risk == "CRITICAL"
    assert len(c.sensor_sites) == 3
    assert len(c.gateway_sites) == 1
    assert c.geometry["type"] == "LineString"


def test_corridor_summary(temp_registry):
    summary = temp_registry.summary()
    assert summary["total_corridors"] == 5
    assert summary["validation_state"] == "FIELD_VALIDATION_READY"
    assert summary["total_sensor_sites"] >= 9
    assert summary["total_gateway_sites"] >= 5


def test_valid_status_transitions(temp_registry):
    # SURVEYED -> APPROVED
    updated = temp_registry.update_status("CORR-NH717A-PEDONG-RISSI", STATUS_APPROVED, "Geotechnical review completed")
    assert updated.status == STATUS_APPROVED

    # APPROVED -> DEPLOYMENT_PENDING
    updated2 = temp_registry.update_status("CORR-NH717A-PEDONG-RISSI", STATUS_DEPLOYMENT_PENDING, "Sensors allocated")
    assert updated2.status == STATUS_DEPLOYMENT_PENDING


def test_illegal_status_transition_raises_error(temp_registry):
    # Cannot jump directly from SURVEYED to VALIDATED
    with pytest.raises(ValueError) as excinfo:
        temp_registry.update_status("CORR-DIMA-HASAO-ASSAM", STATUS_VALIDATED)
    assert "Illegal corridor status transition" in str(excinfo.value)


def test_nonexistent_corridor_raises_keyerror(temp_registry):
    with pytest.raises(KeyError):
        temp_registry.update_status("CORR-NONEXISTENT", STATUS_APPROVED)
