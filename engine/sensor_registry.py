# -*- coding: utf-8 -*-
"""
engine/sensor_registry.py
=========================
PARVAT NETRA • PAHAD AI — In-Situ Sensor & Edge Gateway Registry
----------------------------------------------------------------
Maintains authoritative hardware identity, geographic coordinates, lifecycle states,
calibration certificates, and health heartbeats for geotechnical field instrumentation.

Sensor Types:
  - piezometer       : Vibrating-wire pore-water pressure (kPa)
  - inclinometer     : In-place MEMS borehole displacement (mm)
  - tilt             : Biaxial surface deflection (deg)
  - soil_moisture    : Time-domain reflectometry VWC (m3/m3)
  - rain_gauge       : Digital tipping bucket precipitation (mm)
  - crack_sensor     : Extensometer joint dilation (mm)
  - water_level      : Ultrasonic/radar channel stage (m)
  - temperature      : Ambient and ground thermistor (C)

Device Statuses:
  - REGISTERED       : Initial registration before physical installation
  - COMMISSIONING    : Undergoing field deployment and calibration checks
  - ACTIVE           : Authenticated, calibrated, and streaming live telemetry
  - STALE            : Heartbeat missing beyond warning window (>5 min)
  - OFFLINE          : Device disconnected (>15 min)
  - DECOMMISSIONED   : Permanently retired from corridor network
  - SIMULATED        : Software mock node used strictly under PAHAD_EDGE_SIMULATION=1
"""

from __future__ import annotations

import os
import time
import sqlite3
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("SENSOR_REGISTRY")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Supported Sensor Types
VALID_SENSOR_TYPES = {
    "piezometer",
    "inclinometer",
    "tilt",
    "soil_moisture",
    "rain_gauge",
    "crack_sensor",
    "water_level",
    "temperature"
}

# Supported Device Statuses
STATUS_REGISTERED = "REGISTERED"
STATUS_COMMISSIONING = "COMMISSIONING"
STATUS_ACTIVE = "ACTIVE"
STATUS_STALE = "STALE"
STATUS_OFFLINE = "OFFLINE"
STATUS_DECOMMISSIONED = "DECOMMISSIONED"
STATUS_SIMULATED = "SIMULATED"

VALID_DEVICE_STATUSES = {
    STATUS_REGISTERED,
    STATUS_COMMISSIONING,
    STATUS_ACTIVE,
    STATUS_STALE,
    STATUS_OFFLINE,
    STATUS_DECOMMISSIONED,
    STATUS_SIMULATED
}

# 8-Stage Commissioning Flow
COMMISSIONING_STAGES = [
    "REGISTER",
    "INSTALL",
    "CALIBRATE",
    "CONNECT",
    "HEARTBEAT",
    "TELEMETRY",
    "VALIDATE",
    "ACCEPT"
]

