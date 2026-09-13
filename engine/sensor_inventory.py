# -*- coding: utf-8 -*-
"""
engine/sensor_inventory.py
==========================
PARVAT NETRA • PAHAD AI — Physical Sensor & Asset Inventory Management
----------------------------------------------------------------------
Maintains authoritative physical equipment tracking, serial numbers, manufacturers,
metrological calibration certificates, and installation lifecycles for on-site hardware.

Physical Asset Lifecycles:
  PLANNED     -> Equipment budgeted and specified for a corridor site
  DELIVERED   -> Hardware arrived at regional staging warehouse / BRO camp
  INSTALLED   -> Sensor anchored/grouted on mountain slope or in borehole
  CALIBRATED  -> Zero-point and span calibrated with physical certificate
  CONNECTED   -> Paired with local LoRa concentrator gateway
  ACTIVE      -> Streaming validated operational telemetry
  FAILED      -> Telemetry degraded, power failure, or physical damage
  REMOVED     -> De-instrumented, retired, or sent for depot repair
"""

from __future__ import annotations

import os
import json
import sqlite3
import logging
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("SENSOR_INVENTORY")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Status Constants
STATUS_PLANNED = "PLANNED"
STATUS_DELIVERED = "DELIVERED"
STATUS_INSTALLED = "INSTALLED"
STATUS_CALIBRATED = "CALIBRATED"
STATUS_CONNECTED = "CONNECTED"
STATUS_ACTIVE = "ACTIVE"
STATUS_FAILED = "FAILED"
STATUS_REMOVED = "REMOVED"

VALID_INVENTORY_STATUSES = {
    STATUS_PLANNED,
    STATUS_DELIVERED,
    STATUS_INSTALLED,
    STATUS_CALIBRATED,
    STATUS_CONNECTED,
    STATUS_ACTIVE,
    STATUS_FAILED,
    STATUS_REMOVED
}

ALLOWED_INVENTORY_TRANSITIONS: Dict[str, List[str]] = {
    STATUS_PLANNED: [STATUS_DELIVERED, STATUS_REMOVED],
    STATUS_DELIVERED: [STATUS_INSTALLED, STATUS_REMOVED],
    STATUS_INSTALLED: [STATUS_CALIBRATED, STATUS_FAILED, STATUS_REMOVED],
    STATUS_CALIBRATED: [STATUS_CONNECTED, STATUS_FAILED, STATUS_REMOVED],
    STATUS_CONNECTED: [STATUS_ACTIVE, STATUS_FAILED, STATUS_REMOVED],
    STATUS_ACTIVE: [STATUS_FAILED, STATUS_REMOVED, STATUS_CALIBRATED],
    STATUS_FAILED: [STATUS_REMOVED, STATUS_INSTALLED],
    STATUS_REMOVED: [STATUS_PLANNED]
}


