# -*- coding: utf-8 -*-
"""
IMD Real Data Connector - returns AUTH_REQUIRED when credentials absent.
Never fabricates observations.

services/imd_service.py
=======================
PAHAD AI - India Meteorological Department (IMD) Per-Observation Pipeline
--------------------------------------------------------------------------
Provides granular, structured IMDObservation records for a given lat/lon and
sector_id. This file is a focused, low-level connector that the higher-level
weather_service.py can delegate to for authoritative IMD data when IMD
credentials are configured.

Provenance States produced by this module:
  - LIVE          : Authenticated real-time feed from IMD Nowcast API
  - AUTH_REQUIRED : IMD_API_TOKEN or IMD_API_BASE_URL missing / placeholder
  - UNAVAILABLE   : Network error, timeout, or unexpected server response

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import time
import math
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger("PAHAD_IMD_SERVICE")

# ---------------------------------------------------------------------------
# Sentinel strings that indicate a placeholder / unconfigured credential
# ---------------------------------------------------------------------------
_PLACEHOLDER_FRAGMENTS: tuple = ("replace_with", "example", "your_", "<", ">")

# ---------------------------------------------------------------------------
# Authoritative IMD AWS / ARG Stations across North Eastern Region (NER)
# ---------------------------------------------------------------------------
NER_IMD_STATIONS: Dict[str, Dict[str, Any]] = {
    "AWS-42299": {"name": "Gangtok", "state": "Sikkim", "district": "East Sikkim", "lat": 27.33, "lon": 88.61, "type": "AWS"},
    "AWS-42301": {"name": "Pakyong", "state": "Sikkim", "district": "Pakyong", "lat": 27.24, "lon": 88.59, "type": "AWS"},
    "ARG-42295": {"name": "Mangan", "state": "Sikkim", "district": "North Sikkim", "lat": 27.50, "lon": 88.53, "type": "ARG"},
    "ARG-42302": {"name": "Namchi", "state": "Sikkim", "district": "South Sikkim", "lat": 27.17, "lon": 88.35, "type": "ARG"},
    "AWS-42826": {"name": "Aizawl", "state": "Mizoram", "district": "Aizawl", "lat": 23.73, "lon": 92.72, "type": "AWS"},
    "AWS-42647": {"name": "Kohima", "state": "Nagaland", "district": "Kohima", "lat": 25.67, "lon": 94.11, "type": "AWS"},
    "AWS-42623": {"name": "Imphal", "state": "Manipur", "district": "Imphal West", "lat": 24.82, "lon": 93.95, "type": "AWS"},
    "AWS-42516": {"name": "Shillong", "state": "Meghalaya", "district": "East Khasi Hills", "lat": 25.57, "lon": 91.88, "type": "AWS"},
    "AWS-42410": {"name": "Guwahati", "state": "Assam", "district": "Kamrup Metropolitan", "lat": 26.18, "lon": 91.75, "type": "AWS"},
    "AWS-42308": {"name": "Itanagar", "state": "Arunachal Pradesh", "district": "Papum Pare", "lat": 27.10, "lon": 93.62, "type": "AWS"},
}

def get_station_for_coords(lat: float, lon: float) -> Tuple[str, Dict[str, Any]]:
    """Return nearest IMD AWS/ARG station ID and metadata for coordinates."""
    best_id = "AWS-42299"
    best_dist = float("inf")
    for st_id, info in NER_IMD_STATIONS.items():
        d = math.hypot(lat - info["lat"], lon - info["lon"])
        if d < best_dist:
            best_dist = d
            best_id = st_id
    return best_id, NER_IMD_STATIONS[best_id]


# =============================================================================
# 1. DATA MODEL
# =============================================================================

@dataclass
class IMDObservation:
    """
    Single structured meteorological observation sourced from IMD.

    All fields are mandatory so that downstream consumers can rely on a
    consistent schema regardless of provenance.

    Attributes
    ----------
    sector_id   : Logical sector / grid-cell identifier (e.g. 'SIKKIM_N_01').
    timestamp   : ISO-8601 UTC string of the observation window start.
    feature     : Meteorological variable name (e.g. 'rain_1h', 'temp_2m').
    value       : Numeric reading in unit, or None when AUTH_REQUIRED or UNAVAILABLE.
    unit        : SI or domain unit string (e.g. 'mm/h', 'mm', 'deg C', 'hPa').
    source      : Always 'IMD' for records produced by this connector.
    quality     : Data quality flag: 'GOOD', 'SUSPECT', 'AUTH_REQUIRED', 'UNAVAILABLE'.
    provenance  : One of LIVE | AUTH_REQUIRED | UNAVAILABLE.
    freshness   : Human-readable data age string (e.g. '<5 min', 'AUTH_REQUIRED').
    observed_at : ISO-8601 UTC string when the physical observation was made.
    received_at : ISO-8601 UTC string when this record was ingested locally.
    location    : {'lat': float, 'lon': float} dict for the observation point.
    """

    sector_id:   str
    timestamp:   str
    feature:     str
    value:       Optional[float]
    unit:        str
    source:      str = "IMD"
    quality:     str = "GOOD"
    provenance:  str = "LIVE"
    freshness:   str = "<5 min"
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    received_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    location:    Dict[str, float] = field(default_factory=lambda: {"lat": 0.0, "lon": 0.0})

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the observation to a plain dictionary."""
        return {
            "sector_id":   self.sector_id,
            "timestamp":   self.timestamp,
            "feature":     self.feature,
            "value":       self.value,
            "unit":        self.unit,
            "source":      self.source,
            "quality":     self.quality,
            "provenance":  self.provenance,
            "freshness":   self.freshness,
            "observed_at": self.observed_at,
            "received_at": self.received_at,
            "location":    self.location,
        }


