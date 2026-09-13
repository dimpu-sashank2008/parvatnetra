# -*- coding: utf-8 -*-
"""
engine/incident_manager.py
==========================
PARVAT NETRA • PAHAD AI — Incident Entity & Response Prioritization Manager
---------------------------------------------------------------------------
Links PAHAD decisions, geofenced alerts, field tasks, alternative bypass routes,
and staged rescue units into a unified incident lifecycle:

  OPEN -> RESPONDING -> STABILIZING -> RESOLVED -> CLOSED
"""

from __future__ import annotations

import os
import json
import uuid
import sqlite3
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from engine.pahad_prioritization import EmergencyResponsePrioritizer
from engine.pahad_routing import RoadConnectivityRoutingEngine
from engine.corridor_registry import CORRIDOR_REGISTRY

logger = logging.getLogger("INCIDENT_MANAGER")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

INCIDENT_OPEN = "OPEN"
INCIDENT_RESPONDING = "RESPONDING"
INCIDENT_STABILIZING = "STABILIZING"
INCIDENT_RESOLVED = "RESOLVED"
INCIDENT_CLOSED = "CLOSED"

VALID_INCIDENT_STATUSES = {
    INCIDENT_OPEN,
    INCIDENT_RESPONDING,
    INCIDENT_STABILIZING,
    INCIDENT_RESOLVED,
    INCIDENT_CLOSED
}


class IncidentManager:
    """Manages disaster incident entities, response forces, routes, and priority scoring."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._prioritizer = EmergencyResponsePrioritizer()
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
                    CREATE TABLE IF NOT EXISTS operational_incidents (
                        incident_id TEXT PRIMARY KEY,
                        decision_id TEXT NOT NULL,
                        alert_id TEXT NOT NULL,
                        corridor_id TEXT NOT NULL,
                        geofence_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        assigned_force TEXT NOT NULL,
                        route_bypass TEXT NOT NULL,
                        priority_score REAL NOT NULL,
                        created_at TEXT NOT NULL,
                        resolved_at TEXT,
                        notes TEXT NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_inc_status ON operational_incidents(status)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_inc_corr ON operational_incidents(corridor_id)")
                conn.commit()
            finally:
                conn.close()

    def create_incident(
        self,
        decision_id: str,
        alert_id: str,
        corridor_id: str = "CORR-NH10-SIKKIM-KM48",
        geofence_id: str = "GEO-DEFAULT",
        cri_score: float = 85.0,
        population_at_risk: int = 2500,
        assigned_force: str = "BRO Project Swastik QRT / SDRF Pakyong"
    ) -> Dict[str, Any]:
        """Creates and indexes a new operational disaster incident."""
        incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        # 1. Routing calculation
        corridor = CORRIDOR_REGISTRY.get_corridor(corridor_id)
        bypass_name = "NH-717A Strategic Bypass"
        if corridor and corridor.evacuation_routes:
            bypass_name = corridor.evacuation_routes[0].get("name", bypass_name)

        # 2. Priority calculation using existing engine formulation
        # Priority Score = (Pop * (CRI / 100) * CritWeight) / max(ETA, 0.5)
        crit_weight = 2.5 if corridor and corridor.risk == "CRITICAL" else 1.8
        eta = 0.8
        priority_score = round((population_at_risk * (cri_score / 100.0) * crit_weight) / max(eta, 0.5), 1)

        record = {
            "incident_id": incident_id,
            "decision_id": decision_id,
            "alert_id": alert_id,
            "corridor_id": corridor_id,
            "geofence_id": geofence_id,
            "status": INCIDENT_OPEN,
            "assigned_force": assigned_force,
            "route_bypass": bypass_name,
            "priority_score": priority_score,
            "created_at": now,
            "resolved_at": None,
            "notes": f"Incident initiated from decision {decision_id}. Initial Priority={priority_score}"
        }

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO operational_incidents (
                        incident_id, decision_id, alert_id, corridor_id,
                        geofence_id, status, assigned_force, route_bypass,
                        priority_score, created_at, resolved_at, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident_id, decision_id, alert_id, corridor_id,
                    geofence_id, INCIDENT_OPEN, assigned_force, bypass_name,
                    priority_score, now, None, record["notes"]
                ))
                conn.commit()
            finally:
                conn.close()

        logger.info(f"Created incident {incident_id} for corridor {corridor_id}: Priority={priority_score}")
        return record

    def update_incident_status(
        self,
        incident_id: str,
        new_status: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Transitions incident lifecycle state."""
        new_status_up = new_status.upper()
        if new_status_up not in VALID_INCIDENT_STATUSES:
            raise ValueError(f"Invalid incident status '{new_status}'. Permitted: {VALID_INCIDENT_STATUSES}")

        now = datetime.now(timezone.utc).isoformat()
        resolved_at = now if new_status_up in [INCIDENT_RESOLVED, INCIDENT_CLOSED] else None

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE operational_incidents
                    SET status = ?, resolved_at = COALESCE(?, resolved_at),
                        notes = notes || ' | ' || ?
                    WHERE incident_id = ?
                """, (new_status_up, resolved_at, notes, incident_id))
                conn.commit()

                cur.execute("""
                    SELECT incident_id, decision_id, alert_id, corridor_id,
                           geofence_id, status, assigned_force, route_bypass,
                           priority_score, created_at, resolved_at, notes
                    FROM operational_incidents WHERE incident_id = ?
                """, (incident_id,))
                r = cur.fetchone()
                if not r:
                    raise KeyError(f"Incident '{incident_id}' not found")
                return self._row_to_dict(r)
            finally:
                conn.close()

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT incident_id, decision_id, alert_id, corridor_id,
                           geofence_id, status, assigned_force, route_bypass,
                           priority_score, created_at, resolved_at, notes
                    FROM operational_incidents WHERE incident_id = ?
                """, (incident_id,))
                r = cur.fetchone()
                if not r:
                    return None
                return self._row_to_dict(r)
            finally:
                conn.close()

    def list_incidents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                if status:
                    cur.execute("""
                        SELECT incident_id, decision_id, alert_id, corridor_id,
                               geofence_id, status, assigned_force, route_bypass,
                               priority_score, created_at, resolved_at, notes
                        FROM operational_incidents WHERE status = ?
                        ORDER BY priority_score DESC
                    """, (status.upper(),))
                else:
                    cur.execute("""
                        SELECT incident_id, decision_id, alert_id, corridor_id,
                               geofence_id, status, assigned_force, route_bypass,
                               priority_score, created_at, resolved_at, notes
                        FROM operational_incidents
                        ORDER BY priority_score DESC
                    """)
                rows = cur.fetchall()
                return [self._row_to_dict(r) for r in rows]
            finally:
                conn.close()

    def _row_to_dict(self, r: tuple) -> Dict[str, Any]:
        return {
            "incident_id": r[0],
            "decision_id": r[1],
            "alert_id": r[2],
            "corridor_id": r[3],
            "geofence_id": r[4],
            "status": r[5],
            "assigned_force": r[6],
            "route_bypass": r[7],
            "priority_score": r[8],
            "created_at": r[9],
            "resolved_at": r[10],
            "notes": r[11]
        }


INCIDENT_MANAGER = IncidentManager()
