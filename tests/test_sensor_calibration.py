# -*- coding: utf-8 -*-
"""
tests/test_sensor_calibration.py
================================
Unit tests for Sensor Calibration Engine (Phase 6A).
Validates:
  - Zero-offset and scale factor linear transfer function
  - Expiration monitoring (CALIBRATION_DUE status transition)
  - Sanity validation (rejection of non-positive scale factors)
  - Degradation penalties on sensor confidence scores
"""

import os
import tempfile
import pytest
from datetime import datetime, timezone, timedelta

from engine.sensor_calibration import (
    SensorCalibrationEngine,
    CalibrationRecord,
    STATUS_CALIBRATED,
    STATUS_CALIBRATION_DUE,
    STATUS_INVALID_CALIBRATION,
    STATUS_UNKNOWN
)


@pytest.fixture
def temp_cal_engine():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_calibrations.db")
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_calibrations (
                calibration_id TEXT PRIMARY KEY,
                sensor_id TEXT NOT NULL,
                calibration_date TEXT NOT NULL,
                calibration_due TEXT NOT NULL,
                zero_offset REAL DEFAULT 0.0,
                scale_factor REAL DEFAULT 1.0,
                calibration_source TEXT DEFAULT 'FACTORY',
                status TEXT DEFAULT 'CALIBRATED',
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

        engine = SensorCalibrationEngine(db_path=db_path)
        yield engine


def test_linear_calibration_transfer_function(temp_cal_engine):
    # Calibrated = (Raw - zero_offset) * scale_factor
    # Raw = 25.0, zero_offset = 5.0, scale_factor = 2.0 -> (25 - 5) * 2 = 40.0
    rec = CalibrationRecord(
        calibration_id="CAL-PZ-01",
        sensor_id="SN-PZ-01",
        calibration_date=datetime.now(timezone.utc).isoformat(),
        calibration_due=(datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
        zero_offset=5.0,
        scale_factor=2.0,
        status=STATUS_CALIBRATED
    )
    temp_cal_engine.register_calibration(rec)

    calibrated_val, status, penalty = temp_cal_engine.apply_calibration("SN-PZ-01", 25.0)
    assert calibrated_val == 40.0
    assert status == STATUS_CALIBRATED
    assert penalty == 0.0


def test_calibration_due_expiration(temp_cal_engine):
    # Calibration due in the past
    past_due = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    rec = CalibrationRecord(
        calibration_id="CAL-EXPIRED-01",
        sensor_id="SN-PZ-EXPIRED",
        calibration_date=(datetime.now(timezone.utc) - timedelta(days=400)).isoformat(),
        calibration_due=past_due,
        zero_offset=0.0,
        scale_factor=1.0,
        status=STATUS_CALIBRATED
    )
    temp_cal_engine.register_calibration(rec)

    # Retrieval should detect expiration and update to CALIBRATION_DUE
    fetched = temp_cal_engine.get_calibration("SN-PZ-EXPIRED")
    assert fetched.status == STATUS_CALIBRATION_DUE

    val, status, penalty = temp_cal_engine.apply_calibration("SN-PZ-EXPIRED", 15.0)
    assert status == STATUS_CALIBRATION_DUE
    assert penalty > 0.0  # Confidence penalty applied for uncalibrated/overdue sensor


def test_invalid_calibration_parameters(temp_cal_engine):
    # Scale factor <= 0 is physically invalid
    rec = CalibrationRecord(
        calibration_id="CAL-BAD-01",
        sensor_id="SN-BAD-01",
        calibration_date=datetime.now(timezone.utc).isoformat(),
        calibration_due=(datetime.now(timezone.utc) + timedelta(days=100)).isoformat(),
        zero_offset=0.0,
        scale_factor=-1.5
    )
    saved = temp_cal_engine.register_calibration(rec)
    assert saved.status == STATUS_INVALID_CALIBRATION

    val, status, penalty = temp_cal_engine.apply_calibration("SN-BAD-01", 10.0)
    assert status == STATUS_INVALID_CALIBRATION
    assert penalty >= 0.70


def test_unregistered_sensor_fallback(temp_cal_engine):
    val, status, penalty = temp_cal_engine.apply_calibration("UNKNOWN-SENSOR", 30.0)
    assert val == 30.0
    assert status == STATUS_UNKNOWN
    assert penalty == 0.50
