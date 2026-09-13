# -*- coding: utf-8 -*-
"""
services/data_registry.py
=========================
PARVAT NETRA • Production Multi-Modal Data Registry & Observation Schemas
--------------------------------------------------------------------------
Formalizes unified schemas, data quality metrics, and source registries for all
environmental, meteorological, geophysical, and in-situ telemetry feeds.

Standardizes:
  - Source attribution (IMD, NCS, Copernicus, GSI, CWC, In-Situ IoT)
  - Quality metrics (GOOD, DEGRADED, SUSPECT, MISSING)
  - Timestamp ISO 8601 UTC compliance
  - Strict provenance badges ([LIVE], [HISTORICAL], [CACHED], [SIMULATED], [MISSING])

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Union

# Standard quality flags
QUALITY_GOOD = "GOOD"
QUALITY_DEGRADED = "DEGRADED"
QUALITY_SUSPECT = "SUSPECT"
QUALITY_MISSING = "MISSING"


@dataclass
class WeatherObservation:
    station_id: str
    latitude: float
    longitude: float
    timestamp: str
    rainfall_1h_mm: float = 0.0
    rainfall_6h_mm: float = 0.0
    rainfall_24h_mm: float = 0.0
    rainfall_72h_mm: float = 0.0
    temperature_c: float = 20.0
    humidity_pct: float = 80.0
    wind_speed_kmh: float = 5.0
    pressure_hpa: float = 1013.25
    source: str = "IMD AWS"
    provenance: str = "[LIVE]"
    quality: str = QUALITY_GOOD

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SeismicObservation:
    event_id: str
    timestamp: str
    latitude: float
    longitude: float
    depth_km: float
    magnitude: float
    region: str
    epicentral_distance_km: float = 999.0
    pga_g: float = 0.0
    seismic_trigger_score: float = 0.0
    source: str = "National Center for Seismology (NCS)"
    provenance: str = "[LIVE]"
    quality: str = QUALITY_GOOD

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DEMObservation:
    latitude: float
    longitude: float
    elevation_m: float
    slope_deg: float
    aspect_deg: float
    curvature: float
    terrain_ruggedness_index: float = 0.0
    topographic_position_index: float = 0.0
    crs: str = "EPSG:4326"
    resolution_m: float = 30.0
    source: str = "Copernicus GLO-30 / ISRO CartoDEM"
    provenance: str = "[HISTORICAL]"
    quality: str = QUALITY_GOOD

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VegetationObservation:
    latitude: float
    longitude: float
    timestamp: str
    ndvi: float
    ndvi_anomaly: float = 0.0
    cloud_cover_pct: float = 0.0
    source: str = "Copernicus Sentinel-2 MSI L2A"
    provenance: str = "[HISTORICAL]"
    quality: str = QUALITY_GOOD

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TelemetryObservation:
    device_id: str
    sensor_type: str  # piezometer, inclinometer, rain_gauge, tiltmeter, extensometer, crack_sensor
    latitude: float
    longitude: float
    timestamp: str
    value: float
    unit: str
    battery_pct: float = 100.0
    signal_rssi_dbm: float = -75.0
    source: str = "In-Situ IoT Gateway"
    provenance: str = "[LIVE]"
    quality: str = QUALITY_GOOD

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DataRegistry:
    """
    In-memory registry maintaining the latest verified multi-modal state for monitored sectors.
    """

    def __init__(self):
        self._weather: Dict[str, WeatherObservation] = {}
        self._seismic: List[SeismicObservation] = []
        self._dem: Dict[str, DEMObservation] = {}
        self._vegetation: Dict[str, VegetationObservation] = {}
        self._telemetry: Dict[str, List[TelemetryObservation]] = {}

    def register_weather(self, sector_id: str, obs: WeatherObservation) -> None:
        self._weather[sector_id] = obs

    def get_weather(self, sector_id: str) -> Optional[WeatherObservation]:
        return self._weather.get(sector_id)

    def register_seismic(self, obs_list: List[SeismicObservation]) -> None:
        self._seismic = list(obs_list)

    def get_latest_seismic(self, limit: int = 10) -> List[SeismicObservation]:
        return self._seismic[:limit]

    def register_dem(self, sector_id: str, obs: DEMObservation) -> None:
        self._dem[sector_id] = obs

    def get_dem(self, sector_id: str) -> Optional[DEMObservation]:
        return self._dem.get(sector_id)

    def register_vegetation(self, sector_id: str, obs: VegetationObservation) -> None:
        self._vegetation[sector_id] = obs

    def get_vegetation(self, sector_id: str) -> Optional[VegetationObservation]:
        return self._vegetation.get(sector_id)

    def register_telemetry(self, obs: TelemetryObservation) -> None:
        if obs.device_id not in self._telemetry:
            self._telemetry[obs.device_id] = []
        self._telemetry[obs.device_id].append(obs)
        # Keep last 50 per sensor
        if len(self._telemetry[obs.device_id]) > 50:
            self._telemetry[obs.device_id].pop(0)

    def get_telemetry_for_device(self, device_id: str) -> List[TelemetryObservation]:
        return self._telemetry.get(device_id, [])

    def get_all_devices(self) -> List[Dict[str, Any]]:
        devices = []
        for dev_id, readings in self._telemetry.items():
            if readings:
                latest = readings[-1]
                devices.append({
                    "device_id": dev_id,
                    "sensor_type": latest.sensor_type,
                    "latitude": latest.latitude,
                    "longitude": latest.longitude,
                    "last_reading": latest.value,
                    "unit": latest.unit,
                    "last_timestamp": latest.timestamp,
                    "battery_pct": latest.battery_pct,
                    "quality": latest.quality,
                    "provenance": latest.provenance
                })
        return devices


# Global singleton data registry
GLOBAL_DATA_REGISTRY = DataRegistry()