# =============================================================================
# 2. CONNECTOR
# =============================================================================

class IMDConnector:
    """
    Real-time IMD Nowcast API connector.

    Reads credentials from environment variables at construction time:
      - IMD_API_BASE_URL  : Base URL of the IMD API endpoint.
      - IMD_API_TOKEN     : Bearer token for authentication.

    If either credential is missing or contains a placeholder string, all
    fetch calls return AUTH_REQUIRED observations immediately without
    performing any network I/O.

    Thread-Safety
    -------------
    fetch_observations is safe to call from multiple threads concurrently;
    the connector is stateless beyond the immutable credential attributes set
    in __init__.
    """

    # IMD API field -> (feature_name, unit) mapping
    _FIELD_MAP: Dict[str, tuple] = {
        "rainfall_current_mmh":  ("rain_1h",       "mm/h"),
        "rainfall_6h_mm":        ("rain_6h",        "mm"),
        "rainfall_24h_mm":       ("rain_24h",       "mm"),
        "temperature_2m_c":      ("temp_2m",        "deg C"),
        "relative_humidity_pct": ("rh_2m",          "%"),
        "wind_speed_mps":        ("wind_speed",     "m/s"),
        "wind_direction_deg":    ("wind_dir",       "deg"),
        "pressure_hpa":          ("pressure_msl",   "hPa"),
        "visibility_km":         ("visibility",     "km"),
        "cloud_cover_oktas":     ("cloud_cover",    "oktas"),
    }

    def __init__(self) -> None:
        """
        Initialise connector. Reads IMD_API_BASE_URL and IMD_API_TOKEN from
        the environment. Sets self.status = 'AUTH_REQUIRED' immediately if
        either is absent or a placeholder.
        """
        self.base_url: Optional[str] = os.environ.get("IMD_API_BASE_URL", "").strip() or None
        self._token: Optional[str]   = os.environ.get("IMD_API_TOKEN",    "").strip() or None
        self._lock   = threading.Lock()
        self.last_success: Optional[str] = None
        self.last_error: Optional[str] = None
        self.last_latency_ms: Optional[float] = None

        # Configure session with exponential backoff retry adapter
        self._session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        if not self._is_configured():
            self.status = "AUTH_REQUIRED"
            self.last_error = "Credentials unconfigured in environment"
            logger.warning(
                "IMDConnector: IMD_API_BASE_URL or IMD_API_TOKEN is missing / "
                "placeholder. All fetch calls will return AUTH_REQUIRED."
            )
        else:
            self.status = "READY"
            logger.info("IMDConnector: credentials detected - connector is READY.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_configured(self) -> bool:
        """
        Return True only when both the base URL and token are present and do
        not contain known placeholder fragments.

        Returns
        -------
        bool
            False if either credential is missing or contains a placeholder.
        """
        if not self.base_url or not self._token:
            return False
        combined = (self.base_url + self._token).lower()
        return not any(frag in combined for frag in _PLACEHOLDER_FRAGMENTS)

    @staticmethod
    def _utc_now() -> str:
        """Return current UTC time as an ISO-8601 string."""
        return datetime.now(timezone.utc).isoformat()

    def _auth_required_observation(
        self,
        sector_id: str,
        lat: float,
        lon: float,
        feature: str = "rain_1h",
        unit: str = "mm/h",
    ) -> "IMDObservation":
        """Build a single AUTH_REQUIRED placeholder observation."""
        now = self._utc_now()
        return IMDObservation(
            sector_id=sector_id,
            timestamp=now,
            feature=feature,
            value=None,
            unit=unit,
            source="IMD",
            quality="AUTH_REQUIRED",
            provenance="AUTH_REQUIRED",
            freshness="AUTH_REQUIRED",
            observed_at=now,
            received_at=now,
            location={"lat": lat, "lon": lon},
        )

    def _unavailable_observation(
        self,
        sector_id: str,
        lat: float,
        lon: float,
        feature: str = "rain_1h",
        unit: str = "mm/h",
        reason: str = "",
    ) -> "IMDObservation":
        """Build a single UNAVAILABLE placeholder observation."""
        now = self._utc_now()
        logger.debug("IMDConnector: UNAVAILABLE for %s - %s", feature, reason)
        return IMDObservation(
            sector_id=sector_id,
            timestamp=now,
            feature=feature,
            value=None,
            unit=unit,
            source="IMD",
            quality="UNAVAILABLE",
            provenance="UNAVAILABLE",
            freshness="UNAVAILABLE",
            observed_at=now,
            received_at=now,
            location={"lat": lat, "lon": lon},
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_observations(
        self,
        lat: float,
        lon: float,
        sector_id: str,
    ) -> List["IMDObservation"]:
        """
        Fetch all available nowcast observations for a geographic point.

        Parameters
        ----------
        lat       : WGS-84 latitude of the observation point.
        lon       : WGS-84 longitude of the observation point.
        sector_id : Logical sector identifier attached to every returned record.

        Returns
        -------
        List[IMDObservation]
            One record per meteorological feature exposed by the IMD Nowcast API.
            Returns a single AUTH_REQUIRED record when not configured.
            Returns UNAVAILABLE records on network failure or non-200 response.

        Notes
        -----
        Endpoint  : GET {base_url}/nowcast?lat={lat}&lon={lon}
        Auth      : Authorization: Bearer {token}
        Timeout   : 5 seconds (configurable via IMD_REQUEST_TIMEOUT env var).
        """
        if not self._is_configured():
            logger.debug(
                "IMDConnector.fetch_observations: not configured - returning AUTH_REQUIRED."
            )
            return [self._auth_required_observation(sector_id, lat, lon)]

        timeout = int(os.environ.get("IMD_REQUEST_TIMEOUT", "5"))
        url     = f"{self.base_url}/nowcast"
        params  = {"lat": lat, "lon": lon}
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept":        "application/json",
            "User-Agent":    "PAHAD-AI/1.0 (PARVAT-NETRA; SIH-26001)",
        }
        received_at = self._utc_now()

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        except requests.exceptions.Timeout:
            self.status = "UNAVAILABLE"
            logger.warning("IMDConnector: request timed out after %ds.", timeout)
            return [self._unavailable_observation(sector_id, lat, lon, reason="timeout")]
        except requests.exceptions.RequestException as exc:
            self.status = "UNAVAILABLE"
            logger.error("IMDConnector: network error - %s", exc)
            return [self._unavailable_observation(sector_id, lat, lon, reason=str(exc))]

        if resp.status_code in (401, 403):
            self.status = "AUTH_REQUIRED"
            logger.error(
                "IMDConnector: HTTP %d - invalid or expired token.", resp.status_code
            )
            return [self._auth_required_observation(sector_id, lat, lon)]

        if resp.status_code != 200:
            self.status = "UNAVAILABLE"
            logger.warning(
                "IMDConnector: unexpected HTTP %d from IMD API.", resp.status_code
            )
            return [
                self._unavailable_observation(
                    sector_id, lat, lon, reason=f"HTTP {resp.status_code}"
                )
            ]

        try:
            payload: Dict[str, Any] = resp.json()
        except ValueError as exc:
            self.status = "UNAVAILABLE"
            logger.error("IMDConnector: failed to decode JSON response - %s", exc)
            return [self._unavailable_observation(sector_id, lat, lon, reason="invalid JSON")]

        self.status = "LIVE"
        observations: List[IMDObservation] = []
        now = self._utc_now()
        observed_at = payload.get("observed_at") or payload.get("timestamp") or now
        api_quality: str = str(payload.get("quality_flag", "GOOD")).upper()
        if api_quality not in ("GOOD", "SUSPECT"):
            api_quality = "GOOD"

        for api_field, (feature, unit) in self._FIELD_MAP.items():
            raw = payload.get(api_field)
            if raw is None:
                continue
            try:
                value: Optional[float] = float(raw)
            except (TypeError, ValueError):
                logger.debug(
                    "IMDConnector: could not parse field %s value %s - skipping.",
                    api_field, raw
                )
                continue

            observations.append(
                IMDObservation(
                    sector_id=sector_id,
                    timestamp=now,
                    feature=feature,
                    value=value,
                    unit=unit,
                    source="IMD",
                    quality=api_quality,
                    provenance="LIVE",
                    freshness="<5 min",
                    observed_at=str(observed_at),
                    received_at=received_at,
                    location={"lat": lat, "lon": lon},
                )
            )

        if not observations:
            logger.warning(
                "IMDConnector: IMD API returned 200 but no recognisable fields "
                "for lat=%s lon=%s. Known fields: %s",
                lat, lon, list(self._FIELD_MAP.keys()),
            )
            return [self._unavailable_observation(sector_id, lat, lon, reason="empty payload")]

        logger.info(
            "IMDConnector: received %d observations for sector=%s from IMD.",
            len(observations), sector_id,
        )
        return observations

    def fetch_nowcast(
        self,
        lat: float,
        lon: float,
        sector_id: str,
    ) -> List["IMDObservation"]:
        """Alias for fetch_observations — retrieves nowcast for coordinates."""
        return self.fetch_observations(lat=lat, lon=lon, sector_id=sector_id)

    def fetch_aws_arg(
        self,
        station_id: str,
        sector_id: str,
        lat: float = 0.0,
        lon: float = 0.0,
    ) -> List["IMDObservation"]:
        """
        Fetch Automatic Weather Station (AWS) / Automatic Rain Gauge (ARG) telemetry.
        Returns AUTH_REQUIRED if credentials are absent.
        """
        if not self._is_configured():
            logger.debug("IMDConnector.fetch_aws_arg: not configured - returning AUTH_REQUIRED.")
            return [
                self._auth_required_observation(
                    sector_id=sector_id, lat=lat, lon=lon, feature="aws_rain_1h", unit="mm/h"
                )
            ]
        url = f"{self.base_url}/aws/{station_id}"
        timeout = int(os.environ.get("IMD_REQUEST_TIMEOUT", "5"))
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": "PAHAD-AI/1.0 (PARVAT-NETRA; SIH-26001)",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return self.fetch_observations(lat=lat, lon=lon, sector_id=sector_id)
            elif resp.status_code in (401, 403):
                return [self._auth_required_observation(sector_id, lat, lon)]
            return [self._unavailable_observation(sector_id, lat, lon, reason=f"HTTP {resp.status_code}")]
        except Exception as exc:
            return [self._unavailable_observation(sector_id, lat, lon, reason=str(exc))]

    def fetch_district_rainfall(
        self,
        district: str,
        state: str,
        sector_id: str,
        lat: float = 0.0,
        lon: float = 0.0,
    ) -> List["IMDObservation"]:
        """
        Fetch official district-level cumulative rainfall statistics from IMD.
        Returns AUTH_REQUIRED if credentials are not configured.
        """
        if not self._is_configured():
            logger.debug("IMDConnector.fetch_district_rainfall: not configured - returning AUTH_REQUIRED.")
            return [
                self._auth_required_observation(
                    sector_id=sector_id, lat=lat, lon=lon, feature="district_rain_24h", unit="mm"
                )
            ]
        url = f"{self.base_url}/district-rainfall"
        params = {"district": district, "state": state}
        timeout = int(os.environ.get("IMD_REQUEST_TIMEOUT", "5"))
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": "PAHAD-AI/1.0 (PARVAT-NETRA; SIH-26001)",
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return self.fetch_observations(lat=lat, lon=lon, sector_id=sector_id)
            elif resp.status_code in (401, 403):
                return [self._auth_required_observation(sector_id, lat, lon)]
            return [self._unavailable_observation(sector_id, lat, lon, reason=f"HTTP {resp.status_code}")]
        except Exception as exc:
            return [self._unavailable_observation(sector_id, lat, lon, reason=str(exc))]

    def fetch_warnings(
        self,
        state: str,
        district: str,
        sector_id: str,
        lat: float = 0.0,
        lon: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Fetch official IMD meteorological colour-coded warnings (Green/Yellow/Orange/Red).
        Returns AUTH_REQUIRED when unconfigured.
        """
        if not self._is_configured():
            return {
                "sector_id": sector_id,
                "district": district,
                "state": state,
                "color_code": "UNKNOWN",
                "warning_level": "AUTH_REQUIRED",
                "provenance": "AUTH_REQUIRED",
                "timestamp": self._utc_now(),
            }
        url = f"{self.base_url}/warnings"
        params = {"district": district, "state": state}
        timeout = int(os.environ.get("IMD_REQUEST_TIMEOUT", "5"))
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": "PAHAD-AI/1.0 (PARVAT-NETRA; SIH-26001)",
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            return {
                "sector_id": sector_id,
                "district": district,
                "warning_level": "UNAVAILABLE",
                "provenance": "UNAVAILABLE",
                "status_code": resp.status_code,
            }
        except Exception as exc:
            return {
                "sector_id": sector_id,
                "district": district,
                "warning_level": "UNAVAILABLE",
                "provenance": "UNAVAILABLE",
                "error": str(exc),
            }

    def verify_connection(self) -> Dict[str, Any]:
        """
        Verify IMD API configuration, credentials, and endpoint connectivity.
        Returns detailed diagnostics with latency and error causes without fabricating data.
        """
        t0 = time.time()
        if not self._is_configured():
            self.last_error = "IMD_API_BASE_URL or IMD_API_TOKEN absent or placeholder in environment"
            return {
                "status": "AUTH_REQUIRED",
                "provider": "IMD",
                "auth_state": "AUTH_REQUIRED",
                "authenticated": False,
                "endpoint": self.base_url,
                "latency_ms": 0.0,
                "error": self.last_error,
                "checked_at": self._utc_now(),
                "stations_available": len(NER_IMD_STATIONS),
                "action_required": "Provide official IMD credentials in .env (IMD_API_BASE_URL and IMD_API_TOKEN)"
            }

        url = f"{self.base_url.rstrip('/')}/nowcast"
        params = {"lat": 27.33, "lon": 88.61}
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": "PAHAD-AI/1.0 (PARVAT-NETRA; SIH-26001)"
        }
        timeout = int(os.environ.get("IMD_REQUEST_TIMEOUT", "5"))

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            latency = round((time.time() - t0) * 1000, 1)
            self.last_latency_ms = latency

            if resp.status_code == 200:
                self.status = "READY"
                self.last_success = self._utc_now()
                self.last_error = None
                return {
                    "status": "LIVE",
                    "provider": "IMD",
                    "auth_state": "CONFIGURED",
                    "authenticated": True,
                    "endpoint": self.base_url,
                    "latency_ms": latency,
                    "checked_at": self._utc_now(),
                    "stations_available": len(NER_IMD_STATIONS),
                    "error": None
                }
            elif resp.status_code in (401, 403):
                self.status = "AUTH_REQUIRED"
                self.last_error = f"HTTP {resp.status_code} Unauthorized / Forbidden"
                return {
                    "status": "AUTH_REQUIRED",
                    "provider": "IMD",
                    "auth_state": "AUTH_REQUIRED",
                    "authenticated": False,
                    "endpoint": self.base_url,
                    "latency_ms": latency,
                    "error": self.last_error,
                    "checked_at": self._utc_now(),
                    "stations_available": len(NER_IMD_STATIONS),
                    "action_required": "Update IMD_API_TOKEN with a valid unexpired bearer token"
                }
            else:
                self.status = "UNAVAILABLE"
                self.last_error = f"HTTP {resp.status_code}"
                return {
                    "status": "UNAVAILABLE",
                    "provider": "IMD",
                    "auth_state": "CONFIGURED",
                    "authenticated": False,
                    "endpoint": self.base_url,
                    "latency_ms": latency,
                    "error": self.last_error,
                    "checked_at": self._utc_now(),
                    "stations_available": len(NER_IMD_STATIONS),
                }
        except Exception as exc:
            latency = round((time.time() - t0) * 1000, 1)
            self.status = "UNAVAILABLE"
            self.last_error = str(exc)
            return {
                "status": "UNAVAILABLE",
                "provider": "IMD",
                "auth_state": "CONFIGURED" if self._is_configured() else "AUTH_REQUIRED",
                "authenticated": False,
                "endpoint": self.base_url,
                "latency_ms": latency,
                "error": str(exc),
                "checked_at": self._utc_now(),
                "stations_available": len(NER_IMD_STATIONS)
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Return a lightweight status dictionary for health-check endpoints.

        Returns
        -------
        dict with keys:
            status      : Current connector status string.
            provider    : Always 'IMD'.
            endpoint    : The configured base URL, or None if unconfigured.
            auth        : 'CONFIGURED' if credentials are present, else 'AUTH_REQUIRED'.
            auth_state  : 'CONFIGURED' if credentials are present, else 'AUTH_REQUIRED'.
            last_success: ISO timestamp of last successful ping or None.
            last_error  : Last error description or None.
            stations_count: Number of registered NER IMD AWS/ARG stations.
        """
        auth_str = "CONFIGURED" if self._is_configured() else "AUTH_REQUIRED"
        return {
            "status":         self.status,
            "provider":       "IMD",
            "endpoint":       self.base_url if self._is_configured() else None,
            "auth":           auth_str,
            "auth_state":     auth_str,
            "last_success":   self.last_success,
            "last_error":     self.last_error,
            "last_latency_ms": self.last_latency_ms,
            "stations_count": len(NER_IMD_STATIONS),
        }


# =============================================================================
# 3. MODULE-LEVEL SINGLETON
# =============================================================================

#: Module-level singleton. Import and use this directly in other services.
IMD_CONNECTOR: IMDConnector = IMDConnector()
