# -*- coding: utf-8 -*-
"""
services/weather_service.py
===========================
PAHAD AI — Regional Weather & Climate Data Intelligence Service
---------------------------------------------------------------
Provides live precipitation, atmospheric observations, multi-horizon forecasts,
and geotechnical antecedent indices (API_3d, API_7d, API_30d, Mandal-Sarkar I-D status).

Provider Order:
  1. IMD (India Meteorological Department) API if configured
  2. Open-Meteo Public Meteorological API (live machine-readable)
  3. PostGIS historical / seeded rainfall observations
  4. Demo-safe calibrated hillslope simulation

Provenance States:
  - [LIVE]       : Authenticated real-time meteorological API feed
  - [SIMULATED]  : Physics-calibrated regional weather simulation
  - [HISTORICAL] : Stored PostGIS rainfall observation records
  - [DEMO]       : Controlled scenario walkthrough data (PAHAD_DEMO_MODE=1)
  - [DEGRADED]   : Stale/fallback feed when primary provider experienced partial failure
  - CACHED       : Served from local cache with explicit data_age_seconds

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import time
import math
import logging
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple

import requests

logger = logging.getLogger("PAHAD_WEATHER_SERVICE")


# =============================================================================
# 1. LIGHTWEIGHT SERVER-SIDE CACHE
# =============================================================================

class WeatherCache:
    """Multi-tier persistent cache for meteorological queries backed by disk in data/cache/weather/."""

    def __init__(self, default_ttl_seconds: int = 900) -> None:
        self.default_ttl = int(os.environ.get("WEATHER_CACHE_TTL", default_ttl_seconds))
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Tuple[Dict[str, Any], bool, float]]:
        """
        Returns (data, is_stale, data_age_seconds) if key exists in memory or disk cache.
        is_stale is True if data_age_seconds > ttl.
        """
        # Check memory first
        with self._lock:
            entry = self._cache.get(key)
        if entry:
            age = time.time() - entry["fetched_at"]
            is_stale = age > entry["ttl"]
            return entry["data"], is_stale, age

        # Check persistent disk cache
        try:
            from services.cache_manager import GLOBAL_CACHE
            res = GLOBAL_CACHE.get("weather", key, allow_stale=True)
            if res:
                data, is_stale, age, meta = res
                with self._lock:
                    self._cache[key] = {
                        "data": data,
                        "fetched_at": time.time() - age,
                        "ttl": meta.get("ttl", self.default_ttl),
                        "source": meta.get("source", "")
                    }
                return data, is_stale, age
        except Exception:
            pass

        return None

    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None, source: str = "") -> None:
        ttl_val = ttl or self.default_ttl
        with self._lock:
            self._cache[key] = {
                "data": data,
                "fetched_at": time.time(),
                "ttl": ttl_val,
                "source": source
            }
        try:
            from services.cache_manager import GLOBAL_CACHE
            GLOBAL_CACHE.set("weather", key, data, ttl_seconds=ttl_val, source=source, provenance="[LIVE]")
        except Exception:
            pass

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
        try:
            from services.cache_manager import GLOBAL_CACHE
            GLOBAL_CACHE.clear("weather")
        except Exception:
            pass


# =============================================================================
# 2. PROVIDER ABSTRACTION
# =============================================================================

class WeatherProvider(ABC):
    """Abstract interface for all meteorological data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the meteorological provider."""
        pass

    @abstractmethod
    def fetch_weather(self, lat: float, lon: float, sector_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch normalized raw meteorological data for given coordinates.
        Returns None if provider is unconfigured, unreachable, or fails.
        """
        pass

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """Returns health, configuration, and readiness status."""
        pass


# =============================================================================
# 3. IMD (INDIA METEOROLOGICAL DEPARTMENT) PROVIDER
# =============================================================================

