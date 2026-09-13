# -*- coding: utf-8 -*-
"""
services/telemetry_contract.py
==============================
PARVAT NETRA • In-Situ Telemetry Contract, Integrity & Quality Engine
----------------------------------------------------------------------
Enforces the canonical packet schema, cryptographic/sequence integrity,
temporal synchronization, geographic bounding, and physical validity
limits for in-situ hillslope instrumentation.
"""

from __future__ import annotations

import os
import math
import time
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    VALID_SENSOR_TYPES,
    STATUS_ACTIVE,
    STATUS_SIMULATED,
    STATUS_COMMISSIONING
)
from engine.sensor_calibration import (
    GLOBAL_CALIBRATION_ENGINE,
    STATUS_CALIBRATED,
    STATUS_CALIBRATION_DUE,
    STATUS_INVALID_CALIBRATION
)

logger = logging.getLogger("TELEMETRY_CONTRACT")

# Physical validity boundaries per sensor type: (min_value, max_value, primary_unit, max_hourly_delta)
PHYSICAL_SENSOR_LIMITS: Dict[str, Tuple[float, float, str, float]] = {
    "piezometer":    (-10.0, 250.0, "kPa", 40.0),       # Pore pressure
    "inclinometer":  (-500.0, 500.0, "mm", 60.0),       # Shear displacement
    "tilt":          (-45.0, 45.0, "deg", 10.0),        # Surface deflection
    "soil_moisture": (0.0, 1.0, "m3/m3", 0.5),          # Volumetric water content
    "rain_gauge":    (0.0, 300.0, "mm", 150.0),         # Rainfall accumulation
    "crack_sensor":  (0.0, 200.0, "mm", 30.0),          # Joint dilation
    "water_level":   (0.0, 50.0, "m", 15.0),            # River / channel stage
    "temperature":   (-30.0, 60.0, "C", 25.0),          # Ambient/ground temp
}

# NER Geographic Bounding Box (Lat: 20.0N to 30.0N, Lon: 87.0E to 98.0E)
NER_LAT_MIN, NER_LAT_MAX = 20.0, 30.0
NER_LON_MIN, NER_LON_MAX = 87.0, 98.0

# Quality Constants
QUALITY_GOOD = "GOOD"
QUALITY_DEGRADED = "DEGRADED"
QUALITY_INVALID = "INVALID"


@dataclass
class MeasurementItem:
    value: float
    unit: str
    quality: str = QUALITY_GOOD
    raw_value: Optional[float] = None
    calibrated_value: Optional[float] = None
    derived_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TelemetryPacket:
    packet_id: str
    device_id: str
    sensor_id: str
    timestamp: str              # Device timestamp (ISO)
    received_at: str            # Server arrival timestamp (ISO)
    sequence_number: int
    latitude: float
    longitude: float
    measurements: Dict[str, MeasurementItem]
    battery: float              # Battery percentage (0-100)
    signal_quality: float       # RSSI in dBm (e.g. -75.0)
    firmware_version: str = "v1.0.0"
    gateway_id: Optional[str] = None
    transport: str = "LORA"     # LORA, MQTT, HTTP, BLE
    provenance: str = "[LIVE]"  # [LIVE], [SIMULATED]
    clock_offset_ms: float = 0.0
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["measurements"] = {k: v.to_dict() for k, v in self.measurements.items()}
        return d


@dataclass
class ValidationResult:
    is_valid: bool
    status: str                 # ACCEPTED, REJECTED_*
    message: str
    packet: Optional[TelemetryPacket] = None
    overall_quality: str = QUALITY_GOOD


