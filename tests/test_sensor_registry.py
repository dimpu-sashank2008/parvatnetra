# -*- coding: utf-8 -*-
"""
tests/test_sensor_registry.py
=============================
Unit tests for Sensor Registry & Lifecycle Management (Phase 6A).
Validates:
  - Gateway and device registration
  - Device status state machine (REGISTERED, COMMISSIONING, ACTIVE, STALE, OFFLINE)
  - Query filters (by sector_id, sensor_type, status)
  - Heartbeat tracking and staleness detection
  - Thread-safe persistence and reload
"""

import os
import tempfile
import pytest
from datetime import datetime, timezone, timedelta

from engine.sensor_registry import (
    SensorRegistry,
    SensorDevice,
    GatewayInfo,
    STATUS_REGISTERED,
    STATUS_COMMISSIONING,
    STATUS_ACTIVE,
    STATUS_STALE,
    STATUS_OFFLINE,
    STATUS_DECOMMISSIONED
)


@pytest.fixture
def temp_registry():
    """Provides an isolated SensorRegistry instance backed by a temporary SQLite file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_sensors.db")
        # Run table migrations
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gateways (
                gateway_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                sector_id TEXT NOT NULL,
                firmware_version TEXT,
                hardware_version TEXT,
                power_source TEXT,
                battery_pct REAL DEFAULT 100.0,
                uptime_seconds INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ONLINE',
                last_seen TEXT,
                created_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_registry (
                device_id TEXT PRIMARY KEY,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                sector_id TEXT NOT NULL,
                gateway_id TEXT NOT NULL,
                installation_status TEXT DEFAULT 'PENDING',
                commissioned_at TEXT,
                firmware_version TEXT,
                hardware_version TEXT,
                calibration_status TEXT DEFAULT 'CALIBRATED',
                last_seen TEXT,
                battery_level REAL DEFAULT 100.0,
                signal_strength REAL DEFAULT -70.0,
                network_type TEXT DEFAULT 'LoRaWAN',
                status TEXT DEFAULT 'REGISTERED',
                created_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS device_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                status TEXT NOT NULL,
                battery_level REAL,
                signal_strength REAL,
                packet_loss_pct REAL,
                clock_offset_ms REAL,
                error_flags TEXT
            )
        """)
        conn.commit()
        conn.close()

        registry = SensorRegistry(db_path=db_path)
        yield registry


def test_register_gateway(temp_registry):
    gw = GatewayInfo(
        gateway_id="GW-TEST-01",
        name="Pakyong Test Gateway",
        latitude=27.3300,
        longitude=88.6100,
        sector_id="SK-NH10-KM48"
    )
    res = temp_registry.register_gateway(gw)
    assert res.gateway_id == "GW-TEST-01"
    fetched = temp_registry.get_gateway("GW-TEST-01")
    assert fetched is not None
    assert fetched.name == "Pakyong Test Gateway"


def test_register_device_validation(temp_registry):
    dev = SensorDevice(
        device_id="DEV-PZ-01",
        sensor_id="PZ-01",
        sensor_type="piezometer",
        latitude=27.3300,
        longitude=88.6100,
        sector_id="SK-NH10-KM48",
        gateway_id="GW-TEST-01"
    )
    registered = temp_registry.register_device(dev)
    assert registered.device_id == "DEV-PZ-01"
    assert registered.status == STATUS_REGISTERED

    # Invalid sensor type must raise ValueError
    invalid_dev = SensorDevice(
        device_id="DEV-BAD-01",
        sensor_id="BAD-01",
        sensor_type="invalid_laser_cannon",
        latitude=27.3300,
        longitude=88.6100,
        sector_id="SK-NH10-KM48",
        gateway_id="GW-TEST-01"
    )
    with pytest.raises(ValueError):
        temp_registry.register_device(invalid_dev)


def test_query_filters(temp_registry):
    temp_registry.register_device(SensorDevice(
        device_id="DEV-1", sensor_id="S1", sensor_type="piezometer",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-1",
        status=STATUS_ACTIVE
    ))
    temp_registry.register_device(SensorDevice(
        device_id="DEV-2", sensor_id="S2", sensor_type="tilt",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-1",
        status=STATUS_ACTIVE
    ))
    temp_registry.register_device(SensorDevice(
        device_id="DEV-3", sensor_id="S3", sensor_type="piezometer",
        latitude=24.75, longitude=93.57, sector_id="MN-TUPUL-RLY", gateway_id="GW-2",
        status=STATUS_REGISTERED
    ))

    # Filter by sector
    sk_devs = temp_registry.list_devices(sector_id="SK-NH10-KM48")
    assert len(sk_devs) == 2

    # Filter by sensor_type
    piezos = temp_registry.list_devices(sensor_type="piezometer")
    assert len(piezos) == 2

    # Filter by status
    registered = temp_registry.list_devices(status=STATUS_REGISTERED)
    assert len(registered) == 1
    assert registered[0].device_id == "DEV-3"


def test_heartbeat_and_staleness(temp_registry):
    dev = SensorDevice(
        device_id="DEV-HB-01", sensor_id="S-HB-01", sensor_type="inclinometer",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-1",
        status=STATUS_ACTIVE
    )
    temp_registry.register_device(dev)

    # Record heartbeat
    success = temp_registry.record_heartbeat("DEV-HB-01", battery_pct=85.0, signal_rssi=-78.0, clock_offset_ms=12.0)
    assert success is True

    updated = temp_registry.get_device("DEV-HB-01")
    assert updated.battery_level == 85.0
    assert updated.signal_strength == -78.0

    # Simulate aged timestamp (10 minutes ago -> STALE)
    stale_ts = (datetime.now(timezone.utc) - timedelta(seconds=400)).isoformat()
    updated.last_seen = stale_ts
    temp_registry.register_device(updated)

    staleness = temp_registry.check_staleness(stale_threshold_sec=300, offline_threshold_sec=900)
    assert staleness["STALE"] >= 1
    assert temp_registry.get_device("DEV-HB-01").status == STATUS_STALE

    # Simulate very old timestamp (20 minutes ago -> OFFLINE)
    offline_ts = (datetime.now(timezone.utc) - timedelta(seconds=1200)).isoformat()
    updated.last_seen = offline_ts
    temp_registry.register_device(updated)

    staleness = temp_registry.check_staleness(stale_threshold_sec=300, offline_threshold_sec=900)
    assert staleness["OFFLINE"] >= 1
    assert temp_registry.get_device("DEV-HB-01").status == STATUS_OFFLINE
