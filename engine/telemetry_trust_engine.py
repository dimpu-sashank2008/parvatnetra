# -*- coding: utf-8 -*-
"""
engine/telemetry_trust_engine.py
================================
PARVAT NETRA • In-Situ Telemetry Trust Scoring & 3-Tier Time Synchronization Engine
-----------------------------------------------------------------------------------
Phase V4.7 Transparent Telemetry Quality Assessment:
Evaluates identity, calibration, physical range, sequence monotonicity,
communication links, and 3-tier clock synchronization (Sensor -> Gateway -> Backend).

Produces deterministic:
TELEMETRY_TRUST = VERIFIED | DEGRADED | UNVERIFIED
with explicit scientific reason codes. No black-box AI confidence scores.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from engine.sensor_acceptance_engine import (
    GLOBAL_ACCEPTANCE_ENGINE,
    STATE_UNVERIFIED_IDENTITY
)
from engine.sensor_calibration import (
    GLOBAL_CALIBRATION_ENGINE,
    STATUS_CALIBRATED,
    STATUS_CALIBRATION_DUE,
    STATUS_INVALID_CALIBRATION
)
from services.telemetry_contract import (
    PHYSICAL_SENSOR_LIMITS,
    NER_LAT_MIN,
    NER_LAT_MAX,
    NER_LON_MIN,
    NER_LON_MAX,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_INVALID
)

logger = logging.getLogger("TELEMETRY_TRUST")

# Telemetry Trust States
TRUST_VERIFIED = "VERIFIED"
TRUST_DEGRADED = "DEGRADED"
TRUST_UNVERIFIED = "UNVERIFIED"

# Canonical Reason Codes
REASON_OUT_OF_RANGE = "OUT_OF_RANGE"
REASON_CLOCK_DRIFT = "CLOCK_DRIFT"
REASON_FUTURE_TIMESTAMP = "FUTURE_TIMESTAMP"
REASON_DUPLICATE = "DUPLICATE"
REASON_SEQUENCE_GAP = "SEQUENCE_GAP"
REASON_CRC_FAILURE = "CRC_FAILURE"
REASON_SENSOR_OFFLINE = "SENSOR_OFFLINE"
REASON_CALIBRATION_EXPIRED = "CALIBRATION_EXPIRED"
REASON_CALIBRATION_MISSING = "CALIBRATION_MISSING"
REASON_NOISE_EXCESS = "NOISE_EXCESS"
REASON_COMMUNICATION_FAILURE = "COMMUNICATION_FAILURE"
REASON_MISSING_METADATA = "MISSING_METADATA"
REASON_IDENTITY_UNVERIFIED = "IDENTITY_UNVERIFIED"
REASON_PROVENANCE_COUNTERFEIT = "PROVENANCE_COUNTERFEIT"
REASON_OUT_OF_BOUNDS = "OUT_OF_BOUNDS"

# Tolerances in seconds
MAX_FUTURE_TIMESTAMP_SECONDS = 30.0
MAX_CLOCK_OFFSET_WARNING_SECONDS = 120.0
MAX_TRANSPORT_LATENCY_SECONDS = 300.0


@dataclass
class TimeSyncMetrics:
    sensor_timestamp_iso: str
    gateway_received_at_iso: str
    backend_received_at_iso: str
    transport_latency_ms: float
    clock_offset_ms: float
    total_latency_ms: float
    is_future_drift: bool = False
    is_excessive_drift: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrustAssessment:
    sensor_id: str
    telemetry_trust: str  # VERIFIED, DEGRADED, UNVERIFIED
    reasons: List[str]
    score_pct: float      # Transparent composite compliance percentage (0-100)
    identity_valid: bool
    calibration_valid: bool
    timestamp_valid: bool
    range_valid: bool
    sequence_valid: bool
    communication_valid: bool
    freshness_valid: bool
    time_sync: Optional[TimeSyncMetrics] = None
    assessed_at_utc: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.time_sync:
            d["time_sync"] = self.time_sync.to_dict()
        return d


class TelemetryTrustEngine:
    """
    Evaluates in-situ observations against 7 objective hardware & physical criteria:
    1. Identity validity
    2. Calibration validity
    3. Timestamp & 3-tier sync
    4. Physical engineering bounds
    5. Sequence monotonicity
    6. RF/LoRa link health
    7. Freshness window compliance
    """

    def __init__(self, acceptance_engine=None, calibration_engine=None):
        self.acceptance_engine = acceptance_engine or GLOBAL_ACCEPTANCE_ENGINE
        self.calibration_engine = calibration_engine or GLOBAL_CALIBRATION_ENGINE

    def compute_3tier_time_sync(
        self,
        sensor_timestamp_str: str,
        gateway_received_at_str: Optional[str] = None,
        backend_received_at_str: Optional[str] = None
    ) -> TimeSyncMetrics:
        """
        Calculates transport latency, clock offset, and drift across sensor -> gateway -> backend.
        """
        now = datetime.now(timezone.utc)
        backend_dt = datetime.fromisoformat(backend_received_at_str.replace("Z", "+00:00")) if backend_received_at_str else now
        gateway_dt = datetime.fromisoformat(gateway_received_at_str.replace("Z", "+00:00")) if gateway_received_at_str else backend_dt

        sensor_str_clean = str(sensor_timestamp_str).replace("Z", "+00:00")
        sensor_dt = datetime.fromisoformat(sensor_str_clean)

        transport_latency_ms = max(0.0, (backend_dt - gateway_dt).total_seconds() * 1000.0)
        clock_offset_ms = (gateway_dt - sensor_dt).total_seconds() * 1000.0
        total_latency_ms = (backend_dt - sensor_dt).total_seconds() * 1000.0

        future_drift = (sensor_dt - backend_dt).total_seconds() > MAX_FUTURE_TIMESTAMP_SECONDS
        excessive_drift = abs(clock_offset_ms) > (MAX_CLOCK_OFFSET_WARNING_SECONDS * 1000.0)

        return TimeSyncMetrics(
            sensor_timestamp_iso=sensor_dt.isoformat(),
            gateway_received_at_iso=gateway_dt.isoformat(),
            backend_received_at_iso=backend_dt.isoformat(),
            transport_latency_ms=round(transport_latency_ms, 2),
            clock_offset_ms=round(clock_offset_ms, 2),
            total_latency_ms=round(total_latency_ms, 2),
            is_future_drift=future_drift,
            is_excessive_drift=excessive_drift
        )

    def assess_observation(
        self,
        observation: Dict[str, Any],
        previous_sequence: int = -1,
        freshness_threshold_seconds: float = 900.0
    ) -> TrustAssessment:
        """
        Conducts multi-factor telemetry trust evaluation.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        sensor_id = str(observation.get("sensor_id", "")).strip()
        reasons: List[str] = []

        # 1. Identity Check
        identity_valid = False
        ident = self.acceptance_engine.get_sensor_identity(sensor_id)
        if ident and ident.get("identity_verified"):
            identity_valid = True
        else:
            reasons.append(REASON_IDENTITY_UNVERIFIED)

        # 2. Calibration Check
        calibration_valid = False
        cal_rec = self.calibration_engine.get_calibration(sensor_id)
        if cal_rec:
            if cal_rec.status == STATUS_CALIBRATED:
                calibration_valid = True
            elif cal_rec.status == STATUS_CALIBRATION_DUE:
                reasons.append(REASON_CALIBRATION_EXPIRED)
            else:
                reasons.append(REASON_CALIBRATION_MISSING)
        else:
            reasons.append(REASON_CALIBRATION_MISSING)

        # 3. Timestamp & Time Sync Check
        timestamp_valid = False
        time_sync = None
        ts_raw = observation.get("timestamp_utc") or observation.get("received_at")
        if not ts_raw:
            reasons.append(REASON_MISSING_METADATA)
        else:
            try:
                time_sync = self.compute_3tier_time_sync(
                    sensor_timestamp_str=str(ts_raw),
                    gateway_received_at_str=observation.get("gateway_received_at"),
                    backend_received_at_str=observation.get("received_at")
                )
                if time_sync.is_future_drift:
                    reasons.append(REASON_FUTURE_TIMESTAMP)
                elif time_sync.is_excessive_drift:
                    reasons.append(REASON_CLOCK_DRIFT)
                else:
                    timestamp_valid = True
            except Exception:
                reasons.append(REASON_MISSING_METADATA)

        # 4. Physical Range & Geographic Bounds Check
        range_valid = False
        val = observation.get("value")
        if val is None:
            reasons.append(REASON_MISSING_METADATA)
        else:
            try:
                f_val = float(val)
                stype = str(observation.get("sensor_type", "")).lower()
                # Find physical limit key
                lim_key = "piezometer"
                for k in PHYSICAL_SENSOR_LIMITS:
                    if k in stype:
                        lim_key = k
                        break
                min_l, max_l, _, _ = PHYSICAL_SENSOR_LIMITS[lim_key]
                if min_l <= f_val <= max_l:
                    range_valid = True
                else:
                    reasons.append(REASON_OUT_OF_RANGE)
            except Exception:
                reasons.append(REASON_OUT_OF_RANGE)

        # 5. Sequence Monotonicity Check
        sequence_valid = False
        seq = observation.get("sequence_number")
        if seq is None:
            reasons.append(REASON_MISSING_METADATA)
        else:
            try:
                i_seq = int(seq)
                if previous_sequence >= 0:
                    if i_seq == previous_sequence:
                        reasons.append(REASON_DUPLICATE)
                    elif i_seq < previous_sequence:
                        reasons.append(REASON_SEQUENCE_GAP)
                    elif i_seq > previous_sequence + 1:
                        # Dropped packets, but monotonic
                        sequence_valid = True
                    else:
                        sequence_valid = True
                else:
                    sequence_valid = True
            except Exception:
                reasons.append(REASON_SEQUENCE_GAP)

        # 6. Communication & Hardware Check
        communication_valid = True
        bat = observation.get("battery_voltage") or observation.get("battery_pct")
        if bat is not None:
            try:
                # Voltage < 11.0V or pct < 15%
                f_bat = float(bat)
                if (f_bat < 11.0 and f_bat > 1.0) or (f_bat < 15.0 and f_bat <= 1.0):
                    reasons.append(REASON_COMMUNICATION_FAILURE)
                    communication_valid = False
            except Exception:
                pass

        sig = observation.get("signal_strength") or observation.get("signal_rssi")
        if sig is not None:
            try:
                if float(sig) < -115.0:
                    reasons.append(REASON_COMMUNICATION_FAILURE)
                    communication_valid = False
            except Exception:
                pass

        # Check provenance counterfeit
        prov = str(observation.get("provenance", "")).upper()
        src = str(observation.get("source", "")).upper()
        if (src in ["BENCH_SIMULATOR", "SYNTHETIC", "REPLAY"]) and (prov == "LIVE"):
            reasons.append(REASON_PROVENANCE_COUNTERFEIT)

        # 7. Freshness Check
        freshness_valid = True
        if time_sync and time_sync.total_latency_ms > (freshness_threshold_seconds * 1000.0):
            reasons.append(REASON_SENSOR_OFFLINE)
            freshness_valid = False

        # Determine overall trust state and compliance score
        criteria = [
            identity_valid, calibration_valid, timestamp_valid,
            range_valid, sequence_valid, communication_valid, freshness_valid
        ]
        score_pct = round((sum(1 for c in criteria if c) / len(criteria)) * 100.0, 1)

        fatal_reasons = {
            REASON_FUTURE_TIMESTAMP,
            REASON_OUT_OF_RANGE,
            REASON_PROVENANCE_COUNTERFEIT,
            REASON_CRC_FAILURE,
            REASON_IDENTITY_UNVERIFIED
        }
        has_fatal = any(r in fatal_reasons for r in reasons)

        if has_fatal:
            trust_state = TRUST_UNVERIFIED
        elif all(criteria):
            trust_state = TRUST_VERIFIED
        else:
            trust_state = TRUST_DEGRADED

        return TrustAssessment(
            sensor_id=sensor_id,
            telemetry_trust=trust_state,
            reasons=reasons,
            score_pct=score_pct,
            identity_valid=identity_valid,
            calibration_valid=calibration_valid,
            timestamp_valid=timestamp_valid,
            range_valid=range_valid,
            sequence_valid=sequence_valid,
            communication_valid=communication_valid,
            freshness_valid=freshness_valid,
            time_sync=time_sync,
            assessed_at_utc=now_iso
        )


# Global singleton trust engine
GLOBAL_TELEMETRY_TRUST_ENGINE = TelemetryTrustEngine()
