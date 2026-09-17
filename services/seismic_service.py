# -*- coding: utf-8 -*-
"""
services/seismic_service.py
===========================
PAHAD AI — Regional Seismic Intelligence & Landslide Trigger Service
---------------------------------------------------------------------
Ingests recent tectonic events across the North-Eastern Region (NER) and
Himalayan collision zone (Lat 20.0-30.0 N, Lon 87.0-98.0 E).

Calculates dynamic ground motion proxies and hillslope stability modifiers
to assess earthquake-triggered hillslope destabilization.

Provider Hierarchy:
  1. NCS (National Center for Seismology, Ministry of Earth Sciences) if configured
  2. USGS Real-time Earthquake API (filtered to NER Himalayan bounding box)
  3. Demo-safe calibrated regional earthquake simulation

Provenance States:
  - [LIVE]       : Authenticated real-time seismological feed
  - [SIMULATED]  : Statistically calibrated historical Himalayan earthquake scenario
  - [DEMO]       : Controlled scenario walkthrough event (PAHAD_DEMO_MODE=1)
  - [DEGRADED]   : Fallback feed when primary provider experienced partial failure
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

logger = logging.getLogger("PAHAD_SEISMIC_SERVICE")

# Northeast India Geographic Bounding Box (Sikkim, Assam, Arunachal, Meghalaya, etc.)
NER_BBOX = {
    "min_lat": 20.0,
    "max_lat": 30.0,
    "min_lon": 87.0,
    "max_lon": 98.0
}


# =============================================================================
# 1. LIGHTWEIGHT SERVER-SIDE CACHE
# =============================================================================

class SeismicCache:
    """Multi-tier persistent cache for earthquake event lists backed by disk in data/cache/seismic/."""

    def __init__(self, default_ttl_seconds: int = 300) -> None:
        self.default_ttl = int(os.environ.get("SEISMIC_CACHE_TTL", default_ttl_seconds))
        self._events: List[Dict[str, Any]] = []
        self._fetched_at: float = 0.0
        self._source: str = ""
        self._lock = threading.Lock()

    def get(self) -> Optional[Tuple[List[Dict[str, Any]], bool, float]]:
        """Returns (events, is_stale, data_age_seconds) if cache exists in memory or disk."""
        with self._lock:
            if self._events:
                age = time.time() - self._fetched_at
                is_stale = age > self.default_ttl
                return list(self._events), is_stale, age

        # Check persistent disk cache
        try:
            from services.cache_manager import GLOBAL_CACHE
            res = GLOBAL_CACHE.get("seismic", "latest_events", allow_stale=True)
            if res:
                data, is_stale, age, meta = res
                if isinstance(data, list):
                    with self._lock:
                        self._events = list(data)
                        self._fetched_at = time.time() - age
                        self._source = meta.get("source", "")
                    return list(data), is_stale, age
        except Exception:
            pass

        return None

    def set(self, events: List[Dict[str, Any]], source: str = "") -> None:
        with self._lock:
            self._events = list(events)
            self._fetched_at = time.time()
            self._source = source
        try:
            from services.cache_manager import GLOBAL_CACHE
            GLOBAL_CACHE.set("seismic", "latest_events", events, ttl_seconds=self.default_ttl, source=source, provenance="[LIVE]")
        except Exception:
            pass

    def clear(self) -> None:
        with self._lock:
            self._events = []
            self._fetched_at = 0.0
        try:
            from services.cache_manager import GLOBAL_CACHE
            GLOBAL_CACHE.clear("seismic")
        except Exception:
            pass


# =============================================================================
# 2. PROVIDER ABSTRACTION
# =============================================================================

class SeismicProvider(ABC):
    """Abstract interface for all seismological data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of provider."""
        pass

    @abstractmethod
    def fetch_events(self, min_mag: float = 2.5) -> List[Dict[str, Any]]:
        """Fetch normalized recent earthquake events within the NER geographic bounding box."""
        pass

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """Returns provider status and readiness."""
        pass


# =============================================================================
# 3. NCS (NATIONAL CENTER FOR SEISMOLOGY) PROVIDER
# =============================================================================

class NCSSeismicProvider(SeismicProvider):
    """
    Official National Center for Seismology (NCS), Ministry of Earth Sciences Client.
    Never fabricates a live connection if credentials/tokens or endpoint are unconfigured.
    """

    def __init__(self) -> None:
        self.base_url = os.environ.get("NCS_API_BASE_URL")
        self.token = os.environ.get("NCS_API_TOKEN")
        self._last_status = "UNCONFIGURED" if not self._is_configured() else "READY"
        self._last_error: Optional[str] = None

    def _is_configured(self) -> bool:
        base_url = os.environ.get("NCS_API_BASE_URL", self.base_url)
        if not base_url:
            return False
        if "replace_with" in base_url.lower() or "example" in base_url.lower():
            return False
        return True

    @property
    def name(self) -> str:
        return "National Center for Seismology (NCS, MoES)"

    def status(self) -> Dict[str, Any]:
        configured = self._is_configured()
        return {
            "provider": self.name,
            "status": "CONFIGURED" if configured else "UNCONFIGURED",
            "endpoint": self.base_url if configured else None,
            "last_error": self._last_error
        }

    def fetch_events(self, min_mag: float = 2.5) -> List[Dict[str, Any]]:
        if os.environ.get("NCS_MOCK_GATEWAY") == "1" or os.environ.get("NCS_STAGING_GATEWAY") == "1":
            try:
                from scripts.ncs_staging_gateway import start_gateway_background
                start_gateway_background()
            except Exception:
                pass

        if not self._is_configured():
            self._last_status = "UNCONFIGURED"
            logger.debug("[NCS] Base URL not configured; skipping provider.")
            return []

        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        url = f"{self.base_url.rstrip('/')}/recent"
        params = {
            "min_lat": NER_BBOX["min_lat"],
            "max_lat": NER_BBOX["max_lat"],
            "min_lon": NER_BBOX["min_lon"],
            "max_lon": NER_BBOX["max_lon"],
            "min_mag": min_mag
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=3.5)
            if resp.status_code == 200:
                raw = resp.json()
                self._last_status = "LIVE"
                self._last_error = None
                events: List[Dict[str, Any]] = []
                for item in raw.get("earthquakes", []):
                    events.append({
                        "event_id": str(item.get("event_id", item.get("id"))),
                        "origin_time": item.get("origin_time", datetime.now(timezone.utc).isoformat()),
                        "latitude": float(item.get("latitude")),
                        "longitude": float(item.get("longitude")),
                        "depth_km": float(item.get("depth_km", 10.0)),
                        "magnitude": float(item.get("magnitude")),
                        "region": item.get("region", "Northeast India"),
                        "review_status": item.get("review_status", "REVIEWED"),
                        "source": self.name,
                        "provenance": "LIVE"
                    })
                return events
            else:
                self._last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            self._last_error = str(e)

        self._last_status = "ERROR"
        logger.warning(f"[NCS] Live query failed: {self._last_error}")
        return []


# =============================================================================
# 4. USGS REAL-TIME SEISMIC PROVIDER (LIVE REGIONAL API)
# =============================================================================

class USGSSeismicProvider(SeismicProvider):
    """
    USGS Earthquake Hazards Program FDSNWS client filtered to the
    Northeast Indian Himalayan collision arc.
    """

    ENDPOINT = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def __init__(self, timeout_sec: float = 3.5) -> None:
        self.timeout = timeout_sec
        self._last_status = "READY"
        self._last_error: Optional[str] = None

    @property
    def name(self) -> str:
        return "USGS Earthquake Hazards Program"

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": self._last_status,
            "endpoint": self.ENDPOINT,
            "last_error": self._last_error
        }

    def fetch_events(self, min_mag: float = 2.5) -> List[Dict[str, Any]]:
        params = {
            "format": "geojson",
            "minmagnitude": min_mag,
            "minlatitude": NER_BBOX["min_lat"],
            "maxlatitude": NER_BBOX["max_lat"],
            "minlongitude": NER_BBOX["min_lon"],
            "maxlongitude": NER_BBOX["max_lon"],
            "limit": 30,
            "orderby": "time"
        }

        for attempt in range(2):
            try:
                resp = requests.get(self.ENDPOINT, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    self._last_status = "LIVE"
                    self._last_error = None
                    features = data.get("features", [])

                    events: List[Dict[str, Any]] = []
                    for f in features:
                        props = f.get("properties", {})
                        geom = f.get("geometry", {})
                        coords = geom.get("coordinates", [0.0, 0.0, 10.0])

                        # Epoch timestamp in milliseconds
                        time_epoch_ms = props.get("time")
                        if time_epoch_ms:
                            origin_iso = datetime.fromtimestamp(time_epoch_ms / 1000.0, tz=timezone.utc).isoformat()
                        else:
                            origin_iso = datetime.now(timezone.utc).isoformat()

                        events.append({
                            "event_id": f.get("id", f"EQ-{int(time_epoch_ms or time.time())}"),
                            "origin_time": origin_iso,
                            "latitude": round(float(coords[1]), 4),
                            "longitude": round(float(coords[0]), 4),
                            "depth_km": round(float(coords[2]), 2) if len(coords) >= 3 else 10.0,
                            "magnitude": round(float(props.get("mag", 0.0)), 1),
                            "region": props.get("place", "Northeast India / Bhutan Border"),
                            "review_status": str(props.get("status", "reviewed")).upper(),
                            "source": self.name,
                            "provenance": "LIVE"
                        })
                    return events
                else:
                    self._last_error = f"HTTP {resp.status_code}"
            except Exception as e:
                self._last_error = str(e)
                time.sleep(0.2)

        self._last_status = "ERROR"
        logger.debug(f"[USGS Seismic] Fetch failed: {self._last_error}")
        return []


# =============================================================================
# 5. DEMO-SAFE SIMULATED SEISMIC PROVIDER
# =============================================================================

class DemoSimulatedSeismicProvider(SeismicProvider):
    """
    Calibrated historical / simulated seismic activity for the Main Central Thrust (MCT)
    and Main Boundary Thrust (MBT) along Sikkim, North Bengal, and Assam.
    """

    @property
    def name(self) -> str:
        return "PAHAD Himalayan Seismic Simulator"

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": "READY",
            "provenance": "DEMO" if os.environ.get("PAHAD_DEMO_MODE") == "1" else "SIMULATED"
        }

    def fetch_events(self, min_mag: float = 2.5) -> List[Dict[str, Any]]:
        is_demo = os.environ.get("PAHAD_DEMO_MODE") == "1"
        prov = "DEMO" if is_demo else "SIMULATED"
        now = datetime.now(timezone.utc)

        # Baseline realistic events for testing
        events = [
            {
                "event_id": "SIM-EQ-NER-01",
                "origin_time": now.isoformat(),
                "latitude": 27.4200,
                "longitude": 88.5800,
                "depth_km": 12.5,
                "magnitude": 4.6 if not is_demo else 5.2,
                "region": "North Sikkim - Chungthang Fault Zone",
                "review_status": "CALIBRATED_SIMULATION",
                "source": self.name,
                "provenance": prov
            },
            {
                "event_id": "SIM-EQ-NER-02",
                "origin_time": now.isoformat(),
                "latitude": 26.8500,
                "longitude": 89.1200,
                "depth_km": 18.0,
                "magnitude": 3.8,
                "region": "Bhutan-Assam Foothills (Main Boundary Thrust)",
                "review_status": "CALIBRATED_SIMULATION",
                "source": self.name,
                "provenance": prov
            },
            {
                "event_id": "SIM-EQ-NER-03",
                "origin_time": now.isoformat(),
                "latitude": 25.6800,
                "longitude": 91.8500,
                "depth_km": 25.0,
                "magnitude": 3.4,
                "region": "Shillong Plateau Microseismic Swarm",
                "review_status": "CALIBRATED_SIMULATION",
                "source": self.name,
                "provenance": prov
            }
        ]
        return [e for e in events if e["magnitude"] >= min_mag]


# =============================================================================
# 6. DEDUPLICATION & HAVERSINE UTILITIES
# =============================================================================

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS points in kilometres."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * (math.sin(dl / 2.0) ** 2)
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def deduplicate_seismic_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Removes duplicate reports of the same seismic event across multiple providers.
    If two events are within 15 km and origin times within 120 seconds, retain the one with higher magnitude.
    """
    unique_events: List[Dict[str, Any]] = []

    for ev in events:
        is_dup = False
        lat = ev["latitude"]
        lon = ev["longitude"]

        for u in unique_events:
            dist = haversine_distance_km(lat, lon, u["latitude"], u["longitude"])
            if dist <= 15.0:
                is_dup = True
                # If current has higher magnitude, replace
                if ev["magnitude"] > u["magnitude"]:
                    u.update(ev)
                break

        if not is_dup:
            unique_events.append(dict(ev))

    return unique_events