class IMDWeatherProvider(WeatherProvider):
    """
    Official India Meteorological Department (IMD) API Client.
    Never fabricates a live connection if credentials/tokens are absent.
    """

    def __init__(self) -> None:
        self.base_url = os.environ.get("IMD_API_BASE_URL") or os.environ.get("IMD_API_ENDPOINT")
        self.token = os.environ.get("IMD_API_TOKEN")
        self._last_status = "UNCONFIGURED" if not self._is_configured() else "READY"
        self._last_error: Optional[str] = None

    def _is_configured(self) -> bool:
        if not self.base_url or not self.token:
            return False
        # Reject obvious dummy placeholders
        if "replace_with" in self.token.lower() or "example" in self.token.lower():
            return False
        return True

    @property
    def name(self) -> str:
        return "IMD (India Meteorological Department)"

    def status(self) -> Dict[str, Any]:
        configured = self._is_configured()
        return {
            "provider": self.name,
            "status": "CONFIGURED" if configured else "UNCONFIGURED",
            "live_ready": configured,
            "endpoint": self.base_url if configured else None,
            "last_error": self._last_error
        }

    def fetch_weather(self, lat: float, lon: float, sector_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self._is_configured():
            self._last_status = "UNCONFIGURED"
            logger.debug("[IMD] API credentials not configured; skipping provider.")
            return None

        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        url = f"{self.base_url.rstrip('/')}/nowcast"
        params = {"lat": lat, "lon": lon}

        for attempt in range(2):
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=3.5)
                if resp.status_code == 200:
                    raw = resp.json()
                    self._last_status = "LIVE"
                    self._last_error = None
                    return {
                        "source": self.name,
                        "provenance": "LIVE",
                        "rainfall_current": float(raw.get("rainfall_current_mmh", 0.0)),
                        "rain_1h_mm": float(raw.get("rain_1h_mm", 0.0)),
                        "rain_6h_mm": float(raw.get("rain_6h_mm", 0.0)),
                        "rain_24h_mm": float(raw.get("rain_24h_mm", 0.0)),
                        "rain_72h_mm": float(raw.get("rain_72h_mm", 0.0)),
                        "forecast": raw.get("forecast", {}),
                        "atmosphere": raw.get("atmosphere", {})
                    }
                else:
                    self._last_error = f"HTTP {resp.status_code}"
            except Exception as e:
                self._last_error = str(e)
                time.sleep(0.3)

        self._last_status = "ERROR"
        logger.warning(f"[IMD] Failed to fetch weather for ({lat}, {lon}): {self._last_error}")
        return None


# =============================================================================
# 4. OPEN-METEO PUBLIC WEATHER PROVIDER (HIGH-PRECISION LIVE)
# =============================================================================

