"""
sector_snapshot.py
==================
PARVAT NETRA / PAHAD AI  —  Deterministic Sector Snapshot Engine
-----------------------------------------------------------------
Produces a complete, timestamped snapshot dict for a given sector_id
covering all 26 Phase-5B model features plus:

  * feature_completeness   (0.0-1.0)
  * per-feature provenance (LIVE / CACHED / MISSING / MODELLED /
                            SIMULATED / AUTH_REQUIRED / UNAVAILABLE)
  * per-modality freshness (FRESH / AGING / STALE / UNAVAILABLE)
  * overall freshness      (worst-case across modalities)
  * data_quality_score     (0.0-1.0, penalised for staleness / gaps)
  * provenance_summary     (human-readable tally string)

All provenance values conform to the PAHAD canonical set:
  LIVE | CACHED | MISSING | MODELLED | SIMULATED | AUTH_REQUIRED | UNAVAILABLE

No synthetic / fabricated readings are ever returned from operational
code paths.  The module is safe to import even when upstream services
are unavailable -- every external dependency is wrapped in a try/except
fallback.

Author : PAHAD AI Platform Team
Created: 2026-09-10
"""

from __future__ import annotations

import os
import time
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency: data_freshness
# ---------------------------------------------------------------------------
try:
    from engine.data_freshness import (
        FRESHNESS_ENGINE,
        FRESH,
        AGING,
        STALE,
        UNAVAILABLE,
    )
    _FRESHNESS_AVAILABLE = True
    logger.debug("sector_snapshot: data_freshness imported successfully.")
except Exception as _e:  # noqa: BLE001
    logger.warning(
        "sector_snapshot: engine.data_freshness unavailable (%s). "
        "Freshness checks will report UNAVAILABLE.",
        _e,
    )
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    FRESHNESS_ENGINE = None
    _FRESHNESS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Optional dependency: observation_store
# ---------------------------------------------------------------------------
try:
    from engine.observation_store import GLOBAL_OBSERVATION_STORE
    _STORE_AVAILABLE = True
    logger.debug("sector_snapshot: observation_store imported successfully.")
except Exception as _e:  # noqa: BLE001
    logger.warning(
        "sector_snapshot: engine.observation_store unavailable (%s). "
        "Snapshot features will all be MISSING.",
        _e,
    )
    GLOBAL_OBSERVATION_STORE = None
    _STORE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Sector Registry
# ---------------------------------------------------------------------------
SECTOR_REGISTRY: Dict[str, Dict[str, Any]] = {
    'SK-NH10-KM48': {
        'lat': 27.3300,
        'lon': 88.6100,
        'state': 'Sikkim',
        'district': 'Pakyong',
    },
    'MN-TUPUL-RLY': {
        'lat': 24.7550,
        'lon': 93.5780,
        'state': 'Manipur',
        'district': 'Noney',
    },
    'MZ-MELTHUM-QRY': {
        'lat': 23.8950,
        'lon': 92.9600,
        'state': 'Mizoram',
        'district': 'Aizawl',
    },
    'AS-HAFLONG-RLY': {
        'lat': 25.1650,
        'lon': 93.0270,
        'state': 'Assam',
        'district': 'Dima Hasao',
    },
    'ML-MAWSYNRAM': {
        'lat': 25.2970,
        'lon': 91.5830,
        'state': 'Meghalaya',
        'district': 'East Khasi Hills',
    },
    'NL-DZUKOU-KOH': {
        'lat': 25.5820,
        'lon': 94.1200,
        'state': 'Nagaland',
        'district': 'Kohima',
    },
    'AR-TAWANG-SELA': {
        'lat': 27.5800,
        'lon': 91.8500,
        'state': 'Arunachal Pradesh',
        'district': 'Tawang',
    },
    'TR-JAMPUI-HILLS': {
        'lat': 23.9500,
        'lon': 92.3100,
        'state': 'Tripura',
        'district': 'North Tripura',
    },
}

