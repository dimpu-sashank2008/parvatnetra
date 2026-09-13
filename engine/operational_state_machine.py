# -*- coding: utf-8 -*-
"""
engine/operational_state_machine.py
===================================
PARVAT NETRA • PAHAD AI — Real-Time Supervised Operational State Machine
------------------------------------------------------------------------
Governs the end-to-end operational lifecycle from continuous sensor monitoring
through anomaly detection, corroboration, authority review, public alert dispatch,
field response, and final closure.

Canonical Lifecycle:
  MONITORING
  -> ANOMALY_DETECTED
  -> PAHAD_EVALUATING
  -> CORROBORATION_PENDING
  -> AUTHORITY_REVIEW
  -> WARNING_AUTHORIZED
  -> PUBLIC_DISPATCH
  -> FIELD_RESPONSE
  -> ACKNOWLEDGED
  -> RESOLVED
  -> CLOSED

Side / Termination States:
  SUPPRESSED | CANCELLED | EXPIRED
"""

from __future__ import annotations

import os
import json
import uuid
import sqlite3
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger("OPERATIONAL_STATE_MACHINE")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Canonical Operational States
STATE_MONITORING = "MONITORING"
STATE_ANOMALY_DETECTED = "ANOMALY_DETECTED"
STATE_PAHAD_EVALUATING = "PAHAD_EVALUATING"
STATE_CORROBORATION_PENDING = "CORROBORATION_PENDING"
STATE_AUTHORITY_REVIEW = "AUTHORITY_REVIEW"
STATE_WARNING_AUTHORIZED = "WARNING_AUTHORIZED"
STATE_PUBLIC_DISPATCH = "PUBLIC_DISPATCH"
STATE_FIELD_RESPONSE = "FIELD_RESPONSE"
STATE_ACKNOWLEDGED = "ACKNOWLEDGED"
STATE_RESOLVED = "RESOLVED"
STATE_CLOSED = "CLOSED"

# Side States
STATE_SUPPRESSED = "SUPPRESSED"
STATE_CANCELLED = "CANCELLED"
STATE_EXPIRED = "EXPIRED"

VALID_OPERATIONAL_STATES: Set[str] = {
    STATE_MONITORING,
    STATE_ANOMALY_DETECTED,
    STATE_PAHAD_EVALUATING,
    STATE_CORROBORATION_PENDING,
    STATE_AUTHORITY_REVIEW,
    STATE_WARNING_AUTHORIZED,
    STATE_PUBLIC_DISPATCH,
    STATE_FIELD_RESPONSE,
    STATE_ACKNOWLEDGED,
    STATE_RESOLVED,
    STATE_CLOSED,
    STATE_SUPPRESSED,
    STATE_CANCELLED,
    STATE_EXPIRED
}

# Permitted Lifecycle Transition Graph
PERMITTED_TRANSITIONS: Dict[str, Set[str]] = {
    STATE_MONITORING: {STATE_ANOMALY_DETECTED, STATE_SUPPRESSED},
    STATE_ANOMALY_DETECTED: {STATE_PAHAD_EVALUATING, STATE_CANCELLED, STATE_SUPPRESSED},
    STATE_PAHAD_EVALUATING: {STATE_CORROBORATION_PENDING, STATE_CANCELLED, STATE_SUPPRESSED},
    STATE_CORROBORATION_PENDING: {STATE_AUTHORITY_REVIEW, STATE_SUPPRESSED, STATE_CANCELLED},
    STATE_AUTHORITY_REVIEW: {STATE_WARNING_AUTHORIZED, STATE_FIELD_RESPONSE, STATE_CANCELLED, STATE_SUPPRESSED, STATE_EXPIRED},
    STATE_WARNING_AUTHORIZED: {STATE_PUBLIC_DISPATCH, STATE_FIELD_RESPONSE, STATE_CANCELLED, STATE_SUPPRESSED},
    STATE_PUBLIC_DISPATCH: {STATE_FIELD_RESPONSE, STATE_ACKNOWLEDGED, STATE_CANCELLED},
    STATE_FIELD_RESPONSE: {STATE_ACKNOWLEDGED, STATE_RESOLVED, STATE_AUTHORITY_REVIEW},
    STATE_ACKNOWLEDGED: {STATE_FIELD_RESPONSE, STATE_RESOLVED, STATE_CLOSED},
    STATE_RESOLVED: {STATE_CLOSED, STATE_MONITORING},
    STATE_CLOSED: {STATE_MONITORING},
    STATE_SUPPRESSED: {STATE_MONITORING},
    STATE_CANCELLED: {STATE_MONITORING},
    STATE_EXPIRED: {STATE_MONITORING}
}