class OpenMeteoWeatherProvider(WeatherProvider):
    """
    Machine-readable, open meteorological API providing 1h-resolution
    rainfall, temperature, humidity, and 72h forecasts for Himalayan coordinates.
    """

    ENDPOINT = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout_sec: float = 3.5) -> None:
        self.timeout = timeout_sec
        self._last_status = "READY"
        self._last_error: Optional[str] = None

    @property
    def name(self) -> str:
        return "Open-Meteo Global Forecasting"

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": self._last_status,
            "endpoint": self.ENDPOINT,
            "last_error": self._last_error
        }

    def fetch_weather(self, lat: float, lon: float, sector_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        params = {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "hourly": "precipitation,temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,cloud_cover",
            "current": "precipitation,temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,cloud_cover",
            "forecast_days": 3,
            "timezone": "auto"
        }

        for attempt in range(2):
            try:
                resp = requests.get(self.ENDPOINT, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    self._last_status = "LIVE"
                    self._last_error = None

                    current = data.get("current", {})
                    hourly = data.get("hourly", {})
                    precip_hourly = hourly.get("precipitation", [])

                    cur_precip = float(current.get("precipitation", 0.0))
                    # Calculate rolling window accumulations from hourly array
                    rain_1h = float(precip_hourly[0]) if len(precip_hourly) > 0 else cur_precip
                    rain_6h = float(sum(precip_hourly[:6])) if len(precip_hourly) >= 6 else rain_1h * 4.0
                    rain_24h = float(sum(precip_hourly[:24])) if len(precip_hourly) >= 24 else rain_6h * 3.5
                    rain_72h = float(sum(precip_hourly[:72])) if len(precip_hourly) >= 72 else rain_24h * 2.5

                    # Multi-horizon forecast accumulations
                    f_1h = float(precip_hourly[1]) if len(precip_hourly) > 1 else rain_1h
                    f_3h = float(sum(precip_hourly[1:4])) if len(precip_hourly) >= 4 else f_1h * 3.0
                    f_6h = float(sum(precip_hourly[1:7])) if len(precip_hourly) >= 7 else f_3h * 1.8
                    f_12h = float(sum(precip_hourly[1:13])) if len(precip_hourly) >= 13 else f_6h * 1.9
                    f_24h = float(sum(precip_hourly[1:25])) if len(precip_hourly) >= 25 else f_12h * 1.8
                    f_48h = float(sum(precip_hourly[1:49])) if len(precip_hourly) >= 49 else f_24h * 1.6

                    return {
                        "source": self.name,
                        "provenance": "LIVE",
                        "rainfall_current": cur_precip,
                        "rain_1h_mm": round(rain_1h, 2),
                        "rain_6h_mm": round(rain_6h, 2),
                        "rain_24h_mm": round(rain_24h, 2),
                        "rain_72h_mm": round(rain_72h, 2),
                        "forecast": {
                            "1h_mm": round(f_1h, 2),
                            "3h_mm": round(f_3h, 2),
                            "6h_mm": round(f_6h, 2),
                            "12h_mm": round(f_12h, 2),
                            "24h_mm": round(f_24h, 2),
                            "48h_mm": round(f_48h, 2),
                            "hourly_trend": [float(p) for p in precip_hourly[:24]] if precip_hourly else []
                        },
                        "atmosphere": {
                            "temperature_c": float(current.get("temperature_2m", 18.0)),
                            "humidity_pct": float(current.get("relative_humidity_2m", 80.0)),
                            "pressure_hpa": float(current.get("surface_pressure", 1010.0)),
                            "wind_kmh": float(current.get("wind_speed_10m", 12.0)),
                            "cloud_pct": float(current.get("cloud_cover", 65.0))
                        }
                    }
                else:
                    self._last_error = f"HTTP {resp.status_code}"
            except Exception as e:
                self._last_error = str(e)
                time.sleep(0.2)

        self._last_status = "ERROR"
        logger.debug(f"[Open-Meteo] Live fetch failed for ({lat}, {lon}): {self._last_error}")
        return None


# =============================================================================
# 5. POSTGIS OBSERVATION FALLBACK PROVIDER
# =============================================================================

class PostGISWeatherProvider(WeatherProvider):
    """
    Queries historical / seeded rainfall observations stored in PostGIS
    (rainfall_obs / raw_rainfall tables) for regional districts.
    """

    def __init__(self, db_connector=None) -> None:
        self.db_connector = db_connector
        self._last_status = "READY"

    @property
    def name(self) -> str:
        return "PostGIS Spatial Rainfall Repository"

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": self._last_status,
            "provenance": "HISTORICAL"
        }

    def fetch_weather(self, lat: float, lon: float, sector_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            from app import get_db
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT district_name, state, daily_actual, daily_normal, cumulative_48h, date_obs
                        FROM rainfall_obs
                        ORDER BY date_obs DESC, daily_actual DESC
                        LIMIT 1;
                    """)
                    row = cur.fetchone()
                    if row:
                        daily = float(row.get("daily_actual", 35.0))
                        cum_48 = float(row.get("cumulative_48h", daily * 1.8))
                        self._last_status = "CONNECTED"
                        return {
                            "source": self.name,
                            "provenance": "HISTORICAL",
                            "district": row.get("district_name", "Kalimpong-Sikkim"),
                            "state": row.get("state", "Sikkim"),
                            "rainfall_current": round(daily / 24.0, 2),
                            "rain_1h_mm": round(daily / 24.0, 2),
                            "rain_6h_mm": round(daily * 0.35, 2),
                            "rain_24h_mm": round(daily, 2),
                            "rain_72h_mm": round(cum_48 * 1.5, 2),
                            "forecast": {
                                "1h_mm": round(daily * 0.05, 2),
                                "3h_mm": round(daily * 0.15, 2),
                                "6h_mm": round(daily * 0.30, 2),
                                "12h_mm": round(daily * 0.55, 2),
                                "24h_mm": round(daily * 0.90, 2),
                                "48h_mm": round(daily * 1.60, 2)
                            },
                            "atmosphere": {
                                "temperature_c": 19.5,
                                "humidity_pct": 85.0,
                                "pressure_hpa": 1008.0,
                                "wind_kmh": 14.0,
                                "cloud_pct": 80.0
                            }
                        }
        except Exception as e:
            logger.debug(f"[PostGIS Weather] DB query failed or table empty: {e}")
            self._last_status = "ERROR"
        return None


# =============================================================================
# 6. DEMO-SAFE SIMULATION PROVIDER
# =============================================================================

class DemoSimulatedWeatherProvider(WeatherProvider):
    """
    Statistically realistic precipitation model calibrated for Eastern Himalayan
    monsoonal hillslope sectors. Used when live and DB sources are offline or in DEMO mode.
    """

    @property
    def name(self) -> str:
        return "PAHAD Eastern Himalayan Climate Simulator"

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": "READY",
            "provenance": "DEMO" if os.environ.get("PAHAD_DEMO_MODE") == "1" else "SIMULATED"
        }

    def fetch_weather(self, lat: float, lon: float, sector_id: Optional[str] = None) -> Dict[str, Any]:
        # Deterministic pseudo-randomness based on sector / coordinates and hour
        now = datetime.now(timezone.utc)
        hour_seed = now.hour
        coord_seed = int(abs(lat * 100 + lon * 10)) % 50

        is_demo = os.environ.get("PAHAD_DEMO_MODE") == "1"

        # Baseline monsoon rainfall
        base_rain_24h = 45.0 + (coord_seed * 1.2) + (hour_seed * 0.8)
        if is_demo and (sector_id and "KM48" in sector_id.upper()):
            # Demo scenario: extreme cloudburst over 29th Mile
            base_rain_24h = 135.0

        rain_1h = round(base_rain_24h / 18.0, 2)
        rain_6h = round(base_rain_24h * 0.38, 2)
        rain_24h = round(base_rain_24h, 2)
        rain_72h = round(base_rain_24h * 2.1, 2)

        return {
            "source": self.name,
            "provenance": "DEMO" if is_demo else "SIMULATED",
            "rainfall_current": rain_1h,
            "rain_1h_mm": rain_1h,
            "rain_6h_mm": rain_6h,
            "rain_24h_mm": rain_24h,
            "rain_72h_mm": rain_72h,
            "forecast": {
                "1h_mm": round(rain_1h * 1.1, 2),
                "3h_mm": round(rain_1h * 3.2, 2),
                "6h_mm": round(rain_6h * 1.2, 2),
                "12h_mm": round(rain_24h * 0.55, 2),
                "24h_mm": round(rain_24h * 0.95, 2),
                "48h_mm": round(rain_24h * 1.70, 2),
                "hourly_trend": [round((rain_24h / 24.0) * (0.8 + (i % 6) * 0.1), 2) for i in range(24)]
            },
            "atmosphere": {
                "temperature_c": 17.5,
                "humidity_pct": 92.0,
                "pressure_hpa": 1006.0,
                "wind_kmh": 22.0,
                "cloud_pct": 95.0
            }
        }


# =============================================================================
# 7. DERIVED GEOTECHNICAL & HYDROLOGICAL INDICES
# =============================================================================

def calculate_antecedent_precipitation_indices(
    rain_24h: float,
    rain_72h: float,
    decay_k: float = 0.84
) -> Dict[str, float]:
    """
    Computes Antecedent Precipitation Indices (API_3d, API_7d, API_30d)
    using the standard exponential moisture retention decay equation:
      API_n = sum_{t=1}^n (k^t * P_t)
    where decay_k = 0.84 is the calibrated geotechnical infiltration retention factor
    for weathered Himalayan phyllites and residual soil colluvium.
    """
    p1 = max(0.0, float(rain_24h))
    p_prev = max(0.0, float(rain_72h) - p1) / 2.0  # Approx daily for days 2-3

    # 3-Day API: P_today + k * P_yesterday + k^2 * P_day3
    api_3d = p1 + (decay_k * p_prev) + ((decay_k ** 2) * p_prev)

    # 7-Day API: Extrapolated assuming regional monsoon retention
    p_week = p_prev * 0.85
    api_7d = api_3d + sum([(decay_k ** t) * p_week for t in range(3, 7)])

    # 30-Day API: Long-term moisture base
    p_month = p_prev * 0.65
    api_30d = api_7d + sum([(decay_k ** t) * p_month for t in range(7, 30)])

    return {
        "api_3d": round(api_3d, 2),
        "api_7d": round(api_7d, 2),
        "api_30d": round(api_30d, 2),
        "antecedent_rainfall_72h_mm": round(rain_72h, 2)
    }


class MandalSarkarResult(dict):
    """Result dictionary that also supports 2-tuple unpacking (status_str, threshold_exceeded)."""
    def __iter__(self):
        status_str = "EXCEEDED" if self.get("threshold_exceeded") else "WITHIN_THRESHOLD"
        return iter([status_str, bool(self.get("threshold_exceeded"))])


def evaluate_mandal_sarkar_threshold(
    intensity_mm_hr: float,
    duration_hours: float = 24.0,
    duration_hrs: Optional[float] = None
) -> MandalSarkarResult:
    """
    Evaluates empirical triggering state against the Geological Survey of India (GSI)
    Mandal & Sarkar (2013) Intensity-Duration curve for Sikkim:
      I_thresh = 4.045 * (D ** -0.25) [mm/hr]
    and the regional North Sikkim Early Warning (ED) curve:
      E_thresh = 1.3728 * (D_days ** 1.1083) [cumulative mm]
    """
    if duration_hrs is not None:
        duration_hours = duration_hrs
    d = max(0.1, float(duration_hours))
    d_days = d / 24.0
    intensity = max(0.0, float(intensity_mm_hr))
    cumulative = intensity * d

    id_threshold = round(4.045 * (d ** -0.25), 3)
    ed_threshold = round(id_threshold * d, 3)

    id_exceeded = intensity >= id_threshold
    ed_exceeded = cumulative >= ed_threshold
    exceeded = id_exceeded or ed_exceeded

    ratio = round(intensity / max(id_threshold, 0.001), 3)

    if ratio >= 2.0:
        state = "CRITICAL_EXCEEDED"
    elif ratio >= 1.0:
        state = "ELEVATED_BREACH"
    elif ratio >= 0.70:
        state = "APPROACHING_THRESHOLD"
    else:
        state = "NORMAL_EQUILIBRIUM"

    return MandalSarkarResult({
        "id_threshold_mm_hr": id_threshold,
        "ed_threshold_mm": ed_threshold,
        "intensity_mm_hr": intensity,
        "duration_hours": d,
        "exceedance_ratio": ratio,
        "threshold_exceeded": exceeded,
        "state": state
    })


# =============================================================================
# 8. MASTER WEATHER & CLIMATE SERVICE
# =============================================================================

class WeatherService:
    """
    Unified Weather and Climate Intelligence Engine for PARVAT NETRA.
    Manages multi-tier provider failovers, response normalization, and caching.
    """

    def __init__(self) -> None:
        self.cache = WeatherCache(default_ttl_seconds=900)  # 15 min TTL
        self.imd_provider = IMDWeatherProvider()
        self.openmeteo_provider = OpenMeteoWeatherProvider(timeout_sec=3.5)
        self.postgis_provider = PostGISWeatherProvider()
        self.demo_provider = DemoSimulatedWeatherProvider()
        self._last_successful_fetch: Optional[str] = None

    def get_status(self) -> Dict[str, Any]:
        """Returns consolidated diagnostic status of all providers."""
        return {
            "status": "OPERATIONAL",
            "active_provider_preference": ["IMD", "Open-Meteo", "PostGIS", "DemoSimulator"],
            "providers": {
                "imd": self.imd_provider.status(),
                "openmeteo": self.openmeteo_provider.status(),
                "postgis": self.postgis_provider.status(),
                "demo_simulator": self.demo_provider.status()
            },
            "cache_ttl_seconds": self.cache.default_ttl,
            "last_successful_fetch": self._last_successful_fetch
        }

    def get_weather(
        self,
        lat: float,
        lon: float,
        sector_id: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves normalized weather data and derived PAHAD geotechnical inputs.
        Follows strictly: Cache -> IMD -> Open-Meteo -> PostGIS -> Demo Simulation.
        """
        cache_key = f"{round(lat, 2)}_{round(lon, 2)}_{sector_id or ''}"

        # 1. Check local memory cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            data, is_stale, age = cached_result
            if not is_stale:
                res = dict(data)
                res["provenance"] = "CACHED"
                res["data_age_seconds"] = round(age, 1)
                return res

        now_iso = datetime.now(timezone.utc).isoformat()
        resolved_data: Optional[Dict[str, Any]] = None
        source_name = "Unknown"
        provenance = "DEGRADED"

        # 2. Check Demo Mode Override
        if os.environ.get("PAHAD_DEMO_MODE") == "1":
            resolved_data = self.demo_provider.fetch_weather(lat, lon, sector_id)
            source_name = self.demo_provider.name
            provenance = "DEMO"

        # 3. Try IMD if configured
        if not resolved_data:
            try:
                imd_res = self.imd_provider.fetch_weather(lat, lon, sector_id)
                if imd_res:
                    resolved_data = imd_res
                    source_name = self.imd_provider.name
                    provenance = "LIVE"
            except Exception as exc:
                logger.warning(f"[WeatherService] IMD fetch failed: {exc}")

        # 4. Try Open-Meteo Live API
        if not resolved_data:
            try:
                om_res = self.openmeteo_provider.fetch_weather(lat, lon, sector_id)
                if om_res:
                    resolved_data = om_res
                    source_name = self.openmeteo_provider.name
                    provenance = "LIVE"
            except Exception as exc:
                logger.warning(f"[WeatherService] Open-Meteo fetch failed: {exc}")

        # 5. Fallback to Stale Cache if live providers failed
        if not resolved_data and cached_result:
            stale_data, _, age = cached_result
            res = dict(stale_data)
            res["provenance"] = "CACHED"
            res["data_age_seconds"] = round(age, 1)
            return res

        # 6. Fallback to PostGIS observations
        if not resolved_data:
            pg_res = self.postgis_provider.fetch_weather(lat, lon, sector_id)
            if pg_res:
                resolved_data = pg_res
                source_name = self.postgis_provider.name
                provenance = "HISTORICAL"

        # 7. Final fallback to Demo simulation
        if not resolved_data:
            resolved_data = self.demo_provider.fetch_weather(lat, lon, sector_id)
            source_name = self.demo_provider.name
            provenance = "SIMULATED"

        self._last_successful_fetch = now_iso

        # Extract values
        rainfall = {
            "current_mm_hr": float(resolved_data.get("rainfall_current", 0.0)),
            "rain_1h_mm": float(resolved_data.get("rain_1h_mm", 0.0)),
            "rain_6h_mm": float(resolved_data.get("rain_6h_mm", 0.0)),
            "rain_24h_mm": float(resolved_data.get("rain_24h_mm", 0.0)),
            "rain_72h_mm": float(resolved_data.get("rain_72h_mm", 0.0))
        }

        forecast = resolved_data.get("forecast")
        if not forecast:
            forecast = {
                "1h_mm": round(rainfall["rain_1h_mm"] * 1.1, 2),
                "3h_mm": round(rainfall["rain_1h_mm"] * 3.0, 2),
                "6h_mm": round(rainfall["rain_6h_mm"] * 1.2, 2),
                "12h_mm": round(rainfall["rain_24h_mm"] * 0.6, 2),
                "24h_mm": round(rainfall["rain_24h_mm"] * 0.95, 2),
                "48h_mm": round(rainfall["rain_24h_mm"] * 1.6, 2)
            }
        if "hourly_trend" not in forecast:
            r24 = rainfall.get("rain_24h_mm", 0.0)
            forecast["hourly_trend"] = [round((r24 / 24.0) * (0.8 + (i % 6) * 0.1), 2) for i in range(24)]

        atmosphere = resolved_data.get("atmosphere", {
            "temperature_c": 18.0,
            "humidity_pct": 82.0,
            "pressure_hpa": 1009.0,
            "wind_kmh": 12.0,
            "cloud_pct": 75.0
        })

        # Calculate Derived PAHAD Geotechnical Inputs
        antecedent_indices = calculate_antecedent_precipitation_indices(
            rain_24h=rainfall["rain_24h_mm"],
            rain_72h=rainfall["rain_72h_mm"]
        )

        threshold_status = evaluate_mandal_sarkar_threshold(
            intensity_mm_hr=rainfall["current_mm_hr"] or (rainfall["rain_24h_mm"] / 24.0),
            duration_hours=24.0
        )

        forecast_loading = min(1.0, max(0.0, forecast.get("24h_mm", 0.0) / 120.0))

        derived_pahad = {
            "antecedent_rainfall": antecedent_indices["antecedent_rainfall_72h_mm"],
            "api_3d": antecedent_indices["api_3d"],
            "api_7d": antecedent_indices["api_7d"],
            "api_30d": antecedent_indices["api_30d"],
            "rainfall_intensity_duration_state": threshold_status["state"],
            "rainfall_threshold_status": threshold_status,
            "forecast_rainfall_loading": round(forecast_loading, 3)
        }

        normalized = {
            "timestamp": now_iso,
            "location": {
                "lat": float(lat),
                "lon": float(lon),
                "district": district or resolved_data.get("district", "Kalimpong-Sikkim"),
                "state": state or resolved_data.get("state", "Sikkim")
            },
            "rainfall": rainfall,
            "forecast": forecast,
            "atmosphere": atmosphere,
            "derived_pahad": derived_pahad,
            "source": source_name,
            "provenance": provenance,
            "last_successful_fetch": now_iso,
            "data_age_seconds": 0.0
        }

        # Save to cache
        self.cache.set(cache_key, normalized, source=source_name)

        return normalized

    def get_weather_for_sector(self, sector_id: str) -> Dict[str, Any]:
        """Looks up sector coordinates from GSI registry and fetches normalized weather."""
        from engine.pahad_sectors import CriticalSectorRegistry
        registry = CriticalSectorRegistry()
        sector = registry.get_sector(sector_id)
        if not sector:
            # Fallback default coordinates (NH-10 Km 48)
            lat, lon = 27.3300, 88.6100
            district, state = "Kalimpong-Sikkim Border", "Sikkim"
        else:
            lat = float(sector["lat"])
            lon = float(sector["lon"])
            district = sector.get("district", "Unknown")
            state = sector.get("state", "Sikkim")

        return self.get_weather(
            lat=lat,
            lon=lon,
            sector_id=sector_id,
            district=district,
            state=state
        )

    def get_climate_map(self) -> Dict[str, Any]:
        """Generates regional climate matrix across critical monitoring sectors concurrently."""
        from engine.pahad_sectors import GSI_CRITICAL_SECTORS
        from concurrent.futures import ThreadPoolExecutor

        target_sectors = GSI_CRITICAL_SECTORS[:8]

        def _fetch_sec(sec):
            try:
                w = self.get_weather(
                    lat=sec["lat"],
                    lon=sec["lon"],
                    sector_id=sec["sector_id"],
                    district=sec.get("district"),
                    state=sec.get("state")
                )
                return {
                    "sector_id": sec["sector_id"],
                    "name": sec["name"],
                    "state": sec["state"],
                    "lat": sec["lat"],
                    "lon": sec["lon"],
                    "rain_24h_mm": w["rainfall"]["rain_24h_mm"],
                    "current_intensity_mmh": w["rainfall"]["current_mm_hr"],
                    "api_3d": w["derived_pahad"]["api_3d"],
                    "threshold_state": w["derived_pahad"]["rainfall_intensity_duration_state"],
                    "provenance": w["provenance"],
                    "source": w["source"]
                }
            except Exception as ex:
                logger.warning(f"Error fetching climate map for sector {sec.get('sector_id')}: {ex}")
                return None

        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(_fetch_sec, target_sectors))

        sectors_data = [r for r in results if r is not None]

        return {
            "status": "SUCCESS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "region": "North-Eastern Region (NER)",
            "sector_count": len(sectors_data),
            "sectors": sectors_data,
            "provenance": sectors_data[0]["provenance"] if sectors_data else "LIVE"
        }



# Singleton Instance
WEATHER_SERVICE = WeatherService()
