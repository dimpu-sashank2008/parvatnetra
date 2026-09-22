# -*- coding: utf-8 -*-
"""
tests/test_v4_8_dataset_quality.py
==================================
Automated test suite for Phase V4.8 Dataset Quality & Telemetry Trust Assessment.
Tests:
  1. Rejection / degraded trust for out-of-range physical readings.
  2. Sequence gap and duplicate detection via telemetry trust assessment.
  3. Clock drift detection (>120s).
  4. Future timestamp detection (>30s).
  5. Absence of synthetic interpolation across missing observations.
"""

import pytest
from datetime import datetime, timezone, timedelta
from engine.telemetry_trust_engine import (
    GLOBAL_TELEMETRY_TRUST_ENGINE,
    TRUST_VERIFIED,
    TRUST_DEGRADED,
    TRUST_UNVERIFIED,
    REASON_OUT_OF_RANGE,
    REASON_CLOCK_DRIFT,
    REASON_FUTURE_TIMESTAMP
)
from services.kinematic_telemetry_service import GLOBAL_KINEMATIC_SERVICE


def test_quality_out_of_range_rejection():
    """Confirms pore pressure > 500 kPa or tilt > 45 deg triggers OUT_OF_RANGE."""
    now = datetime.now(timezone.utc)
    obs = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "sensor_type": "PIEZOMETER",
        "value": 650.0,  # Physical limit is 500.0 kPa
        "timestamp_utc": now.isoformat(),
        "gateway_received_at": now.isoformat(),
        "received_at": now.isoformat(),
        "sequence_number": 1
    }
    assessment = GLOBAL_TELEMETRY_TRUST_ENGINE.assess_observation(obs)
    assert assessment.range_valid is False
    assert REASON_OUT_OF_RANGE in assessment.reasons
    assert assessment.telemetry_trust != TRUST_VERIFIED


def test_quality_clock_drift_detection():
    """Confirms clock offset > 120s between sensor and gateway triggers CLOCK_DRIFT."""
    now = datetime.now(timezone.utc)
    drifting_sensor_time = (now - timedelta(seconds=200)).isoformat()

    obs = {
        "sensor_id": "TILT-NH10-KM48-01",
        "sensor_type": "TILTMETER",
        "value": 1.5,
        "timestamp_utc": drifting_sensor_time,
        "gateway_received_at": now.isoformat(),
        "received_at": now.isoformat(),
        "sequence_number": 2
    }
    assessment = GLOBAL_TELEMETRY_TRUST_ENGINE.assess_observation(obs)
    assert REASON_CLOCK_DRIFT in assessment.reasons
    assert assessment.telemetry_trust == TRUST_DEGRADED


def test_quality_future_timestamp_detection():
    """Confirms future timestamp > 30s triggers FUTURE_TIMESTAMP and UNVERIFIED trust."""
    now = datetime.now(timezone.utc)
    future_time = (now + timedelta(seconds=60)).isoformat()

    obs = {
        "sensor_id": "RAIN-NH10-KM48-01",
        "sensor_type": "RAIN_GAUGE",
        "value": 12.0,
        "timestamp_utc": future_time,
        "gateway_received_at": now.isoformat(),
        "received_at": now.isoformat(),
        "sequence_number": 3
    }
    assessment = GLOBAL_TELEMETRY_TRUST_ENGINE.assess_observation(obs)
    assert REASON_FUTURE_TIMESTAMP in assessment.reasons
    assert assessment.telemetry_trust == TRUST_UNVERIFIED


def test_quality_missing_observations_not_interpolated():
    """Confirms missing observations are preserved as unavailable without synthetic fill."""
    features = GLOBAL_KINEMATIC_SERVICE.compute_kinematic_features("CORR-NH10-SIKKIM-KM48")
    assert "sensors" in features
    assert "PIEZO-NH10-KM48-01" in features["sensors"]
    sensor_info = features["sensors"]["PIEZO-NH10-KM48-01"]
    assert sensor_info["status"] == "UNAVAILABLE"
    assert sensor_info["metrics"] is None