@dataclass
class GatewayInfo:
    gateway_id: str
    name: str
    latitude: float
    longitude: float
    sector_id: str
    firmware_version: str = "v1.0.0-lora"
    hardware_version: str = "RPi-CM4-LoRa"
    power_source: str = "SOLAR_BATTERY"
    battery_pct: float = 100.0
    uptime_seconds: int = 0
    status: str = "ONLINE"  # ONLINE, DEGRADED, OFFLINE
    last_seen: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SensorDevice:
    device_id: str
    sensor_id: str
    sensor_type: str
    latitude: float
    longitude: float
    sector_id: str
    gateway_id: Optional[str] = None
    installation_status: str = "INSTALLED"
    commissioned_at: Optional[str] = None
    firmware_version: str = "v1.0.0"
    hardware_version: str = "REV-A"
    calibration_status: str = "CALIBRATED"
    last_seen: Optional[str] = None
    battery_level: float = 100.0
    signal_strength: float = -75.0
    clock_offset_ms: float = 0.0
    network_type: str = "LORA"
    status: str = STATUS_REGISTERED
    created_at: Optional[str] = None
    commissioning_progress: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SensorRegistry:
    """Central authoritative manager of physical devices and concentrator topology."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._devices: Dict[str, SensorDevice] = {}
        self._gateways: Dict[str, GatewayInfo] = {}
        self._load_from_db()

    def _get_conn(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _load_from_db(self) -> None:
        """Loads gateways and devices from persistent store."""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            # Gateways
            cur.execute("""
                SELECT gateway_id, name, latitude, longitude, sector_id,
                       firmware_version, hardware_version, power_source,
                       battery_pct, uptime_seconds, status, last_seen, created_at
                FROM gateways
            """)
            for r in cur.fetchall():
                gw = GatewayInfo(
                    gateway_id=r[0], name=r[1], latitude=float(r[2]), longitude=float(r[3]),
                    sector_id=r[4], firmware_version=r[5], hardware_version=r[6],
                    power_source=r[7], battery_pct=float(r[8]), uptime_seconds=int(r[9]),
                    status=r[10], last_seen=r[11], created_at=r[12]
                )
                self._gateways[gw.gateway_id] = gw

            # Devices
            cur.execute("""
                SELECT device_id, sensor_id, sensor_type, latitude, longitude,
                       sector_id, gateway_id, installation_status, commissioned_at,
                       firmware_version, hardware_version, calibration_status,
                       last_seen, battery_level, signal_strength, network_type,
                       status, created_at
                FROM sensor_registry
            """)
            for r in cur.fetchall():
                dev = SensorDevice(
                    device_id=r[0], sensor_id=r[1], sensor_type=r[2],
                    latitude=float(r[3]), longitude=float(r[4]), sector_id=r[5],
                    gateway_id=r[6], installation_status=r[7], commissioned_at=r[8],
                    firmware_version=r[9], hardware_version=r[10], calibration_status=r[11],
                    last_seen=r[12], battery_level=float(r[13]), signal_strength=float(r[14]),
                    network_type=r[15], status=r[16], created_at=r[17]
                )
                self._devices[dev.device_id] = dev
            conn.close()
            logger.info(f"Loaded {len(self._gateways)} gateways and {len(self._devices)} devices from DB.")
        except Exception as e:
            logger.warning(f"Could not load sensor registry from DB: {e}")

    def register_gateway(self, gw: GatewayInfo) -> GatewayInfo:
        """Registers an edge concentrator gateway."""
        if not gw.created_at:
            gw.created_at = datetime.now(timezone.utc).isoformat()
        if not gw.last_seen:
            gw.last_seen = gw.created_at

        self._gateways[gw.gateway_id] = gw

        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO gateways (
                    gateway_id, name, latitude, longitude, sector_id,
                    firmware_version, hardware_version, power_source,
                    battery_pct, uptime_seconds, status, last_seen, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gw.gateway_id, gw.name, gw.latitude, gw.longitude, gw.sector_id,
                gw.firmware_version, gw.hardware_version, gw.power_source,
                gw.battery_pct, gw.uptime_seconds, gw.status, gw.last_seen, gw.created_at
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving gateway {gw.gateway_id}: {e}")

        return gw

    def register_device(self, dev: SensorDevice) -> SensorDevice:
        """Registers a sensor device into the registry."""
        if dev.sensor_type not in VALID_SENSOR_TYPES:
            raise ValueError(f"Invalid sensor_type '{dev.sensor_type}'. Must be one of: {VALID_SENSOR_TYPES}")

        if dev.status not in VALID_DEVICE_STATUSES:
            dev.status = STATUS_REGISTERED

        now_iso = datetime.now(timezone.utc).isoformat()
        if not dev.created_at:
            dev.created_at = now_iso
        if not dev.last_seen:
            dev.last_seen = now_iso

        self._devices[dev.device_id] = dev

        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO sensor_registry (
                    device_id, sensor_id, sensor_type, latitude, longitude,
                    sector_id, gateway_id, installation_status, commissioned_at,
                    firmware_version, hardware_version, calibration_status,
                    last_seen, battery_level, signal_strength, network_type,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dev.device_id, dev.sensor_id, dev.sensor_type, dev.latitude, dev.longitude,
                dev.sector_id, dev.gateway_id, dev.installation_status, dev.commissioned_at,
                dev.firmware_version, dev.hardware_version, dev.calibration_status,
                dev.last_seen, dev.battery_level, dev.signal_strength, dev.network_type,
                dev.status, dev.created_at
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving device {dev.device_id}: {e}")

        return dev

    def advance_commissioning(
        self, device_id: str, stage: str, details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes the 8-stage commissioning workflow:
        REGISTER -> INSTALL -> CALIBRATE -> CONNECT -> HEARTBEAT -> TELEMETRY -> VALIDATE -> ACCEPT
        Device cannot become ACTIVE until all stages up to ACCEPT succeed.
        """
        dev = self._devices.get(device_id)
        if not dev:
            return {"status": "ERROR", "message": f"Device {device_id} not registered."}

        stage = stage.upper()
        if stage not in COMMISSIONING_STAGES:
            return {"status": "ERROR", "message": f"Invalid stage '{stage}'. Must be one of {COMMISSIONING_STAGES}"}

        # Check prerequisite
        curr_idx = COMMISSIONING_STAGES.index(stage)
        for prev_stage in COMMISSIONING_STAGES[:curr_idx]:
            if prev_stage not in dev.commissioning_progress:
                return {
                    "status": "REJECTED_PREREQUISITE_MISSING",
                    "message": f"Cannot execute '{stage}'. Missing prerequisite stage '{prev_stage}'."
                }

        if stage not in dev.commissioning_progress:
            dev.commissioning_progress.append(stage)

        if stage == "ACCEPT":
            dev.status = STATUS_ACTIVE
            dev.commissioned_at = datetime.now(timezone.utc).isoformat()
        else:
            dev.status = STATUS_COMMISSIONING

        self.register_device(dev)

        return {
            "status": "SUCCESS",
            "device_id": device_id,
            "stage_completed": stage,
            "current_status": dev.status,
            "progress": dev.commissioning_progress
        }

    def record_heartbeat(
        self, device_id: str, battery_pct: float, signal_rssi: float, clock_offset_ms: float = 0.0
    ) -> bool:
        """Records device heartbeat, clock drift, and battery telemetry."""
        dev = self._devices.get(device_id)
        if not dev:
            return False

        now_iso = datetime.now(timezone.utc).isoformat()
        dev.last_seen = now_iso
        dev.battery_level = battery_pct
        dev.signal_strength = signal_rssi
        dev.clock_offset_ms = clock_offset_ms

        if dev.status in (STATUS_STALE, STATUS_OFFLINE):
            dev.status = STATUS_ACTIVE

        # Update sensor_registry and log to device_health table
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE sensor_registry
                SET last_seen = ?, battery_level = ?, signal_strength = ?, status = ?
                WHERE device_id = ?
            """, (now_iso, battery_pct, signal_rssi, dev.status, device_id))
            cur.execute("""
                INSERT INTO device_health (
                    device_id, recorded_at, status, battery_level, signal_strength,
                    packet_loss_pct, clock_offset_ms, error_flags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device_id, now_iso, dev.status, battery_pct, signal_rssi,
                0.0, clock_offset_ms, None
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Heartbeat log error: {e}")

        return True

    def get_device(self, device_id: str) -> Optional[SensorDevice]:
        dev = self._devices.get(device_id)
        if dev is None or dev.status in (STATUS_COMMISSIONING, STATUS_OFFLINE, STATUS_STALE, STATUS_REGISTERED):
            try:
                conn = self._get_conn()
                cur = conn.cursor()
                cur.execute("""
                    SELECT device_id, sensor_id, sensor_type, latitude, longitude,
                           sector_id, gateway_id, installation_status, commissioned_at,
                           firmware_version, hardware_version, calibration_status,
                           last_seen, battery_level, signal_strength, network_type,
                           status, created_at
                    FROM sensor_registry
                    WHERE device_id = ?
                """, (device_id,))
                row = cur.fetchone()
                conn.close()
                if row:
                    if dev is None:
                        dev = SensorDevice(
                            device_id=row[0], sensor_id=row[1], sensor_type=row[2],
                            latitude=float(row[3]), longitude=float(row[4]), sector_id=row[5],
                            gateway_id=row[6], installation_status=row[7], commissioned_at=row[8],
                            firmware_version=row[9], hardware_version=row[10], calibration_status=row[11],
                            last_seen=row[12], battery_level=float(row[13]), signal_strength=float(row[14]),
                            network_type=row[15], status=row[16], created_at=row[17],
                            commissioning_progress=list(COMMISSIONING_STAGES) if row[16] == STATUS_ACTIVE else []
                        )
                        self._devices[device_id] = dev
                    elif row[16] == STATUS_ACTIVE:
                        is_staleness_override = dev.status in (STATUS_STALE, STATUS_OFFLINE) and row[12] == dev.last_seen
                        if not is_staleness_override:
                            dev.status = STATUS_ACTIVE
                            dev.commissioned_at = row[8]
                            dev.last_seen = row[12]
                            dev.battery_level = float(row[13])
                            dev.signal_strength = float(row[14])
                            dev.commissioning_progress = list(COMMISSIONING_STAGES)
            except Exception:
                pass
        return self._devices.get(device_id)

    def get_gateway(self, gateway_id: str) -> Optional[GatewayInfo]:
        return self._gateways.get(gateway_id)

    def list_devices(
        self,
        sector_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[SensorDevice]:
        """Lists registered devices filtered by sector, sensor_type, or status."""
        # Refresh staleness first
        self.check_staleness()

        res = list(self._devices.values())
        if sector_id:
            res = [d for d in res if d.sector_id == sector_id]
        if sensor_type:
            res = [d for d in res if d.sensor_type == sensor_type]
        if status:
            res = [d for d in res if d.status == status]
        return res

    def list_gateways(self, sector_id: Optional[str] = None) -> List[GatewayInfo]:
        res = list(self._gateways.values())
        if sector_id:
            res = [g for g in res if g.sector_id == sector_id]
        return res

    def check_staleness(
        self, stale_threshold_sec: int = 300, offline_threshold_sec: int = 900
    ) -> Dict[str, int]:
        """Evaluates last_seen timestamps and flags STALE or OFFLINE devices."""
        now = datetime.now(timezone.utc)
        counts = {"ACTIVE": 0, "STALE": 0, "OFFLINE": 0, "OTHER": 0}

        for dev in self._devices.values():
            if dev.status in (STATUS_DECOMMISSIONED, STATUS_REGISTERED, STATUS_SIMULATED):
                counts["OTHER"] += 1
                continue

            if not dev.last_seen:
                dev.status = STATUS_OFFLINE
                counts["OFFLINE"] += 1
                continue

            try:
                ls_dt = datetime.fromisoformat(dev.last_seen.replace("Z", "+00:00"))
                age = (now - ls_dt).total_seconds()
                if age > offline_threshold_sec:
                    dev.status = STATUS_OFFLINE
                    counts["OFFLINE"] += 1
                elif age > stale_threshold_sec:
                    dev.status = STATUS_STALE
                    counts["STALE"] += 1
                else:
                    counts["ACTIVE"] += 1
            except Exception:
                dev.status = STATUS_STALE
                counts["STALE"] += 1

        return counts

    def get_health_summary(self) -> Dict[str, Any]:
        """Returns aggregate IoT network health breakdown."""
        staleness = self.check_staleness()
        total_devices = len(self._devices)
        total_gateways = len(self._gateways)

        low_battery_devices = [
            d.device_id for d in self._devices.values() if d.battery_level < 20.0
        ]
        weak_signal_devices = [
            d.device_id for d in self._devices.values() if d.signal_strength < -95.0
        ]

        return {
            "total_devices": total_devices,
            "total_gateways": total_gateways,
            "status_breakdown": staleness,
            "low_battery_count": len(low_battery_devices),
            "low_battery_devices": low_battery_devices,
            "weak_signal_count": len(weak_signal_devices),
            "weak_signal_devices": weak_signal_devices,
            "overall_health": "HEALTHY" if staleness["OFFLINE"] == 0 and len(low_battery_devices) == 0 else "DEGRADED"
        }

    def is_device_authenticated(self, device_id: str) -> bool:
        """Returns True if device is registered and in an operational or commissioning state (not decommissioned)."""
        dev = self._devices.get(device_id)
        if not dev:
            return False
        return dev.status != STATUS_DECOMMISSIONED

    def get_composite_sensor_health(self, device_id: str) -> Dict[str, Any]:
        """
        Calculates composite runtime health score for a sensor:
        Evaluates battery, signal RSSI, clock offset, calibration status, and freshness.
        Returns overall rating: GOOD, DEGRADED, INVALID, or OFFLINE.
        """
        dev = self._devices.get(device_id)
        if not dev:
            return {
                "device_id": device_id,
                "overall_health": "OFFLINE",
                "reason": "DEVICE_NOT_REGISTERED",
                "factors": {}
            }

        if dev.status in (STATUS_OFFLINE, STATUS_DECOMMISSIONED):
            return {
                "device_id": device_id,
                "overall_health": "OFFLINE",
                "reason": f"Device status is {dev.status}",
                "factors": {"status": dev.status}
            }

        factors = {
            "battery_level": dev.battery_level,
            "signal_strength": dev.signal_strength,
            "clock_offset_ms": dev.clock_offset_ms,
            "last_seen": dev.last_seen
        }

        # Check calibration
        cal_status = "UNKNOWN"
        try:
            from engine.sensor_calibration import GLOBAL_CALIBRATION_ENGINE
            cal_status = GLOBAL_CALIBRATION_ENGINE.verify_calibration_status(dev.sensor_id)
        except Exception:
            pass
        factors["calibration_status"] = cal_status

        # Check freshness
        age_seconds = None
        if dev.last_seen:
            try:
                ls_dt = datetime.fromisoformat(dev.last_seen.replace("Z", "+00:00"))
                age_seconds = (datetime.now(timezone.utc) - ls_dt).total_seconds()
            except Exception:
                pass
        factors["age_seconds"] = age_seconds

        # Evaluate criteria
        # 1. OFFLINE
        if age_seconds is not None and age_seconds > 900.0:
            return {
                "device_id": device_id,
                "overall_health": "OFFLINE",
                "reason": f"No heartbeat received for {int(age_seconds)}s (>900s limit)",
                "factors": factors
            }

        # 2. INVALID
        invalid_reasons = []
        if dev.battery_level < 10.0:
            invalid_reasons.append("Battery depleted (<10%)")
        if dev.signal_strength < -115.0:
            invalid_reasons.append("Signal unreachable (RSSI <-115 dBm)")
        if abs(dev.clock_offset_ms) > 300000.0:
            invalid_reasons.append("Severe clock drift (>300s)")
        if cal_status == "INVALID_CALIBRATION":
            invalid_reasons.append("Calibration curve mathematically invalid")

        if invalid_reasons:
            return {
                "device_id": device_id,
                "overall_health": "INVALID",
                "reason": "; ".join(invalid_reasons),
                "factors": factors
            }

        # 3. DEGRADED
        degraded_reasons = []
        if dev.battery_level < 30.0:
            degraded_reasons.append("Low battery (<30%)")
        if dev.signal_strength < -95.0:
            degraded_reasons.append("Weak RF link (RSSI <-95 dBm)")
        if abs(dev.clock_offset_ms) > 30000.0:
            degraded_reasons.append("Clock offset drift (>30s)")
        if cal_status in ("CALIBRATION_DUE", "UNKNOWN"):
            degraded_reasons.append(f"Calibration status: {cal_status}")
        if age_seconds is not None and age_seconds > 300.0:
            degraded_reasons.append("Observation telemetry aging (>300s)")

        if degraded_reasons:
            return {
                "device_id": device_id,
                "overall_health": "DEGRADED",
                "reason": "; ".join(degraded_reasons),
                "factors": factors
            }

        # 4. GOOD
        return {
            "device_id": device_id,
            "overall_health": "GOOD",
            "reason": "All operational telemetry, calibration, and RF link metrics nominal",
            "factors": factors
        }

    def get_commissioning_readiness(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns granular 8-stage readiness tracking:
        REGISTERED, INSTALLED, CALIBRATED, CONNECTED, HEARTBEAT_OK, TELEMETRY_OK, VALIDATED, ACCEPTED
        """
        check_labels = [
            "REGISTERED", "INSTALLED", "CALIBRATED", "CONNECTED",
            "HEARTBEAT_OK", "TELEMETRY_OK", "VALIDATED", "ACCEPTED"
        ]

        def _format_dev_readiness(d: SensorDevice) -> Dict[str, Any]:
            prog = d.commissioning_progress
            stages_map = {
                "REGISTERED": "REGISTER" in prog or d.status != STATUS_REGISTERED,
                "INSTALLED": "INSTALL" in prog,
                "CALIBRATED": "CALIBRATE" in prog,
                "CONNECTED": "CONNECT" in prog,
                "HEARTBEAT_OK": "HEARTBEAT" in prog or bool(d.last_seen),
                "TELEMETRY_OK": "TELEMETRY" in prog,
                "VALIDATED": "VALIDATE" in prog,
                "ACCEPTED": "ACCEPT" in prog or d.status == STATUS_ACTIVE,
            }
            completed_count = sum(1 for v in stages_map.values() if v)
            return {
                "device_id": d.device_id,
                "sensor_id": d.sensor_id,
                "sensor_type": d.sensor_type,
                "sector_id": d.sector_id,
                "status": d.status,
                "stages": stages_map,
                "completed_count": completed_count,
                "total_stages": len(check_labels),
                "readiness_pct": round((completed_count / len(check_labels)) * 100.0, 1),
                "is_accepted": stages_map["ACCEPTED"]
            }

        if device_id:
            dev = self._devices.get(device_id)
            if not dev:
                return {"status": "NOT_FOUND", "message": f"Device {device_id} not registered."}
            return {"status": "SUCCESS", "readiness": _format_dev_readiness(dev)}

        all_readiness = [_format_dev_readiness(d) for d in self._devices.values()]
        total = len(all_readiness)
        accepted_count = sum(1 for r in all_readiness if r["is_accepted"])

        return {
            "status": "SUCCESS",
            "total_devices": total,
            "accepted_devices_count": accepted_count,
            "pending_commissioning_count": total - accepted_count,
            "devices": all_readiness
        }


# Global Singleton
GLOBAL_SENSOR_REGISTRY = SensorRegistry()

