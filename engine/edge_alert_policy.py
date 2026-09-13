# -*- coding: utf-8 -*-
"""
engine/edge_alert_policy.py
===========================
PARVAT NETRA • Autonomous Edge Corridor Safety & Siren Policy
--------------------------------------------------------------
Evaluates localized geotechnical and hydrometeorological sensor observations
directly at the on-site edge gateway (e.g. NH-10 Pakyong Km 48) to trigger
immediate acoustic sirens and bypass advisories.

Critical Safety Invariant:
  Local Edge Siren != Regional Public Warning Broadcast (CAP v1.2)
  Local sirens provide zero-latency immediate tactical warning for vehicles
  and road workers in the direct runout zone when cloud backhaul is severed.
"""

from __future__ import annotations

import os
import json
import sqlite3
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("EDGE_ALERT_POLICY")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Deterministic Corridor Physical Thresholds
CORRIDOR_THRESHOLDS = {
    "pore_pressure": {"warning": 30.0, "critical": 45.0, "unit": "kPa"},
    "inclinometer_velocity": {"warning": 5.0, "critical": 15.0, "unit": "mm/day"},
    "tilt_rate": {"warning": 1.0, "critical": 2.5, "unit": "deg/day"},
    "rain_intensity": {"warning": 35.0, "critical": 50.0, "unit": "mm/hr"},
    "crack_aperture": {"warning": 10.0, "critical": 25.0, "unit": "mm"},
}


class EdgeAlertPolicy:
    """Evaluates local geotechnical thresholds and triggers immediate edge sirens."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        return sqlite3.connect(self.db_path)

    def evaluate_reading(
        self,
        measurements: Dict[str, Any],
        sector_id: str = "SK-NH10-KM48",
        gateway_id: str = "GW-NH10-KM48-01"
    ) -> Dict[str, Any]:
        """
        Evaluates a set of sensor observations against local corridor thresholds.
        Requires 1 CRITICAL or 2 WARNING signals to sound local siren.
        """
        warning_signals = []
        critical_signals = []

        for m_name, m_data in measurements.items():
            val = float(m_data.get("value", 0.0) if isinstance(m_data, dict) else m_data)

            # Match threshold
            thresh = None
            for t_key, t_val in CORRIDOR_THRESHOLDS.items():
                if t_key in m_name.lower():
                    thresh = t_val
                    break

            if thresh:
                if val >= thresh["critical"]:
                    critical_signals.append(f"{m_name} ({val} {thresh['unit']} >= {thresh['critical']})")
                elif val >= thresh["warning"]:
                    warning_signals.append(f"{m_name} ({val} {thresh['unit']} >= {thresh['warning']})")

        is_critical = len(critical_signals) >= 1 or len(warning_signals) >= 2
        is_warning = len(warning_signals) >= 1

        severity = "CRITICAL" if is_critical else ("WARNING" if is_warning else "NORMAL")
        siren_recommended = is_critical
        bypass_recommended = is_critical

        alert_record = None
        if is_critical or is_warning:
            now_iso = datetime.now(timezone.utc).isoformat()
            alert_id = f"EDGE-ALT-{int(datetime.now(timezone.utc).timestamp())}"
            triggers = critical_signals + warning_signals

            # Persist to edge_alerts table
            try:
                conn = self._get_conn()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO edge_alerts (
                        alert_id, gateway_id, sector_id, severity, trigger_source,
                        details_json, siren_activated, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert_id, gateway_id, sector_id, severity, "LOCAL_SENSOR_THRESHOLD",
                    json.dumps({"critical": critical_signals, "warning": warning_signals}),
                    1 if siren_recommended else 0, now_iso
                ))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error logging edge alert: {e}")

            alert_record = {
                "alert_id": alert_id,
                "severity": severity,
                "triggers": triggers,
                "timestamp": now_iso
            }

        return {
            "status": "EVALUATED",
            "severity": severity,
            "siren_trigger_recommended": siren_recommended,
            "siren_recommended": siren_recommended,
            "bypass_recommended": bypass_recommended,
            "critical_signals": critical_signals,
            "warning_signals": warning_signals,
            "alert_record": alert_record
        }


# Global Singleton
GLOBAL_EDGE_ALERT_POLICY = EdgeAlertPolicy()
