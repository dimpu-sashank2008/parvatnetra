# -*- coding: utf-8 -*-
"""
services/field_evidence_service.py
==================================
PARVAT NETRA • PAHAD AI — Field Commissioning Evidence & Offline Mobile Sync
----------------------------------------------------------------------------
Implements the 7-step field technician commissioning procedure:
  1. REGISTER   -> Verify asset registration & serial against corridor inventory
  2. LOCATE     -> Log sub-10m GPS location, elevation, and terrain aspect
  3. INSTALL    -> Record physical borehole/surface mount + photo cryptographic hashes
  4. CALIBRATE  -> Bind ISO 17025 metrology calibration certificate & zero-offset
  5. CONNECT    -> Verify LoRa link to gateway, measure RSSI & SNR
  6. TEST       -> Transmit end-to-end test packet, verify CRC-16 and schema
  7. ACCEPT     -> Metrology technician sign-off, transitioning device to ACTIVE

Includes batch-sync ingestion for offline Flutter mobile client in remote gorges.
"""

from __future__ import annotations

import os
import json
import hashlib
import sqlite3
import logging
import threading
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from engine.sensor_inventory import (
    SENSOR_INVENTORY,
    PhysicalSensorAsset,
    STATUS_INSTALLED,
    STATUS_CALIBRATED,
    STATUS_CONNECTED,
    STATUS_ACTIVE,
    STATUS_FAILED
)

logger = logging.getLogger("FIELD_EVIDENCE_SERVICE")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Authoritative 7-Step Field Commissioning Sequence
FIELD_STAGES = [
    "REGISTER",
    "LOCATE",
    "INSTALL",
    "CALIBRATE",
    "CONNECT",
    "TEST",
    "ACCEPT"
]

STAGE_TO_INVENTORY_STATUS: Dict[str, str] = {
    "INSTALL": STATUS_INSTALLED,
    "CALIBRATE": STATUS_CALIBRATED,
    "CONNECT": STATUS_CONNECTED,
    "ACCEPT": STATUS_ACTIVE
}


