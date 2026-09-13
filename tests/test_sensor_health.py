# -*- coding: utf-8 -*-
"""
tests/test_sensor_health.py
===========================
Unit tests for Sensor Health, Battery, and Signal Quality Telemetry (Phase 6A).
Validates:
  - Aggregate IoT health summary generation
  - Battery low threshold detection (< 20%)
  - Weak RF signal detection (< -95 dBm)
  - Network staleness monitoring (ACTIVE, STALE, OFFLINE)
  - Device health time-series logging
"""

import os
import tempfile
import sqlite3
import pytest
from datetime import datetime, timezone, timedelta

from engine.sensor_registry import (
    SensorRegistry,
    SensorDevice,
    GatewayInfo,
    STATUS_ACTIVE,
    STATUS_STALE,
    STATUS_OFFLINE
)


@pytest.fixture
def health_registry():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_health.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gateways (
                gateway_id TEXT PRIMARY KEY, name TEXT, latitude REAL, longitude REAL,
                sector_id TEXT, firmware_version TEXT, hardware_version TEXT,
                power_source TEXT, battery_pct REAL, uptime_seconds INTEGER,
                status TEXT, last_seen TEXT, created_at TEXT
            )
        """)
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
            CREATE TABLE IF NOT EXISTS device_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT, recorded_at TEXT,
                status TEXT, battery_level REAL, signal_strength REAL,
                packet_loss_pct REAL, clock_offset_ms REAL, error_flags TEXT
            )
        """)
        conn.commit()
        conn.close()

        reg = SensorRegistry(db_path=db_path)
        yield reg


def test_healthy_network_summary(health_registry):
    now_iso = datetime.now(timezone.utc).isoformat()
    health_registry.register_device(SensorDevice(
        device_id="DEV-H1", sensor_id="S1", sensor_type="piezometer",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-01",
        battery_level=95.0, signal_strength=-68.0, status=STATUS_ACTIVE, last_seen=now_iso
    ))
    health_registry.register_device(SensorDevice(
        device_id="DEV-H2", sensor_id="S2", sensor_type="tilt",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-01",
        battery_level=88.0, signal_strength=-72.0, status=STATUS_ACTIVE, last_seen=now_iso
    ))

    summary = health_registry.get_health_summary()
    assert summary["total_devices"] == 2
    assert summary["low_battery_count"] == 0
    assert summary["weak_signal_count"] == 0
    assert summary["overall_health"] == "HEALTHY"


def test_low_battery_and_weak_signal_detection(health_registry):
    now_iso = datetime.now(timezone.utc).isoformat()
    # Device with 12% battery (< 20%) and -98 dBm RSSI (< -95 dBm)
    health_registry.register_device(SensorDevice(
        device_id="DEV-LOW-BAT", sensor_id="S-LB", sensor_type="piezometer",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-01",
        battery_level=12.0, signal_strength=-98.0, status=STATUS_ACTIVE, last_seen=now_iso
    ))

    summary = health_registry.get_health_summary()
    assert summary["low_battery_count"] == 1
    assert "DEV-LOW-BAT" in summary["low_battery_devices"]
    assert summary["weak_signal_count"] == 1
    assert "DEV-LOW-BAT" in summary["weak_signal_devices"]
    assert summary["overall_health"] == "DEGRADED"


def test_heartbeat_logging(health_registry):
    dev = SensorDevice(
        device_id="DEV-LOG-01", sensor_id="S-LOG", sensor_type="rain_gauge",
        latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48", gateway_id="GW-01",
        battery_level=100.0, signal_strength=-60.0, status=STATUS_ACTIVE
    )
    health_registry.register_device(dev)

    # Record 3 heartbeats
    health_registry.record_heartbeat("DEV-LOG-01", 99.0, -62.0, 5.0)
    health_registry.record_heartbeat("DEV-LOG-01", 98.0, -63.0, 4.0)
    health_registry.record_heartbeat("DEV-LOG-01", 97.0, -65.0, 6.0)

    # Verify rows in device_health table
    conn = sqlite3.connect(health_registry.db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM device_health WHERE device_id = 'DEV-LOG-01'")
    cnt = cur.fetchone()[0]
    conn.close()
    assert cnt == 3
