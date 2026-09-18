# -*- coding: utf-8 -*-
"""
backend/edge/edge_store.py
==========================
PARVAT NETRA • Local SQLite Persistence for Autonomous Edge Gateways
-------------------------------------------------------------------
Implements Section 6 & 7: Local persistent store ensuring zero-loss telemetry
buffering, local audit trails, and device state tracking during cloud blackouts.

Tables:
  1. edge_devices (allowlist, sequence, battery, RSSI, health)
  2. edge_sensor_readings (geotechnical in-situ measurements)
  3. edge_alerts (local safety alerts and siren test activations)
  4. edge_packets (raw RF byte captures for diagnostic replay)
  5. edge_sync_queue (asynchronous cloud synchronization queue)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


class EdgeStore:
    """Thread-safe SQLite storage engine for edge gateway deployments."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            # Detect serverless / Vercel read-only filesystem
            if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                base_dir = os.path.join("/tmp", "edge")
            else:
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "edge")
            try:
                os.makedirs(base_dir, exist_ok=True)
                self.db_path = os.path.join(base_dir, "edge_store.db")
            except (OSError, PermissionError):
                self.db_path = ":memory:"
        else:
            if db_path != ":memory:":
                try:
                    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
                except (OSError, PermissionError):
                    db_path = ":memory:"
            self.db_path = db_path

        self._lock = threading.Lock()
        self._mem_conn = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._mem_conn.row_factory = sqlite3.Row

        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    _get_conn = _get_connection

    def _init_schema(self) -> None:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()

                # 1. edge_devices
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS edge_devices (
                        node_id TEXT PRIMARY KEY,
                        registered_at TEXT NOT NULL,
                        last_seen TEXT NOT NULL,
                        last_sequence INTEGER DEFAULT 0,
                        rssi REAL,
                        snr REAL,
                        battery INTEGER DEFAULT 100,
                        packet_count INTEGER DEFAULT 0,
                        health TEXT DEFAULT 'HEALTHY',
                        role TEXT DEFAULT 'SENSOR',
                        is_allowed INTEGER DEFAULT 1
                    );
                """)

                # 2. edge_sensor_readings
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS edge_sensor_readings (
                        reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_id TEXT NOT NULL,
                        sequence INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        soil_moisture REAL,
                        pore_pressure REAL,
                        tilt REAL,
                        rainfall REAL,
                        battery INTEGER,
                        temperature REAL,
                        humidity INTEGER,
                        is_demo INTEGER DEFAULT 0,
                        provenance TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (node_id) REFERENCES edge_devices(node_id)
                    );
                """)

                # 3. edge_alerts
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS edge_alerts (
                        alert_id TEXT PRIMARY KEY,
                        severity TEXT NOT NULL,
                        trigger_source TEXT NOT NULL,
                        node_id TEXT,
                        gateway_id TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        siren_activated INTEGER DEFAULT 0,
                        dry_run INTEGER DEFAULT 1,
                        acknowledged INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL
                    );
                """)

                # 4. edge_packets
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS edge_packets (
                        packet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        raw_bytes BLOB NOT NULL,
                        node_id TEXT,
                        sequence INTEGER,
                        received_at TEXT NOT NULL,
                        rssi REAL,
                        crc_valid INTEGER DEFAULT 1
                    );
                """)

                # 5. edge_sync_queue
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS edge_sync_queue (
                        queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        record_type TEXT NOT NULL,
                        local_ref_id TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        sync_status TEXT DEFAULT 'PENDING',
                        retry_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        queued_at TEXT NOT NULL,
                        synced_at TEXT
                    );
                """)

                # 6. edge_field_reports (First Responder Offline Triage Reports)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS edge_field_reports (
                        report_id TEXT PRIMARY KEY,
                        incident_type TEXT NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        severity TEXT NOT NULL,
                        casualties INTEGER DEFAULT 0,
                        crack_aperture_mm REAL DEFAULT 0.0,
                        notes TEXT,
                        reporter_name TEXT,
                        reporter_role TEXT DEFAULT 'FIRST_RESPONDER',
                        sync_status TEXT DEFAULT 'SYNCED_EDGE',
                        created_at TEXT NOT NULL,
                        synced_at TEXT
                    );
                """)

                # Indexes
                cur.execute("CREATE INDEX IF NOT EXISTS idx_readings_node_ts ON edge_sensor_readings(node_id, timestamp);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON edge_sync_queue(sync_status);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_field_reports_created ON edge_field_reports(created_at);")
                conn.commit()

    # --------------------------------------------------------------------------
    # Device Registration & Allowlist
    # --------------------------------------------------------------------------

    def register_device(
        self,
        node_id: str,
        role: str = "SENSOR",
        is_allowed: bool = True,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a sensor or relay node in the device directory."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO edge_devices (
                        node_id, registered_at, last_seen, last_sequence, health, role, is_allowed
                    ) VALUES (?, ?, ?, 0, 'HEALTHY', ?, ?)
                    ON CONFLICT(node_id) DO UPDATE SET
                        role = excluded.role,
                        is_allowed = excluded.is_allowed;
                """, (node_id, now_iso, now_iso, role, 1 if is_allowed else 0))
                conn.commit()
        return self.get_device(node_id) or {}

    def get_device(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Queries device state by node_id."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM edge_devices WHERE node_id = ?", (node_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def get_all_devices(self, allowed_only: bool = False) -> List[Dict[str, Any]]:
        """Queries all registered edge nodes."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                if allowed_only:
                    cur.execute("SELECT * FROM edge_devices WHERE is_allowed = 1 ORDER BY node_id ASC")
                else:
                    cur.execute("SELECT * FROM edge_devices ORDER BY node_id ASC")
                return [dict(r) for r in cur.fetchall()]

    def update_device_last_seen(
        self,
        node_id: str,
        sequence: int = 0,
        rssi: Optional[float] = None,
        snr: Optional[float] = None,
        battery: Optional[int] = None
    ) -> None:
        """Updates device last_seen, sequence counter, and RF signal strength."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO edge_devices (
                        node_id, registered_at, last_seen, last_sequence, rssi, snr, battery, packet_count, health
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'HEALTHY')
                    ON CONFLICT(node_id) DO UPDATE SET
                        last_seen = excluded.last_seen,
                        last_sequence = MAX(edge_devices.last_sequence, excluded.last_sequence),
                        rssi = COALESCE(excluded.rssi, edge_devices.rssi),
                        snr = COALESCE(excluded.snr, edge_devices.snr),
                        battery = COALESCE(excluded.battery, edge_devices.battery),
                        packet_count = edge_devices.packet_count + 1;
                """, (node_id, now_iso, now_iso, sequence, rssi, snr, battery))
                conn.commit()

    # --------------------------------------------------------------------------
    # Sensor Reading Ingestion & Query
    # --------------------------------------------------------------------------

    def insert_reading(self, reading: Dict[str, Any], buffer_for_cloud: bool = True) -> int:
        """
        Inserts decoded sensor telemetry into local edge store.
        Optionally enqueues into edge_sync_queue for asynchronous cloud upload.
        """
        node_id = str(reading["node_id"])
        sequence = int(reading.get("sequence", 0))
        ts = reading.get("timestamp") or datetime.now(timezone.utc).isoformat()
        sm = float(reading.get("soil_moisture", 0.0))
        pp = float(reading.get("pore_pressure", 0.0))
        tilt = float(reading.get("tilt", 0.0))
        rain = float(reading.get("rainfall", 0.0))
        batt = int(reading.get("battery", 100))
        temp = float(reading.get("temperature", 20.0))
        hum = int(reading.get("humidity", 70))
        is_demo = 1 if (reading.get("is_demo") or "[DEMO]" in str(reading.get("provenance", ""))) else 0
        prov = "[DEMO]" if is_demo else reading.get("provenance", "[LIVE]")
        created_at = datetime.now(timezone.utc).isoformat()

        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO edge_sensor_readings (
                        node_id, sequence, timestamp, soil_moisture, pore_pressure,
                        tilt, rainfall, battery, temperature, humidity, is_demo, provenance, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (node_id, sequence, ts, sm, pp, tilt, rain, batt, temp, hum, is_demo, prov, created_at))
                reading_id = cur.lastrowid

                if buffer_for_cloud:
                    cur.execute("""
                        INSERT INTO edge_sync_queue (
                            record_type, local_ref_id, payload_json, sync_status, queued_at
                        ) VALUES ('READING', ?, ?, 'PENDING', ?)
                    """, (f"RDG-{reading_id}", json.dumps(reading), created_at))

                conn.commit()

        # Keep device last seen in sync
        self.update_device_last_seen(node_id, sequence, battery=batt)
        return reading_id or 0

    def query_readings(
        self,
        node_id: Optional[str] = None,
        limit: int = 50,
        is_demo: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Queries recent sensor observations."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                query = "SELECT * FROM edge_sensor_readings WHERE 1=1"
                params: List[Any] = []
                if node_id:
                    query += " AND node_id = ?"
                    params.append(node_id)
                if is_demo is not None:
                    query += " AND is_demo = ?"
                    params.append(1 if is_demo else 0)
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                cur.execute(query, params)
                return [dict(r) for r in cur.fetchall()]

    # --------------------------------------------------------------------------
    # Edge Alerts & Siren Event Logs
    # --------------------------------------------------------------------------

    def insert_alert(self, alert_data: Dict[str, Any], buffer_for_cloud: bool = True) -> str:
        """Persists a local edge alert / siren activation event."""
        alert_id = alert_data.get("alert_id") or f"ALT-EDGE-{int(datetime.now().timestamp() * 1000)}"
        sev = alert_data.get("severity", "WARNING")
        src = alert_data.get("trigger_source", "EDGE_THRESHOLD")
        node_id = alert_data.get("node_id")
        gw_id = alert_data.get("gateway_id", "GW-01")
        reason = alert_data.get("reason", "Threshold exceedance")
        siren_act = 1 if alert_data.get("siren_activated") else 0
        dry_run = 1 if alert_data.get("dry_run", True) else 0
        ack = 1 if alert_data.get("acknowledged") else 0
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO edge_alerts (
                        alert_id, severity, trigger_source, node_id, gateway_id,
                        reason, siren_activated, dry_run, acknowledged, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (alert_id, sev, src, node_id, gw_id, reason, siren_act, dry_run, ack, now_iso))

                if buffer_for_cloud:
                    cur.execute("""
                        INSERT INTO edge_sync_queue (
                            record_type, local_ref_id, payload_json, sync_status, queued_at
                        ) VALUES ('ALERT', ?, ?, 'PENDING', ?)
                    """, (alert_id, json.dumps(alert_data), now_iso))

                conn.commit()
        return alert_id

    def query_alerts(self, limit: int = 50, unacknowledged_only: bool = False) -> List[Dict[str, Any]]:
        """Queries local safety alerts."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                query = "SELECT * FROM edge_alerts"
                params: List[Any] = []
                if unacknowledged_only:
                    query += " WHERE acknowledged = 0"
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                cur.execute(query, params)
                return [dict(r) for r in cur.fetchall()]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Marks alert as acknowledged by human officer."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE edge_alerts SET acknowledged = 1 WHERE alert_id = ?", (alert_id,))
                conn.commit()
                return cur.rowcount > 0

    # --------------------------------------------------------------------------
    # Raw Packet Diagnostics
    # --------------------------------------------------------------------------

    def log_raw_packet(
        self,
        raw_bytes: bytes,
        node_id: Optional[str] = None,
        sequence: Optional[int] = None,
        rssi: Optional[float] = None,
        crc_valid: bool = True
    ) -> int:
        """Stores raw byte buffer for protocol debugging and signal analysis."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO edge_packets (raw_bytes, node_id, sequence, received_at, rssi, crc_valid)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (raw_bytes, node_id, sequence, now_iso, rssi, 1 if crc_valid else 0))
                conn.commit()
                return cur.lastrowid or 0

    # --------------------------------------------------------------------------
    # Cloud Sync Buffer & Queue Management
    # --------------------------------------------------------------------------

    def get_pending_sync_items(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves items queued for cloud synchronization."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM edge_sync_queue
                    WHERE sync_status IN ('PENDING', 'RETRY_PENDING')
                    ORDER BY queue_id ASC LIMIT ?
                """, (limit,))
                return [dict(r) for r in cur.fetchall()]

    def mark_synced(self, queue_ids: List[int]) -> None:
        """Marks items as successfully transmitted to central cloud."""
        if not queue_ids:
            return
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                q_marks = ",".join("?" for _ in queue_ids)
                cur.execute(f"""
                    UPDATE edge_sync_queue
                    SET sync_status = 'SYNCED', synced_at = ?
                    WHERE queue_id IN ({q_marks})
                """, [now_iso] + queue_ids)
                conn.commit()

    def mark_sync_failed(self, queue_id: int, error_msg: str) -> None:
        """Increments retry count or sets status to FAILED."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE edge_sync_queue
                    SET retry_count = retry_count + 1,
                        last_error = ?,
                        sync_status = CASE WHEN retry_count >= 5 THEN 'FAILED' ELSE 'RETRY_PENDING' END
                    WHERE queue_id = ?
                """, (error_msg, queue_id))
                conn.commit()

    def get_queue_stats(self) -> Dict[str, Any]:
        """Returns buffer metrics (pending, synced, failed, total)."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM edge_sync_queue WHERE sync_status IN ('PENDING', 'RETRY_PENDING')")
                pending = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM edge_sync_queue WHERE sync_status = 'SYNCED'")
                synced = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM edge_sync_queue WHERE sync_status = 'FAILED'")
                failed = cur.fetchone()[0]
                cur.execute("SELECT MIN(queued_at) FROM edge_sync_queue WHERE sync_status IN ('PENDING', 'RETRY_PENDING')")
                oldest_queued = cur.fetchone()[0]
                cur.execute("SELECT MAX(queued_at) FROM edge_sync_queue WHERE sync_status IN ('PENDING', 'RETRY_PENDING')")
                newest_queued = cur.fetchone()[0]

                cur.execute("SELECT MAX(synced_at) FROM edge_sync_queue WHERE sync_status = 'SYNCED'")
                last_cloud_sync = cur.fetchone()[0]

                # Estimate storage bytes
                db_size = 0
                if self.db_path and self.db_path != ":memory:" and os.path.exists(self.db_path):
                    db_size = os.path.getsize(self.db_path)
                else:
                    db_size = (pending + synced + failed) * 512

                max_capacity_bytes = 100 * 1024 * 1024  # 100 MB
                storage_pct = min(100.0, round((db_size / max_capacity_bytes) * 100.0, 2))

                return {
                    "buffered_count": pending,
                    "synced_count": synced,
                    "failed_count": failed,
                    "total_records": pending + synced + failed,
                    "oldest_queued_at": oldest_queued,
                    "newest_queued_at": newest_queued,
                    "used_storage_bytes": db_size,
                    "capacity_bytes": max_capacity_bytes,
                    "storage_used_pct": storage_pct,
                    "is_overflow": pending > 50000 or db_size > max_capacity_bytes,
                    "overflow_policy": "OLDEST_DROP_WITH_QUARANTINE",
                    "last_cloud_sync": last_cloud_sync or "NEVER"
                }

    # Alias for reading registration
    register_reading = insert_reading

    def set_gateway_power(self, power_status: str, battery_pct: int) -> Dict[str, Any]:
        """Tracks gateway power telemetry (NORMAL, BATTERY_LOW, BATTERY_CRITICAL, SHUTDOWN, RECOVERED)."""
        st = power_status.upper()
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "power_status": st,
            "battery_pct": int(battery_pct),
            "is_critical": st in ["BATTERY_CRITICAL", "SHUTDOWN"],
            "timestamp": now_iso,
            "safe_shutdown_engaged": st == "SHUTDOWN"
        }

    @staticmethod
    def verify_packet_checksum(raw_payload: bytes, expected_crc: Optional[int] = None) -> bool:
        """Validates 16-bit CRC / checksum of incoming edge RF packet."""
        if not raw_payload:
            return False
        calc_crc = sum(raw_payload) & 0xFFFF
        if expected_crc is not None:
            return calc_crc == (expected_crc & 0xFFFF)
        return True

    # --------------------------------------------------------------------------
    # First Responder Offline Field Triage Reports
    # --------------------------------------------------------------------------

    def insert_field_report(
        self,
        report_data: Dict[str, Any],
        buffer_for_cloud: bool = True
    ) -> str:
        """Inserts a first responder damage/casualty report and buffers for central sync."""
        now_iso = datetime.now(timezone.utc).isoformat()
        report_id = str(report_data.get("report_id") or f"RPT-FIELD-{int(datetime.now().timestamp() * 1000)}")
        inc_type = str(report_data.get("incident_type", "SLOPE_CRACK"))
        lat = float(report_data.get("latitude", 27.0984))
        lng = float(report_data.get("longitude", 88.4892))
        severity = str(report_data.get("severity", "HIGH")).upper()
        casualties = int(report_data.get("casualties", 0))
        crack_mm = float(report_data.get("crack_aperture_mm", 0.0))
        notes = str(report_data.get("notes", ""))
        reporter_name = str(report_data.get("reporter_name", "Anonymous Responder"))
        reporter_role = str(report_data.get("reporter_role", "FIRST_RESPONDER"))

        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO edge_field_reports (
                        report_id, incident_type, latitude, longitude, severity,
                        casualties, crack_aperture_mm, notes, reporter_name,
                        reporter_role, sync_status, created_at, synced_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED_EDGE', ?, NULL)
                    ON CONFLICT(report_id) DO UPDATE SET
                        severity = excluded.severity,
                        casualties = excluded.casualties,
                        crack_aperture_mm = excluded.crack_aperture_mm,
                        notes = excluded.notes;
                """, (
                    report_id, inc_type, lat, lng, severity,
                    casualties, crack_mm, notes, reporter_name,
                    reporter_role, now_iso
                ))

                if buffer_for_cloud:
                    cur.execute("""
                        INSERT INTO edge_sync_queue (
                            record_type, local_ref_id, payload_json, sync_status, queued_at
                        ) VALUES (?, ?, ?, 'PENDING', ?)
                    """, (
                        "FIELD_REPORT",
                        report_id,
                        json.dumps({
                            "report_id": report_id,
                            "incident_type": inc_type,
                            "latitude": lat,
                            "longitude": lng,
                            "severity": severity,
                            "casualties": casualties,
                            "crack_aperture_mm": crack_mm,
                            "notes": notes,
                            "reporter_name": reporter_name,
                            "created_at": now_iso
                        }),
                        now_iso
                    ))
                conn.commit()

        return report_id

    def query_field_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent locally-stored field triage reports."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM edge_field_reports
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                return [dict(r) for r in cur.fetchall()]