# ---------------------------------------------------------------------------
# Phase-5B Feature Columns (26 features)
# ---------------------------------------------------------------------------
PHASE5B_FEATURE_COLUMNS: List[str] = [
    # Rainfall accumulations
    'rain_1h',
    'rain_3h',
    'rain_6h',
    'rain_12h',
    'rain_24h',
    'rain_48h',
    'rain_72h',
    # Antecedent rainfall
    'antecedent_rain_3d',
    'antecedent_rain_7d',
    # Rainfall intensity / threshold
    'rain_intensity',
    'rainfall_threshold_exceedance',
    # Terrain / slope stability
    'fos',
    'slope',
    'aspect',
    'elevation',
    'curvature',
    # Subsurface / geotechnical
    'soil_moisture',
    'pore_pressure',
    # In-situ sensor
    'tilt',
    'ground_displacement',
    # Vegetation / remote sensing
    'ndvi',
    'ndvi_anomaly',
    # Seismicity
    'seismic_count_24h',
    'max_magnitude_24h',
    'nearest_seismic_distance',
    # Historical susceptibility
    'historical_susceptibility',
]

# ---------------------------------------------------------------------------
# Freshness ordering (worst = lowest rank)
# ---------------------------------------------------------------------------
_FRESHNESS_RANK: Dict[str, int] = {
    FRESH: 3,
    AGING: 2,
    STALE: 1,
    UNAVAILABLE: 0,
}

_FRESHNESS_PENALTY: Dict[str, float] = {
    FRESH: 0.00,
    AGING: 0.10,
    STALE: 0.25,
    UNAVAILABLE: 0.50,
}

# Valid provenance tokens recognised by the platform
_VALID_PROVENANCE = frozenset(
    {"LIVE", "CACHED", "MISSING", "MODELLED", "SIMULATED", "AUTH_REQUIRED", "UNAVAILABLE"}
)


# ---------------------------------------------------------------------------
# SectorSnapshot dataclass
# ---------------------------------------------------------------------------
@dataclass
class SectorSnapshot:
    """
    Immutable snapshot of all Phase-5B features for a single sector at a
    single point in time.

    Attributes
    ----------
    sector_id : str
        Canonical sector identifier (e.g. 'SK-NH10-KM48').
    latitude : float
        Decimal-degree latitude of the sector centroid.
    longitude : float
        Decimal-degree longitude of the sector centroid.
    state : str
        Indian state name.
    district : str
        District name.
    snapshot_time : str
        ISO-8601 UTC timestamp at which the snapshot was assembled.
    features : Dict[str, Any]
        Mapping of feature name to observed value (or None when absent).
    feature_provenance : Dict[str, str]
        Mapping of feature name to provenance token.
    feature_completeness : float
        Fraction of the 26 features that carry a non-None value (0.0-1.0).
    missing_features : List[str]
        Names of features whose value is None.
    freshness_by_modality : Dict[str, str]
        Modality label to freshness token (FRESH/AGING/STALE/UNAVAILABLE).
    overall_freshness : str
        Worst-case freshness token across all modalities.
    data_quality_score : float
        Composite quality metric in [0, 1]:
        ``feature_completeness * (1 - freshness_penalty)``.
    provenance_summary : str
        Human-readable tally, e.g. 'LIVE:3 CACHED:5 MISSING:18'.
    """

    sector_id: str
    latitude: float
    longitude: float
    state: str
    district: str
    snapshot_time: str
    features: Dict[str, Any] = field(default_factory=dict)
    feature_provenance: Dict[str, str] = field(default_factory=dict)
    feature_completeness: float = 0.0
    missing_features: List[str] = field(default_factory=list)
    freshness_by_modality: Dict[str, str] = field(default_factory=dict)
    overall_freshness: str = "UNAVAILABLE"
    data_quality_score: float = 0.0
    provenance_summary: str = ""

    def to_dict(self) -> dict:
        """Return a fully serialisable plain-dict representation."""
        return {
            "sector_id": self.sector_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "state": self.state,
            "district": self.district,
            "snapshot_time": self.snapshot_time,
            "features": self.features,
            "feature_provenance": self.feature_provenance,
            "feature_completeness": self.feature_completeness,
            "missing_features": self.missing_features,
            "freshness_by_modality": self.freshness_by_modality,
            "overall_freshness": self.overall_freshness,
            "data_quality_score": self.data_quality_score,
            "provenance_summary": self.provenance_summary,
        }


