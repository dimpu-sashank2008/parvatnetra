# -*- coding: utf-8 -*-
"""
engine/pahad_decision_store.py
==============================
PARVAT NETRA • PAHAD AI — Authoritative Operational Decision Record Store
-------------------------------------------------------------------------
Evaluates multi-modal inputs, assesses data freshness, detects Out-Of-Distribution (OOD)
features, executes corroboration, and records immutable decision records.

Operational Safeguards:
  1. Stale Data: Telemetry exceeding TTL reduces confidence penalty.
  2. OOD Detection: Inputs outside physical or historical envelopes (e.g. rainfall > 400mm/24h)
     force confidence = REDUCED and mandate human authority review.
  3. Safety Gate: Decision determines whether alert is safe for authority elevation.
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

from engine.pahad_corroboration import PAHAD_CORROBORATION

logger = logging.getLogger("PAHAD_DECISION_STORE")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)


class DecisionRecordStore:
    """Thread-safe persistent decision registry for PAHAD risk evaluations."""

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
                    CREATE TABLE IF NOT EXISTS pahad_decisions (
                        decision_id TEXT PRIMARY KEY,
                        sector_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        risk TEXT NOT NULL,
                        fos REAL,
                        probability REAL,
                        confidence REAL NOT NULL,
                        model_version TEXT NOT NULL,
                        dataset_version TEXT NOT NULL,
                        input_provenance TEXT NOT NULL,
                        freshness TEXT NOT NULL,
                        signals TEXT NOT NULL,
                        safety_gate_result TEXT NOT NULL,
                        recommended_action TEXT NOT NULL,
                        is_ood INTEGER NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_dec_sec ON pahad_decisions(sector_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_dec_ts ON pahad_decisions(timestamp)")
                conn.commit()
            finally:
                conn.close()

    def check_ood(self, features: Dict[str, Any]) -> tuple[bool, str]:
        """
        Detects Out-Of-Distribution (OOD) operational inputs outside training/physics domain.
        """
        rain_24h = float(features.get("rain_24h_mm", 0.0) or 0.0)
        pore_pressure = float(features.get("pore_pressure_kpa", 0.0) or 0.0)
        tilt = float(features.get("tilt_deg", 0.0) or 0.0)
        slope = float(features.get("slope_deg", 40.0) or 40.0)

        ood_reasons = []
        if rain_24h > 400.0:
            ood_reasons.append(f"Rainfall ({rain_24h:.1f}mm/24h) exceeds extreme monsoon ceiling")
        if pore_pressure > 180.0:
            ood_reasons.append(f"Pore pressure ({pore_pressure:.1f}kPa) exceeds sensor saturation boundary")
        if tilt > 15.0:
            ood_reasons.append(f"Surface tilt ({tilt:.1f}°) indicates total structural dislocation")
        if slope > 70.0:
            ood_reasons.append(f"Slope angle ({slope:.1f}°) exceeds infinite slope geotechnical model")

        if ood_reasons:
            return True, "; ".join(ood_reasons)
        return False, "IN_DISTRIBUTION"

    def evaluate_and_record(
        self,
        sector_id: str,
        observations: Dict[str, Any],
        model_version: str = "v3.1.0-gbdt",
        dataset_version: str = "v3.1-real-ner"
    ) -> Dict[str, Any]:
        """
        Executes multi-signal evaluation, checks OOD & freshness, and stores decision record.
        """
        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        # 1. Corroboration Engine Check
        corrob_res = PAHAD_CORROBORATION.evaluate_signals(observations)

        # 2. Extract Key Metrics
        fos = observations.get("fos")
        fos_val = float(fos) if fos is not None else 1.50
        prob = observations.get("event_probability")
        prob_val = float(prob) if prob is not None else 0.15

        # 3. Freshness Assessment
        freshness_status = observations.get("freshness_status", "FRESH")
        confidence_penalty = 0.0
        if freshness_status == "AGING":
            confidence_penalty = 0.15
        elif freshness_status in ["STALE", "UNAVAILABLE"]:
            confidence_penalty = 0.40

        # 4. Out-Of-Distribution (OOD) Check
        is_ood, ood_reason = self.check_ood(observations)
        if is_ood:
            confidence_penalty = max(confidence_penalty, 0.50)

        base_confidence = 0.90
        confidence = max(0.10, round(base_confidence - confidence_penalty, 2))

        # 5. Risk Classification
        if (fos_val < 1.05 or prob_val >= 0.75) and corrob_res["is_corroborated"]:
            risk = "CRITICAL"
        elif (fos_val < 1.25 or prob_val >= 0.50) and corrob_res["is_corroborated"]:
            risk = "HIGH"
        elif fos_val < 1.40 or prob_val >= 0.30:
            risk = "MODERATE"
        else:
            risk = "LOW"

        # 6. Safety Gate and Action Determination
        has_abnormal_signal = len(corrob_res.get("participating_abnormal_groups", [])) > 0

        if is_ood:
            safety_gate = "HOLD_MANDATORY_HUMAN_REVIEW"
            action = "ESCALATE_OOD_TO_AUTHORITY"
        elif not corrob_res["is_corroborated"] and (risk in ["CRITICAL", "HIGH"] or has_abnormal_signal):
            safety_gate = "HOLD_UNCONFIRMED_ANOMALY"
            action = "REQUEST_FIELD_VERIFICATION"
        elif corrob_res["is_corroborated"] and risk in ["CRITICAL", "HIGH"]:
            safety_gate = "PASSED_CORROBORATED"
            action = "READY_FOR_AUTHORITY_REVIEW"
        else:
            safety_gate = "PASSED_NOMINAL"
            action = "CONTINUE_MONITORING"

        record = {
            "decision_id": decision_id,
            "sector_id": sector_id,
            "timestamp": now,
            "risk": risk,
            "fos": fos_val,
            "probability": prob_val,
            "confidence": confidence,
            "model_version": model_version,
            "dataset_version": dataset_version,
            "input_provenance": observations.get("provenance", "LIVE"),
            "freshness": freshness_status,
            "signals": corrob_res,
            "safety_gate_result": safety_gate,
            "recommended_action": action,
            "is_ood": is_ood,
            "ood_reason": ood_reason
        }

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO pahad_decisions (
                        decision_id, sector_id, timestamp, risk, fos,
                        probability, confidence, model_version, dataset_version,
                        input_provenance, freshness, signals, safety_gate_result,
                        recommended_action, is_ood
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    decision_id, sector_id, now, risk, fos_val, prob_val,
                    confidence, model_version, dataset_version,
                    observations.get("provenance", "LIVE"), freshness_status,
                    json.dumps(corrob_res), safety_gate, action, 1 if is_ood else 0
                ))
                conn.commit()
            finally:
                conn.close()

        logger.info(f"Recorded PAHAD decision {decision_id} for {sector_id}: Risk={risk}, Confidence={confidence}, OOD={is_ood}")
        return record

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT decision_id, sector_id, timestamp, risk, fos,
                           probability, confidence, model_version, dataset_version,
                           input_provenance, freshness, signals, safety_gate_result,
                           recommended_action, is_ood
                    FROM pahad_decisions WHERE decision_id = ?
                """, (decision_id,))
                r = cur.fetchone()
                if not r:
                    return None
                return self._row_to_decision(r)
            finally:
                conn.close()

    def list_decisions(self, sector_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                if sector_id:
                    cur.execute("""
                        SELECT decision_id, sector_id, timestamp, risk, fos,
                               probability, confidence, model_version, dataset_version,
                               input_provenance, freshness, signals, safety_gate_result,
                               recommended_action, is_ood
                        FROM pahad_decisions WHERE sector_id = ?
                        ORDER BY timestamp DESC LIMIT ?
                    """, (sector_id, limit))
                else:
                    cur.execute("""
                        SELECT decision_id, sector_id, timestamp, risk, fos,
                               probability, confidence, model_version, dataset_version,
                               input_provenance, freshness, signals, safety_gate_result,
                               recommended_action, is_ood
                        FROM pahad_decisions
                        ORDER BY timestamp DESC LIMIT ?
                    """, (limit,))
                rows = cur.fetchall()
                return [self._row_to_decision(r) for r in rows]
            finally:
                conn.close()

    def _row_to_decision(self, r: tuple) -> Dict[str, Any]:
        return {
            "decision_id": r[0],
            "sector_id": r[1],
            "timestamp": r[2],
            "risk": r[3],
            "fos": r[4],
            "probability": r[5],
            "confidence": r[6],
            "model_version": r[7],
            "dataset_version": r[8],
            "input_provenance": r[9],
            "freshness": r[10],
            "signals": json.loads(r[11]),
            "safety_gate_result": r[12],
            "recommended_action": r[13],
            "is_ood": bool(r[14])
        }


PAHAD_DECISION_STORE = DecisionRecordStore()
