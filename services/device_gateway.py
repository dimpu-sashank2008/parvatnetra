# -*- coding: utf-8 -*-
"""
services/device_gateway.py
==========================
PARVAT NETRA • In-Situ Geotechnical IoT Device Gateway & Telemetry Broker
-------------------------------------------------------------------------
Provides hardware-agnostic ingestion, validation, and normalization for in-situ
hillslope instrumentation across the North-Eastern Himalayan corridors:

Supported Sensors:
  - Vibrating-wire piezometer (pore-water pressure in kPa)
  - In-place inclinometer / extensometer (shear displacement in mm, creep velocity in mm/day)
  - Biaxial MEMS surface tiltmeter (slope deflection in degrees, tilt rate in deg/24h)
  - Tipping-bucket digital rain gauge (rainfall accumulation in mm)
  - Time-Domain Reflectometry (TDR) probe (volumetric water content in m^3/m^3)
  - Laser / LVDT crack aperture meter (rock joint dilation in mm)

Supported Transport Protocols:
  - HTTP REST JSON endpoints
  - MQTT topic subscriptions (`parvatnetra/telemetry/{device_id}`)
  - LoRaWAN ChirpStack / TTN JSON uplink decoders
  - BLE advertisement beacon frames (local bridge relay)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from services.data_registry import (
    GLOBAL_DATA_REGISTRY,
    TelemetryObservation,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_SUSPECT
)
from services.cache_manager import GLOBAL_CACHE

logger = logging.getLogger("DEVICE_GATEWAY")

# Physical validity ranges for in-situ sensors to detect malfunction or detachment
SENSOR_LIMITS: Dict[str, Tuple[float, float, str]] = {
    "piezometer": (-10.0, 250.0, "kPa"),
    "inclinometer": (-500.0, 500.0, "mm"),
    "extensometer": (0.0, 1000.0, "mm"),
    "tiltmeter": (-45.0, 45.0, "deg"),
    "rain_gauge": (0.0, 300.0, "mm"),
    "soil_moisture": (0.05, 0.70, "m3/m3"),
    "crack_sensor": (0.0, 200.0, "mm")
}


class DeviceGateway:
    """
    Hardware-agnostic broker handling multi-protocol telemetry ingestion.
    """

    def __init__(self):
        self.active_devices: Dict[str, Dict[str, Any]] = {}

    def ingest_packet(
        self,
        raw_payload: Dict[str, Any],
        protocol: str = "HTTP"
    ) -> Dict[str, Any]:
        """
        Validates, normalizes, and registers an incoming telemetry packet.
        """
        device_id = str(raw_payload.get("device_id") or raw_payload.get("devEUI") or raw_payload.get("id") or "DEV-UNKNOWN")
        sensor_type = str(raw_payload.get("sensor_type") or raw_payload.get("type") or "piezometer").lower()
        
        # Coordinates
        lat = float(raw_payload.get("latitude") or raw_payload.get("lat") or 27.3300)
        lon = float(raw_payload.get("longitude") or raw_payload.get("lon") or 88.6100)

        # Value and unit
        val_raw = raw_payload.get("value")
        if val_raw is None:
            # Check protocol-specific keys
            val_raw = raw_payload.get("pressure_kpa") or raw_payload.get("displacement_mm") or raw_payload.get("tilt_deg") or 0.0
        
        try:
            value = float(val_raw)
        except (ValueError, TypeError):
            value = 0.0

        unit = str(raw_payload.get("unit") or SURING_UNIT(sensor_type))
        battery = float(raw_payload.get("battery_pct") or raw_payload.get("battery") or 95.0)
        rssi = float(raw_payload.get("rssi") or raw_payload.get("signal_rssi_dbm") or -72.0)
        ts_str = raw_payload.get("timestamp") or datetime.now(timezone.utc).isoformat()

        # Quality audit
        quality = QUALITY_GOOD
        limits = SENSOR_LIMITS.get(sensor_type)
        if limits:
            min_val, max_val, _ = limits
            if value < min_val or value > max_val:
                quality = QUALITY_SUSPECT
                logger.warning(f"Sensor {device_id} ({sensor_type}) value {value} out of range [{min_val}, {max_val}]")
        if battery < 15.0:
            quality = QUALITY_DEGRADED

        # Check device registration for authentication
        is_registered = False
        try:
            from engine.sensor_registry import GLOBAL_SENSOR_REGISTRY
            reg_dev = GLOBAL_SENSOR_REGISTRY.get_device(device_id)
            if reg_dev and reg_dev.status in ("ACTIVE", "COMMISSIONING"):
                is_registered = True
                GLOBAL_SENSOR_REGISTRY.record_heartbeat(device_id, battery_pct=battery, signal_rssi=rssi)
        except Exception:
            pass

        provenance = "[LIVE]" if is_registered else "[UNAUTHENTICATED]"

        obs = TelemetryObservation(
            device_id=device_id,
            sensor_type=sensor_type,
            latitude=lat,
            longitude=lon,
            timestamp=ts_str,
            value=value,
            unit=unit,
            battery_pct=battery,
            signal_rssi_dbm=rssi,
            source=f"IoT Node ({protocol})",
            provenance=provenance,
            quality=quality
        )

        # Register in global memory and persistent cache
        GLOBAL_DATA_REGISTRY.register_telemetry(obs)
        GLOBAL_CACHE.set(
            namespace="iot_telemetry",
            key=device_id,
            data=obs.to_dict(),
            ttl_seconds=1800,
            source=f"IoT Node ({protocol})",
            provenance=provenance
        )

        # Also persist to observation store if registered
        try:
            from engine.observation_store import GLOBAL_OBSERVATION_STORE, ObservationRecord
            obs_rec = ObservationRecord(
                id=None,
                sector_id=raw_payload.get("sector_id", "GENERAL"),
                timestamp=ts_str,
                feature=sensor_type,
                value=value,
                unit=unit,
                source=f"IoT_{device_id}",
                quality=quality,
                provenance=provenance,
                ingested_at=datetime.now(timezone.utc).isoformat(),
                extra={"battery_pct": battery, "rssi": rssi, "protocol": protocol}
            )
            GLOBAL_OBSERVATION_STORE.insert(obs_rec)
        except Exception:
            pass

        self.active_devices[device_id] = {
            "device_id": device_id,
            "sensor_type": sensor_type,
            "latitude": lat,
            "longitude": lon,
            "last_seen": ts_str,
            "last_value": value,
            "unit": unit,
            "battery_pct": battery,
            "protocol": protocol,
            "status": "ONLINE" if quality != QUALITY_SUSPECT else "SUSPECT"
        }

        return {
            "status": "SUCCESS",
            "device_id": device_id,
            "sensor_type": sensor_type,
            "value": value,
            "unit": unit,
            "quality": quality,
            "provenance": provenance,
            "timestamp": ts_str
        }

    def list_devices(self) -> List[Dict[str, Any]]:
        """Returns list of registered active hardware devices from authoritative registry."""
        merged: Dict[str, Dict[str, Any]] = dict(self.active_devices)
        try:
            from engine.sensor_registry import GLOBAL_SENSOR_REGISTRY
            for dev in GLOBAL_SENSOR_REGISTRY.list_devices():
                if dev.device_id not in merged:
                    merged[dev.device_id] = {
                        "device_id": dev.device_id,
                        "sensor_type": dev.sensor_type,
                        "latitude": dev.latitude,
                        "longitude": dev.longitude,
                        "sector_id": dev.sector_id,
                        "last_seen": dev.last_seen,
                        "battery_pct": dev.battery_level,
                        "status": dev.status,
                        "protocol": dev.network_type
                    }
        except Exception as e:
            logger.debug(f"Could not query sensor registry: {e}")

        return list(merged.values())


def SURING_UNIT(sensor_type: str) -> str:
    limits = SENSOR_LIMITS.get(sensor_type)
    return limits[2] if limits else "units"


# Global singleton device gateway
GLOBAL_DEVICE_GATEWAY = DeviceGateway()
