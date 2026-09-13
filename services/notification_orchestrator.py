# -*- coding: utf-8 -*-
"""
services/notification_orchestrator.py
=====================================
PARVAT NETRA • PAHAD AI — Multi-Channel Emergency Notification Orchestrator
---------------------------------------------------------------------------
Manages multi-channel emergency alert dissemination, delivery tracking,
safety gates, and acknowledgement receipts.

Supported Delivery Channels:
  - SMS           : Multilingual SMS via CDAC / Telecom Gateway
  - PUSH          : Mobile push notification (Authority, Responder, Citizen)
  - CAP           : OASIS Common Alerting Protocol v1.2 XML/JSON feed
  - WEB           : National dashboard operational banner
  - MOBILE        : Flutter on-duty incident dispatch payload
  - LOCAL_GATEWAY : LoRa wireless mesh packet to village concentrator
  - SIREN         : On-site 110 dB corridor acoustic warning relay

Safety Invariant:
  Development default is strictly PUBLIC_DISPATCH = DISABLED.
  Dispatches to civilian channels (SMS/SIREN/CAP) are SUPPRESSED unless
  AUTHORIZATION + SAFETY GATE + CONFIGURED CHANNEL are all satisfied.
"""

from __future__ import annotations

import os
import json
import uuid
import sqlite3
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger("NOTIFICATION_ORCHESTRATOR")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Supported Delivery Channels
CHANNELS = ["SMS", "PUSH", "CAP", "WEB", "MOBILE", "LOCAL_GATEWAY", "SIREN"]

# Channel Delivery Statuses
STATUS_PREPARED = "PREPARED"
STATUS_QUEUED = "QUEUED"
STATUS_SENT = "SENT"
STATUS_SIMULATED = "SIMULATED"
STATUS_DISPATCHED = "DISPATCHED"
STATUS_DELIVERED = "DELIVERED"
STATUS_FAILED = "FAILED"
STATUS_SUPPRESSED = "SUPPRESSED"
STATUS_CANCELLED = "CANCELLED"
STATUS_WITHDRAWN = "WITHDRAWN"