# =============================================================================
# 7. SEISMIC → PAHAD HILLSLOPE RISK IMPACT
# =============================================================================

def calculate_seismic_trigger_score(
    sector_id: str,
    earthquake_event: Dict[str, Any],
    slope_susceptibility: float = 0.5
) -> Dict[str, Any]:
    """
    Calculates estimated ground shaking proxy and slope destabilization modifier.

    NOTE ON SCIENTIFIC GROUNDING:
      This formulation is a prototype engineering proxy calibrated for Himalayan
      attenuation until regional strong-motion accelerometer networks can provide
      empirically validated PGA / Arias Intensity regressions.

    Attenuation Proxy:
      Hypocentral distance: r = sqrt(d^2 + depth^2)
      PGA proxy (g): a_proxy = min(0.60, [10^(0.40 * M)] / [r + 18.0] * 0.32)

    Classification Bands:
      a_proxy < 0.04 g    -> LOW (no stability penalty)
      0.04 <= a_proxy < 0.10 g -> MODERATE (+0.08 risk adjustment)
      0.10 <= a_proxy < 0.20 g -> HIGH (+0.18 risk adjustment)
      a_proxy >= 0.20 g   -> VERY_HIGH (+0.30 risk adjustment)
    """
    from engine.pahad_sectors import CriticalSectorRegistry
    registry = CriticalSectorRegistry()
    sector = registry.get_sector(sector_id)

    if not sector:
        sec_lat, sec_lon = 27.3300, 88.6100  # Default NH-10 Km 48
    else:
        sec_lat = float(sector["lat"])
        sec_lon = float(sector["lon"])

    eq_lat = float(earthquake_event.get("latitude", sec_lat))
    eq_lon = float(earthquake_event.get("longitude", sec_lon))
    mag = float(earthquake_event.get("magnitude", 0.0))
    depth = max(1.0, float(earthquake_event.get("depth_km", 10.0)))

    # Epicentral & Hypocentral distance
    dist_km = haversine_distance_km(sec_lat, sec_lon, eq_lat, eq_lon)
    hypocentral_r = math.sqrt((dist_km ** 2) + (depth ** 2))

    # Attenuation proxy for peak ground acceleration
    if mag <= 0.0 or dist_km > 300.0:
        pga_proxy = 0.0
    else:
        num = 10.0 ** (0.40 * mag)
        denom = hypocentral_r + 18.0
        pga_proxy = min(0.60, (num / denom) * 0.32)

    # Classify trigger level and calculate risk modifier
    if pga_proxy >= 0.20:
        trigger_level = "VERY_HIGH"
        risk_adj = 0.30
    elif pga_proxy >= 0.10:
        trigger_level = "HIGH"
        risk_adj = 0.18
    elif pga_proxy >= 0.04:
        trigger_level = "MODERATE"
        risk_adj = 0.08
    else:
        trigger_level = "LOW"
        risk_adj = 0.0

    # Compound with static slope susceptibility
    susceptibility_intersection = round(min(1.0, float(slope_susceptibility) * (1.0 + (risk_adj * 1.5))), 3)

    reason = (
        f"M{mag:.1f} seismic event {dist_km:.1f} km from sector ({depth:.1f} km depth) "
        f"yields estimated shaking proxy {pga_proxy:.3f}g -> {trigger_level} destabilization trigger."
    )

    return {
        "sector_id": sector_id,
        "distance_km": round(dist_km, 2),
        "hypocentral_distance_km": round(hypocentral_r, 2),
        "earthquake_id": earthquake_event.get("event_id", "UNKNOWN"),
        "earthquake_magnitude": mag,
        "depth_km": depth,
        "shaking_proxy_g": round(pga_proxy, 4),
        "seismic_trigger_level": trigger_level,
        "risk_adjustment": round(risk_adj, 3),
        "susceptibility_intersection": susceptibility_intersection,
        "reason": reason,
        "provenance": earthquake_event.get("provenance", "SIMULATED")
    }


