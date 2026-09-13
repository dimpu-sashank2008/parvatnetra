# -*- coding: utf-8 -*-
"""
tests/test_sensor_health_runtime.py
===================================
Phase 6C Test Suite: Multi-Factor Sensor Runtime Health Scoring
"""

import sys
import os
import time
import pytest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.sensor_registry import (
    SensorRegistry,
    SensorDevice,
    STATUS_ACTIVE,
    STATUS_OFFLINE,
    STATUS_REGISTERED
)
from engine.sensor_calibration import (
    SensorCalibrationEngine,
    CalibrationRecord,
    STATUS_CALIBRATED,
    STATUS_CALIBRATION_DUE,
    STATUS_INVALID_CALIBRATION
)


@pytest.fixture
def isolated_reg(tmp_path):
    db_path = str(tmp_path / "test_health_reg.db")
    return SensorRegistry(db_path=db_path)


class TestSensorHealthRuntime:

    def test_nominal_sensor_health_is_good(self, isolated_reg):
        reg = isolated_reg
        dev_id = "HEALTH-GOOD-01"
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        due_iso = (now_dt + timedelta(days=365)).isoformat()

        # Register valid calibration for this sensor
        from engine.sensor_calibration import GLOBAL_CALIBRATION_ENGINE, CalibrationRecord
        GLOBAL_CALIBRATION_ENGINE.register_calibration(
            CalibrationRecord(
                calibration_id="CAL-GOOD-01",
                sensor_id=dev_id,
                calibration_date=now_iso,
                calibration_due=due_iso,
                zero_offset=0.0,
                scale_factor=1.0,
                status="CALIBRATED"
            )
        )

        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE,
            battery_level=95.0,
            signal_strength=-65.0,
            clock_offset_ms=25.0,
            last_seen=now_iso
        )
        reg.register_device(dev)

        health = reg.get_composite_sensor_health(dev_id)
        assert health["overall_health"] == "GOOD"
        assert "nominal" in health["reason"].lower()

    def test_low_battery_downgrades_to_degraded(self, isolated_reg):
        reg = isolated_reg
        dev_id = "HEALTH-LOW-BAT-01"
        now_iso = datetime.now(timezone.utc).isoformat()

        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE,
            battery_level=22.0,  # <30%
            signal_strength=-70.0,
            clock_offset_ms=10.0,
            last_seen=now_iso
        )
        reg.register_device(dev)

        health = reg.get_composite_sensor_health(dev_id)
        assert health["overall_health"] == "DEGRADED"
        assert "Low battery" in health["reason"]

    def test_weak_signal_downgrades_to_degraded(self, isolated_reg):
        reg = isolated_reg
        dev_id = "HEALTH-WEAK-SIG-01"
        now_iso = datetime.now(timezone.utc).isoformat()

        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE,
            battery_level=90.0,
            signal_strength=-102.0,  # <-95 dBm
            clock_offset_ms=10.0,
            last_seen=now_iso
        )
        reg.register_device(dev)

        health = reg.get_composite_sensor_health(dev_id)
        assert health["overall_health"] == "DEGRADED"
        assert "Weak RF link" in health["reason"]

    def test_severe_clock_drift_flags_invalid(self, isolated_reg):
        reg = isolated_reg
        dev_id = "HEALTH-DRIFT-01"
        now_iso = datetime.now(timezone.utc).isoformat()

        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE,
            battery_level=90.0,
            signal_strength=-70.0,
            clock_offset_ms=400000.0,  # >300s (400s)
            last_seen=now_iso
        )
        reg.register_device(dev)

        health = reg.get_composite_sensor_health(dev_id)
        assert health["overall_health"] == "INVALID"
        assert "clock drift" in health["reason"].lower()

    def test_depleted_battery_flags_invalid(self, isolated_reg):
        reg = isolated_reg
        dev_id = "HEALTH-DEPLETED-01"
        now_iso = datetime.now(timezone.utc).isoformat()

        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE,
            battery_level=6.0,  # <10%
            signal_strength=-70.0,
            last_seen=now_iso
        )
        reg.register_device(dev)

        health = reg.get_composite_sensor_health(dev_id)
        assert health["overall_health"] == "INVALID"
        assert "Battery depleted" in health["reason"]

    def test_stale_device_flags_offline(self, isolated_reg):
        reg = isolated_reg
        dev_id = "HEALTH-STALE-01"
        # 25 minutes in the past (>900s)
        old_iso = (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()

        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE,
            last_seen=old_iso
        )
        reg.register_device(dev)

        health = reg.get_composite_sensor_health(dev_id)
        assert health["overall_health"] == "OFFLINE"
        assert "limit" in health["reason"]

    def test_unregistered_device_flags_offline(self, isolated_reg):
        health = isolated_reg.get_composite_sensor_health("NON-EXISTENT-DEVICE")
        assert health["overall_health"] == "OFFLINE"
        assert health["reason"] == "DEVICE_NOT_REGISTERED"