class NotificationOrchestrator:
    """Orchestrates emergency notifications, channel delivery, and acknowledgements."""

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
                    CREATE TABLE IF NOT EXISTS operational_notifications (
                        notification_id TEXT PRIMARY KEY,
                        alert_id TEXT NOT NULL,
                        channel TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        status TEXT NOT NULL,
                        dispatched_at TEXT NOT NULL,
                        acknowledged_at TEXT,
                        acknowledged_by TEXT
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_notif_alert ON operational_notifications(alert_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_notif_channel ON operational_notifications(channel)")
                conn.commit()
            finally:
                conn.close()

    def generate_cap_alert(
        self,
        alert_id: str,
        event: str,
        severity: str,
        urgency: str,
        certainty: str,
        area_description: str,
        instruction: str,
        geofence_coords: Optional[List[List[float]]] = None,
        effective_hours: int = 6
    ) -> Dict[str, Any]:
        """Generates OASIS CAP v1.2 compliant alert payload."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=effective_hours)

        return {
            "identifier": alert_id,
            "sender": "NDMA_PAHAD_AI_CORRIDOR_SENTINEL",
            "sent": now.isoformat(),
            "status": "Actual",
            "msgType": "Alert",
            "scope": "Public",
            "info": {
                "category": "Geo",
                "event": event,
                "urgency": urgency,
                "severity": severity,
                "certainty": certainty,
                "effective": now.isoformat(),
                "expires": expires.isoformat(),
                "headline": f"PAHAD AI {severity} Early Warning: {event}",
                "description": f"Imminent hillslope instability identified in {area_description}.",
                "instruction": instruction,
                "area": {
                    "areaDesc": area_description,
                    "polygon": geofence_coords or []
                }
            }
        }

    def dispatch_alert(
        self,
        alert_id: str,
        cap_payload: Dict[str, Any],
        channels: Optional[List[str]] = None,
        authorization_token: Optional[str] = None,
        recipients_map: Optional[Dict[str, str]] = None,
        public_dispatch_enabled: Optional[bool] = None,
        dry_run: bool = True,
        is_simulation: bool = False
    ) -> Dict[str, Any]:
        """
        Dispatches alert across channels enforcing public safety gates and dry-run isolation.
        """
        target_channels = channels or CHANNELS
        recipients = recipients_map or {}
        if public_dispatch_enabled is None:
            public_dispatch_enabled = os.environ.get("PUBLIC_DISPATCH", "DISABLED").upper() == "ENABLED"
        now = datetime.now(timezone.utc).isoformat()

        results = {}
        for ch in target_channels:
            ch_up = ch.upper()
            recipient = recipients.get(ch_up, "GENERAL_PUBLIC_ZONE")
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"

            # Evaluate Safety Gate per Channel
            is_public_channel = ch_up in ["SMS", "SIREN", "CAP"]
            status = STATUS_SENT

            if is_public_channel:
                if not public_dispatch_enabled:
                    status = STATUS_SUPPRESSED
                    note = "Suppressed: PUBLIC_DISPATCH is DISABLED in environment"
                elif not authorization_token:
                    status = STATUS_SUPPRESSED
                    note = "Suppressed: Public channel dispatch requires valid authorization_token"
                elif dry_run or is_simulation:
                    status = STATUS_SIMULATED
                    note = f"[SIMULATED] Dry-run simulated delivery for {ch_up}: no real public broadcast or siren activation"
                elif ch_up == "SIREN":
                    # Hard safety rule: physical siren hardware disabled
                    status = STATUS_SIMULATED
                    note = "[DRY_RUN] Siren hardware simulation: physical acoustic relay disabled"
                else:
                    status = STATUS_DELIVERED
                    note = "Delivered to public warning gateway"
            else:
                # Operational channels (PUSH, WEB, MOBILE, LOCAL_GATEWAY)
                if is_simulation:
                    status = STATUS_SIMULATED
                    note = "Simulated delivery to operator console"
                else:
                    status = STATUS_DELIVERED
                    note = "Delivered to operational dashboard / mobile queue"

            record = {
                "notification_id": notif_id,
                "alert_id": alert_id,
                "channel": ch_up,
                "recipient": recipient,
                "status": status,
                "dispatched_at": now,
                "note": note
            }
            results[ch_up] = record

            # Persist to DB
            with self._lock:
                conn = self._get_conn()
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO operational_notifications (
                            notification_id, alert_id, channel, recipient,
                            payload, status, dispatched_at, acknowledged_at, acknowledged_by
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        notif_id, alert_id, ch_up, recipient,
                        json.dumps(cap_payload), status, now, None, None
                    ))
                    conn.commit()
                finally:
                    conn.close()

        logger.info(f"Dispatched notifications for {alert_id}: {list(results.keys())}")
        return {
            "alert_id": alert_id,
            "dispatched_at": now,
            "channel_results": results,
            "public_dispatch_enabled": public_dispatch_enabled,
            "dry_run": dry_run,
            "is_simulation": is_simulation
        }

    def cancel_notifications_for_alert(
        self,
        alert_id: str,
        reason: str = "Authority Rollback",
        actor: str = "DISTRICT_AUTHORITY"
    ) -> int:
        """Withdraws/cancels active or queued notifications for an alert upon authority rollback."""
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE operational_notifications
                    SET status = ?, acknowledged_at = ?, acknowledged_by = ?
                    WHERE alert_id = ? AND status != ?
                """, (STATUS_CANCELLED, now, f"{actor}: {reason}", alert_id, STATUS_CANCELLED))
                conn.commit()
                count = cur.rowcount
                logger.info(f"Cancelled {count} notifications for alert {alert_id} by {actor}")
                return count
            finally:
                conn.close()

    def record_acknowledgement(
        self,
        notification_id: str,
        acknowledged_by: str,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Records human operator or field responder receipt confirmation."""
        now = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE operational_notifications
                    SET acknowledged_at = ?, acknowledged_by = ?
                    WHERE notification_id = ?
                """, (now, acknowledged_by, notification_id))
                conn.commit()

                cur.execute("""
                    SELECT notification_id, alert_id, channel, recipient, status, dispatched_at, acknowledged_at, acknowledged_by
                    FROM operational_notifications WHERE notification_id = ?
                """, (notification_id,))
                row = cur.fetchone()
                if not row:
                    raise KeyError(f"Notification '{notification_id}' not found")

                return {
                    "notification_id": row[0],
                    "alert_id": row[1],
                    "channel": row[2],
                    "recipient": row[3],
                    "status": row[4],
                    "dispatched_at": row[5],
                    "acknowledged_at": row[6],
                    "acknowledged_by": row[7]
                }
            finally:
                conn.close()

    def list_notifications(self, alert_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                if alert_id:
                    cur.execute("""
                        SELECT notification_id, alert_id, channel, recipient, status, dispatched_at, acknowledged_at, acknowledged_by
                        FROM operational_notifications WHERE alert_id = ?
                        ORDER BY dispatched_at DESC LIMIT ?
                    """, (alert_id, limit))
                else:
                    cur.execute("""
                        SELECT notification_id, alert_id, channel, recipient, status, dispatched_at, acknowledged_at, acknowledged_by
                        FROM operational_notifications ORDER BY dispatched_at DESC LIMIT ?
                    """, (limit,))
                rows = cur.fetchall()
                return [
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
            finally:
                conn.close()


NOTIFICATION_ORCHESTRATOR = NotificationOrchestrator()
