# -*- coding: utf-8 -*-
"""
services/ncs_service.py
========================
NCS Real Data Connector with USGS public API fallback for NER Himalayan
bounding box. Never fabricates seismic events.

Provider hierarchy:
  1. NCS (National Center for Seismology, MoES) — if NCS_API_BASE_URL configured
  2. USGS Earthquake Hazards API — public endpoint, no auth required

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

import requests

logger = logging.getLogger("PAHAD_NCS_SERVICE")

# NER Himalayan bounding box
NER_BBOX = {
    "min_lat": 20.0, "max_lat": 30.0,
    "min_lon": 87.0, "max_lon": 98.0,
}

# USGS public FDSNws event API — no authentication required
USGS_FDSN_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


@dataclass
class NCSObservation:
    """A single structured seismic event observation."""
    event_id: str
    timestamp: str          # ISO 8601 origin time
    magnitude: float
    magnitude_type: str     # 'Mw', 'ML', 'mb', etc.
    depth_km: float
    latitude: float
    longitude: float
    region: str
    source: str             # 'NCS' or 'USGS'
    provenance: str         # LIVE / AUTH_REQUIRED / UNAVAILABLE
    quality: str            # GOOD / DEGRADED / UNAVAILABLE
    received_at: str        # ISO 8601 ingestion time
    distance_to_sector: Optional[float] = None
    origin_time: Optional[str] = None

    def __post_init__(self):
        if self.origin_time is None:
            self.origin_time = self.timestamp

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d.get("origin_time") is None:
            d["origin_time"] = self.timestamp
        return d


class NCSConnector:
    """
    Seismic event connector with NCS primary + USGS public fallback.

    NCS (National Center for Seismology):
      - Requires NCS_API_BASE_URL and optionally NCS_API_TOKEN
      - Returns UNAVAILABLE if endpoint unreachable

    USGS Earthquake Hazards Program:
      - Public API, no authentication required
      - Used automatically when NCS is not configured
      - Bounding box: NER Himalayan region (20–30°N, 87–98°E)
    """

    def __init__(self) -> None:
        self.ncs_base_url = os.environ.get("NCS_API_BASE_URL", "")
        self.ncs_token = os.environ.get("NCS_API_TOKEN", "")
        self.status = "READY" if self._is_ncs_configured() else "USGS_FALLBACK"
        self._last_error: Optional[str] = None
        logger.info(f"[NCS] Connector initialized. Status: {self.status}")

    def _is_ncs_configured(self) -> bool:
        if not self.ncs_base_url:
            return False
        for placeholder in ("replace_with", "example", "http://localhost"):
            if placeholder in self.ncs_base_url.lower():
                return False
        return True

    def verify_connection(self) -> Dict[str, Any]:
        """
        Verify NCS endpoint configuration and fallback status.
        Returns status diagnostics distinguishing NCS auth state from USGS fallback.
        """
        t0 = time.time()
        if not self._is_ncs_configured():
            return {
                "status": "AUTH_REQUIRED",
                "ncs_status": "AUTH_REQUIRED",
                "auth_state": "AUTH_REQUIRED",
                "provider": "National Center for Seismology (NCS, MoES)",
                "authenticated": False,
                "endpoint": None,
                "fallback_provider": "USGS",
                "fallback_status": "ACTIVE",
                "error": "NCS_API_BASE_URL is not configured in .env",
                "action_required": "Configure official NCS credentials in .env (NCS_API_BASE_URL and NCS_API_TOKEN)",
                "checked_at": datetime.now(timezone.utc).isoformat()
            }

        url = f"{self.ncs_base_url.rstrip('/')}/health"
        headers = {"Accept": "application/json"}
        if self.ncs_token:
            headers["Authorization"] = f"Bearer {self.ncs_token}"

        try:
            resp = requests.get(url, headers=headers, timeout=5.0)
            latency = round((time.time() - t0) * 1000, 1)
            if resp.status_code == 200:
                return {
                    "status": "LIVE",
                    "ncs_status": "LIVE",
                    "auth_state": "CONFIGURED",
                    "provider": "National Center for Seismology (NCS, MoES)",
                    "authenticated": True,
                    "endpoint": self.ncs_base_url,
                    "latency_ms": latency,
                    "error": None,
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            elif resp.status_code in (401, 403):
                return {
                    "status": "AUTH_REQUIRED",
                    "ncs_status": "AUTH_REQUIRED",
                    "auth_state": "AUTH_REQUIRED",
                    "provider": "National Center for Seismology (NCS, MoES)",
                    "authenticated": False,
                    "endpoint": self.ncs_base_url,
                    "latency_ms": latency,
                    "error": f"HTTP {resp.status_code} Unauthorized",
                    "action_required": "Provide valid unexpired NCS_API_TOKEN in .env",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "status": "UNAVAILABLE",
                    "ncs_status": "UNAVAILABLE",
                    "auth_state": "CONFIGURED",
                    "provider": "National Center for Seismology (NCS, MoES)",
                    "authenticated": False,
                    "endpoint": self.ncs_base_url,
                    "latency_ms": latency,
                    "error": f"HTTP {resp.status_code}",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
        except Exception as exc:
            latency = round((time.time() - t0) * 1000, 1)
            return {
                "status": "UNAVAILABLE",
                "ncs_status": "UNAVAILABLE",
                "auth_state": "CONFIGURED",
                "provider": "National Center for Seismology (NCS, MoES)",
                "authenticated": False,
                "endpoint": self.ncs_base_url,
                "latency_ms": latency,
                "error": str(exc),
                "checked_at": datetime.now(timezone.utc).isoformat()
            }

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "National Center for Seismology (NCS, MoES)",
            "status": self.status,
            "ncs_status": "READY" if self._is_ncs_configured() else "AUTH_REQUIRED",
            "auth_state": "CONFIGURED" if self._is_ncs_configured() else "AUTH_REQUIRED",
            "active_source": "NCS" if self._is_ncs_configured() else "USGS",
            "ncs_configured": self._is_ncs_configured(),
            "usgs_fallback": "ALWAYS_AVAILABLE",
            "endpoint": self.ncs_base_url if self._is_ncs_configured() else None,
            "last_error": self._last_error,
            "note": (
                "NCS primary not configured (status=AUTH_REQUIRED). Using USGS public API fallback. "
                "Set NCS_API_BASE_URL in .env for official NCS data."
                if not self._is_ncs_configured()
                else "NCS primary endpoint configured."
            )
        }

    def fetch_recent_events(
        self,
        min_mag: float = 2.5,
        hours_back: int = 24,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[NCSObservation]:
        """
        Fetch recent seismic events within the NER bounding box.

        Tries NCS first if configured, then falls back to USGS public API.
        Returns empty list only if both are unreachable.
        """
        bb = bbox or NER_BBOX

        # Try NCS first
        if self._is_ncs_configured():
            ncs_result = self._fetch_from_ncs(min_mag, hours_back, bb)
            if ncs_result is not None:
                return ncs_result

        # USGS fallback (always attempted)
        return self._fetch_from_usgs(min_mag, hours_back, bb)

    def _fetch_from_ncs(
        self,
        min_mag: float,
        hours_back: int,
        bb: Dict[str, float]
    ) -> Optional[List[NCSObservation]]:
        """Attempt NCS API. Returns None on failure so USGS fallback can proceed."""
        received_at = datetime.now(timezone.utc).isoformat()
        headers = {"Accept": "application/json"}
        if self.ncs_token:
            headers["Authorization"] = f"Bearer {self.ncs_token}"

        url = f"{self.ncs_base_url.rstrip('/')}/recent"
        params = {
            "min_lat": bb["min_lat"], "max_lat": bb["max_lat"],
            "min_lon": bb["min_lon"], "max_lon": bb["max_lon"],
            "min_mag": min_mag,
            "hours": hours_back
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=5.0)
            if resp.status_code == 200:
                raw = resp.json()
                self.status = "LIVE_NCS"
                self._last_error = None
                events = []
                for item in raw.get("earthquakes", raw.get("features", [])):
                    events.append(NCSObservation(
                        event_id=str(item.get("id", "")),
                        timestamp=item.get("time", received_at),
                        magnitude=float(item.get("magnitude", item.get("mag", 0.0))),
                        magnitude_type=item.get("magnitude_type", "ML"),
                        depth_km=float(item.get("depth", 0.0)),
                        latitude=float(item.get("latitude", item.get("lat", 0.0))),
                        longitude=float(item.get("longitude", item.get("lon", 0.0))),
                        region=item.get("region", "NER Himalayan Zone"),
                        source="NCS",
                        provenance="LIVE",
                        quality="GOOD",
                        received_at=received_at
                    ))
                logger.info(f"[NCS] Fetched {len(events)} events from NCS")
                return events
            logger.warning(f"[NCS] HTTP {resp.status_code}")
            return None
        except Exception as exc:
            logger.warning(f"[NCS] Failed to reach NCS: {exc}")
            self._last_error = str(exc)
            return None

    def _fetch_from_usgs(
        self,
        min_mag: float,
        hours_back: int,
        bb: Dict[str, float]
    ) -> List[NCSObservation]:
        """Fetch from USGS public FDSNws event API. No auth required."""
        received_at = datetime.now(timezone.utc).isoformat()
        start_time = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        params = {
            "format": "geojson",
            "minmagnitude": min_mag,
            "minlatitude": bb["min_lat"],
            "maxlatitude": bb["max_lat"],
            "minlongitude": bb["min_lon"],
            "maxlongitude": bb["max_lon"],
            "starttime": start_time,
            "limit": 100,
            "orderby": "time"
        }

        try:
            resp = requests.get(USGS_FDSN_URL, params=params, timeout=8.0)
            if resp.status_code == 200:
                data = resp.json()
                events = self._parse_usgs_response(data, received_at)
                self.status = "LIVE_USGS"
                self._last_error = None
                logger.info(f"[NCS/USGS] Fetched {len(events)} events from USGS")
                return events

            logger.warning(f"[NCS/USGS] USGS returned HTTP {resp.status_code}")
            self.status = "UNAVAILABLE"
            return []

        except requests.exceptions.ConnectionError:
            logger.warning("[NCS/USGS] USGS unreachable (network error)")
            self.status = "UNAVAILABLE"
            self._last_error = "USGS unreachable"
            return []
        except Exception as exc:
            logger.error(f"[NCS/USGS] Unexpected error: {exc}")
            self.status = "UNAVAILABLE"
            self._last_error = str(exc)
            return []

    def _parse_usgs_response(
        self,
        data: Dict[str, Any],
        received_at: str
    ) -> List[NCSObservation]:
        """Parse USGS GeoJSON FeatureCollection into NCSObservation list."""
        events = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [0.0, 0.0, 0.0])  # [lon, lat, depth]

            # Convert USGS epoch milliseconds to ISO
            epoch_ms = props.get("time")
            if epoch_ms:
                ts = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()
            else:
                ts = received_at

            events.append(NCSObservation(
                event_id=feature.get("id", "USGS_UNKNOWN"),
                timestamp=ts,
                magnitude=float(props.get("mag", 0.0) or 0.0),
                magnitude_type=str(props.get("magType", "Mw")),
                depth_km=float(coords[2]) if len(coords) > 2 else 0.0,
                latitude=float(coords[1]) if len(coords) > 1 else 0.0,
                longitude=float(coords[0]) if coords else 0.0,
                region=str(props.get("place", "NER Himalayan Zone")),
                source="USGS",
                provenance="LIVE",
                quality="GOOD",
                received_at=received_at
            ))
        return events

    def derive_seismic_indicators(
        self,
        events: List[NCSObservation],
        sector_lat: float,
        sector_lon: float
    ) -> Dict[str, Any]:
        """
        Derive aggregated seismic metrics for a sector location from recent events:
          - count_24h: number of events within past 24h
          - count_72h: number of events within past 72h
          - max_magnitude: maximum magnitude observed in past 72h (or 0.0)
          - nearest_distance_km: distance in km to closest event (or 999.0)
          - recency_hours: hours since most recent event (or None)
          - source: 'NCS', 'USGS', or 'UNAVAILABLE'
          - quality: 'GOOD', 'DEGRADED', or 'UNAVAILABLE'
        """
        import math
        now = datetime.now(timezone.utc)
        count_24h = 0
        count_72h = 0
        max_mag = 0.0
        nearest_dist = 999.0
        most_recent_hours: Optional[float] = None

        if not events:
            return {
                "count_24h": 0,
                "count_72h": 0,
                "max_magnitude": 0.0,
                "nearest_distance_km": 999.0,
                "recency_hours": None,
                "source": "UNAVAILABLE",
                "quality": "UNAVAILABLE",
            }

        source = events[0].source
        quality = events[0].quality

        def _calc_dist(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            r = 6371.0
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return r * c

        for ev in events:
            try:
                ev_time = datetime.fromisoformat(ev.timestamp.replace("Z", "+00:00"))
                age_h = (now - ev_time).total_seconds() / 3600.0
            except Exception:
                age_h = 12.0

            dist = _calc_dist(sector_lat, sector_lon, ev.latitude, ev.longitude)
            ev.distance_to_sector = round(dist, 2)

            if age_h <= 24.0:
                count_24h += 1
            if age_h <= 72.0:
                count_72h += 1
                if ev.magnitude > max_mag:
                    max_mag = ev.magnitude

            if dist < nearest_dist:
                nearest_dist = dist

            if most_recent_hours is None or age_h < most_recent_hours:
                most_recent_hours = age_h

        return {
            "count_24h": count_24h,
            "count_72h": count_72h,
            "max_magnitude": round(max_mag, 2),
            "nearest_distance_km": round(nearest_dist, 1) if nearest_dist < 999.0 else 999.0,
            "recency_hours": round(most_recent_hours, 1) if most_recent_hours is not None else None,
            "source": source,
            "quality": quality,
        }


# Global singleton
NCS_CONNECTOR = NCSConnector()
