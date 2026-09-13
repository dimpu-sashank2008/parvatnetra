# -*- coding: utf-8 -*-
"""
tests/test_device_auth.py
=========================
Phase 6B Test Suite: In-Situ Device Authentication & Telemetry Ingress Security
"""

import sys
import os
import pytest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    SensorDevice,
    STATUS_REGISTERED,
    STATUS_ACTIVE,
    STATUS_DECOMMISSIONED
)
from services.telemetry_contract import (
    TelemetryValidator,
    QUALITY_GOOD
)


@pytest.fixture
def validator():
    return TelemetryValidator()


class TestDeviceAuthentication:

    def test_unknown_device_rejected_when_enforced(self, validator):
        packet = {
            "device_id": "UNKNOWN_ROGUE_DEVICE_999",
            "sequence_number": 1,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "measurements": {"piezometer": {"value": 20.0, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet, enforce_registered=True)
        assert res.is_valid is False
        assert res.status == "REJECTED_UNKNOWN_DEVICE"

    def test_decommissioned_device_rejected(self, validator):
        dev_id = "DEV-DECOMMISSIONED-01"
        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_DECOMMISSIONED
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        packet = {
            "device_id": dev_id,
            "sequence_number": 1,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "measurements": {"piezometer": {"value": 20.0, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet, enforce_registered=True)
        assert res.is_valid is False
        assert res.status == "REJECTED_DECOMMISSIONED_DEVICE"

    def test_missing_device_id_rejected(self, validator):
        packet = {
            "sequence_number": 1,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "measurements": {"piezometer": {"value": 20.0, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet)
        assert res.is_valid is False
        assert res.status == "REJECTED_MISSING_DEVICE_ID"

    def test_duplicate_packet_detection(self, validator):
        dev_id = "DEV-DUP-TEST"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="tilt",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        packet = {
            "device_id": dev_id,
            "sequence_number": 5,
            "packet_id": "PACKET_UNIQUE_123",
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "measurements": {"tilt": {"value": 1.2, "unit": "deg"}}
        }

        # First delivery: ACCEPTED
        r1 = validator.validate_and_normalize(packet, enforce_registered=True)
        assert r1.is_valid is True

        # Second delivery (replay): REJECTED_DUPLICATE
        r2 = validator.validate_and_normalize(packet, enforce_registered=True)
        assert r2.is_valid is False
        assert r2.status == "REJECTED_DUPLICATE"

    def test_future_timestamp_rejected(self, validator):
        dev_id = "DEV-TIME-TEST"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        future_ts = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        packet = {
            "device_id": dev_id,
            "sequence_number": 10,
            "latitude": 27.33,
            "longitude": 88.61,
            "timestamp": future_ts,
            "measurements": {"piezometer": {"value": 20.0, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet, enforce_registered=True)
        assert res.is_valid is False
        assert res.status == "REJECTED_FUTURE_TIMESTAMP"

    def test_out_of_bounds_coordinates_rejected(self, validator):
        dev_id = "DEV-GEO-TEST"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=12.97, longitude=77.59,  # Bangalore (outside NER)
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        packet = {
            "device_id": dev_id,
            "sequence_number": 1,
            "latitude": 12.97,
            "longitude": 77.59,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "measurements": {"piezometer": {"value": 20.0, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(packet)
        assert res.is_valid is False
        assert res.status == "REJECTED_OUT_OF_BOUNDS"

    def test_is_device_authenticated_helper(self):
        dev_id = "DEV-AUTH-HELPER"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)
        assert GLOBAL_SENSOR_REGISTRY.is_device_authenticated(dev_id) is True

        # Unknown device
        assert GLOBAL_SENSOR_REGISTRY.is_device_authenticated("NON_EXISTENT") is False

        # Decommissioned
        dev.status = STATUS_DECOMMISSIONED
        GLOBAL_SENSOR_REGISTRY.register_device(dev)
        assert GLOBAL_SENSOR_REGISTRY.is_device_authenticated(dev_id) is False
