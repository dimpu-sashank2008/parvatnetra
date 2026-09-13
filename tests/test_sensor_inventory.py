# -*- coding: utf-8 -*-
"""
tests/test_sensor_inventory.py
==============================
Unit tests for physical equipment inventory, serial tracking, metrological
calibration assignment, and lifecycle state machines.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.sensor_inventory import (
    SensorInventory,
    PhysicalSensorAsset,
    STATUS_PLANNED,
    STATUS_DELIVERED,
    STATUS_INSTALLED,
    STATUS_CALIBRATED,
    STATUS_CONNECTED,
    STATUS_ACTIVE,
    STATUS_FAILED,
    STATUS_REMOVED
)


@pytest.fixture
def temp_inventory(tmp_path):
    db_file = str(tmp_path / "test_inventory.db")
    return SensorInventory(db_path=db_file)


def test_register_and_retrieve_asset(temp_inventory):
    asset = PhysicalSensorAsset(
        device_id="SN-PIEZ-TEST-01",
        sensor_id="PIEZ-01",
        sensor_type="piezometer",
        serial_number="VW-2026-9901",
        manufacturer="Geokon Inc.",
        model="4500S-High-Pressure",
        firmware_version="v2.1.0",
        calibration_certificate=None,
        installation_location={"corridor_id": "CORR-NH10-SIKKIM-KM48", "depth_m": 15.0},
        status=STATUS_PLANNED
    )
    temp_inventory.register_asset(asset)

    retrieved = temp_inventory.get_asset("SN-PIEZ-TEST-01")
    assert retrieved is not None
    assert retrieved.serial_number == "VW-2026-9901"
    assert retrieved.manufacturer == "Geokon Inc."
    assert retrieved.status == STATUS_PLANNED


def test_asset_lifecycle_progression(temp_inventory):
    asset = PhysicalSensorAsset(
        device_id="SN-TILT-TEST-02",
        sensor_id="TILT-02",
        sensor_type="tilt",
        serial_number="TL-2026-4412",
        manufacturer="RST Instruments",
        model="MEMS-Tilt-Dual",
        firmware_version="v1.4.2",
        calibration_certificate=None,
        installation_location={"corridor_id": "CORR-TUPUL-MANIPUR-RLY"},
        status=STATUS_PLANNED
    )
    temp_inventory.register_asset(asset)

    # PLANNED -> DELIVERED
    temp_inventory.update_status("SN-TILT-TEST-02", STATUS_DELIVERED, technician="Tech Roy")
    assert temp_inventory.get_asset("SN-TILT-TEST-02").status == STATUS_DELIVERED

    # DELIVERED -> INSTALLED
    temp_inventory.update_status("SN-TILT-TEST-02", STATUS_INSTALLED, technician="Tech Roy")
    assert temp_inventory.get_asset("SN-TILT-TEST-02").status == STATUS_INSTALLED

    # INSTALLED -> CALIBRATED
    temp_inventory.assign_calibration("SN-TILT-TEST-02", "CERT-ISO17025-2026-004", "Metrology Lead")
    temp_inventory.update_status("SN-TILT-TEST-02", STATUS_CALIBRATED, technician="Metrology Lead")
    assert temp_inventory.get_asset("SN-TILT-TEST-02").status == STATUS_CALIBRATED
    assert temp_inventory.get_asset("SN-TILT-TEST-02").calibration_certificate == "CERT-ISO17025-2026-004"

    # CALIBRATED -> CONNECTED
    temp_inventory.update_status("SN-TILT-TEST-02", STATUS_CONNECTED, technician="Comms Tech")
    assert temp_inventory.get_asset("SN-TILT-TEST-02").status == STATUS_CONNECTED

    # CONNECTED -> ACTIVE
    temp_inventory.update_status("SN-TILT-TEST-02", STATUS_ACTIVE, technician="Lead Engineer")
    assert temp_inventory.get_asset("SN-TILT-TEST-02").status == STATUS_ACTIVE


def test_illegal_asset_lifecycle_transition(temp_inventory):
    asset = PhysicalSensorAsset(
        device_id="SN-RAIN-TEST-03",
        sensor_id="RAIN-03",
        sensor_type="rain_gauge",
        serial_number="RG-2026-1188",
        manufacturer="Davis Instruments",
        model="AeroCone-TB",
        firmware_version="v1.0.0",
        calibration_certificate=None,
        installation_location={"corridor_id": "CORR-MELTHUM-MIZORAM"},
        status=STATUS_PLANNED
    )
    temp_inventory.register_asset(asset)

    # Cannot jump directly from PLANNED to ACTIVE
    with pytest.raises(ValueError) as excinfo:
        temp_inventory.update_status("SN-RAIN-TEST-03", STATUS_ACTIVE)
    assert "Illegal asset transition" in str(excinfo.value)


def test_inventory_summary_physical_deployment_state(temp_inventory):
    # Empty inventory
    summary = temp_inventory.summary()
    assert summary["total_assets"] == 0
    assert summary["physical_deployment_state"] == "PHYSICAL_DEPLOYMENT_PENDING"

    # Add planned asset
    asset = PhysicalSensorAsset(
        device_id="SN-TEST-04",
        sensor_id="TEST-04",
        sensor_type="soil_moisture",
        serial_number="SM-2026-0001",
        manufacturer="Campbell Scientific",
        model="CS655-TDR",
        firmware_version="v1.2.0",
        calibration_certificate=None,
        installation_location={"corridor_id": "CORR-NH717A-PEDONG-RISSI"},
        status=STATUS_PLANNED
    )
    temp_inventory.register_asset(asset)
    summary2 = temp_inventory.summary()
    assert summary2["total_assets"] == 1
    assert summary2["active_count"] == 0
    assert summary2["physical_deployment_state"] == "PHYSICAL_DEPLOYMENT_PENDING"