class OperationalStateMachine:
    """Thread-safe state machine governing monitored hazard entities."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._current_states: Dict[str, str] = {}
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
                    CREATE TABLE IF NOT EXISTS operational_state_transitions (
                        transition_id TEXT PRIMARY KEY,
                        entity_id TEXT NOT NULL,
                        previous_state TEXT NOT NULL,
                        new_state TEXT NOT NULL,
                        actor TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        authorization TEXT,
                        timestamp TEXT NOT NULL,
                        metadata TEXT
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_op_entity ON operational_state_transitions(entity_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_op_state ON operational_state_transitions(new_state)")
                conn.commit()

                # Hydrate latest states
                cur.execute("""
                    SELECT entity_id, new_state
                    FROM operational_state_transitions
                    ORDER BY timestamp ASC
                """)
                for r in cur.fetchall():
                    self._current_states[r[0]] = r[1]
            finally:
                conn.close()

    def get_state(self, entity_id: str) -> str:
        with self._lock:
            return self._current_states.get(entity_id, STATE_MONITORING)

    def is_valid_transition(self, current_state: str, target_state: str) -> bool:
        if current_state == target_state:
            return True
        allowed = PERMITTED_TRANSITIONS.get(current_state, set())
        return target_state in allowed

    def transition(
        self,
        entity_id: str,
        new_state: str,
        actor: str,
        reason: str,
        authorization: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validates and executes a formal state machine transition, logging it permanently."""
        new_state = new_state.upper()
        if new_state not in VALID_OPERATIONAL_STATES:
            raise ValueError(f"Unknown operational state '{new_state}'")

        with self._lock:
            current_state = self._current_states.get(entity_id, STATE_MONITORING)
            if not self.is_valid_transition(current_state, new_state):
                raise ValueError(
                    f"Illegal operational transition for {entity_id}: "
                    f"'{current_state}' -> '{new_state}'. Permitted: {PERMITTED_TRANSITIONS.get(current_state)}"
                )

            # Special validation: PUBLIC_DISPATCH requires explicit authorization
            if new_state == STATE_PUBLIC_DISPATCH and not authorization:
                raise PermissionError("Transition to PUBLIC_DISPATCH requires valid authority authorization token")

            transition_id = f"OPTR-{uuid.uuid4().hex[:8].upper()}"
            now = datetime.now(timezone.utc).isoformat()
            meta_json = json.dumps(metadata or {})

            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO operational_state_transitions (
                        transition_id, entity_id, previous_state, new_state,
                        actor, reason, authorization, timestamp, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transition_id, entity_id, current_state, new_state,
                    actor, reason, authorization, now, meta_json
                ))
                conn.commit()
            finally:
                conn.close()

            self._current_states[entity_id] = new_state
            logger.info(f"Entity {entity_id}: '{current_state}' -> '{new_state}' by {actor}. Reason: {reason}")

            return {
                "transition_id": transition_id,
                "entity_id": entity_id,
                "previous_state": current_state,
                "new_state": new_state,
                "actor": actor,
                "reason": reason,
                "authorization": authorization,
                "timestamp": now,
                "metadata": metadata or {}
            }

    def get_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """Retrieves append-only chronological transition history for an entity."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT transition_id, entity_id, previous_state, new_state,
                           actor, reason, authorization, timestamp, metadata
                    FROM operational_state_transitions
                    WHERE entity_id = ?
                    ORDER BY timestamp ASC
                """, (entity_id,))
                rows = cur.fetchall()
                return [
                    {
                        "transition_id": r[0],
                        "entity_id": r[1],
                        "previous_state": r[2],
                        "new_state": r[3],
                        "actor": r[4],
                        "reason": r[5],
                        "authorization": r[6],
                        "timestamp": r[7],
                        "metadata": json.loads(r[8]) if r[8] else {}
                    }
                    for r in rows
                ]
            finally:
                conn.close()

    def list_active_entities(self) -> Dict[str, str]:
        with self._lock:
            return dict(self._current_states)


OPERATIONAL_STATE_MACHINE = OperationalStateMachine()
