# -*- coding: utf-8 -*-
"""
engine/sensor_calibration.py
============================
PARVAT NETRA • PAHAD AI — Geotechnical Sensor Calibration Engine
---------------------------------------------------------------
Tracks factory and field calibration certificates, zero offsets, scale factors,
and expiration timelines for in-situ hillslope transducers (piezometers, inclinometers,
tiltmeters, rain gauges).

Calibration Statuses:
  - CALIBRATED          : Within validity window; certified calibration applied
  - CALIBRATION_DUE     : Passed calibration_due date; reading accepted with confidence penalty
  - INVALID_CALIBRATION : Zero-offset or scale factor out of physical bounds
  - UNKNOWN             : No calibration record registered
"""

from __future__ import annotations

import os
import sqlite3
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("SENSOR_CALIBRATION")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

STATUS_CALIBRATED = "CALIBRATED"
STATUS_CALIBRATION_DUE = "CALIBRATION_DUE"
STATUS_INVALID_CALIBRATION = "INVALID_CALIBRATION"
STATUS_UNKNOWN = "UNKNOWN"

@dataclass
class CalibrationRecord:
    calibration_id: str
    sensor_id: str
    calibration_date: str          # ISO format
    calibration_due: str           # ISO format
    zero_offset: float = 0.0
    scale_factor: float = 1.0
    calibration_source: str = "FACTORY"
    certificate_ref: str = "NABL-CAL-CERT-DEFAULT"
    technician: str = "Metrology Specialist"
    status: str = STATUS_CALIBRATED
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class SensorCalibrationEngine:
    """Manages physical sensor calibration transfer functions and validity timelines."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._cache: Dict[str, CalibrationRecord] = {}
        self._load_from_db()

    def _get_conn(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _load_from_db(self) -> None:
        """Hydrates calibration cache from database."""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT calibration_id, sensor_id, calibration_date, calibration_due,
                       zero_offset, scale_factor, calibration_source, status, created_at
                FROM sensor_calibrations
            """)
            for row in cur.fetchall():
                rec = CalibrationRecord(
                    calibration_id=row[0],
                    sensor_id=row[1],
                    calibration_date=row[2],
                    calibration_due=row[3],
                    zero_offset=float(row[4]),
                    scale_factor=float(row[5]),
                    calibration_source=row[6],
                    status=row[7],
                    created_at=row[8]
                )
                self._cache[rec.sensor_id] = rec
            conn.close()
            logger.info(f"Loaded {len(self._cache)} calibration records into memory.")
        except Exception as e:
            logger.warning(f"Could not load calibrations from DB: {e}")

    def register_calibration(self, record: CalibrationRecord) -> CalibrationRecord:
        """Registers or updates a sensor calibration record."""
        # Sanity check scale factor and zero offset
        if record.scale_factor <= 0.0 or abs(record.zero_offset) > 10000.0:
            record.status = STATUS_INVALID_CALIBRATION
        else:
            # Check expiration
            try:
                due_dt = datetime.fromisoformat(record.calibration_due.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > due_dt:
                    record.status = STATUS_CALIBRATION_DUE
                else:
                    record.status = STATUS_CALIBRATED
            except Exception:
                record.status = STATUS_UNKNOWN

        if not record.created_at:
            record.created_at = datetime.now(timezone.utc).isoformat()

        self._cache[record.sensor_id] = record

        # Persist
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO sensor_calibrations (
                    calibration_id, sensor_id, calibration_date, calibration_due,
                    zero_offset, scale_factor, calibration_source, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.calibration_id, record.sensor_id, record.calibration_date,
                record.calibration_due, record.zero_offset, record.scale_factor,
                record.calibration_source, record.status, record.created_at
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to persist calibration for {record.sensor_id}: {e}")

        return record

    def get_calibration(self, sensor_id: str) -> Optional[CalibrationRecord]:
        """Retrieves active calibration for sensor."""
        rec = self._cache.get(sensor_id)
        if rec and rec.status == STATUS_CALIBRATED:
            # Dynamically verify expiration
            try:
                due_dt = datetime.fromisoformat(rec.calibration_due.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > due_dt:
                    rec.status = STATUS_CALIBRATION_DUE
            except Exception:
                pass
        return rec

    def verify_calibration_status(self, sensor_id: str) -> str:
        """Returns calibration status string."""
        rec = self.get_calibration(sensor_id)
        if not rec:
            return STATUS_UNKNOWN
        return rec.status

    def is_calibrated(self, sensor_id: str) -> bool:
        """Returns True if sensor is actively calibrated within valid expiration date."""
        rec = self.get_calibration(sensor_id)
        return bool(rec and rec.status == STATUS_CALIBRATED)

    def apply_calibration(
        self, sensor_id: str, raw_value: float
    ) -> Tuple[float, str, float]:
        """
        Applies linear calibration: Calibrated = (Raw - Zero_Offset) * Scale_Factor
        Returns: (calibrated_value, calibration_status, confidence_penalty)
          confidence_penalty: 0.0 for CALIBRATED, 0.25 for CALIBRATION_DUE, 0.70 for UNKNOWN/INVALID
        """
        rec = self.get_calibration(sensor_id)
        if not rec:
            # Default uncalibrated passthrough with confidence penalty
            return round(raw_value, 4), STATUS_UNKNOWN, 0.50

        status = rec.status
        if status == STATUS_INVALID_CALIBRATION:
            return round(raw_value, 4), STATUS_INVALID_CALIBRATION, 0.80

        # Transfer function: (raw - zero_offset) * scale_factor
        calibrated = (raw_value - rec.zero_offset) * rec.scale_factor
        penalty = 0.0 if status == STATUS_CALIBRATED else 0.25
        return round(calibrated, 4), status, penalty


# Global singleton
GLOBAL_CALIBRATION_ENGINE = SensorCalibrationEngine()
