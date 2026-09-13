# -*- coding: utf-8 -*-
"""
services/field_task_service.py
==============================
PARVAT NETRA • PAHAD AI — Field Ground Verification Task & Report Service
-------------------------------------------------------------------------
Coordinates the physical ground truth verification loop:
  ALERT_CANDIDATE
  -> FIELD_TASK
  -> GPS
  -> PHOTO/VIDEO
  -> OBSERVATION
  -> VERIFY
  -> AUTHORITY_DECISION

Supports offline mobile capture and batch synchronization for mountain field units.
"""

from __future__ import annotations

import os
import json
import uuid
import sqlite3
import logging
import threading
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("FIELD_TASK_SERVICE")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)


@dataclass
class FieldVerificationReport:
    report_id: str
    task_id: str
    operator: str
    location: Dict[str, float]
    timestamp: str
    media_reference: List[str]
    observation: str
    severity: str
    verification_result: str
    observed_cracks: bool = False
    slope_movement: bool = False
    blocked_road: bool = False
    debris: bool = False
    water_seepage: bool = False
    ground_deformation: bool = False
    photographs: List[str] = field(default_factory=list)
    confidence: float = 1.0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FieldTaskService:
    """Manages ground reconnaissance task dispatches and incoming mobile field reports."""

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
                    CREATE TABLE IF NOT EXISTS field_tasks (
                        task_id TEXT PRIMARY KEY,
                        decision_id TEXT NOT NULL,
                        sector_id TEXT NOT NULL,
                        assigned_team TEXT NOT NULL,
                        target_location TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        completed_at TEXT
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS field_reports (
                        report_id TEXT PRIMARY KEY,
                        task_id TEXT NOT NULL,
                        operator TEXT NOT NULL,
                        location TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        media_reference TEXT NOT NULL,
                        observation TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        verification_result TEXT NOT NULL,
                        evidence_details TEXT
                    )
                """)
                cur.execute("PRAGMA table_info(field_reports)")
                cols = [c[1] for c in cur.fetchall()]
                if "evidence_details" not in cols:
                    try:
                        cur.execute("ALTER TABLE field_reports ADD COLUMN evidence_details TEXT")
                    except Exception:
                        pass
                cur.execute("CREATE INDEX IF NOT EXISTS idx_rep_task ON field_reports(task_id)")
                conn.commit()
            finally:
                conn.close()

    def dispatch_field_task(
        self,
        decision_id: str,
        sector_id: str,
        assigned_team: str = "BRO Project Swastik QRT",
        target_location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Dispatches an on-site reconnaissance mission to verify an unconfirmed AI anomaly."""
        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        loc = target_location or {"latitude": 27.3300, "longitude": 88.6100}

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO field_tasks (
                        task_id, decision_id, sector_id, assigned_team,
                        target_location, status, created_at, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id, decision_id, sector_id, assigned_team,
                    json.dumps(loc), "DISPATCHED", now, None
                ))
                conn.commit()
            finally:
                conn.close()

        logger.info(f"Dispatched field task {task_id} for decision {decision_id} to {assigned_team}")
        return {
            "task_id": task_id,
            "decision_id": decision_id,
            "sector_id": sector_id,
            "assigned_team": assigned_team,
            "target_location": loc,
            "status": "DISPATCHED",
            "created_at": now
        }

    def submit_field_report(self, report: FieldVerificationReport) -> Dict[str, Any]:
        """Submits physical ground observation evidence, closing the assigned field task."""
        # Validate GPS Accuracy
        loc = report.location if isinstance(report.location, dict) else {}
        acc = loc.get("accuracy_m", 5.0)
        if acc > 25.0:
            raise ValueError(f"Field report GPS accuracy ({acc}m) exceeds 25.0m precision threshold")

        now = datetime.now(timezone.utc).isoformat()
        if not report.timestamp:
            report.timestamp = now

        evidence_dict = {
            "observed_cracks": getattr(report, "observed_cracks", False),
            "slope_movement": getattr(report, "slope_movement", False),
            "blocked_road": getattr(report, "blocked_road", False),
            "debris": getattr(report, "debris", False),
            "water_seepage": getattr(report, "water_seepage", False),
            "ground_deformation": getattr(report, "ground_deformation", False),
            "photographs": getattr(report, "photographs", []) or report.media_reference,
            "confidence": getattr(report, "confidence", 1.0),
            "notes": getattr(report, "notes", "") or report.observation
        }

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO field_reports (
                        report_id, task_id, operator, location,
                        timestamp, media_reference, observation,
                        severity, verification_result, evidence_details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.report_id, report.task_id, report.operator,
                    json.dumps(report.location), report.timestamp,
                    json.dumps(report.media_reference), report.observation,
                    report.severity, report.verification_result, json.dumps(evidence_dict)
                ))
                # Update task status to COMPLETED
                cur.execute("""
                    UPDATE field_tasks
                    SET status = 'COMPLETED', completed_at = ?
                    WHERE task_id = ?
                """, (now, report.task_id))
                conn.commit()
            finally:
                conn.close()

        logger.info(f"Field report {report.report_id} recorded for {report.task_id}. Result: {report.verification_result}")
        return report.to_dict()

    def get_task_reports(self, task_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT report_id, task_id, operator, location,
                           timestamp, media_reference, observation,
                           severity, verification_result, evidence_details
                    FROM field_reports WHERE task_id = ?
                    ORDER BY timestamp DESC
                """, (task_id,))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    ev = json.loads(r[9]) if (len(r) > 9 and r[9]) else {}
                    item = {
                        "report_id": r[0],
                        "task_id": r[1],
                        "operator": r[2],
                        "location": json.loads(r[3]),
                        "timestamp": r[4],
                        "media_reference": json.loads(r[5]),
                        "observation": r[6],
                        "severity": r[7],
                        "verification_result": r[8],
                        "observed_cracks": ev.get("observed_cracks", False),
                        "slope_movement": ev.get("slope_movement", False),
                        "blocked_road": ev.get("blocked_road", False),
                        "debris": ev.get("debris", False),
                        "water_seepage": ev.get("water_seepage", False),
                        "ground_deformation": ev.get("ground_deformation", False),
                        "photographs": ev.get("photographs", []),
                        "confidence": ev.get("confidence", 1.0),
                        "notes": ev.get("notes", r[6])
                    }
                    results.append(item)
                return results
            finally:
                conn.close()

    def list_tasks(self, sector_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                if sector_id:
                    cur.execute("""
                        SELECT task_id, decision_id, sector_id, assigned_team,
                               target_location, status, created_at, completed_at
                        FROM field_tasks WHERE sector_id = ?
                        ORDER BY created_at DESC
                    """, (sector_id,))
                else:
                    cur.execute("""
                        SELECT task_id, decision_id, sector_id, assigned_team,
                               target_location, status, created_at, completed_at
                        FROM field_tasks ORDER BY created_at DESC
                    """)
                rows = cur.fetchall()
                return [
                    {
                        "task_id": r[0],
                        "decision_id": r[1],
                        "sector_id": r[2],
                        "assigned_team": r[3],
                        "target_location": json.loads(r[4]),
                        "status": r[5],
                        "created_at": r[6],
                        "completed_at": r[7]
                    }
                    for r in rows
                ]
            finally:
                conn.close()


FIELD_TASK_SERVICE = FieldTaskService()