@dataclass
class PhysicalSensorAsset:
    device_id: str
    sensor_id: str
    sensor_type: str
    serial_number: str
    manufacturer: str
    model: str
    firmware_version: str
    calibration_certificate: Optional[str]
    installation_location: Dict[str, Any]
    installation_date: Optional[str] = None
    technician: Optional[str] = None
    gateway_id: Optional[str] = None
    status: str = STATUS_PLANNED
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SensorInventory:
    """Thread-safe persistent asset registry for geotechnical instrumentation."""

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
                    CREATE TABLE IF NOT EXISTS physical_sensor_inventory (
                        device_id TEXT PRIMARY KEY,
                        sensor_id TEXT NOT NULL,
                        sensor_type TEXT NOT NULL,
                        serial_number TEXT NOT NULL UNIQUE,
                        manufacturer TEXT NOT NULL,
                        model TEXT NOT NULL,
                        firmware_version TEXT NOT NULL,
                        calibration_certificate TEXT,
                        installation_location TEXT NOT NULL,
                        installation_date TEXT,
                        technician TEXT,
                        gateway_id TEXT,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_inv_status ON physical_sensor_inventory(status)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_inv_type ON physical_sensor_inventory(sensor_type)")
                conn.commit()
            finally:
                conn.close()

    def register_asset(self, asset: PhysicalSensorAsset) -> PhysicalSensorAsset:
        """Enrolls or updates a physical hardware asset."""
        if asset.status not in VALID_INVENTORY_STATUSES:
            raise ValueError(f"Invalid status: {asset.status}")

        now = datetime.now(timezone.utc).isoformat()
        if not asset.created_at:
            asset.created_at = now
        asset.updated_at = now

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO physical_sensor_inventory (
                        device_id, sensor_id, sensor_type, serial_number, manufacturer,
                        model, firmware_version, calibration_certificate, installation_location,
                        installation_date, technician, gateway_id, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    asset.device_id, asset.sensor_id, asset.sensor_type, asset.serial_number,
                    asset.manufacturer, asset.model, asset.firmware_version,
                    asset.calibration_certificate, json.dumps(asset.installation_location),
                    asset.installation_date, asset.technician, asset.gateway_id,
                    asset.status, asset.created_at, asset.updated_at
                ))
                conn.commit()
                return asset
            finally:
                conn.close()

    def get_asset(self, device_id: str) -> Optional[PhysicalSensorAsset]:
        """Looks up asset by device_id."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT device_id, sensor_id, sensor_type, serial_number, manufacturer,
                           model, firmware_version, calibration_certificate, installation_location,
                           installation_date, technician, gateway_id, status, created_at, updated_at
                    FROM physical_sensor_inventory WHERE device_id = ?
                """, (device_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_asset(row)
            finally:
                conn.close()

    def list_assets(
        self,
        status: Optional[str] = None,
        corridor_id: Optional[str] = None,
        sensor_type: Optional[str] = None
    ) -> List[PhysicalSensorAsset]:
        """Lists physical assets filtered by status, corridor, or sensor type."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                query = """
                    SELECT device_id, sensor_id, sensor_type, serial_number, manufacturer,
                           model, firmware_version, calibration_certificate, installation_location,
                           installation_date, technician, gateway_id, status, created_at, updated_at
                    FROM physical_sensor_inventory WHERE 1=1
                """
                params: List[Any] = []
                if status:
                    query += " AND status = ?"
                    params.append(status)
                if sensor_type:
                    query += " AND sensor_type = ?"
                    params.append(sensor_type)

                cur.execute(query, params)
                rows = cur.fetchall()
                assets = [self._row_to_asset(r) for r in rows]

                if corridor_id:
                    assets = [
                        a for a in assets
                        if a.installation_location.get("corridor_id") == corridor_id
                    ]

                return assets
            finally:
                conn.close()

    def update_status(
        self,
        device_id: str,
        new_status: str,
        technician: Optional[str] = None,
        notes: str = ""
    ) -> PhysicalSensorAsset:
        """Transitions asset state adhering to physical lifecycle rules."""
        if new_status not in VALID_INVENTORY_STATUSES:
            raise ValueError(f"Unknown inventory status: {new_status}")

        asset = self.get_asset(device_id)
        if not asset:
            raise KeyError(f"Asset {device_id} not found in inventory")

        allowed = ALLOWED_INVENTORY_TRANSITIONS.get(asset.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Illegal asset transition from {asset.status} to {new_status}. "
                f"Allowed transitions: {allowed}"
            )

        asset.status = new_status
        if technician:
            asset.technician = technician
        asset.updated_at = datetime.now(timezone.utc).isoformat()

        logger.info(f"Asset {device_id} status updated to {new_status} by {technician}. Note: {notes}")
        return self.register_asset(asset)

    def assign_calibration(self, device_id: str, cert_ref: str, technician: str) -> PhysicalSensorAsset:
        """Binds an ISO/IEC 17025 calibration certificate reference to an asset."""
        asset = self.get_asset(device_id)
        if not asset:
            raise KeyError(f"Asset {device_id} not found")

        asset.calibration_certificate = cert_ref
        asset.technician = technician
        asset.updated_at = datetime.now(timezone.utc).isoformat()
        return self.register_asset(asset)

    def summary(self) -> Dict[str, Any]:
        """Provides high-level count of inventory equipment and readiness."""
        all_assets = self.list_assets()
        by_status: Dict[str, int] = {}
        by_type: Dict[str, int] = {}

        for a in all_assets:
            by_status[a.status] = by_status.get(a.status, 0) + 1
            by_type[a.sensor_type] = by_type.get(a.sensor_type, 0) + 1

        active_count = by_status.get(STATUS_ACTIVE, 0)
        return {
            "total_assets": len(all_assets),
            "by_status": by_status,
            "by_type": by_type,
            "active_count": active_count,
            "physical_deployment_state": "PHYSICAL_DEVICE_ACTIVE" if active_count > 0 else "PHYSICAL_DEPLOYMENT_PENDING"
        }

    def _row_to_asset(self, row: tuple) -> PhysicalSensorAsset:
        return PhysicalSensorAsset(
            device_id=row[0],
            sensor_id=row[1],
            sensor_type=row[2],
            serial_number=row[3],
            manufacturer=row[4],
            model=row[5],
            firmware_version=row[6],
            calibration_certificate=row[7],
            installation_location=json.loads(row[8]),
            installation_date=row[9],
            technician=row[10],
            gateway_id=row[11],
            status=row[12],
            created_at=row[13],
            updated_at=row[14]
        )


SENSOR_INVENTORY = SensorInventory()