class TelemetryValidator:
    """Validates packet integrity, sequence monotonicity, time synchronization, and physical bounds."""

    def __init__(self):
        # In-memory tracking of sequence numbers and previous observations per device
        # device_id -> {"last_seq": int, "seen_packets": set, "last_obs": dict, "last_time": float}
        self._device_state: Dict[str, Dict[str, Any]] = {}
        self._metrics = {
            "total_packets": 0,
            "accepted_packets": 0,
            "rejected_packets": 0,
            "rejections_by_reason": {},
            "start_time": time.time(),
        }

    def _record_result(self, res: ValidationResult) -> ValidationResult:
        self._metrics["total_packets"] += 1
        if res.is_valid:
            self._metrics["accepted_packets"] += 1
        else:
            self._metrics["rejected_packets"] += 1
            self._metrics["rejections_by_reason"][res.status] = (
                self._metrics["rejections_by_reason"].get(res.status, 0) + 1
            )
        return res

    def get_metrics(self) -> Dict[str, Any]:
        """Returns ingestion metrics, drop rates, and packet statistics."""
        uptime = time.time() - self._metrics["start_time"]
        total = self._metrics["total_packets"]
        drop_rate = (self._metrics["rejected_packets"] / max(total, 1)) * 100.0
        rate = total / max(uptime, 1.0)
        return {
            "total_packets": total,
            "accepted_packets": self._metrics["accepted_packets"],
            "rejected_packets": self._metrics["rejected_packets"],
            "drop_rate_pct": round(drop_rate, 2),
            "packets_per_second": round(rate, 3),
            "rejections_by_reason": dict(self._metrics["rejections_by_reason"]),
            "uptime_seconds": int(uptime)
        }

    def validate_and_normalize(
        self,
        raw_dict: Dict[str, Any],
        transport: str = "HTTP",
        enforce_registered: bool = False
    ) -> ValidationResult:
        """
        Validates an incoming telemetry dictionary against the canonical contract.
        Normalizes measurements, applies calibration, tracks sequences, and scores data quality.
        """
        res = self._validate_and_normalize_inner(raw_dict, transport=transport, enforce_registered=enforce_registered)
        return self._record_result(res)

    def _validate_and_normalize_inner(
        self,
        raw_dict: Dict[str, Any],
        transport: str = "HTTP",
        enforce_registered: bool = False
    ) -> ValidationResult:
        device_id = str(raw_dict.get("device_id") or raw_dict.get("devEUI") or raw_dict.get("id") or "").strip()
        if not device_id:
            return ValidationResult(is_valid=False, status="REJECTED_MISSING_DEVICE_ID", message="Missing device_id")

        sensor_id = str(raw_dict.get("sensor_id") or device_id)
        gateway_id = raw_dict.get("gateway_id")

        # 1. Device Registration Check
        should_enforce = enforce_registered or (os.environ.get("PAHAD_ENFORCE_REGISTERED_DEVICES") == "1")
        dev = GLOBAL_SENSOR_REGISTRY.get_device(device_id)
        if should_enforce and not dev:
            return ValidationResult(
                is_valid=False,
                status="REJECTED_UNKNOWN_DEVICE",
                message=f"Device {device_id} is not registered in SensorRegistry"
            )

        if dev and dev.status == "DECOMMISSIONED":
            return ValidationResult(
                is_valid=False,
                status="REJECTED_DECOMMISSIONED_DEVICE",
                message=f"Device {device_id} is decommissioned and cannot stream telemetry"
            )

        # 2. Sequence Number Integrity
        try:
            seq = int(raw_dict.get("sequence_number") if raw_dict.get("sequence_number") is not None else raw_dict.get("seq", 0))
        except (ValueError, TypeError):
            return ValidationResult(is_valid=False, status="REJECTED_CORRUPT_SEQUENCE", message="Invalid sequence_number")

        dev_state = self._device_state.setdefault(device_id, {
            "last_seq": -1,
            "seen_packet_ids": set(),
            "last_obs": {},
            "last_ts": None
        })

        # Check duplicate sequence
        packet_id = str(raw_dict.get("packet_id") or f"{device_id}_{seq}_{raw_dict.get('timestamp', '')}")
        if transport != "EDGE_BUFFER_REPLAY" and packet_id in dev_state["seen_packet_ids"]:
            return ValidationResult(
                is_valid=False,
                status="REJECTED_DUPLICATE",
                message=f"Duplicate packet detected for device {device_id} (seq={seq})"
            )

        # 3. Coordinates & Geographic Bounds
        try:
            lat = float(raw_dict.get("latitude") or (dev.latitude if dev else 27.33))
            lon = float(raw_dict.get("longitude") or (dev.longitude if dev else 88.61))
        except (ValueError, TypeError):
            return ValidationResult(is_valid=False, status="REJECTED_INVALID_COORDINATES", message="Invalid coordinates")

        if not (NER_LAT_MIN <= lat <= NER_LAT_MAX and NER_LON_MIN <= lon <= NER_LON_MAX):
            return ValidationResult(
                is_valid=False,
                status="REJECTED_OUT_OF_BOUNDS",
                message=f"Coordinates ({lat}, {lon}) outside NER bounding box"
            )

        # 4. Time Synchronization & Clock Drift
        now_dt = datetime.now(timezone.utc)
        server_ts = now_dt.isoformat()
        raw_ts = raw_dict.get("timestamp")

        if not raw_ts:
            dev_ts = server_ts
            clock_offset_ms = 0.0
        else:
            try:
                # Parse device timestamp
                parsed_ts = datetime.fromisoformat(str(raw_ts).replace("Z", "+00:00"))
                dev_ts = parsed_ts.isoformat()
                clock_offset_ms = (now_dt - parsed_ts).total_seconds() * 1000.0

                # Reject future timestamps beyond 30-second leeway
                if (parsed_ts - now_dt).total_seconds() > 30.0:
                    return ValidationResult(
                        is_valid=False,
                        status="REJECTED_FUTURE_TIMESTAMP",
                        message=f"Packet timestamp {dev_ts} is >30s in the future compared to server {server_ts}"
                    )
            except Exception as e:
                return ValidationResult(is_valid=False, status="REJECTED_CORRUPT_TIMESTAMP", message=f"Invalid timestamp format: {e}")

        # 5. Provenance Assessment
        is_simulated = bool(
            raw_dict.get("simulated")
            or (dev and dev.status == STATUS_SIMULATED)
            or os.environ.get("PAHAD_EDGE_SIMULATION") == "1"
        )
        provenance = "[SIMULATED]" if is_simulated else "[LIVE]"

        # 6. Parse and Validate Measurements
        measurements_raw = raw_dict.get("measurements")
        if not measurements_raw or not isinstance(measurements_raw, dict):
            # Fallback single measurement payload format: {value, unit, sensor_type}
            s_type = str(raw_dict.get("sensor_type") or (dev.sensor_type if dev else "piezometer")).lower()
            val = raw_dict.get("value")
            if val is None:
                val = raw_dict.get("pore_pressure_kpa") or raw_dict.get("displacement_mm") or raw_dict.get("tilt_deg") or 0.0
            measurements_raw = {s_type: {"value": val, "unit": raw_dict.get("unit")}}

        processed_measurements: Dict[str, MeasurementItem] = {}
        overall_quality = QUALITY_GOOD

        # Timestamp drift quality penalty
        if abs(clock_offset_ms) > 120000.0:  # > 2 min drift
            overall_quality = QUALITY_DEGRADED

        battery = float(raw_dict.get("battery") or raw_dict.get("battery_pct") or 90.0)
        signal = float(raw_dict.get("signal_quality") or raw_dict.get("signal_rssi_dbm") or -75.0)

        if battery < 15.0 or signal < -95.0:
            overall_quality = QUALITY_DEGRADED

        for m_key, m_val in measurements_raw.items():
            if isinstance(m_val, dict):
                raw_v = float(m_val.get("value", 0.0))
                m_unit = str(m_val.get("unit") or "")
            else:
                raw_v = float(m_val)
                m_unit = ""

            # Check physical limits with alias resolution
            limit_key = m_key.lower()
            if "pore" in limit_key or "piezo" in limit_key:
                limit_key = "piezometer"
            elif "inclinometer" in limit_key or "displacement" in limit_key:
                limit_key = "inclinometer"
            elif "tilt" in limit_key:
                limit_key = "tilt"
            elif "rain" in limit_key:
                limit_key = "rain_gauge"
            elif "moisture" in limit_key or "vwc" in limit_key:
                limit_key = "soil_moisture"
            elif "crack" in limit_key:
                limit_key = "crack_sensor"
            elif "level" in limit_key or "water" in limit_key:
                limit_key = "water_level"
            elif "temp" in limit_key:
                limit_key = "temperature"

            limits = PHYSICAL_SENSOR_LIMITS.get(limit_key)
            if limits:
                min_l, max_l, default_unit, max_rate = limits
                if not m_unit:
                    m_unit = default_unit

                # Check impossible physical range
                if raw_v < min_l or raw_v > max_l:
                    return ValidationResult(
                        is_valid=False,
                        status="REJECTED_IMPOSSIBLE_VALUE",
                        message=f"Measurement '{m_key}' value {raw_v} exceeds physical limits [{min_l}, {max_l}]"
                    )

                # Check rate of change against last observation
                prev_v = dev_state["last_obs"].get(m_key)
                if prev_v is not None and dev_state["last_ts"]:
                    dt_hours = max((now_dt - dev_state["last_ts"]).total_seconds() / 3600.0, 0.01)
                    rate = abs(raw_v - prev_v) / dt_hours
                    if rate > max_rate * 3.0:
                        overall_quality = QUALITY_DEGRADED
                        logger.warning(f"Abnormal rate of change for {device_id}.{m_key}: {rate:.2f} {m_unit}/h")

            # Apply Calibration
            cal_val, cal_status, cal_penalty = GLOBAL_CALIBRATION_ENGINE.apply_calibration(sensor_id, raw_v)
            m_quality = QUALITY_GOOD
            if cal_status == STATUS_INVALID_CALIBRATION:
                m_quality = QUALITY_INVALID
                overall_quality = QUALITY_DEGRADED
            elif cal_status == STATUS_CALIBRATION_DUE:
                m_quality = QUALITY_DEGRADED
                overall_quality = QUALITY_DEGRADED

            derived: Dict[str, float] = {}
            # Multi-axis tilt / deformation derivative preservation
            if "tilt" in m_key.lower() or "inclinometer" in m_key.lower():
                prev_v = dev_state["last_obs"].get(m_key, raw_v)
                derived["delta"] = round(raw_v - prev_v, 4)

            processed_measurements[m_key] = MeasurementItem(
                value=cal_val,
                unit=m_unit or "units",
                quality=m_quality,
                raw_value=raw_v,
                calibrated_value=cal_val,
                derived_metrics=derived
            )
            dev_state["last_obs"][m_key] = raw_v

        # Compute Biaxial Tilt Resultant if tilt_x and tilt_y are present
        if "tilt_x" in processed_measurements and "tilt_y" in processed_measurements:
            tx = processed_measurements["tilt_x"].value
            ty = processed_measurements["tilt_y"].value
            import math
            res_val = round(math.sqrt(tx**2 + ty**2), 4)
            processed_measurements["tilt_resultant"] = MeasurementItem(
                value=res_val,
                unit="deg",
                quality=QUALITY_GOOD,
                raw_value=res_val,
                calibrated_value=res_val,
                derived_metrics={"source": "biaxial_pythagorean"}
            )

        # Update Device Tracking State
        dev_state["last_seq"] = seq
        dev_state["seen_packet_ids"].add(packet_id)
        dev_state["last_ts"] = now_dt
        if len(dev_state["seen_packet_ids"]) > 5000:
            dev_state["seen_packet_ids"].clear()  # prevent memory leak while keeping recent window

        # Update Sensor Registry heartbeat
        GLOBAL_SENSOR_REGISTRY.record_heartbeat(
            device_id=device_id,
            battery_pct=battery,
            signal_rssi=signal,
            clock_offset_ms=clock_offset_ms
        )

        packet = TelemetryPacket(
            packet_id=packet_id,
            device_id=device_id,
            sensor_id=sensor_id,
            timestamp=dev_ts,
            received_at=server_ts,
            sequence_number=seq,
            latitude=lat,
            longitude=lon,
            measurements=processed_measurements,
            battery=battery,
            signal_quality=signal,
            firmware_version=str(raw_dict.get("firmware_version", "v1.0.0")),
            gateway_id=gateway_id,
            transport=transport,
            provenance=provenance,
            clock_offset_ms=clock_offset_ms,
            checksum=raw_dict.get("checksum")
        )

        return ValidationResult(
            is_valid=True,
            status="ACCEPTED",
            message="Packet validated and calibrated successfully",
            packet=packet,
            overall_quality=overall_quality
        )


# Global singleton validator
GLOBAL_TELEMETRY_VALIDATOR = TelemetryValidator()
