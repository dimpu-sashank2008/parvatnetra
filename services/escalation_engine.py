# -*- coding: utf-8 -*-
"""
services/escalation_engine.py
=============================
PARVAT NETRA • PAHAD AI — Timeout-Based Automated Escalation Engine
-------------------------------------------------------------------
Monitors unacknowledged critical emergency notifications. If an on-duty
operator fails to acknowledge receipt within the configured timeout window,
the alert is automatically escalated up the authority hierarchy:

  FIELD_OPERATOR -> DISTRICT_AUTHORITY -> STATE_AUTHORITY -> ADMIN
"""

from __future__ import annotations

import os
import uuid
import sqlite3
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from services.notification_orchestrator import NOTIFICATION_ORCHESTRATOR
from engine.operational_state_machine import OPERATIONAL_STATE_MACHINE, STATE_AUTHORITY_REVIEW

logger = logging.getLogger("ESCALATION_ENGINE")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

DEFAULT_TIMEOUT_SECONDS = int(os.getenv("ESCALATION_TIMEOUT_SECONDS", "300"))  # 5 minutes

ESCALATION_TIERS = [
    "FIELD_OPERATOR",
    "DISTRICT_AUTHORITY",
    "STATE_AUTHORITY",
    "ADMIN"
]


class EscalationEngine:
    """Monitors notification acknowledgement timestamps and executes multi-tier escalation."""

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
                    CREATE TABLE IF NOT EXISTS escalation_events (
                        escalation_id TEXT PRIMARY KEY,
                        alert_id TEXT NOT NULL,
                        notification_id TEXT,
                        from_tier TEXT NOT NULL,
                        to_tier TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        elapsed_seconds REAL NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_esc_alert ON escalation_events(alert_id)")
                conn.commit()
            finally:
                conn.close()

    def check_and_escalate_unacknowledged(
        self,
        timeout_seconds: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Scans all dispatched operational notifications and escalates those exceeding timeout.
        """
        timeout = timeout_seconds if timeout_seconds is not None else DEFAULT_TIMEOUT_SECONDS
        now_dt = datetime.now(timezone.utc)
        escalated_records = []

        all_notifs = []
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operational_notifications'")
                if cur.fetchone():
                    cur.execute("""
                        SELECT notification_id, alert_id, channel, recipient, status, dispatched_at, acknowledged_at, acknowledged_by
                        FROM operational_notifications ORDER BY dispatched_at DESC LIMIT 100
                    """)
                    rows = cur.fetchall()
                    all_notifs = [
                        {
                            "notification_id": r[0],
                            "alert_id": r[1],
                            "channel": r[2],
                            "recipient": r[3],
                            "status": r[4],
                            "dispatched_at": r[5],
                            "acknowledged_at": r[6],
                            "acknowledged_by": r[7]
                        }
                        for r in rows
                    ]
                else:
                    all_notifs = NOTIFICATION_ORCHESTRATOR.list_notifications(limit=100)
            except Exception:
                all_notifs = NOTIFICATION_ORCHESTRATOR.list_notifications(limit=100)
            finally:
                conn.close()

        for n in all_notifs:
            if n["status"] in ["DELIVERED", "SENT"] and not n["acknowledged_at"]:
                dispatched_dt = datetime.fromisoformat(n["dispatched_at"].replace("Z", "+00:00"))
                elapsed = (now_dt - dispatched_dt).total_seconds()

                if elapsed >= timeout:
                    from_tier = "FIELD_OPERATOR"
                    to_tier = "DISTRICT_AUTHORITY"
                    esc_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
                    now_str = now_dt.isoformat()

                    # Record escalation event
                    with self._lock:
                        conn = self._get_conn()
                        try:
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO escalation_events (
                                    escalation_id, alert_id, notification_id,
                                    from_tier, to_tier, reason, elapsed_seconds, timestamp
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                esc_id, n["alert_id"], n["notification_id"],
                                from_tier, to_tier,
                                f"Unacknowledged after {elapsed:.0f}s (Threshold: {timeout}s)",
                                elapsed, now_str
                            ))
                            conn.commit()
                        finally:
                            conn.close()

                    escalated_records.append({
                        "escalation_id": esc_id,
                        "alert_id": n["alert_id"],
                        "notification_id": n["notification_id"],
                        "from_tier": from_tier,
                        "to_tier": to_tier,
                        "elapsed_seconds": elapsed,
                        "timestamp": now_str
                    })
                    logger.warning(f"Notification {n['notification_id']} for {n['alert_id']} escalated to {to_tier} ({elapsed:.0f}s unacked)")

        return escalated_records

    def manual_escalate(
        self,
        alert_id: str,
        current_role: str,
        reason: str
    ) -> Dict[str, Any]:
        """Allows an operator to explicitly escalate an alert up the command chain."""
        curr_idx = ESCALATION_TIERS.index(current_role.upper()) if current_role.upper() in ESCALATION_TIERS else 0
        next_idx = min(len(ESCALATION_TIERS) - 1, curr_idx + 1)
        next_role = ESCALATION_TIERS[next_idx]

        esc_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO escalation_events (
                        escalation_id, alert_id, notification_id,
                        from_tier, to_tier, reason, elapsed_seconds, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    esc_id, alert_id, None,
                    current_role.upper(), next_role, reason, 0.0, now_str
                ))
                conn.commit()
            finally:
                conn.close()

        logger.info(f"Manual escalation {esc_id} for {alert_id} from {current_role} to {next_role}: {reason}")
        return {
            "escalation_id": esc_id,
            "alert_id": alert_id,
            "from_tier": current_role.upper(),
            "to_tier": next_role,
            "reason": reason,
            "timestamp": now_str
        }

    def list_escalations(self, alert_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                if alert_id:
                    cur.execute("""
                        SELECT escalation_id, alert_id, notification_id,
                               from_tier, to_tier, reason, elapsed_seconds, timestamp
                        FROM escalation_events WHERE alert_id = ?
                        ORDER BY timestamp DESC
                    """, (alert_id,))
                else:
                    cur.execute("""
                        SELECT escalation_id, alert_id, notification_id,
                               from_tier, to_tier, reason, elapsed_seconds, timestamp
                        FROM escalation_events ORDER BY timestamp DESC
                    """)
                rows = cur.fetchall()
                return [
                    {
                        "escalation_id": r[0],
                        "alert_id": r[1],
                        "notification_id": r[2],
                        "from_tier": r[3],
                        "to_tier": r[4],
                        "reason": r[5],
                        "elapsed_seconds": r[6],
                        "timestamp": r[7]
                    }
                    for r in rows
                ]
            finally:
                conn.close()


ESCALATION_ENGINE = EscalationEngine()
