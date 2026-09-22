# -*- coding: utf-8 -*-
"""
tests/test_v4_7_calibration.py
==============================
Phase V4.7 Test Suite: Calibration Traceability, NABL Accreditation & Tolerance Gating
"""

import os
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
def calibration_engine(tmp_path):
    db_file = str(tmp_path / "test_calibration.db")
    return SensorCalibrationEngine(db_path=db_file)


class TestCalibrationRecordRegistration:
    """Tests registration, retrieval, and validation of calibration records."""

    def test_register_valid_nabl_calibration(self, calibration_engine):
        now = datetime.now(timezone.utc)
        due = now + timedelta(days=365)
        rec = CalibrationRecord(
            calibration_id="CAL-PIEZO-2026-001",
            sensor_id="PIEZO-NH10-KM48-01",
            calibration_date=now.isoformat(),
            calibration_due=due.isoformat(),
            zero_offset=0.25,
            scale_factor=1.002,
            calibration_source="NABL_ACCREDITED_LAB",
            certificate_ref="NABL-GEO-2026-P8821",
            technician="Metrology Specialist A. Sharma"
        )
        saved = calibration_engine.register_calibration(rec)
        assert saved.status == STATUS_CALIBRATED
        assert saved.certificate_ref == "NABL-GEO-2026-P8821"

        retrieved = calibration_engine.get_calibration("PIEZO-NH10-KM48-01")
        assert retrieved is not None
        assert retrieved.calibration_id == "CAL-PIEZO-2026-001"
        assert retrieved.zero_offset == 0.25
        assert retrieved.scale_factor == 1.002

    def test_unregistered_sensor_returns_unknown_status(self, calibration_engine):
        cal = calibration_engine.get_calibration("SENSOR-UNREGISTERED-99")
        assert cal is None
        val, status, penalty = calibration_engine.apply_calibration("SENSOR-UNREGISTERED-99", 50.0)
        assert status == STATUS_UNKNOWN
        assert val == 50.0
        assert penalty > 0.0


class TestCalibrationValidityAndExpiration:
    """Tests calibration validity intervals, expired calibration gating, and due notices."""

    def test_expired_calibration_marked_due(self, calibration_engine):
        # Calibration due 30 days ago
        now = datetime.now(timezone.utc)
        past_cal = now - timedelta(days=395)
        past_due = now - timedelta(days=30)

        rec = CalibrationRecord(
            calibration_id="CAL-EXPIRED-01",
            sensor_id="INCL-NH10-KM48-01",
            calibration_date=past_cal.isoformat(),
            calibration_due=past_due.isoformat(),
            zero_offset=0.0,
            scale_factor=1.0,
            calibration_source="FACTORY",
            certificate_ref="NABL-GEO-2025-I4409"
        )
        calibration_engine.register_calibration(rec)

        # When evaluated at present time, it should be recognized as CALIBRATION_DUE
        val, status, penalty = calibration_engine.apply_calibration("INCL-NH10-KM48-01", 12.5)
        assert status == STATUS_CALIBRATION_DUE
        assert penalty == 0.25  # Confidence penalty applied for uncalibrated/overdue instrument


class TestCalibrationToleranceAndRejection:
    """Tests physical bounds for scale factors and zero offsets to prevent corrupted calibrations."""

    def test_zero_or_negative_scale_factor_rejected(self, calibration_engine):
        now = datetime.now(timezone.utc)
        due = now + timedelta(days=365)
        rec = CalibrationRecord(
            calibration_id="CAL-BAD-SCALE",
            sensor_id="TILT-NH10-KM48-01",
            calibration_date=now.isoformat(),
            calibration_due=due.isoformat(),
            zero_offset=0.0,
            scale_factor=-1.0,  # Physically impossible / inverted scale
            certificate_ref="BAD-CERT-01"
        )
        saved = calibration_engine.register_calibration(rec)
        assert saved.status == STATUS_INVALID_CALIBRATION

        val, status, penalty = calibration_engine.apply_calibration("TILT-NH10-KM48-01", 10.0)
        assert status == STATUS_INVALID_CALIBRATION

    def test_excessive_zero_offset_rejected(self, calibration_engine):
        now = datetime.now(timezone.utc)
        due = now + timedelta(days=365)
        rec = CalibrationRecord(
            calibration_id="CAL-BAD-OFFSET",
            sensor_id="RAIN-NH10-KM48-01",
            calibration_date=now.isoformat(),
            calibration_due=due.isoformat(),
            zero_offset=999999.0,  # Unrealistic offset
            scale_factor=1.0,
            certificate_ref="BAD-OFFSET-CERT"
        )
        saved = calibration_engine.register_calibration(rec)
        assert saved.status == STATUS_INVALID_CALIBRATION


class TestDeterministicCalibrationApplication:
    """Tests deterministic transformation: cal_val = (raw_val - zero_offset) * scale_factor."""

    def test_calibration_math_application(self, calibration_engine):
        now = datetime.now(timezone.utc)
        due = now + timedelta(days=365)
        rec = CalibrationRecord(
            calibration_id="CAL-MATH-01",
            sensor_id="PIEZO-TEST-MATH",
            calibration_date=now.isoformat(),
            calibration_due=due.isoformat(),
            zero_offset=2.0,
            scale_factor=1.5,
            certificate_ref="NABL-MATH-CERT"
        )
        calibration_engine.register_calibration(rec)

        raw_reading = 12.0
        # Expected: (12.0 - 2.0) * 1.5 = 15.0
        cal_val, status, penalty = calibration_engine.apply_calibration("PIEZO-TEST-MATH", raw_reading)
        assert status == STATUS_CALIBRATED
        assert pytest.approx(cal_val, 0.001) == 15.0
        assert penalty == 0.0
