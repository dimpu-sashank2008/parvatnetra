# -*- coding: utf-8 -*-
"""
tests/test_telemetry_contract.py
================================
Unit tests for Canonical Telemetry Contract & Ingress Validation (Phase 6A).
Validates:
  - Strict JSON packet schema validation
  - Physical boundary limits per transducer type
  - Future timestamp and clock drift rejection (>30s)
  - Geographic bounding box enforcement [20-30 deg N, 87-98 deg E]
  - Idempotent duplicate packet detection
  - Multi-axis biaxial tilt resultant computation
  - Ingestion metrics tracking
"""

import time
import pytest
from datetime import datetime, timezone, timedelta

from services.telemetry_contract import (
    TelemetryValidator,
    NER_LAT_MIN, NER_LAT_MAX, NER_LON_MIN, NER_LON_MAX
)


@pytest.fixture
def validator():
    return TelemetryValidator()


def test_valid_telemetry_packet(validator):
    now_iso = datetime.now(timezone.utc).isoformat()
    raw_packet = {
        "device_id": "SN-NH10-PZ-01",
        "sensor_id": "PZ-01",
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 27.3300,
        "longitude": 88.6100,
        "battery": 94.0,
        "signal_quality": -72.0,
        "measurements": {
            "pore_pressure": {"value": 24.5, "unit": "kPa"}
        }
    }

    res = validator.validate_and_normalize(raw_packet, transport="HTTP")
    assert res.is_valid is True
    assert res.status == "ACCEPTED"
    assert res.packet is not None
    assert res.packet.device_id == "SN-NH10-PZ-01"
    assert "pore_pressure" in res.packet.measurements
    assert res.packet.measurements["pore_pressure"].value == 24.5


def test_missing_device_id_rejected(validator):
    raw_packet = {
        "sequence_number": 1,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 10.0}
    }
    res = validator.validate_and_normalize(raw_packet)
    assert res.is_valid is False
    assert res.status == "REJECTED_MISSING_DEVICE_ID"


def test_out_of_bounds_coordinates_rejected(validator):
    now_iso = datetime.now(timezone.utc).isoformat()
    # Coordinates in Delhi/Mumbai (outside NER)
    raw_packet = {
        "device_id": "DEV-OUT-01",
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 19.0760,  # Mumbai < 20.0
        "longitude": 72.8777, # Mumbai < 87.0
        "measurements": {"pore_pressure": 15.0}
    }
    res = validator.validate_and_normalize(raw_packet)
    assert res.is_valid is False
    assert res.status == "REJECTED_OUT_OF_BOUNDS"


def test_future_timestamp_rejected(validator):
    future_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    raw_packet = {
        "device_id": "DEV-TIME-01",
        "sequence_number": 1,
        "timestamp": future_time,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 12.0}
    }
    res = validator.validate_and_normalize(raw_packet)
    assert res.is_valid is False
    assert res.status == "REJECTED_FUTURE_TIMESTAMP"


def test_duplicate_packet_detection(validator):
    now_iso = datetime.now(timezone.utc).isoformat()
    raw_packet = {
        "packet_id": "PKT-UNIQUE-101",
        "device_id": "DEV-DUP-01",
        "sequence_number": 10,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 18.0}
    }
    res1 = validator.validate_and_normalize(raw_packet)
    assert res1.is_valid is True

    # Same packet replay
    res2 = validator.validate_and_normalize(raw_packet)
    assert res2.is_valid is False
    assert res2.status == "REJECTED_DUPLICATE"


def test_physical_limits_flagging(validator):
    now_iso = datetime.now(timezone.utc).isoformat()
    # Piezometer valid range: -10 to 250 kPa. Submit 9999 kPa
    raw_packet = {
        "device_id": "DEV-EXTREME-01",
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {
            "pore_pressure": {"value": 9999.0, "unit": "kPa"}
        }
    }
    res = validator.validate_and_normalize(raw_packet)
    assert res.is_valid is False
    assert res.status == "REJECTED_IMPOSSIBLE_VALUE"
    assert "exceeds physical limits" in res.message


def test_biaxial_tilt_resultant(validator):
    now_iso = datetime.now(timezone.utc).isoformat()
    # tilt_x = 3.0, tilt_y = 4.0 -> resultant sqrt(3^2 + 4^2) = 5.0
    raw_packet = {
        "device_id": "DEV-TILT-01",
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {
            "tilt_x": {"value": 3.0, "unit": "deg"},
            "tilt_y": {"value": 4.0, "unit": "deg"}
        }
    }
    res = validator.validate_and_normalize(raw_packet)
    assert res.is_valid is True
    assert "tilt_resultant" in res.packet.measurements
    assert res.packet.measurements["tilt_resultant"].value == 5.0


def test_metrics_tracking(validator):
    now_iso = datetime.now(timezone.utc).isoformat()
    # 1 valid packet
    validator.validate_and_normalize({
        "device_id": "DEV-M-01",
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 15.0}
    })
    # 1 rejected packet (no device_id)
    validator.validate_and_normalize({"sequence_number": 2})

    metrics = validator.get_metrics()
    assert metrics["total_packets"] >= 2
    assert metrics["accepted_packets"] >= 1
    assert metrics["rejected_packets"] >= 1
    assert metrics["drop_rate_pct"] > 0
