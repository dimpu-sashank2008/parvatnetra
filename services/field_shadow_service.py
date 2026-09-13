# -*- coding: utf-8 -*-
"""
services/field_shadow_service.py
================================
PARVAT NETRA • PAHAD AI — Operational Field Shadow Operations Runtime
---------------------------------------------------------------------
Executes supervised multi-modal geotechnical and event risk assessments on
monitored corridors in FIELD_SHADOW_ACTIVE mode.

Safety Invariant:
  All public siren broadcasts and civilian alert dispatches are STRICTLY SUPPRESSED
  under disposition: "SUPPRESSED_FIELD_SHADOW_TRIAL".
  Complete decision matrices, FoS, CRI, and bypass routes are archived to `field_shadow_log`.
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

from engine.corridor_registry import CORRIDOR_REGISTRY

logger = logging.getLogger("FIELD_SHADOW_SERVICE")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)


class FieldShadowService:
    """Evaluates corridor hazard telemetry and logs shadow decisions without public siren dispatch."""

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
                    CREATE TABLE IF NOT EXISTS field_shadow_log (
                        shadow_id TEXT PRIMARY KEY,
                        corridor_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        fos REAL NOT NULL,
                        event_probability REAL NOT NULL,
                        cri REAL NOT NULL,
                        alert_level TEXT NOT NULL,
                        advisory TEXT NOT NULL,
                        siren_disposition TEXT NOT NULL,
                        bypass_route TEXT NOT NULL,
                        telemetry_snapshot TEXT NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_shadow_corr ON field_shadow_log(corridor_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_shadow_ts ON field_shadow_log(timestamp)")
                conn.commit()
            finally:
                conn.close()

    def evaluate_corridor_risk(
        self,
        corridor_id: str,
        telemetry: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates corridor FoS, Event Probability, and CRI in supervised shadow mode.
        """
        corridor = CORRIDOR_REGISTRY.get_corridor(corridor_id)
        if not corridor:
            raise KeyError(f"Corridor {corridor_id} not registered")

        telem = telemetry or {}

        # 1. Physics Factor of Safety (FoS) estimation
        pore_pressure_kpa = float(telem.get("pore_pressure_kpa", 15.0))
        slope_deg = corridor.slope
        # Basic infinite slope mechanics response: baseline FoS ~ 1.5, dropping with pore pressure
        fos = max(0.65, round(1.55 - (pore_pressure_kpa / 80.0) * 0.70, 3))

        # 2. Landslide Event Model Probability (separate classifier model)
        rain_24h = float(telem.get("rain_24h_mm", 45.0))
        tilt_deg = float(telem.get("tilt_deflection_deg", 0.08))
        prob_score = min(0.98, max(0.02, (rain_24h / 150.0) * 0.5 + (tilt_deg / 2.0) * 0.4))
        event_probability = round(prob_score, 3)

        # 3. Composite Risk Index (CRI, 0-100)
        # Geotechnical hazard scales from 0 at FoS >= 1.6 to 1.0 at FoS <= 1.0 (limit equilibrium failure)
        geotech_hazard = max(0.0, min(1.0, (1.60 - fos) / 0.60))
        cri = min(100.0, max(0.0, round((event_probability * 50.0) + (geotech_hazard * 50.0), 1)))

        # 4. Multi-threshold Level Determination
        if fos < 1.05 or event_probability >= 0.75 or cri >= 75.0:
            alert_level = "RED_CRITICAL"
            advisory = "Imminent slope failure detected. Immediate convoy diversion recommended."
        elif fos < 1.25 or event_probability >= 0.50 or cri >= 50.0:
            alert_level = "AMBER_WARNING"
            advisory = "Significant stability degradation. Restrict heavy transit across slope."
        elif fos < 1.45 or event_probability >= 0.25 or cri >= 30.0:
            alert_level = "YELLOW_WATCH"
            advisory = "Elevated moisture detected. Intensify telemetry polling."
        else:
            alert_level = "GREEN_NORMAL"
            advisory = "Corridor slope equilibrium within baseline tolerances."

        # 5. Safety Invariant: Siren Suppression
        siren_disposition = "SUPPRESSED_FIELD_SHADOW_TRIAL"

        # 6. Evacuation / Bypass Route recommendation
        evac_routes = corridor.evacuation_routes
        bypass_route = evac_routes[0].get("name", "Standard Highway Alignment") if evac_routes else "No alternate route"

        shadow_id = f"SHADOW-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "shadow_id": shadow_id,
            "corridor_id": corridor_id,
            "timestamp": now,
            "fos": fos,
            "event_probability": event_probability,
            "cri": cri,
            "alert_level": alert_level,
            "advisory": advisory,
            "siren_disposition": siren_disposition,
            "bypass_route": bypass_route,
            "telemetry_snapshot": telem,
            "operational_mode": "FIELD_SHADOW_ACTIVE",
            "safety_gate": "PUBLIC_SIREN_DISPATCH_LOCKED"
        }

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO field_shadow_log (
                        shadow_id, corridor_id, timestamp, fos, event_probability,
                        cri, alert_level, advisory, siren_disposition, bypass_route,
                        telemetry_snapshot
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    shadow_id, corridor_id, now, fos, event_probability,
                    cri, alert_level, advisory, siren_disposition, bypass_route,
                    json.dumps(telem)
                ))
                conn.commit()
            finally:
                conn.close()

        logger.info(f"Field shadow evaluated for {corridor_id}: CRI={cri}, Level={alert_level}, Disposition={siren_disposition}")
        return record

    def get_shadow_audit_logs(
        self,
        corridor_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieves recent shadow evaluation records."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                if corridor_id:
                    cur.execute("""
                        SELECT shadow_id, corridor_id, timestamp, fos, event_probability,
                               cri, alert_level, advisory, siren_disposition, bypass_route,
                               telemetry_snapshot
                        FROM field_shadow_log
                        WHERE corridor_id = ?
                        ORDER BY timestamp DESC LIMIT ?
                    """, (corridor_id, limit))
                else:
                    cur.execute("""
                        SELECT shadow_id, corridor_id, timestamp, fos, event_probability,
                               cri, alert_level, advisory, siren_disposition, bypass_route,
                               telemetry_snapshot
                        FROM field_shadow_log
                        ORDER BY timestamp DESC LIMIT ?
                    """, (limit,))

                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "shadow_id": r[0],
                        "corridor_id": r[1],
                        "timestamp": r[2],
                        "fos": r[3],
                        "event_probability": r[4],
                        "cri": r[5],
                        "alert_level": r[6],
                        "advisory": r[7],
                        "siren_disposition": r[8],
                        "bypass_route": r[9],
                        "telemetry_snapshot": json.loads(r[10])
                    })
                return results
            finally:
                conn.close()

    def get_shadow_status(self) -> Dict[str, Any]:
        logs = self.get_shadow_audit_logs(limit=10)
        return {
            "mode": "FIELD_SHADOW_ACTIVE",
            "public_siren_dispatch": "SUPPRESSED",
            "cap_alerts_dispatch": "SUPPRESSED",
            "total_evaluations_logged": len(logs),
            "recent_evaluations": logs[:5]
        }


FIELD_SHADOW_SERVICE = FieldShadowService()
