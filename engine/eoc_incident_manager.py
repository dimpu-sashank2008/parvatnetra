# -*- coding: utf-8 -*-
"""
engine/eoc_incident_manager.py
==============================
PARVAT NETRA — PAHAD AI — EOC Persistent Incident Manager & Prioritization Engine
---------------------------------------------------------------------------------
Checkpoint 8-03 & 8-04:
Persistent EOC incident management supporting the full operational lifecycle:
  NEW -> TRIAGED -> FIELD_VERIFICATION -> AUTHORITY_REVIEW -> AUTHORIZED
      -> DISPATCHED -> ACKNOWLEDGED -> MONITORING -> RESOLVED
  (Plus: REJECTED, CANCELLED, EXPIRED)

Enforces 18 required schema fields, tamper-evident SHA-256 audit chaining,
and weighted multi-factor incident queue prioritization.
"""

from __future__ import annotations

import os
import json
import uuid
import time
import hashlib
import sqlite3
import logging
import threading
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("EOC_INCIDENT_MANAGER")

SQLITE_DB_PATH = os.environ.get(
    "EOC_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Canonical Lifecycle States
STATE_NEW = "NEW"
STATE_TRIAGED = "TRIAGED"
STATE_FIELD_VERIFICATION = "FIELD_VERIFICATION"
STATE_AUTHORITY_REVIEW = "AUTHORITY_REVIEW"
STATE_AUTHORIZED = "AUTHORIZED"
STATE_DISPATCHED = "DISPATCHED"
STATE_ACKNOWLEDGED = "ACKNOWLEDGED"
STATE_MONITORING = "MONITORING"
STATE_RESOLVED = "RESOLVED"

# Terminal / Alternative States
STATE_REJECTED = "REJECTED"
STATE_CANCELLED = "CANCELLED"
STATE_EXPIRED = "EXPIRED"

VALID_STATES = {
    STATE_NEW,
    STATE_TRIAGED,
    STATE_FIELD_VERIFICATION,
    STATE_AUTHORITY_REVIEW,
    STATE_AUTHORIZED,
    STATE_DISPATCHED,
    STATE_ACKNOWLEDGED,
    STATE_MONITORING,
    STATE_RESOLVED,
    STATE_REJECTED,
    STATE_CANCELLED,
    STATE_EXPIRED,
}

PERMITTED_TRANSITIONS: Dict[str, Set[str]] = {
    STATE_NEW: {STATE_TRIAGED, STATE_CANCELLED, STATE_REJECTED},
    STATE_TRIAGED: {STATE_FIELD_VERIFICATION, STATE_AUTHORITY_REVIEW, STATE_CANCELLED, STATE_REJECTED},
    STATE_FIELD_VERIFICATION: {STATE_AUTHORITY_REVIEW, STATE_TRIAGED, STATE_CANCELLED, STATE_REJECTED},
    STATE_AUTHORITY_REVIEW: {STATE_AUTHORIZED, STATE_REJECTED, STATE_FIELD_VERIFICATION, STATE_EXPIRED, STATE_CANCELLED},
    STATE_AUTHORIZED: {STATE_DISPATCHED, STATE_CANCELLED},
    STATE_DISPATCHED: {STATE_ACKNOWLEDGED, STATE_MONITORING, STATE_CANCELLED},
    STATE_ACKNOWLEDGED: {STATE_MONITORING, STATE_RESOLVED, STATE_CANCELLED},
    STATE_MONITORING: {STATE_RESOLVED, STATE_FIELD_VERIFICATION, STATE_AUTHORITY_REVIEW, STATE_CANCELLED},
    STATE_RESOLVED: {STATE_MONITORING},  # Can reopen if re-triggered
    STATE_REJECTED: set(),
    STATE_CANCELLED: set(),
    STATE_EXPIRED: {STATE_AUTHORITY_REVIEW, STATE_CANCELLED},
}


@dataclass
class EOCIncident:
    # Exactly the 18 required fields from Checkpoint 8-03
    incident_id: str
    sector_id: str
    created_at: str
    risk_score: float
    risk_band: str
    model_probability: float
    FoS: float
    rainfall: float
    seismic_state: str
    sensor_state: str
    signal_agreement: str
    data_quality: float
    provenance: str
    recommended_action: str
    incident_status: str
    assigned_authority: str
    assigned_field_team: str
    geofence_radius: float
    audit_hash: str

    # Extended operational context metadata
    description: str = ""
    latitude: float = 27.3300
    longitude: float = 88.6100
    population_at_risk: int = 4200
    road_criticality: float = 95.0
    corridor_name: str = "NH-10 (Sikkim Lifeline KM 48)"
    history: List[Dict[str, Any]] = field(default_factory=list)

    def compute_hash(self, prev_hash: str = "GENESIS_HASH") -> str:
        payload = (
            f"{self.incident_id}:{self.sector_id}:{self.incident_status}:"
            f"{self.risk_score}:{self.model_probability}:{self.FoS}:"
            f"{self.rainfall}:{self.signal_agreement}:{prev_hash}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Ensure display projection fields are attached (Checkpoint 8-04)
        d["display_projection"] = {
            "ai_prediction": f"Event Prob: {self.model_probability*100:.1f}% ({self.risk_band})",
            "signal_agreement": self.signal_agreement,
            "data_quality": f"{self.data_quality*100:.1f}% Validated",
            "provenance": self.provenance,
            "authority_state": self.incident_status,
        }
        return d


class EOCIncidentManager:
    """Persistent EOC Incident Repository & Multi-Criteria Queue Prioritizer."""

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
                    CREATE TABLE IF NOT EXISTS eoc_incidents (
                        incident_id TEXT PRIMARY KEY,
                        sector_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        risk_score REAL NOT NULL,
                        risk_band TEXT NOT NULL,
                        model_probability REAL NOT NULL,
                        FoS REAL NOT NULL,
                        rainfall REAL NOT NULL,
                        seismic_state TEXT NOT NULL,
                        sensor_state TEXT NOT NULL,
                        signal_agreement TEXT NOT NULL,
                        data_quality REAL NOT NULL,
                        provenance TEXT NOT NULL,
                        recommended_action TEXT NOT NULL,
                        incident_status TEXT NOT NULL,
                        assigned_authority TEXT NOT NULL,
                        assigned_field_team TEXT NOT NULL,
                        geofence_radius REAL NOT NULL,
                        audit_hash TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_eoc_status ON eoc_incidents(incident_status)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_eoc_sector ON eoc_incidents(sector_id)")
                conn.commit()
            finally:
                conn.close()

    def create_incident(
        self,
        sector_id: str,
        risk_score: float,
        risk_band: str,
        model_probability: float,
        FoS: float,
        rainfall: float,
        seismic_state: str = "QUIET",
        sensor_state: str = "HEALTHY",
        signal_agreement: str = "2-of-3 Corroborated",
        data_quality: float = 0.95,
        provenance: str = "[SIMULATED]",
        recommended_action: str = "INSPECT",
        assigned_authority: str = "DISTRICT_MAGISTRATE_PAKYONG",
        assigned_field_team: str = "BRO_TASK_FORCE_KM48",
        geofence_radius: float = 15.0,
        incident_id: Optional[str] = None,
        description: str = "",
        latitude: float = 27.3300,
        longitude: float = 88.6100,
        population_at_risk: int = 4200,
        road_criticality: float = 95.0,
        corridor_name: str = "NH-10 (Sikkim Lifeline KM 48)"
    ) -> EOCIncident:
        """Creates and persists an EOC incident in NEW state with SHA-256 audit hash."""
        now_iso = datetime.now(timezone.utc).isoformat()
        inc_id = incident_id or f"INC-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"

        initial_history = [{
            "timestamp": now_iso,
            "transition": "INITIAL_CREATION",
            "from_state": "NONE",
            "to_state": STATE_NEW,
            "actor": "PAHAD_EOC_INTELLIGENCE",
            "note": f"Incident initialized with CRI={risk_score:.1f}, FoS={FoS:.3f}, Rain={rainfall:.1f}mm"
        }]

        incident = EOCIncident(
            incident_id=inc_id,
            sector_id=sector_id,
            created_at=now_iso,
            risk_score=float(risk_score),
            risk_band=risk_band,
            model_probability=float(model_probability),
            FoS=float(FoS),
            rainfall=float(rainfall),
            seismic_state=seismic_state,
            sensor_state=sensor_state,
            signal_agreement=signal_agreement,
            data_quality=float(data_quality),
            provenance=provenance,
            recommended_action=recommended_action,
            incident_status=STATE_NEW,
            assigned_authority=assigned_authority,
            assigned_field_team=assigned_field_team,
            geofence_radius=float(geofence_radius),
            audit_hash="",
            description=description or f"Hillslope instability incident along {corridor_name}",
            latitude=latitude,
            longitude=longitude,
            population_at_risk=population_at_risk,
            road_criticality=road_criticality,
            corridor_name=corridor_name,
            history=initial_history,
        )

        incident.audit_hash = incident.compute_hash(prev_hash="GENESIS_INCIDENT_CHAIN")
        self._save(incident)
        logger.info(f"Created persistent EOC Incident: {inc_id} [{incident.incident_status}]")
        return incident

    def _save(self, incident: EOCIncident) -> None:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                payload = json.dumps({
                    "description": incident.description,
                    "latitude": incident.latitude,
                    "longitude": incident.longitude,
                    "population_at_risk": incident.population_at_risk,
                    "road_criticality": incident.road_criticality,
                    "corridor_name": incident.corridor_name,
                    "history": incident.history,
                })
                cur.execute("""
                    INSERT INTO eoc_incidents (
                        incident_id, sector_id, created_at, risk_score, risk_band,
                        model_probability, FoS, rainfall, seismic_state, sensor_state,
                        signal_agreement, data_quality, provenance, recommended_action,
                        incident_status, assigned_authority, assigned_field_team,
                        geofence_radius, audit_hash, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(incident_id) DO UPDATE SET
                        risk_score=excluded.risk_score,
                        risk_band=excluded.risk_band,
                        model_probability=excluded.model_probability,
                        FoS=excluded.FoS,
                        rainfall=excluded.rainfall,
                        seismic_state=excluded.seismic_state,
                        sensor_state=excluded.sensor_state,
                        signal_agreement=excluded.signal_agreement,
                        data_quality=excluded.data_quality,
                        provenance=excluded.provenance,
                        recommended_action=excluded.recommended_action,
                        incident_status=excluded.incident_status,
                        assigned_authority=excluded.assigned_authority,
                        assigned_field_team=excluded.assigned_field_team,
                        geofence_radius=excluded.geofence_radius,
                        audit_hash=excluded.audit_hash,
                        payload_json=excluded.payload_json
                """, (
                    incident.incident_id,
                    incident.sector_id,
                    incident.created_at,
                    incident.risk_score,
                    incident.risk_band,
                    incident.model_probability,
                    incident.FoS,
                    incident.rainfall,
                    incident.seismic_state,
                    incident.sensor_state,
                    incident.signal_agreement,
                    incident.data_quality,
                    incident.provenance,
                    incident.recommended_action,
                    incident.incident_status,
                    incident.assigned_authority,
                    incident.assigned_field_team,
                    incident.geofence_radius,
                    incident.audit_hash,
                    payload
                ))
                conn.commit()
            finally:
                conn.close()

    def get_incident(self, incident_id: str) -> Optional[EOCIncident]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT incident_id, sector_id, created_at, risk_score, risk_band,
                           model_probability, FoS, rainfall, seismic_state, sensor_state,
                           signal_agreement, data_quality, provenance, recommended_action,
                           incident_status, assigned_authority, assigned_field_team,
                           geofence_radius, audit_hash, payload_json
                    FROM eoc_incidents WHERE incident_id = ?
                """, (incident_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_incident(row)
            finally:
                conn.close()

    def _row_to_incident(self, row: Tuple[Any, ...]) -> EOCIncident:
        payload = json.loads(row[19]) if row[19] else {}
        return EOCIncident(
            incident_id=row[0],
            sector_id=row[1],
            created_at=row[2],
            risk_score=row[3],
            risk_band=row[4],
            model_probability=row[5],
            FoS=row[6],
            rainfall=row[7],
            seismic_state=row[8],
            sensor_state=row[9],
            signal_agreement=row[10],
            data_quality=row[11],
            provenance=row[12],
            recommended_action=row[13],
            incident_status=row[14],
            assigned_authority=row[15],
            assigned_field_team=row[16],
            geofence_radius=row[17],
            audit_hash=row[18],
            description=payload.get("description", ""),
            latitude=payload.get("latitude", 27.3300),
            longitude=payload.get("longitude", 88.6100),
            population_at_risk=payload.get("population_at_risk", 4200),
            road_criticality=payload.get("road_criticality", 95.0),
            corridor_name=payload.get("corridor_name", "NH-10 (Sikkim Lifeline KM 48)"),
            history=payload.get("history", []),
        )

    def transition_state(
        self,
        incident_id: str,
        target_state: str,
        actor_role: str,
        actor_id: str,
        note: str = "",
        force: bool = False
    ) -> Tuple[bool, str, Optional[EOCIncident]]:
        """
        Transitions an incident along its authorized lifecycle.
        Validates permitted state transitions and updates tamper-evident audit hash.
        """
        incident = self.get_incident(incident_id)
        if not incident:
            return False, f"Incident {incident_id} not found", None

        curr_state = incident.incident_status
        target_state = target_state.upper()

        if target_state not in VALID_STATES:
            return False, f"Invalid target state: {target_state}", incident

        if not force and target_state not in PERMITTED_TRANSITIONS.get(curr_state, set()):
            return False, f"Illegal transition from {curr_state} to {target_state}", incident

        now_iso = datetime.now(timezone.utc).isoformat()
        transition_record = {
            "timestamp": now_iso,
            "transition": f"{curr_state}_TO_{target_state}",
            "from_state": curr_state,
            "to_state": target_state,
            "actor_role": actor_role,
            "actor_id": actor_id,
            "note": note or f"State transitioned to {target_state}"
        }
        incident.history.append(transition_record)
        incident.incident_status = target_state
        incident.audit_hash = incident.compute_hash(prev_hash=incident.audit_hash)

        self._save(incident)
        logger.info(f"Transitioned incident {incident_id}: {curr_state} -> {target_state} by {actor_role} ({actor_id})")
        return True, f"Successfully transitioned to {target_state}", incident

    def calculate_priority(self, incident: EOCIncident) -> float:
        """
        Checkpoint 8-04: Multi-criteria queue prioritization score (0 - 100).
        Evaluates CRI, population at risk, response time, road criticality,
        model confidence, data quality, and time since detection.
        """
        # 1. Base CRI / Risk Score contribution (weight: 0.30)
        cri_component = min(100.0, max(0.0, incident.risk_score)) * 0.30

        # 2. Model Confidence contribution (weight: 0.20)
        model_component = min(100.0, max(0.0, incident.model_probability * 100.0)) * 0.20

        # 3. Road Criticality contribution (weight: 0.15)
        road_component = min(100.0, max(0.0, incident.road_criticality)) * 0.15

        # 4. Population at Risk contribution (weight: 0.15, normalized to 10k max)
        pop_normalized = min(100.0, (incident.population_at_risk / 10000.0) * 100.0)
        pop_component = pop_normalized * 0.15

        # 5. Data Quality contribution (weight: 0.10)
        quality_component = min(100.0, max(0.0, incident.data_quality * 100.0)) * 0.10

        # 6. Elapsed Detection Time Urgency (weight: 0.10)
        try:
            created_dt = datetime.fromisoformat(incident.created_at.replace("Z", "+00:00"))
            elapsed_hours = (datetime.now(timezone.utc) - created_dt).total_seconds() / 3600.0
            urgency_normalized = min(100.0, elapsed_hours * 10.0)
        except Exception:
            urgency_normalized = 50.0
        urgency_component = urgency_normalized * 0.10

        total_priority = (
            cri_component +
            model_component +
            road_component +
            pop_component +
            quality_component +
            urgency_component
        )
        return round(total_priority, 2)

    def list_incidents(
        self,
        status: Optional[str] = None,
        sector_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Returns prioritized incident list with display projections."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                query = """
                    SELECT incident_id, sector_id, created_at, risk_score, risk_band,
                           model_probability, FoS, rainfall, seismic_state, sensor_state,
                           signal_agreement, data_quality, provenance, recommended_action,
                           incident_status, assigned_authority, assigned_field_team,
                           geofence_radius, audit_hash, payload_json
                    FROM eoc_incidents
                """
                params: List[Any] = []
                clauses: List[str] = []
                if status:
                    clauses.append("incident_status = ?")
                    params.append(status.upper())
                if sector_id:
                    clauses.append("sector_id = ?")
                    params.append(sector_id)
                if clauses:
                    query += " WHERE " + " AND ".join(clauses)

                cur.execute(query, tuple(params))
                rows = cur.fetchall()
            finally:
                conn.close()

        incidents: List[Tuple[float, Dict[str, Any]]] = []
        for row in rows:
            inc = self._row_to_incident(row)
            prio = self.calculate_priority(inc)
            inc_dict = inc.to_dict()
            inc_dict["priority_score"] = prio
            incidents.append((prio, inc_dict))

        # Sort descending by priority_score
        incidents.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in incidents[:limit]]


# Singleton EOC Incident Manager instance
EOC_INCIDENT_MANAGER = EOCIncidentManager()
