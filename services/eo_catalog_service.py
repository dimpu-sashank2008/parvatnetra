# -*- coding: utf-8 -*-
"""
services/eo_catalog_service.py
==============================
PARVAT NETRA • Earth Observation Catalogue Service (Phase 5C)
--------------------------------------------------------------
Tracks Sentinel-1 SAR, Sentinel-2 Optical, NISAR, CartoDEM and
NDVI/SAR product availability from NRSC Bhoonidhi catalogue.

Each acquisition moves through these states:
  DISCOVERED  : Tile known from catalogue metadata
  AVAILABLE   : Product confirmed downloadable
  DOWNLOADED  : Product file on local disk
  PROCESSED   : InSAR/NDVI processing completed
  FEATURE_READY: Feature extracted and stored in ObservationStore
  MISSING     : Acquisition expected but not found

Provenance States:
  - AUTH_REQUIRED : Copernicus/Bhoonidhi credentials not configured
  - UNAVAILABLE   : Catalogue endpoint unreachable
  - [CACHED]      : Metadata served from local catalogue cache
  - [LIVE]        : Authenticated catalogue query

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import requests

logger = logging.getLogger("PAHAD_EO_CATALOG")

# Acquisition states
STATE_DISCOVERED    = "DISCOVERED"
STATE_AVAILABLE     = "AVAILABLE"
STATE_DOWNLOADED    = "DOWNLOADED"
STATE_PROCESSED     = "PROCESSED"
STATE_FEATURE_READY = "FEATURE_READY"
STATE_MISSING       = "MISSING"

# Supported sensor types
SENSOR_SAR_S1    = "SENTINEL1_IW_SLC"
SENSOR_OPT_S2    = "SENTINEL2_MSI_L2A"
SENSOR_NISAR     = "NISAR_SBAND"
SENSOR_CARTDEM   = "ISRO_CARTODEM_V3R1"
SENSOR_MODIS     = "MODIS_MOD13Q1"


@dataclass
class EOAcquisitionRecord:
    """Represents a single satellite acquisition tracked through the EO pipeline."""
    acquisition_id: str
    sensor_type: str                     # SENSOR_* constant
    platform: str                        # e.g. 'Sentinel-1A'
    acquisition_time: str                # ISO 8601
    orbit_track: Optional[int]
    direction: Optional[str]             # 'Ascending' / 'Descending'
    cloud_cover_pct: Optional[float]
    processing_level: str                # 'L1C', 'L2A', 'SLC', 'GRD'
    state: str                           # One of STATE_* constants
    product_url: Optional[str]
    local_path: Optional[str]
    footprint_bbox: Optional[Dict[str, float]]  # {'min_lat', 'max_lat', 'min_lon', 'max_lon'}
    sector_ids_covered: List[str]        # Which NER sectors this acquisition covers
    source: str                          # 'Copernicus Open Access Hub' / 'NRSC Bhoonidhi' / etc.
    provenance: str                      # AUTH_REQUIRED / [LIVE] / [CACHED]
    discovered_at: str                   # ISO when we first saw this record
    feature_extracted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EOCatalogConnector:
    """
    Queries the Copernicus Data Space Ecosystem (CDSE) catalogue for Sentinel acquisitions
    over the NER bounding box. Falls back gracefully to UNAVAILABLE when credentials absent.

    Copernicus CDSE OData API is partially public (search), but downloading requires
    Copernicus account. We separate catalogue query from download.

    NRSC Bhoonidhi requires institutional MOU — always AUTH_REQUIRED until configured.
    """

    # NER bounding box
    NER_BBOX = (20.0, 30.0, 87.0, 98.0)  # (min_lat, max_lat, min_lon, max_lon)

    # Copernicus CDSE OData catalogue endpoint (partially public for search)
    CDSE_ODATA_BASE = "https://catalogue.dataspace.copernicus.eu/odata/v1"

    # NRSC Bhoonidhi (requires registration)
    BHOONIDHI_BASE = os.getenv("BHOONIDHI_API_URL", "")
    BHOONIDHI_TOKEN = os.getenv("BHOONIDHI_API_TOKEN", "")

    # Copernicus account (required for download, not catalogue search)
    COPERNICUS_CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID", "")
    COPERNICUS_CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET", "")

    def __init__(self) -> None:
        self._catalogue_cache: List[EOAcquisitionRecord] = []
        self._cache_time: float = 0.0
        self._cache_ttl: float = float(os.getenv("EO_CATALOG_CACHE_TTL", "3600"))  # 1 hour
        self._status = self._determine_status()
        logger.info(f"[EO-CATALOG] Initialized. Status: {self._status}")

    def _determine_status(self) -> str:
        """Determine initial auth / readiness status."""
        if self.COPERNICUS_CLIENT_ID and self.COPERNICUS_CLIENT_SECRET:
            if ("replace_with" not in self.COPERNICUS_CLIENT_ID.lower()
                    and "example" not in self.COPERNICUS_CLIENT_ID.lower()):
                return "COPERNICUS_CONFIGURED"
        return "AUTH_REQUIRED"

    def _is_copernicus_configured(self) -> bool:
        return self._status == "COPERNICUS_CONFIGURED"

    def _is_bhoonidhi_configured(self) -> bool:
        return bool(self.BHOONIDHI_BASE and self.BHOONIDHI_TOKEN
                    and "replace_with" not in self.BHOONIDHI_TOKEN.lower())

    def query_sentinel1_catalogue(
        self,
        days_back: int = 12,
        max_results: int = 20
    ) -> List[EOAcquisitionRecord]:
        """
        Query CDSE OData catalogue for Sentinel-1 IW SLC acquisitions over NER.
        The CDSE catalogue search is publicly accessible (no auth required for metadata).
        Download requires Copernicus account.
        """
        try:
            from datetime import timedelta
            cutoff = (datetime.now(timezone.utc).replace(tzinfo=None)
                      - __import__('datetime').timedelta(days=days_back))
            cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Construct OData filter for NER bbox and Sentinel-1
            bbox_wkt = (f"POLYGON(({self.NER_BBOX[2]} {self.NER_BBOX[0]},"
                        f"{self.NER_BBOX[3]} {self.NER_BBOX[0]},"
                        f"{self.NER_BBOX[3]} {self.NER_BBOX[1]},"
                        f"{self.NER_BBOX[2]} {self.NER_BBOX[1]},"
                        f"{self.NER_BBOX[2]} {self.NER_BBOX[0]}))")

            params = {
                "$filter": (
                    f"Collection/Name eq 'SENTINEL-1'"
                    f" and ContentDate/Start gt {cutoff_str!r}"
                    f" and OData.CSC.Intersects(area=geography'SRID=4326;{bbox_wkt}')"
                ),
                "$orderby": "ContentDate/Start desc",
                "$top": max_results,
                "$count": "true"
            }

            resp = requests.get(
                f"{self.CDSE_ODATA_BASE}/Products",
                params=params,
                timeout=8.0
            )

            if resp.status_code == 200:
                data = resp.json()
                records = []
                for item in data.get("value", []):
                    rec = EOAcquisitionRecord(
                        acquisition_id=item.get("Id", ""),
                        sensor_type=SENSOR_SAR_S1,
                        platform=item.get("Name", "Sentinel-1").split("_")[0],
                        acquisition_time=item.get("ContentDate", {}).get("Start", ""),
                        orbit_track=item.get("Attributes", [{}])[0].get("Value") if item.get("Attributes") else None,
                        direction=None,
                        cloud_cover_pct=None,
                        processing_level=item.get("Name", "").split("_")[3] if "_" in item.get("Name", "") else "SLC",
                        state=STATE_AVAILABLE if self._is_copernicus_configured() else STATE_DISCOVERED,
                        product_url=item.get("S3Path", None),
                        local_path=None,
                        footprint_bbox={
                            "min_lat": self.NER_BBOX[0],
                            "max_lat": self.NER_BBOX[1],
                            "min_lon": self.NER_BBOX[2],
                            "max_lon": self.NER_BBOX[3]
                        },
                        sector_ids_covered=[],
                        source="Copernicus Data Space Ecosystem (CDSE)",
                        provenance="[LIVE]",
                        discovered_at=datetime.now(timezone.utc).isoformat()
                    )
                    records.append(rec)
                self._catalogue_cache = records
                self._cache_time = time.time()
                logger.info(f"[EO-CATALOG] Fetched {len(records)} Sentinel-1 records from CDSE")
                return records
            else:
                logger.warning(f"[EO-CATALOG] CDSE returned HTTP {resp.status_code}")
                return self._return_unavailable("CDSE_HTTP_ERROR")

        except requests.exceptions.ConnectionError:
            logger.warning("[EO-CATALOG] CDSE catalogue unreachable (network error)")
            return self._return_unavailable("CDSE_UNREACHABLE")
        except Exception as exc:
            logger.error(f"[EO-CATALOG] Unexpected error querying CDSE: {exc}")
            return self._return_unavailable(str(exc))

    def _return_unavailable(self, reason: str) -> List[EOAcquisitionRecord]:
        """Return a single record indicating the catalogue is unavailable."""
        return [EOAcquisitionRecord(
            acquisition_id="CATALOGUE_UNAVAILABLE",
            sensor_type=SENSOR_SAR_S1,
            platform="unknown",
            acquisition_time=datetime.now(timezone.utc).isoformat(),
            orbit_track=None,
            direction=None,
            cloud_cover_pct=None,
            processing_level="unknown",
            state=STATE_MISSING,
            product_url=None,
            local_path=None,
            footprint_bbox=None,
            sector_ids_covered=[],
            source="Copernicus Data Space Ecosystem (CDSE)",
            provenance="UNAVAILABLE",
            discovered_at=datetime.now(timezone.utc).isoformat(),
            feature_extracted=False
        )]

    def get_bhoonidhi_status(self) -> Dict[str, Any]:
        """Report NRSC Bhoonidhi connectivity (AUTH_REQUIRED until MOU configured)."""
        return {
            "provider": "NRSC Bhoonidhi",
            "status": "CONFIGURED" if self._is_bhoonidhi_configured() else "AUTH_REQUIRED",
            "note": (
                "NRSC Bhoonidhi requires institutional MOU registration at bhoonidhi.nrsc.gov.in. "
                "No credentials in .env. Set BHOONIDHI_API_URL and BHOONIDHI_API_TOKEN."
                if not self._is_bhoonidhi_configured()
                else "Configured."
            )
        }

    def get_catalogue_status(self) -> Dict[str, Any]:
        """Return overall EO catalogue health."""
        cache_age = time.time() - self._cache_time if self._cache_time > 0 else None
        return {
            "copernicus_cdse": {
                "status": "CATALOGUE_ACCESSIBLE",  # Search is public
                "download_auth": "CONFIGURED" if self._is_copernicus_configured() else "AUTH_REQUIRED",
                "note": (
                    "Catalogue search is publicly accessible. "
                    "Download requires Copernicus account credentials (COPERNICUS_CLIENT_ID / COPERNICUS_CLIENT_SECRET)."
                )
            },
            "nrsc_bhoonidhi": self.get_bhoonidhi_status(),
            "cache": {
                "record_count": len(self._catalogue_cache),
                "cache_age_seconds": round(cache_age, 1) if cache_age is not None else None,
                "stale": (cache_age or 0) > self._cache_ttl
            }
        }

    def get_acquisition_summary(self) -> Dict[str, Any]:
        """Returns count of acquisitions by state."""
        from collections import Counter
        state_counts = Counter(r.state for r in self._catalogue_cache)
        return {
            "total": len(self._catalogue_cache),
            "by_state": dict(state_counts),
            "feature_ready_count": sum(1 for r in self._catalogue_cache if r.feature_extracted)
        }


# Global singleton
EO_CATALOG_SERVICE = EOCatalogConnector()
