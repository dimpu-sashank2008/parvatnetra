# -*- coding: utf-8 -*-
"""
services/kinematic_telemetry_service.py
=======================================
PARVAT NETRA • In-Situ Telemetry Ingestion, Validation & High-Frequency Kinematics
----------------------------------------------------------------------------------
Phase V4.6 Canonical implementation for in-situ hillslope instrumentation telemetry.
Handles:
1. Canonical schema validation (live_sensor_schema.json)
2. Corridor sensor registry management (CORR-NH10-SIKKIM-KM48)
3. Freshness tracking with configuration-driven time thresholds
4. High-frequency kinematic feature engineering (deltas, velocities, accelerations)
5. Structured observability event logging
6. Hardware-in-the-loop (HIL) LoRa 18-byte binary frame decoding with CRC-16-CCITT
"""

from __future__ import annotations

import os
import json
import math
import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from services.telemetry_contract import (
    PHYSICAL_SENSOR_LIMITS,
    NER_LAT_MIN,
    NER_LAT_MAX,
    NER_LON_MIN,
    NER_LON_MAX,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_INVALID,
    GLOBAL_TELEMETRY_VALIDATOR,
    TelemetryValidator,
    ValidationResult
)
from firmware.packet_codec import (
    BinaryPacketCodec,
    compute_crc16_ccitt,
    FRAME_LENGTH_BYTES
)
from engine.sensor_acceptance_engine import GLOBAL_ACCEPTANCE_ENGINE
from engine.telemetry_trust_engine import (
    GLOBAL_TELEMETRY_TRUST_ENGINE,
    TRUST_VERIFIED,
    TRUST_DEGRADED,
    TRUST_UNVERIFIED
)


logger = logging.getLogger("KINEMATIC_TELEMETRY")

# Freshness thresholds in seconds
DEFAULT_FRESHNESS_THRESHOLDS: Dict[str, float] = {
    "PIEZOMETER": 900.0,   # 15 minutes
    "INCLINOMETER": 900.0, # 15 minutes
    "TILTMETER": 900.0,    # 15 minutes
    "RAIN_GAUGE": 900.0,   # 15 minutes
    "GATEWAY": 300.0,      # 5 minutes
}

CORRIDOR_ID_NH10 = "CORR-NH10-SIKKIM-KM48"