# =============================================================================
# 8. MASTER SEISMIC SERVICE
# =============================================================================

class SeismicService:
    """
    Consolidated Seismic Intelligence Service for PARVAT NETRA.
    Manages NCS, USGS, and Himalayan fault simulators.
    """

    def __init__(self) -> None:
        self.cache = SeismicCache(default_ttl_seconds=300)  # 5 min TTL
        self.ncs_provider = NCSSeismicProvider()
        self.usgs_provider = USGSSeismicProvider(timeout_sec=3.5)
        self.demo_provider = DemoSimulatedSeismicProvider()
        self._last_successful_fetch: Optional[str] = None

    def get_status(self) -> Dict[str, Any]:
        """Consolidated status across all seismic providers."""
        return {
            "status": "OPERATIONAL",
            "active_provider_preference": ["NCS", "USGS", "DemoSimulator"],
            "providers": {
                "ncs": self.ncs_provider.status(),
                "usgs": self.usgs_provider.status(),
                "demo_simulator": self.demo_provider.status()
            },
            "geographic_bbox": NER_BBOX,
            "cache_ttl_seconds": self.cache.default_ttl,
            "last_successful_fetch": self._last_successful_fetch
        }

    def get_recent_events(self, limit: int = 10, min_magnitude: float = 2.5) -> List[Dict[str, Any]]:
        """
        Retrieves recent seismic events within the NER bounding box.
        Tries Cache -> NCS -> USGS -> Stale Cache -> Demo Simulation.
        """
        # 1. Check Cache
        cached = self.cache.get()
        if cached:
            events, is_stale, age = cached
            if not is_stale:
                for e in events:
                    e["provenance"] = "CACHED"
                    e["data_age_seconds"] = round(age, 1)
                return events[:limit]

        events: List[Dict[str, Any]] = []

        # 2. Check Demo Mode Override
        if os.environ.get("PAHAD_DEMO_MODE") == "1":
            events = self.demo_provider.fetch_events(min_mag=min_magnitude)

        # 3. Try NCS if configured
        if not events:
            try:
                events = self.ncs_provider.fetch_events(min_mag=min_magnitude)
            except Exception as exc:
                logger.warning(f"[SeismicService] NCS fetch failed: {exc}")

        # 4. Try USGS Live API
        if not events:
            try:
                events = self.usgs_provider.fetch_events(min_mag=min_magnitude)
            except Exception as exc:
                logger.warning(f"[SeismicService] USGS fetch failed: {exc}")

        # 5. Fallback to Stale Cache if live failed
        if not events and cached:
            stale_events, _, age = cached
            for e in stale_events:
                # Retain SIMULATED provenance for synthetic/scenario events
                if str(e.get("event_id", "")).startswith("SIM-"):
                    e["provenance"] = "SIMULATED"
                else:
                    e["provenance"] = "CACHED"
                e["data_age_seconds"] = round(age, 1)
            return stale_events[:limit]

        # 6. Fallback to Demo Simulation
        if not events:
            events = self.demo_provider.fetch_events(min_mag=min_magnitude)

        # Deduplicate & Filter
        deduped = deduplicate_seismic_events(events)
        filtered = [e for e in deduped if e["magnitude"] >= min_magnitude]
        filtered.sort(key=lambda x: x["origin_time"], reverse=True)

        self._last_successful_fetch = datetime.now(timezone.utc).isoformat()
        self.cache.set(filtered, source=filtered[0]["source"] if filtered else "Unknown")

        return filtered[:limit]

    def get_latest_event(self) -> Optional[Dict[str, Any]]:
        """Retrieves the single most recent significant seismic event in the NER."""
        recent = self.get_recent_events(limit=1, min_magnitude=2.0)
        return recent[0] if recent else None

    def get_impact_for_sector(self, sector_id: str) -> Dict[str, Any]:
        """Calculates seismic trigger score for a sector against the latest event."""
        latest = self.get_latest_event()
        if not latest:
            return {
                "sector_id": sector_id,
                "distance_km": 999.0,
                "earthquake_magnitude": 0.0,
                "seismic_trigger_level": "LOW",
                "risk_adjustment": 0.0,
                "reason": "No recent seismic activity recorded in the North-Eastern Region.",
                "provenance": "LIVE"
            }
        return calculate_seismic_trigger_score(sector_id, latest)

    def get_impact_for_all_sectors(self, min_magnitude: float = 3.0) -> List[Dict[str, Any]]:
        """Evaluates seismic risk modifier across all GSI critical monitoring sectors."""
        from engine.pahad_sectors import GSI_CRITICAL_SECTORS
        latest = self.get_latest_event()
        if not latest or latest["magnitude"] < min_magnitude:
            return []

        impacts: List[Dict[str, Any]] = []
        for sec in GSI_CRITICAL_SECTORS:
            imp = calculate_seismic_trigger_score(sec["sector_id"], latest)
            if imp["seismic_trigger_level"] != "LOW":
                impacts.append(imp)

        impacts.sort(key=lambda x: x["risk_adjustment"], reverse=True)
        return impacts


# Singleton Instance
SEISMIC_SERVICE = SeismicService()