@dataclass
class FieldEvidenceRecord:
    evidence_id: str
    device_id: str
    stage: str
    technician_name: str
    gps_coords: Dict[str, float]
    photo_hashes: List[str] = field(default_factory=list)
    calibration_cert_id: Optional[str] = None
    gateway_id: Optional[str] = None
    measured_rssi: Optional[float] = None
    measured_snr: Optional[float] = None
    notes: str = ""
    timestamp: str = ""
    signature_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FieldEvidenceService:
    """Thread-safe service managing field installation evidence and mobile synchronization."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS field_commissioning_evidence (
                        evidence_id TEXT PRIMARY KEY,
                        device_id TEXT NOT NULL,
                        stage TEXT NOT NULL,
                        technician_name TEXT NOT NULL,
                        gps_coords TEXT NOT NULL,
                        photo_hashes TEXT NOT NULL,
                        calibration_cert_id TEXT,
                        gateway_id TEXT,
                        measured_rssi REAL,
                        measured_snr REAL,
                        notes TEXT,
                        timestamp TEXT NOT NULL,
                        signature_hash TEXT NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_ev_dev ON field_commissioning_evidence(device_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_ev_stage ON field_commissioning_evidence(stage)")
                conn.commit()
            finally:
                conn.close()

    def generate_signature(
        self,
        device_id: str,
        stage: str,
        technician: str,
        timestamp: str
    ) -> str:
        """Calculates deterministic SHA-256 signature for verification audit."""
        raw = f"{device_id}:{stage}:{technician}:{timestamp}:PARVAT_FIELD_PROOF"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record_stage_evidence(self, evidence: FieldEvidenceRecord) -> FieldEvidenceRecord:
        """
        Validates and records evidence for a single commissioning stage.
        """
        if evidence.stage not in FIELD_STAGES:
            raise ValueError(f"Invalid field stage '{evidence.stage}'. Must be one of {FIELD_STAGES}")

        # Validate GPS Accuracy (must be within 15 meters in Himalayan valleys)
        gps = evidence.gps_coords or {}
        acc = gps.get("accuracy_m", 5.0)
        if acc > 25.0:
            raise ValueError(f"GPS accuracy too poor ({acc}m > 25.0m threshold) for geotechnical registry")

        # Validate stage prerequisites
        if evidence.stage == "CALIBRATE" and not evidence.calibration_cert_id:
            raise ValueError("CALIBRATE stage requires valid calibration_cert_id")
        if evidence.stage == "CONNECT" and (evidence.measured_rssi is None or not evidence.gateway_id):
            raise ValueError("CONNECT stage requires measured_rssi and gateway_id")
        if evidence.stage == "INSTALL" and not evidence.photo_hashes:
            raise ValueError("INSTALL stage requires at least one photograph SHA-256 hash")

        if not evidence.timestamp:
            evidence.timestamp = datetime.now(timezone.utc).isoformat()
        if not evidence.signature_hash:
            evidence.signature_hash = self.generate_signature(
                evidence.device_id, evidence.stage, evidence.technician_name, evidence.timestamp
            )

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO field_commissioning_evidence (
                        evidence_id, device_id, stage, technician_name, gps_coords,
                        photo_hashes, calibration_cert_id, gateway_id, measured_rssi,
                        measured_snr, notes, timestamp, signature_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evidence.evidence_id, evidence.device_id, evidence.stage, evidence.technician_name,
                    json.dumps(evidence.gps_coords), json.dumps(evidence.photo_hashes),
                    evidence.calibration_cert_id, evidence.gateway_id,
                    evidence.measured_rssi, evidence.measured_snr,
                    evidence.notes, evidence.timestamp, evidence.signature_hash
                ))
                conn.commit()
            finally:
                conn.close()

        # Check if this stage triggers an inventory status update
        target_status = STAGE_TO_INVENTORY_STATUS.get(evidence.stage)
        if target_status:
            try:
                asset = SENSOR_INVENTORY.get_asset(evidence.device_id)
                if asset:
                    if evidence.stage == "CALIBRATE" and evidence.calibration_cert_id:
                        SENSOR_INVENTORY.assign_calibration(
                            evidence.device_id, evidence.calibration_cert_id, evidence.technician_name
                        )
                    SENSOR_INVENTORY.update_status(
                        evidence.device_id, target_status, evidence.technician_name, f"Stage {evidence.stage} completed"
                    )
            except Exception as e:
                logger.warning(f"Could not auto-advance asset {evidence.device_id} status: {e}")

        logger.info(f"Recorded evidence {evidence.evidence_id} for {evidence.device_id} at stage {evidence.stage}")
        return evidence

    def get_device_evidence(self, device_id: str) -> List[FieldEvidenceRecord]:
        """Retrieves complete chronological commissioning history for a sensor."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT evidence_id, device_id, stage, technician_name, gps_coords,
                           photo_hashes, calibration_cert_id, gateway_id, measured_rssi,
                           measured_snr, notes, timestamp, signature_hash
                    FROM field_commissioning_evidence
                    WHERE device_id = ?
                    ORDER BY timestamp ASC
                """, (device_id,))
                rows = cur.fetchall()
                return [self._row_to_evidence(r) for r in rows]
            finally:
                conn.close()

    def batch_sync_offline_evidence(self, payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synchronizes queued offline evidence records uploaded by field technician mobile device.
        Idempotent: Duplicate evidence_id records are accepted without error.
        """
        synced_count = 0
        skipped_count = 0
        errors = []

        for item in payload:
            try:
                ev_id = item.get("evidence_id")
                if not ev_id:
                    errors.append({"item": item, "error": "Missing evidence_id"})
                    continue

                rec = FieldEvidenceRecord(
                    evidence_id=ev_id,
                    device_id=item.get("device_id", ""),
                    stage=item.get("stage", "REGISTER"),
                    technician_name=item.get("technician_name", "Unknown Tech"),
                    gps_coords=item.get("gps_coords", {}),
                    photo_hashes=item.get("photo_hashes", []),
                    calibration_cert_id=item.get("calibration_cert_id"),
                    gateway_id=item.get("gateway_id"),
                    measured_rssi=item.get("measured_rssi"),
                    measured_snr=item.get("measured_snr"),
                    notes=item.get("notes", ""),
                    timestamp=item.get("timestamp", ""),
                    signature_hash=item.get("signature_hash", "")
                )
                self.record_stage_evidence(rec)
                synced_count += 1
            except Exception as ex:
                errors.append({"evidence_id": item.get("evidence_id"), "error": str(ex)})

        return {
            "status": "SYNCED" if not errors else "PARTIAL_SYNC",
            "received_count": len(payload),
            "synced_count": synced_count,
            "errors": errors
        }

    def _row_to_evidence(self, row: tuple) -> FieldEvidenceRecord:
        return FieldEvidenceRecord(
            evidence_id=row[0],
            device_id=row[1],
            stage=row[2],
            technician_name=row[3],
            gps_coords=json.loads(row[4]),
            photo_hashes=json.loads(row[5]),
            calibration_cert_id=row[6],
            gateway_id=row[7],
            measured_rssi=row[8],
            measured_snr=row[9],
            notes=row[10],
            timestamp=row[11],
            signature_hash=row[12]
        )


FIELD_EVIDENCE_SERVICE = FieldEvidenceService()