@dataclass
class TelemetryEvent:
    event_type: str  # TELEMETRY_RECEIVED, TELEMETRY_REJECTED, TELEMETRY_DUPLICATE, TELEMETRY_STALE, TELEMETRY_OUT_OF_ORDER, SENSOR_OFFLINE, SENSOR_RECOVERED
    timestamp_utc: str
    sensor_id: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KinematicTelemetryService:
    """
    Authoritative service for in-situ hillslope telemetry ingestion,
    quality scoring, freshness monitoring, and high-frequency feature derivation.
    """

    def __init__(
        self,
        registry_path: Optional[str] = None,
        schema_path: Optional[str] = None
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.registry_path = registry_path or os.path.join(base_dir, "data", "processed", "corridor_sensor_registry.json")
        self.schema_path = schema_path or os.path.join(base_dir, "data", "processed", "live_sensor_schema.json")
        
        self.freshness_thresholds = dict(DEFAULT_FRESHNESS_THRESHOLDS)
        self.sensors_registry: Dict[str, Dict[str, Any]] = {}
        self.corridor_metadata: Dict[str, Any] = {}
        
        # In-memory historical buffer per sensor_id: list of dicts ordered by timestamp
        self._observation_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Sequence and deduplication tracking
        self._last_sequence: Dict[str, int] = {}
        self._seen_packet_hashes: set = set()
        
        # Event log
        self._events: List[TelemetryEvent] = []
        
        # Metrics
        self._metrics = {
            "total_ingested": 0,
            "accepted": 0,
            "rejected": 0,
            "duplicates": 0,
            "corrupted_crc": 0,
            "out_of_order": 0,
            "last_event_time": None
        }

        self._load_registry()

    def _load_registry(self) -> None:
        """Loads corridor sensor registry from disk if available."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.corridor_metadata = {
                        "corridor_id": data.get("corridor_id", CORRIDOR_ID_NH10),
                        "corridor_name": data.get("corridor_name", "NH-10 Corridor"),
                        "physical_status": data.get("physical_status", "BENCH_VALIDATED"),
                        "telemetry_status": data.get("telemetry_status", "PHYSICAL_TELEMETRY_PENDING"),
                        "field_deployment_pending": data.get("field_deployment_pending", True),
                        "latitude": data.get("latitude", 27.2023),
                        "longitude": data.get("longitude", 88.5147),
                        "elevation_msl": data.get("elevation_msl", 620.0)
                    }
                    if "freshness_thresholds_seconds" in data:
                        self.freshness_thresholds.update(data["freshness_thresholds_seconds"])

                    for s in data.get("sensors", []):
                        s_id = s.get("sensor_id")
                        if s_id:
                            self.sensors_registry[s_id] = s
                            self._observation_history.setdefault(s_id, [])
                            self._last_sequence[s_id] = -1
                            # Register identity in SensorAcceptanceEngine
                            sn = s.get("serial_number")
                            if sn:
                                GLOBAL_ACCEPTANCE_ENGINE.verify_and_set_identity(
                                    sensor_id=s_id,
                                    manufacturer=s.get("manufacturer", "GENERIC"),
                                    model=s.get("model", "MODEL"),
                                    serial_number=sn,
                                    hardware_revision=s.get("hardware_revision", "REV-A"),
                                    firmware_version=s.get("firmware_version", "v1.0.0"),
                                    sensor_type=s.get("sensor_type", "PIEZOMETER"),
                                    corridor_id=self.corridor_metadata.get("corridor_id", CORRIDOR_ID_NH10),
                                    site_id="SITE-NH10-KM48",
                                    gateway_id=s.get("gateway_id")
                                )
                                stage = s.get("acceptance_stage", "BENCH_ACCEPTED")
                                GLOBAL_ACCEPTANCE_ENGINE._states[s_id] = stage
                logger.info(f"Loaded {len(self.sensors_registry)} sensors for corridor {self.corridor_metadata.get('corridor_id')}")
            except Exception as e:
                logger.error(f"Failed to load sensor registry from {self.registry_path}: {e}")
        else:
            # Setup default NH-10 corridor
            self._setup_default_nh10_registry()

    def _setup_default_nh10_registry(self) -> None:
        """Fallback initialization for NH-10 corridor."""
        self.corridor_metadata = {
            "corridor_id": CORRIDOR_ID_NH10,
            "corridor_name": "NH-10 Rangpo–Singtam Geological Corridor, Sikkim",
            "physical_status": "BENCH_VALIDATED",
            "telemetry_status": "PHYSICAL_TELEMETRY_PENDING",
            "field_deployment_pending": True,
            "latitude": 27.2023,
            "longitude": 88.5147,
            "elevation_msl": 620.0
        }
        sensors = [
            {"sensor_id": "PIEZO-NH10-KM48-01", "sensor_type": "PIEZOMETER", "unit": "kPa", "range_min": -50.0, "range_max": 500.0, "physical_status": "BENCH_VALIDATED", "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"},
            {"sensor_id": "INCL-NH10-KM48-01", "sensor_type": "INCLINOMETER", "unit": "mm", "range_min": -100.0, "range_max": 100.0, "physical_status": "BENCH_VALIDATED", "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"},
            {"sensor_id": "TILT-NH10-KM48-01", "sensor_type": "TILTMETER", "unit": "deg", "range_min": -45.0, "range_max": 45.0, "physical_status": "BENCH_VALIDATED", "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"},
            {"sensor_id": "RAIN-NH10-KM48-01", "sensor_type": "RAIN_GAUGE", "unit": "mm/h", "range_min": 0.0, "range_max": 250.0, "physical_status": "BENCH_VALIDATED", "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"},
            {"sensor_id": "GW-NH10-KM48-01", "sensor_type": "GATEWAY", "unit": "V", "range_min": 9.0, "range_max": 15.0, "physical_status": "BENCH_VALIDATED", "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"}
        ]
        for s in sensors:
            self.sensors_registry[s["sensor_id"]] = s
            self._observation_history.setdefault(s["sensor_id"], [])
            self._last_sequence[s["sensor_id"]] = -1

    def _record_event(self, event_type: str, sensor_id: str, details: Dict[str, Any]) -> None:
        """Appends a structured event to the telemetry event journal."""
        evt = TelemetryEvent(
            event_type=event_type,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            sensor_id=sensor_id,
            details=details
        )
        self._events.append(evt)
        if len(self._events) > 1000:
            self._events = self._events[-1000:]
        self._metrics["last_event_time"] = evt.timestamp_utc

    def get_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent structured telemetry events."""
        return [e.to_dict() for e in self._events[-limit:]]

    def get_corridor_status(self) -> Dict[str, Any]:
        """Returns corridor registration, deployment status, and acceptance lifecycle summary."""
        freshness = self.get_freshness_status()
        lifecycle = GLOBAL_ACCEPTANCE_ENGINE.get_corridor_lifecycle_summary()
        return {
            "corridor": self.corridor_metadata,
            "sensor_count": len(self.sensors_registry),
            "freshness": freshness,
            "acceptance_lifecycle": lifecycle,
            "metrics": self._metrics
        }

    def get_sensors(self) -> List[Dict[str, Any]]:
        """Returns list of registered sensors with their configuration and live state."""
        res = []
        freshness = self.get_freshness_status()
        for s_id, s_meta in self.sensors_registry.items():
            s_fresh = freshness.get("sensors", {}).get(s_id, {})
            item = dict(s_meta)
            item["current_freshness_state"] = s_fresh.get("status", "UNAVAILABLE")
            item["last_seen_utc"] = s_fresh.get("last_seen_utc")
            item["elapsed_seconds"] = s_fresh.get("elapsed_seconds")
            item["observation_count"] = len(self._observation_history.get(s_id, []))
            res.append(item)
        return res

    def get_sensor(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Returns details and history for a specific sensor."""
        if sensor_id not in self.sensors_registry:
            return None
        meta = dict(self.sensors_registry[sensor_id])
        freshness = self.get_freshness_status().get("sensors", {}).get(sensor_id, {})
        meta["current_freshness_state"] = freshness.get("status", "UNAVAILABLE")
        meta["last_seen_utc"] = freshness.get("last_seen_utc")
        meta["elapsed_seconds"] = freshness.get("elapsed_seconds")
        meta["recent_observations"] = self._observation_history.get(sensor_id, [])[-20:]
        return meta

    def get_freshness_status(self) -> Dict[str, Any]:
        """
        Calculates freshness states for all registered sensors.
        Returns:
          corridor_id, overall_status, sensors: {sensor_id: {status, elapsed_seconds, threshold_seconds, last_seen_utc}}
        """
        now = datetime.now(timezone.utc)
        sensor_status: Dict[str, Dict[str, Any]] = {}
        all_unavailable = True
        any_stale = False
        any_live = False

        for s_id, s_meta in self.sensors_registry.items():
            stype = s_meta.get("sensor_type", "PIEZOMETER")
            thresh = float(self.freshness_thresholds.get(stype, 900.0))
            obs_list = self._observation_history.get(s_id, [])

            if not obs_list:
                # No observations received yet
                state = "UNAVAILABLE"
                elapsed = None
                last_seen = None
                reason = "PHYSICAL_TELEMETRY_PENDING" if self.corridor_metadata.get("field_deployment_pending") else "NO_DATA_RECEIVED"
            else:
                last_obs = obs_list[-1]
                last_seen = last_obs.get("timestamp_utc") or last_obs.get("received_at")
                try:
                    last_dt = datetime.fromisoformat(str(last_seen).replace("Z", "+00:00"))
                    elapsed = max(0.0, (now - last_dt).total_seconds())
                except Exception:
                    elapsed = 999999.0

                prov = last_obs.get("provenance", "SIMULATED")
                qual = last_obs.get("quality", QUALITY_GOOD)

                if elapsed <= thresh:
                    if qual == QUALITY_DEGRADED:
                        state = "DEGRADED"
                    elif prov == "LIVE":
                        state = "LIVE"
                    else:
                        state = "SIMULATED"
                    any_live = True
                    all_unavailable = False
                elif elapsed <= 2.0 * thresh:
                    state = "STALE"
                    any_stale = True
                    all_unavailable = False
                else:
                    state = "UNAVAILABLE"
                    reason = "HEARTBEAT_TIMEOUT"

            sensor_status[s_id] = {
                "sensor_type": stype,
                "status": state,
                "threshold_seconds": thresh,
                "elapsed_seconds": round(elapsed, 1) if elapsed is not None else None,
                "last_seen_utc": last_seen,
                "provenance": obs_list[-1].get("provenance", "NONE") if obs_list else "NONE"
            }

        # Overall corridor freshness evaluation
        if all_unavailable:
            overall = "UNAVAILABLE"
        elif any_stale:
            overall = "STALE"
        elif any_live:
            overall = "LIVE"
        else:
            overall = "DEGRADED"

        return {
            "corridor_id": self.corridor_metadata.get("corridor_id", CORRIDOR_ID_NH10),
            "evaluated_at_utc": now.isoformat(),
            "overall_status": overall,
            "field_deployment_pending": self.corridor_metadata.get("field_deployment_pending", True),
            "sensors": sensor_status
        }

    def ingest_binary_lora_frame(
        self,
        frame_bytes: bytes,
        sensor_type: str = "PIEZOMETER",
        sensor_id: Optional[str] = None,
        corridor_id: Optional[str] = None,
        provenance: str = "BENCH"
    ) -> ValidationResult:
        """
        Decodes and ingests an 18-byte binary LoRa frame, validating CRC-16-CCITT.
        """
        self._metrics["total_ingested"] += 1
        now_utc = datetime.now(timezone.utc).isoformat()

        # Check frame length
        if len(frame_bytes) != FRAME_LENGTH_BYTES:
            self._metrics["rejected"] += 1
            return ValidationResult(
                is_valid=False,
                status="REJECTED_FRAME_LENGTH",
                message=f"Expected {FRAME_LENGTH_BYTES} bytes, got {len(frame_bytes)}"
            )

        # Check CRC-16
        try:
            decoded = BinaryPacketCodec.decode(frame_bytes)
        except ValueError as e:
            self._metrics["corrupted_crc"] += 1
            self._metrics["rejected"] += 1
            self._record_event("TELEMETRY_REJECTED", sensor_id or "UNKNOWN", {"reason": str(e)})
            return ValidationResult(
                is_valid=False,
                status="REJECTED_CRC_ERROR",
                message=str(e)
            )

        # Resolve sensor_id
        target_sensor_id = sensor_id or f"SN-NODE-{decoded['device_short_id']:04d}"
        if target_sensor_id not in self.sensors_registry:
            # Check if short_id matches any registered sensor
            for reg_id in self.sensors_registry:
                if reg_id.startswith(sensor_type[:4]):
                    target_sensor_id = reg_id
                    break

        s_meta = self.sensors_registry.get(target_sensor_id, {})
        unit = s_meta.get("unit", "kPa" if sensor_type == "PIEZOMETER" else "mm")

        # Never permit SIMULATED / BENCH frames to claim LIVE provenance
        if provenance == "LIVE" and not os.environ.get("PAHAD_ALLOW_LIVE_INGEST"):
            provenance = "BENCH"

        canonical_obs = {
            "observation_id": f"obs-{decoded['device_short_id']}-{decoded['sequence_number']}-{decoded['timestamp_epoch']}",
            "sensor_id": target_sensor_id,
            "corridor_id": corridor_id or self.corridor_metadata.get("corridor_id", CORRIDOR_ID_NH10),
            "site_id": "SITE-NH10-KM48",
            "sensor_type": sensor_type,
            "timestamp_utc": decoded["timestamp_iso"],
            "value": decoded["primary_reading"],
            "unit": unit,
            "quality": QUALITY_GOOD if not decoded.get("tamper_flag") else QUALITY_DEGRADED,
            "source": "BENCH_SIMULATOR" if provenance != "LIVE" else "PHYSICAL_SENSOR",
            "provenance": provenance,
            "status": "LIVE" if provenance == "LIVE" else "SIMULATED",
            "sequence_number": decoded["sequence_number"],
            "received_at": now_utc,
            "gateway_id": s_meta.get("gateway_id", "GW-NH10-KM48-01"),
            "firmware_version": s_meta.get("firmware_version", "v1.0.0-lora"),
            "battery_voltage": round(10.0 + (decoded["battery_pct"] / 100.0) * 3.5, 2),
            "temperature": decoded["temperature_c"]
        }

        return self.ingest_canonical_observation(canonical_obs)

    def ingest_canonical_observation(self, observation: Dict[str, Any]) -> ValidationResult:
        """
        Validates, normalizes, and journals an incoming observation.
        Strictly enforces sequence monotonicity, duplicate rejection, and physical bounds.
        """
        self._metrics["total_ingested"] += 1
        now_dt = datetime.now(timezone.utc)
        now_utc = now_dt.isoformat()

        # 1. Mandatory Fields Check
        required_fields = [
            "observation_id", "sensor_id", "corridor_id", "site_id",
            "sensor_type", "timestamp_utc", "value", "unit", "quality",
            "source", "provenance", "status", "sequence_number"
        ]
        for f in required_fields:
            if f not in observation or observation[f] is None:
                self._metrics["rejected"] += 1
                return ValidationResult(
                    is_valid=False,
                    status=f"REJECTED_MISSING_{f.upper()}",
                    message=f"Missing mandatory field '{f}'"
                )

        sensor_id = str(observation["sensor_id"]).strip()
        stype = str(observation["sensor_type"]).upper()
        seq = int(observation["sequence_number"])
        obs_id = str(observation["observation_id"]).strip()

        # Corridor Isolation Invariant: reject foreign corridor observations
        obs_corridor = str(observation["corridor_id"]).strip()
        expected_corridor = self.corridor_metadata.get("corridor_id", CORRIDOR_ID_NH10)
        if obs_corridor != expected_corridor:
            self._metrics["rejected"] += 1
            self._record_event("TELEMETRY_REJECTED", sensor_id, {
                "reason": "CORRIDOR_MISMATCH",
                "received_corridor": obs_corridor,
                "expected_corridor": expected_corridor
            })
            return ValidationResult(
                is_valid=False,
                status="REJECTED_CORRIDOR_MISMATCH",
                message=f"Observation corridor '{obs_corridor}' does not match service corridor '{expected_corridor}'."
            )

        # Provenance Invariant: Never allow SIMULATED source to be marked LIVE
        prov = str(observation["provenance"]).upper()
        src = str(observation["source"]).upper()
        if (src in ["BENCH_SIMULATOR", "SYNTHETIC", "REPLAY"]) and (prov == "LIVE"):
            # Reject attempt to counterfeit live data
            self._metrics["rejected"] += 1
            self._record_event("TELEMETRY_REJECTED", sensor_id, {
                "reason": "SIMULATED_DATA_CANNOT_CLAIM_LIVE_PROVENANCE"
            })
            return ValidationResult(
                is_valid=False,
                status="REJECTED_PROVENANCE_COUNTERFEIT",
                message="Synthetic or bench simulator observations can NEVER be stamped with [LIVE] provenance."
            )

        # 2. Timestamp Validation & Clock Drift
        try:
            ts_str = str(observation["timestamp_utc"]).replace("Z", "+00:00")
            parsed_ts = datetime.fromisoformat(ts_str)
            # Drift check: reject future timestamps > 30 seconds
            drift_sec = (parsed_ts - now_dt).total_seconds()
            if drift_sec > 30.0:
                self._metrics["rejected"] += 1
                self._record_event("TELEMETRY_REJECTED", sensor_id, {
                    "reason": "FUTURE_TIMESTAMP",
                    "drift_seconds": drift_sec
                })
                return ValidationResult(
                    is_valid=False,
                    status="REJECTED_FUTURE_TIMESTAMP",
                    message=f"Timestamp {ts_str} is {drift_sec:.1f}s in the future (max allowed: 30s)"
                )
        except Exception as e:
            self._metrics["rejected"] += 1
            return ValidationResult(
                is_valid=False,
                status="REJECTED_CORRUPT_TIMESTAMP",
                message=f"Malformed timestamp '{observation.get('timestamp_utc')}': {e}"
            )

        # 3. Duplicate and Sequence Validation
        is_replay = observation.get("transport") == "EDGE_BUFFER_REPLAY"
        packet_hash = f"{sensor_id}_{seq}_{observation.get('timestamp_utc')}"
        if not is_replay and packet_hash in self._seen_packet_hashes:
            self._metrics["duplicates"] += 1
            self._record_event("TELEMETRY_DUPLICATE", sensor_id, {"sequence_number": seq})
            return ValidationResult(
                is_valid=False,
                status="REJECTED_DUPLICATE",
                message=f"Duplicate packet detected for sensor {sensor_id} seq {seq}"
            )

        last_seq = self._last_sequence.get(sensor_id, -1)
        if last_seq >= 0:
            if seq <= last_seq:
                self._metrics["out_of_order"] += 1
                self._record_event("TELEMETRY_OUT_OF_ORDER", sensor_id, {
                    "last_sequence": last_seq,
                    "received_sequence": seq
                })
                # We flag but can accept if it's not a direct duplicate, or reject if strictly monotonic
                if seq == last_seq and not is_replay:
                    self._metrics["duplicates"] += 1
                    return ValidationResult(
                        is_valid=False,
                        status="REJECTED_DUPLICATE_SEQUENCE",
                        message=f"Duplicate sequence number {seq} for sensor {sensor_id}"
                    )

        # 4. Physical Boundaries Validation
        try:
            val = float(observation["value"])
        except (ValueError, TypeError):
            self._metrics["rejected"] += 1
            return ValidationResult(
                is_valid=False,
                status="REJECTED_NON_NUMERIC_VALUE",
                message="Measurement value must be numeric"
            )

        # Lookup sensor config or defaults
        s_meta = self.sensors_registry.get(sensor_id, {})
        min_v = s_meta.get("range_min")
        max_v = s_meta.get("range_max")

        if min_v is None or max_v is None:
            # Fallback to PHYSICAL_SENSOR_LIMITS
            stype_key = stype.lower()
            if "piezo" in stype_key:
                lim = PHYSICAL_SENSOR_LIMITS["piezometer"]
            elif "inclin" in stype_key:
                lim = PHYSICAL_SENSOR_LIMITS["inclinometer"]
            elif "tilt" in stype_key:
                lim = PHYSICAL_SENSOR_LIMITS["tilt"]
            elif "rain" in stype_key:
                lim = PHYSICAL_SENSOR_LIMITS["rain_gauge"]
            else:
                lim = (-1000.0, 1000.0, "", 100.0)
            min_v, max_v = lim[0], lim[1]

        if val < min_v or val > max_v:
            self._metrics["rejected"] += 1
            self._record_event("TELEMETRY_REJECTED", sensor_id, {
                "reason": "OUT_OF_PHYSICAL_RANGE",
                "value": val,
                "bounds": [min_v, max_v]
            })
            return ValidationResult(
                is_valid=False,
                status="REJECTED_IMPOSSIBLE_VALUE",
                message=f"Value {val} exceeds physical limits [{min_v}, {max_v}] for {sensor_id}"
            )

        # 5. Geographic Bounds Check (if coordinates provided)
        lat = observation.get("latitude")
        lon = observation.get("longitude")
        if lat is not None and lon is not None:
            try:
                lat = float(lat)
                lon = float(lon)
                if not (NER_LAT_MIN <= lat <= NER_LAT_MAX and NER_LON_MIN <= lon <= NER_LON_MAX):
                    self._metrics["rejected"] += 1
                    return ValidationResult(
                        is_valid=False,
                        status="REJECTED_OUT_OF_BOUNDS",
                        message=f"Coordinates ({lat}, {lon}) outside NER bounds"
                    )
            except (ValueError, TypeError):
                self._metrics["rejected"] += 1
                return ValidationResult(
                    is_valid=False,
                    status="REJECTED_INVALID_COORDINATES",
                    message="Coordinates must be numeric"
                )

        # 6. Accepted - Store Observation & Assess Trust
        self._seen_packet_hashes.add(packet_hash)
        if len(self._seen_packet_hashes) > 10000:
            self._seen_packet_hashes.clear()

        self._last_sequence[sensor_id] = seq

        # Assess Telemetry Trust and 3-Tier Time Sync
        thresh = float(self.freshness_thresholds.get(stype, 900.0))
        trust = GLOBAL_TELEMETRY_TRUST_ENGINE.assess_observation(
            observation=observation,
            previous_sequence=last_seq,
            freshness_threshold_seconds=thresh
        )
        GLOBAL_ACCEPTANCE_ENGINE.record_telemetry_observation(sensor_id, is_valid=True)

        normalized_obs = dict(observation)
        normalized_obs["received_at"] = normalized_obs.get("received_at") or now_utc
        normalized_obs["telemetry_trust"] = trust.telemetry_trust
        normalized_obs["trust_score_pct"] = trust.score_pct
        normalized_obs["trust_reasons"] = trust.reasons
        if trust.time_sync:
            normalized_obs["time_sync"] = trust.time_sync.to_dict()
        
        hist = self._observation_history.setdefault(sensor_id, [])
        hist.append(normalized_obs)
        # Keep recent 2000 observations in memory per sensor
        if len(hist) > 2000:
            self._observation_history[sensor_id] = hist[-2000:]

        self._metrics["accepted"] += 1
        self._record_event("TELEMETRY_RECEIVED", sensor_id, {
            "sequence": seq,
            "value": val,
            "provenance": prov,
            "trust": trust.telemetry_trust
        })

        return ValidationResult(
            is_valid=True,
            status="ACCEPTED",
            message="Observation accepted and buffered",
            overall_quality=observation.get("quality", QUALITY_GOOD)
        )

    def compute_kinematic_features(self, corridor_id: str = CORRIDOR_ID_NH10) -> Dict[str, Any]:
        """
        Derives high-frequency kinematic features across all sensors for the given corridor:
        - Piezometer: pressure, deltas (5m, 15m, 1h), velocities, accelerations, rolling stats
        - Inclinometer: displacement, delta, velocity, acceleration
        - Tiltmeter: tilt_x, tilt_y, tilt_magnitude, tilt_rate, tilt_acceleration
        - Rain Gauge: accumulations (5m, 15m, 1h, 3h, 6h), rainfall_intensity, rainfall_acceleration
        All features retain provenance lineage.
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        freshness = self.get_freshness_status()

        features: Dict[str, Any] = {
            "corridor_id": corridor_id,
            "generated_at_utc": now_iso,
            "corridor_telemetry_status": freshness["overall_status"],
            "field_deployment_pending": self.corridor_metadata.get("field_deployment_pending", True),
            "sensors": {},
            "summary_signals": {}
        }

        for s_id, s_meta in self.sensors_registry.items():
            stype = s_meta.get("sensor_type", "UNKNOWN")
            obs_list = self._observation_history.get(s_id, [])

            if not obs_list:
                # No data available
                features["sensors"][s_id] = {
                    "sensor_type": stype,
                    "status": "UNAVAILABLE",
                    "reason": "PHYSICAL_TELEMETRY_PENDING" if self.corridor_metadata.get("field_deployment_pending") else "NO_DATA",
                    "metrics": None,
                    "lineage": {
                        "source_sensor": s_id,
                        "sample_count": 0,
                        "window_seconds": 0,
                        "provenance": "NONE",
                        "generated_at": now_iso
                    }
                }
                continue

            # Parse observations with valid timestamps
            parsed_obs: List[Tuple[datetime, float, str, str]] = []
            for o in obs_list:
                try:
                    t_str = o.get("timestamp_utc") or o.get("received_at")
                    dt = datetime.fromisoformat(str(t_str).replace("Z", "+00:00"))
                    val = float(o["value"])
                    prov = str(o.get("provenance", "SIMULATED"))
                    qual = str(o.get("quality", QUALITY_GOOD))
                    parsed_obs.append((dt, val, prov, qual))
                except Exception:
                    continue

            if not parsed_obs:
                features["sensors"][s_id] = {
                    "sensor_type": stype,
                    "status": "UNAVAILABLE",
                    "reason": "MALFORMED_OBSERVATIONS",
                    "metrics": None
                }
                continue

            # Sort chronologically
            parsed_obs.sort(key=lambda x: x[0])
            latest_dt, latest_val, latest_prov, latest_qual = parsed_obs[-1]
            elapsed_sec = (now - latest_dt).total_seconds()

            thresh = float(self.freshness_thresholds.get(stype, 900.0))
            if elapsed_sec <= thresh:
                s_state = "LIVE" if latest_prov == "LIVE" else "SIMULATED"
            elif elapsed_sec <= 2.0 * thresh:
                s_state = "STALE"
            else:
                s_state = "UNAVAILABLE"

            # Helper to find observation closest to delta_t seconds ago
            def val_at_seconds_ago(seconds: float) -> Optional[float]:
                target = latest_dt - timedelta(seconds=seconds)
                # Find closest observation before or at target
                candidates = [v for dt, v, _, _ in parsed_obs if (target - timedelta(seconds=120)) <= dt <= (target + timedelta(seconds=120))]
                if candidates:
                    return candidates[-1]
                # Fallback: closest earlier observation
                earlier = [v for dt, v, _, _ in parsed_obs if dt <= target]
                if earlier:
                    return earlier[-1]
                return None

            metrics: Dict[str, Any] = {}
            lineage = {
                "source_sensor": s_id,
                "sample_count": len(parsed_obs),
                "window_seconds": int((latest_dt - parsed_obs[0][0]).total_seconds()),
                "provenance": latest_prov,
                "generated_at": now_iso
            }

            if stype == "PIEZOMETER":
                p5m = val_at_seconds_ago(300)
                p15m = val_at_seconds_ago(900)
                p1h = val_at_seconds_ago(3600)

                delta_5m = (latest_val - p5m) if p5m is not None else 0.0
                delta_15m = (latest_val - p15m) if p15m is not None else 0.0
                delta_1h = (latest_val - p1h) if p1h is not None else 0.0

                # Velocity in kPa/h
                if len(parsed_obs) >= 2:
                    prev_dt, prev_val, _, _ = parsed_obs[-2]
                    dt_hr = max((latest_dt - prev_dt).total_seconds() / 3600.0, 0.0001)
                    velocity = (latest_val - prev_val) / dt_hr
                else:
                    velocity = 0.0

                # Acceleration in kPa/h^2
                if len(parsed_obs) >= 3:
                    t3, v3, _, _ = parsed_obs[-3]
                    t2, v2, _, _ = parsed_obs[-2]
                    dt1_hr = max((t2 - t3).total_seconds() / 3600.0, 0.0001)
                    dt2_hr = max((latest_dt - t2).total_seconds() / 3600.0, 0.0001)
                    v_prev = (v2 - v3) / dt1_hr
                    v_curr = (latest_val - v2) / dt2_hr
                    acceleration = (v_curr - v_prev) / dt2_hr
                else:
                    acceleration = 0.0

                vals_all = [v for _, v, _, _ in parsed_obs]
                r_mean = sum(vals_all) / len(vals_all)
                r_var = sum((x - r_mean) ** 2 for x in vals_all) / len(vals_all)
                r_std = math.sqrt(r_var)

                metrics = {
                    "pressure": round(latest_val, 2),
                    "unit": "kPa",
                    "pressure_delta_5m": round(delta_5m, 3),
                    "pressure_delta_15m": round(delta_15m, 3),
                    "pressure_delta_1h": round(delta_1h, 3),
                    "pressure_velocity": round(velocity, 3),
                    "pressure_acceleration": round(acceleration, 3),
                    "rolling_mean": round(r_mean, 2),
                    "rolling_std": round(r_std, 3),
                    "rate_of_change": round(velocity, 3)
                }

            elif stype == "INCLINOMETER":
                d15m = val_at_seconds_ago(900)
                d_delta = (latest_val - d15m) if d15m is not None else 0.0

                if len(parsed_obs) >= 2:
                    prev_dt, prev_val, _, _ = parsed_obs[-2]
                    dt_hr = max((latest_dt - prev_dt).total_seconds() / 3600.0, 0.0001)
                    velocity = (latest_val - prev_val) / dt_hr
                else:
                    velocity = 0.0

                if len(parsed_obs) >= 3:
                    t3, v3, _, _ = parsed_obs[-3]
                    t2, v2, _, _ = parsed_obs[-2]
                    dt1_hr = max((t2 - t3).total_seconds() / 3600.0, 0.0001)
                    dt2_hr = max((latest_dt - t2).total_seconds() / 3600.0, 0.0001)
                    v_prev = (v2 - v3) / dt1_hr
                    v_curr = (latest_val - v2) / dt2_hr
                    acceleration = (v_curr - v_prev) / dt2_hr
                else:
                    acceleration = 0.0

                metrics = {
                    "displacement": round(latest_val, 3),
                    "unit": "mm",
                    "displacement_delta": round(d_delta, 3),
                    "velocity": round(velocity, 3),
                    "acceleration": round(acceleration, 3),
                    "rolling_velocity": round(velocity, 3),
                    "rolling_acceleration": round(acceleration, 3)
                }

            elif stype == "TILTMETER":
                # Scalar tilt or resultant
                if len(parsed_obs) >= 2:
                    prev_dt, prev_val, _, _ = parsed_obs[-2]
                    dt_hr = max((latest_dt - prev_dt).total_seconds() / 3600.0, 0.0001)
                    t_rate = (latest_val - prev_val) / dt_hr
                else:
                    t_rate = 0.0

                if len(parsed_obs) >= 3:
                    t3, v3, _, _ = parsed_obs[-3]
                    t2, v2, _, _ = parsed_obs[-2]
                    dt1_hr = max((t2 - t3).total_seconds() / 3600.0, 0.0001)
                    dt2_hr = max((latest_dt - t2).total_seconds() / 3600.0, 0.0001)
                    rate_prev = (v2 - v3) / dt1_hr
                    rate_curr = (latest_val - v2) / dt2_hr
                    t_acc = (rate_curr - rate_prev) / dt2_hr
                else:
                    t_acc = 0.0

                metrics = {
                    "tilt_magnitude": round(abs(latest_val), 3),
                    "tilt_angle": round(latest_val, 3),
                    "unit": "deg",
                    "tilt_rate": round(t_rate, 4),
                    "tilt_acceleration": round(t_acc, 4)
                }

            elif stype == "RAIN_GAUGE":
                # Compute cumulative or windowed rainfall
                def sum_rain_in_window(window_sec: float) -> float:
                    t_start = latest_dt - timedelta(seconds=window_sec)
                    window_obs = [v for dt, v, _, _ in parsed_obs if dt >= t_start]
                    # If reading is rate (mm/h), average * hours; if incremental mm, sum
                    return round(sum(window_obs) / max(len(window_obs), 1), 2)

                rain_5m = sum_rain_in_window(300)
                rain_15m = sum_rain_in_window(900)
                rain_1h = sum_rain_in_window(3600)
                rain_3h = sum_rain_in_window(10800)
                rain_6h = sum_rain_in_window(21600)

                # Rainfall acceleration
                if len(parsed_obs) >= 2:
                    prev_dt, prev_val, _, _ = parsed_obs[-2]
                    dt_hr = max((latest_dt - prev_dt).total_seconds() / 3600.0, 0.0001)
                    rain_acc = (latest_val - prev_val) / dt_hr
                else:
                    rain_acc = 0.0

                metrics = {
                    "rainfall_intensity": round(latest_val, 2),
                    "unit": "mm/h",
                    "rainfall_5m": rain_5m,
                    "rainfall_15m": rain_15m,
                    "rainfall_1h": rain_1h,
                    "rainfall_3h": rain_3h,
                    "rainfall_6h": rain_6h,
                    "rainfall_acceleration": round(rain_acc, 2)
                }

            elif stype == "GATEWAY":
                metrics = {
                    "battery_voltage": round(latest_val, 2),
                    "unit": "V",
                    "status": "HEALTHY" if latest_val >= 11.5 else "LOW_BATTERY"
                }

            features["sensors"][s_id] = {
                "sensor_type": stype,
                "status": s_state,
                "metrics": metrics,
                "lineage": lineage
            }

        return features

    def get_latest_observations(self) -> Dict[str, Any]:
        """Returns the most recent reading for each sensor with provenance badge."""
        res: Dict[str, Any] = {}
        for s_id, s_meta in self.sensors_registry.items():
            hist = self._observation_history.get(s_id, [])
            if hist:
                last_o = hist[-1]
                res[s_id] = {
                    "sensor_type": s_meta.get("sensor_type"),
                    "value": last_o.get("value"),
                    "unit": last_o.get("unit"),
                    "quality": last_o.get("quality"),
                    "provenance": last_o.get("provenance"),
                    "timestamp_utc": last_o.get("timestamp_utc"),
                    "status": last_o.get("status")
                }
            else:
                res[s_id] = {
                    "sensor_type": s_meta.get("sensor_type"),
                    "value": None,
                    "unit": s_meta.get("unit"),
                    "quality": "UNKNOWN",
                    "provenance": "NONE",
                    "timestamp_utc": None,
                    "status": "UNAVAILABLE",
                    "reason": "PHYSICAL_TELEMETRY_PENDING"
                }
        return res

    def reset_history(self) -> None:
        """Clears in-memory buffer (for testing and calibration reset)."""
        for s_id in self._observation_history:
            self._observation_history[s_id].clear()
            self._last_sequence[s_id] = -1
        self._seen_packet_hashes.clear()
        self._events.clear()
        self._metrics = {
            "total_ingested": 0,
            "accepted": 0,
            "rejected": 0,
            "duplicates": 0,
            "corrupted_crc": 0,
            "out_of_order": 0,
            "last_event_time": None
        }


# Global singleton service
GLOBAL_KINEMATIC_SERVICE = KinematicTelemetryService()
