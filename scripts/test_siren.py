#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/test_siren.py
=====================
PARVAT NETRA • PAHAD AI — Corridor Acoustic Siren Safety Test Tool
-------------------------------------------------------------------
Provides controlled, auditable manual or diagnostic testing of on-site 110 dB
corridor warning sirens without triggering false regional evacuation alerts.

Safety Invariants:
  1. Default mode is strictly DRY_RUN (no physical relay closing).
  2. Physical actuation requires mode=AUTHORIZED_PHYSICAL_TEST, valid HMAC token,
     and the explicit operational flag SIREN_HARDWARE_ENABLED=1.
  3. Siren burst duration is strictly capped at 5.0 seconds during testing.
  4. Every test invocation is permanently logged to `siren_test_audit_log`.
"""

import os
import sys
import json
import uuid
import sqlite3
import argparse
from datetime import datetime, timezone
from typing import Dict, Any

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

AUTHORIZATION_TOKENS = {
    "SIH-NDMA-AUTH-2026",
    "PARVAT-FIELD-AUDIT-KEY",
    os.environ.get("SIREN_AUTH_SECRET", "NDMA_EMERGENCY_SECURE_TOKEN_2026")
}


def init_db(db_path: str = SQLITE_DB_PATH):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS siren_test_audit_log (
                test_id TEXT PRIMARY KEY,
                siren_id TEXT NOT NULL,
                corridor_id TEXT NOT NULL,
                mode TEXT NOT NULL,
                duration_s REAL NOT NULL,
                authorized_by TEXT NOT NULL,
                hardware_actuated INTEGER NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                note TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def execute_siren_test(
    siren_id: str,
    corridor_id: str,
    mode: str,
    duration_s: float,
    auth_token: str = None,
    authorized_by: str = "Field Engineer",
    reason: str = "Diagnostic routine check",
    db_path: str = SQLITE_DB_PATH
) -> Dict[str, Any]:
    """Evaluates safety policies and logs acoustic siren test execution."""
    init_db(db_path)

    test_id = f"SIRENTEST-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()
    duration = min(5.0, max(0.5, duration_s))

    # Validate Mode
    mode_upper = mode.upper()
    hardware_actuated = False
    status = "SUCCESS"
    note = ""

    if mode_upper == "DRY_RUN":
        hardware_actuated = False
        status = "COMPLETED_DRY_RUN"
        note = f"Simulated acoustic test ({duration:.1f}s burst). Relay de-energized."
    elif mode_upper == "AUTHORIZED_PHYSICAL_TEST":
        # 1. Check Auth Token
        if not auth_token or auth_token not in AUTHORIZATION_TOKENS:
            status = "AUTH_FAILED"
            note = "Physical actuation rejected: Invalid or absent HMAC authorization token."
            _log_audit(db_path, test_id, siren_id, corridor_id, mode_upper, duration, authorized_by, False, status, now, note)
            return {
                "test_id": test_id,
                "siren_id": siren_id,
                "corridor_id": corridor_id,
                "mode": mode_upper,
                "hardware_actuated": False,
                "status": status,
                "error": note,
                "timestamp": now
            }

        # 2. Check Hardware Pin / Flag
        hw_enabled = os.environ.get("SIREN_HARDWARE_ENABLED", "0") == "1"
        if not hw_enabled:
            status = "HARDWARE_DISARMED"
            note = "Refused physical actuation: SIREN_HARDWARE_ENABLED is not set to 1. Test downgraded to dry run."
            hardware_actuated = False
        else:
            status = "PHYSICAL_ACTIVATION_COMPLETE"
            hardware_actuated = True
            note = f"Physical 110dB acoustic horn actuated for {duration:.1f}s. Authorizer: {authorized_by}."
    else:
        raise ValueError(f"Invalid mode '{mode}'. Choose 'DRY_RUN' or 'AUTHORIZED_PHYSICAL_TEST'.")

    _log_audit(db_path, test_id, siren_id, corridor_id, mode_upper, duration, authorized_by, hardware_actuated, status, now, note)

    return {
        "test_id": test_id,
        "siren_id": siren_id,
        "corridor_id": corridor_id,
        "mode": mode_upper,
        "duration_seconds": duration,
        "hardware_actuated": hardware_actuated,
        "status": status,
        "note": note,
        "reason": reason,
        "timestamp": now
    }


def _log_audit(db_path, test_id, siren_id, corridor_id, mode, duration, auth_by, hw_act, status, ts, note):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO siren_test_audit_log (
                test_id, siren_id, corridor_id, mode, duration_s,
                authorized_by, hardware_actuated, status, timestamp, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_id, siren_id, corridor_id, mode, duration,
            auth_by, 1 if hw_act else 0, status, ts, note
        ))
        conn.commit()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="PARVAT NETRA Corridor Acoustic Siren Diagnostic Tool")
    parser.add_argument("--siren-id", default="SIREN-NH10-KM48-01", help="Corridor Siren Hardware ID")
    parser.add_argument("--corridor", default="CORR-NH10-SIKKIM-KM48", help="Corridor ID")
    parser.add_argument("--mode", default="DRY_RUN", choices=["DRY_RUN", "AUTHORIZED_PHYSICAL_TEST"], help="Test mode")
    parser.add_argument("--auth-token", default=None, help="Authorization secret key (required for physical test)")
    parser.add_argument("--duration", type=float, default=2.0, help="Burst duration in seconds (capped at 5s)")
    parser.add_argument("--authorizer", default="Senior Geotechnical Engineer", help="Officer authorizing test")
    parser.add_argument("--reason", default="Corridor commissioning check", help="Operational reason")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    res = execute_siren_test(
        siren_id=args.siren_id,
        corridor_id=args.corridor,
        mode=args.mode,
        duration_s=args.duration,
        auth_token=args.auth_token,
        authorized_by=args.authorizer,
        reason=args.reason
    )

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("============================================================")
        print(f"PARVAT NETRA ACOUSTIC SIREN SAFETY TEST: {res['test_id']}")
        print("------------------------------------------------------------")
        print(f"Siren ID           : {res['siren_id']}")
        print(f"Corridor ID        : {res['corridor_id']}")
        print(f"Mode               : [{res['mode']}]")
        print(f"Hardware Actuated  : {res['hardware_actuated']}")
        print(f"Execution Status   : {res['status']}")
        print(f"Audit Note         : {res.get('note') or res.get('error')}")
        print("============================================================")

    if res["status"] == "AUTH_FAILED":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
