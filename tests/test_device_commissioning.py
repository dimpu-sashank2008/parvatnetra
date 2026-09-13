# -*- coding: utf-8 -*-
"""
tests/test_device_commissioning.py
==================================
Unit tests for 8-Stage Device Field Commissioning State Machine (Phase 6A).
Flow: REGISTER -> INSTALL -> CALIBRATE -> CONNECT -> HEARTBEAT -> TELEMETRY -> VALIDATE -> ACCEPT
Validates:
  - Strict step-by-step prerequisite progression
  - Prevention of out-of-order stage skipping
  - Status transition: REGISTERED -> COMMISSIONING -> ACTIVE
  - Setting of authoritative commissioned_at timestamp upon acceptance
"""

import os
import tempfile
import sqlite3
import pytest

from engine.sensor_registry import (
    SensorRegistry,
    SensorDevice,
    STATUS_REGISTERED,
    STATUS_COMMISSIONING,
    STATUS_ACTIVE,
    COMMISSIONING_STAGES
)


@pytest.fixture
def comm_registry():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_comm.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_registry (
                device_id TEXT PRIMARY KEY, sensor_id TEXT, sensor_type TEXT,
                latitude REAL, longitude REAL, sector_id TEXT, gateway_id TEXT,
                installation_status TEXT, commissioned_at TEXT, firmware_version TEXT,
                hardware_version TEXT, calibration_status TEXT, last_seen TEXT,
                battery_level REAL, signal_strength REAL, network_type TEXT,
                status TEXT, created_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gateways (
                gateway_id TEXT PRIMARY KEY, name TEXT, latitude REAL, longitude REAL,
                sector_id TEXT, firmware_version TEXT, hardware_version TEXT,
                power_source TEXT, battery_pct REAL, uptime_seconds INTEGER,
                status TEXT, last_seen TEXT, created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

        reg = SensorRegistry(db_path=db_path)
        yield reg


def test_full_commissioning_happy_path(comm_registry):
    dev = SensorDevice(
        device_id="DEV-FIELD-01",
        sensor_id="SN-01",
        sensor_type="piezometer",
        latitude=27.33,
        longitude=88.61,
        sector_id="SK-NH10-KM48",
        gateway_id="GW-01",
        status=STATUS_REGISTERED
    )
    comm_registry.register_device(dev)

    # Initial state
    assert dev.status == STATUS_REGISTERED
    assert dev.commissioned_at is None

    # Step through stages
    for stage in COMMISSIONING_STAGES:
        res = comm_registry.advance_commissioning("DEV-FIELD-01", stage)
        assert res["status"] == "SUCCESS"
        assert res["stage_completed"] == stage
        if stage == "ACCEPT":
            assert res["current_status"] == STATUS_ACTIVE
        else:
            assert res["current_status"] == STATUS_COMMISSIONING

    # Final verification
    final_dev = comm_registry.get_device("DEV-FIELD-01")
    assert final_dev.status == STATUS_ACTIVE
    assert final_dev.commissioned_at is not None
    assert len(final_dev.commissioning_progress) == 8


def test_out_of_order_stage_rejection(comm_registry):
    dev = SensorDevice(
        device_id="DEV-SKIP-01",
        sensor_id="SN-SKIP",
        sensor_type="inclinometer",
        latitude=27.33,
        longitude=88.61,
        sector_id="SK-NH10-KM48",
        gateway_id="GW-01",
        status=STATUS_REGISTERED
    )
    comm_registry.register_device(dev)

    # First stage is REGISTER
    comm_registry.advance_commissioning("DEV-SKIP-01", "REGISTER")

    # Try to jump straight to ACCEPT without INSTALL, CALIBRATE, etc.
    res = comm_registry.advance_commissioning("DEV-SKIP-01", "ACCEPT")
    assert res["status"] == "REJECTED_PREREQUISITE_MISSING"
    assert "INSTALL" in res["message"]

    # Status must not be ACTIVE
    dev_after = comm_registry.get_device("DEV-SKIP-01")
    assert dev_after.status != STATUS_ACTIVE


def test_invalid_stage_name(comm_registry):
    dev = SensorDevice(
        device_id="DEV-INV-01", sensor_id="SN-INV", sensor_type="tilt",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-01"
    )
    comm_registry.register_device(dev)

    res = comm_registry.advance_commissioning("DEV-INV-01", "NON_EXISTENT_STAGE")
    assert res["status"] == "ERROR"
    assert "Invalid stage" in res["message"]
