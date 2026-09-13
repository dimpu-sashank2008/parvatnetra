# -*- coding: utf-8 -*-
"""
tests/test_sensor_provenance.py
===============================
Phase 6B Test Suite: Sensor Telemetry Provenance, Calibration & Quality Degradation
"""

import sys
import os
import pytest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    SensorDevice,
    STATUS_ACTIVE,
    STATUS_SIMULATED
)
from engine.sensor_calibration import (
    GLOBAL_CALIBRATION_ENGINE,
    CalibrationRecord,
    STATUS_CALIBRATION_DUE,
    STATUS_INVALID_CALIBRATION
)
from services.telemetry_contract import (
    TelemetryValidator,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_INVALID
)


@pytest.fixture
def validator():
    return TelemetryValidator()


class TestSensorProvenanceAndQuality:

    def test_live_sensor_telemetry_provenance(self, validator):
        dev_id = "DEV-PROV-LIVE"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        packet = {
            "device_id": dev_id,
            "sequence_number": 1,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "battery": 95.0,
            "signal_quality": -70.0,
            "measurements": {"piezometer": {"value": 24.5, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet, enforce_registered=True)
        assert res.is_valid is True
        assert res.packet.provenance == "[LIVE]"
        assert res.overall_quality == QUALITY_GOOD

    def test_simulated_sensor_provenance_invariant(self, validator):
        dev_id = "DEV-PROV-SIM"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48",
            status=STATUS_SIMULATED
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        packet = {
            "device_id": dev_id,
            "sequence_number": 1,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulated": True,
            "measurements": {"piezometer": {"value": 24.5, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet)
        assert res.is_valid is True
        # Invariant: Simulated telemetry must never become [LIVE]
        assert res.packet.provenance == "[SIMULATED]"
        assert res.packet.provenance != "[LIVE]"

    def test_expired_calibration_downgrades_quality_to_degraded(self, validator):
        dev_id = "DEV-EXP-CAL"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        # Register calibration that expired 30 days ago
        expired_due = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        past_date = (datetime.now(timezone.utc) - timedelta(days=395)).isoformat()
        cal = CalibrationRecord(
            calibration_id="CAL-EXPIRED",
            sensor_id=dev_id,
            calibration_date=past_date,
            calibration_due=expired_due,
            status=STATUS_CALIBRATION_DUE
        )
        GLOBAL_CALIBRATION_ENGINE.register_calibration(cal)

        packet = {
            "device_id": dev_id,
            "sequence_number": 1,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "measurements": {"piezometer": {"value": 24.5, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet)
        assert res.is_valid is True
        # Calibration due must degrade measurement quality
        assert res.packet.measurements["piezometer"].quality == QUALITY_DEGRADED
        assert res.overall_quality == QUALITY_DEGRADED

    def test_low_battery_and_weak_signal_degradation(self, validator):
        dev_id = "DEV-WEAK-SIG"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="tilt",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        packet = {
            "device_id": dev_id,
            "sequence_number": 1,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "battery": 8.0,             # Critical battery < 15%
            "signal_quality": -102.0,    # Very weak RSSI < -95 dBm
            "measurements": {"tilt": {"value": 0.5, "unit": "deg"}}
        }
        res = validator.validate_and_normalize(packet)
        assert res.is_valid is True
        assert res.overall_quality == QUALITY_DEGRADED