# ---------------------------------------------------------------------------
# SectorSnapshotBuilder
# ---------------------------------------------------------------------------
class SectorSnapshotBuilder:
    """
    Assembles :class:`SectorSnapshot` objects by pulling the latest
    observations from ``GLOBAL_OBSERVATION_STORE`` and freshness metadata
    from ``FRESHNESS_ENGINE``.

    The builder never fabricates feature values.  When a feature has no
    observation within the requested time window its value is ``None`` and
    its provenance is ``'MISSING'``.
    """

    def __init__(
        self,
        store: Optional[Any] = None,
        freshness_engine: Optional[Any] = None,
    ) -> None:
        self._custom_store = store
        self._custom_freshness = freshness_engine

    @property
    def _store(self) -> Any:
        if self._custom_store is not None:
            return self._custom_store
        return GLOBAL_OBSERVATION_STORE

    @property
    def _freshness_engine(self) -> Any:
        if self._custom_freshness is not None:
            return self._custom_freshness
        return FRESHNESS_ENGINE

    def build(
        self,
        sector_id: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        max_age_seconds: float = 3600.0,
    ) -> SectorSnapshot:
        """
        Build a snapshot for *sector_id*.

        Parameters
        ----------
        sector_id : str
            Sector identifier.  Must be present in ``SECTOR_REGISTRY`` or
            *lat* / *lon* must be supplied explicitly.
        lat : float, optional
            Override latitude (decimal degrees).
        lon : float, optional
            Override longitude (decimal degrees).
        max_age_seconds : float
            Maximum age (seconds) of observations accepted as current.
            Defaults to 3600 s (1 hour).

        Returns
        -------
        SectorSnapshot
        """
        snapshot_time = datetime.now(timezone.utc).isoformat()

        # ----------------------------------------------------------------
        # 1. Resolve coordinates & metadata
        # ----------------------------------------------------------------
        registry_meta = SECTOR_REGISTRY.get(sector_id, {})

        resolved_lat: float = lat if lat is not None else registry_meta.get("lat", float("nan"))
        resolved_lon: float = lon if lon is not None else registry_meta.get("lon", float("nan"))
        state: str = registry_meta.get("state", "UNKNOWN")
        district: str = registry_meta.get("district", "UNKNOWN")

        if sector_id not in SECTOR_REGISTRY and (lat is None or lon is None):
            logger.warning(
                "sector_snapshot.build: sector_id '%s' not in SECTOR_REGISTRY "
                "and no lat/lon provided. Coordinates will be NaN.",
                sector_id,
            )

        # ----------------------------------------------------------------
        # 2. Fetch latest observations from the store
        # ----------------------------------------------------------------
        obs_by_feature: Dict[str, Any] = {}

        if self._store is not None:
            try:
                raw = self._store.get_latest_by_sector(
                    sector_id,
                    max_age_seconds=max_age_seconds,
                )
                # raw is expected to be a dict[feature_name, ObservationRecord]
                # or a list[ObservationRecord]; handle both gracefully.
                if isinstance(raw, dict):
                    obs_by_feature = raw
                elif isinstance(raw, (list, tuple)):
                    for rec in raw:
                        feat = getattr(rec, "feature", None)
                        if feat:
                            obs_by_feature[feat] = rec
                else:
                    logger.warning(
                        "sector_snapshot.build: unexpected return type from "
                        "get_latest_by_sector: %s",
                        type(raw),
                    )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "sector_snapshot.build: observation_store query failed for "
                    "sector '%s': %s",
                    sector_id,
                    exc,
                )
        else:
            logger.debug(
                "sector_snapshot.build: observation_store unavailable; "
                "all features will be MISSING for sector '%s'.",
                sector_id,
            )

        # ----------------------------------------------------------------
        # 3. Build features dict + provenance per feature
        # ----------------------------------------------------------------
        features: Dict[str, Any] = {}
        feature_provenance: Dict[str, str] = {}
        missing_features: List[str] = []

        for feat in PHASE5B_FEATURE_COLUMNS:
            rec = obs_by_feature.get(feat)
            if rec is not None:
                val = getattr(rec, "value", None)
                prov = getattr(rec, "provenance", "UNAVAILABLE")
                # Normalise provenance to canonical set
                if prov not in _VALID_PROVENANCE:
                    logger.debug(
                        "sector_snapshot: non-canonical provenance '%s' for "
                        "feature '%s' in sector '%s'; coercing to UNAVAILABLE.",
                        prov,
                        feat,
                        sector_id,
                    )
                    prov = "UNAVAILABLE"
                features[feat] = val
                feature_provenance[feat] = prov
                if val is None:
                    missing_features.append(feat)
            else:
                features[feat] = None
                feature_provenance[feat] = "MISSING"
                missing_features.append(feat)

        # ----------------------------------------------------------------
        # 4. Feature completeness
        # ----------------------------------------------------------------
        total = len(PHASE5B_FEATURE_COLUMNS)
        present = sum(1 for f in PHASE5B_FEATURE_COLUMNS if features.get(f) is not None)
        feature_completeness = round(present / total, 4) if total > 0 else 0.0

        # ----------------------------------------------------------------
        # 5. Freshness by modality
        # ----------------------------------------------------------------
        freshness_by_modality: Dict[str, str] = {}

        if self._freshness_engine is not None:
            try:
                summary = self._freshness_engine.get_summary()
                if isinstance(summary, dict):
                    for modality, token in summary.items():
                        if token not in _FRESHNESS_RANK:
                            token = UNAVAILABLE
                        freshness_by_modality[modality] = token
                else:
                    logger.warning(
                        "sector_snapshot: FRESHNESS_ENGINE.get_summary() returned "
                        "unexpected type: %s",
                        type(summary),
                    )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "sector_snapshot: freshness engine query failed: %s", exc
                )

        if not freshness_by_modality:
            freshness_by_modality = self._derive_modality_freshness(
                obs_by_feature, max_age_seconds
            )

        # ----------------------------------------------------------------
        # 6. Overall freshness  (worst-case across modalities)
        # ----------------------------------------------------------------
        if freshness_by_modality:
            overall_freshness = min(
                freshness_by_modality.values(),
                key=lambda t: _FRESHNESS_RANK.get(t, 0),
            )
        else:
            overall_freshness = UNAVAILABLE

        # ----------------------------------------------------------------
        # 7. Data quality score
        # ----------------------------------------------------------------
        penalty = _FRESHNESS_PENALTY.get(overall_freshness, 0.50)
        data_quality_score = round(feature_completeness * (1.0 - penalty), 4)

        # ----------------------------------------------------------------
        # 8. Provenance summary string
        # ----------------------------------------------------------------
        prov_counts: Dict[str, int] = {}
        for prov in feature_provenance.values():
            prov_counts[prov] = prov_counts.get(prov, 0) + 1

        provenance_summary = " ".join(
            f"{prov}:{count}"
            for prov, count in sorted(prov_counts.items())
        )

        # ----------------------------------------------------------------
        # 9. Assemble and return
        # ----------------------------------------------------------------
        logger.info(
            "sector_snapshot.build: sector='%s' completeness=%.2f "
            "quality=%.2f freshness='%s' provenance='%s'",
            sector_id,
            feature_completeness,
            data_quality_score,
            overall_freshness,
            provenance_summary,
        )

        return SectorSnapshot(
            sector_id=sector_id,
            latitude=resolved_lat,
            longitude=resolved_lon,
            state=state,
            district=district,
            snapshot_time=snapshot_time,
            features=features,
            feature_provenance=feature_provenance,
            feature_completeness=feature_completeness,
            missing_features=missing_features,
            freshness_by_modality=freshness_by_modality,
            overall_freshness=overall_freshness,
            data_quality_score=data_quality_score,
            provenance_summary=provenance_summary,
        )

    def build_all(
        self,
        max_age_seconds: float = 3600.0,
    ) -> Dict[str, SectorSnapshot]:
        """
        Build snapshots for every sector in :data:`SECTOR_REGISTRY`.

        Parameters
        ----------
        max_age_seconds : float
            Forwarded to :meth:`build` for each sector.

        Returns
        -------
        dict[sector_id, SectorSnapshot]
        """
        results: Dict[str, SectorSnapshot] = {}
        for sector_id in SECTOR_REGISTRY:
            try:
                results[sector_id] = self.build(
                    sector_id, max_age_seconds=max_age_seconds
                )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "sector_snapshot.build_all: failed for sector '%s': %s",
                    sector_id,
                    exc,
                )
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _derive_modality_freshness(
        obs_by_feature: Dict[str, Any],
        max_age_seconds: float,
    ) -> Dict[str, str]:
        """
        Derive coarse per-modality freshness from ObservationRecord timestamps
        when FRESHNESS_ENGINE is unavailable.

        Modality groupings mirror the Phase-5B feature columns.
        """
        _MODALITY_FEATURES: Dict[str, List[str]] = {
            "rainfall": [
                "rain_1h", "rain_3h", "rain_6h", "rain_12h",
                "rain_24h", "rain_48h", "rain_72h",
                "antecedent_rain_3d", "antecedent_rain_7d",
                "rain_intensity", "rainfall_threshold_exceedance",
            ],
            "terrain": ["fos", "slope", "aspect", "elevation", "curvature"],
            "geotechnical": [
                "soil_moisture", "pore_pressure",
                "tilt", "ground_displacement",
            ],
            "remote_sensing": ["ndvi", "ndvi_anomaly"],
            "seismicity": [
                "seismic_count_24h", "max_magnitude_24h",
                "nearest_seismic_distance",
            ],
            "susceptibility": ["historical_susceptibility"],
        }

        now_ts = time.time()
        freshness_by_modality: Dict[str, str] = {}

        for modality, feats in _MODALITY_FEATURES.items():
            tokens: List[str] = []
            for feat in feats:
                rec = obs_by_feature.get(feat)
                if rec is None:
                    tokens.append(UNAVAILABLE)
                    continue

                rec_ts: Optional[float] = None
                for attr in ("ingested_at", "timestamp"):
                    val = getattr(rec, attr, None)
                    if val is None:
                        continue
                    if isinstance(val, (int, float)):
                        rec_ts = float(val)
                    elif isinstance(val, str):
                        try:
                            rec_ts = datetime.fromisoformat(val).timestamp()
                        except ValueError:
                            pass
                    elif isinstance(val, datetime):
                        rec_ts = val.timestamp()
                    if rec_ts is not None:
                        break

                if rec_ts is None:
                    tokens.append(UNAVAILABLE)
                    continue

                age = now_ts - rec_ts
                if age < 0:
                    tokens.append(FRESH)
                elif age <= max_age_seconds * 0.5:
                    tokens.append(FRESH)
                elif age <= max_age_seconds:
                    tokens.append(AGING)
                else:
                    tokens.append(STALE)

            if tokens:
                modality_freshness = min(
                    tokens, key=lambda t: _FRESHNESS_RANK.get(t, 0)
                )
            else:
                modality_freshness = UNAVAILABLE

            freshness_by_modality[modality] = modality_freshness

        return freshness_by_modality


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
SECTOR_SNAPSHOT_BUILDER = SectorSnapshotBuilder()
