# -*- coding: utf-8 -*-
"""
engine/data_freshness.py
=========================
PAHAD AI — Configurable Data Freshness TTL Engine (Phase 5C)
------------------------------------------------------------
Tracks data age for each modality and returns freshness status:
  FRESH      : age < 75% of TTL
  AGING      : 75% <= age < 100% of TTL
  STALE      : age >= TTL
  UNAVAILABLE: no record exists or age >= 3x TTL

Confidence penalties scale with staleness and are used to
discount event probability when input data is degraded.

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger("PAHAD_DATA_FRESHNESS")

# ─── Freshness status constants ────────────────────────────────────────────────
FRESH       = "FRESH"
AGING       = "AGING"
STALE       = "STALE"
UNAVAILABLE = "UNAVAILABLE"

# ─── Configurable TTLs per modality ───────────────────────────────────────────
DEFAULT_TTL_SECONDS: Dict[str, int] = {
    "imd":        int(os.getenv("IMD_FRESHNESS_S",        "900")),    # 15 min
    "ncs":        int(os.getenv("NCS_FRESHNESS_S",        "300")),    # 5 min
    "usgs":       int(os.getenv("USGS_FRESHNESS_S",       "300")),    # 5 min
    "iot":        int(os.getenv("IOT_FRESHNESS_S",        "120")),    # 2 min
    "weather":    int(os.getenv("WEATHER_FRESHNESS_S",    "900")),    # 15 min
    "seismic":    int(os.getenv("SEISMIC_FRESHNESS_S",    "300")),    # 5 min
    "satellite":  int(os.getenv("SATELLITE_FRESHNESS_S",  "86400")), # 1 day
    "vegetation": int(os.getenv("VEGETATION_FRESHNESS_S", "604800")), # 7 days
    "terrain":    int(os.getenv("TERRAIN_FRESHNESS_S",    "2592000")), # 30 days
    "historical": int(os.getenv("HISTORICAL_FRESHNESS_S", "31536000")), # 1 year
}

# Fraction of TTL at which data transitions from FRESH to AGING
AGING_RATIO = 0.75

# Fraction of TTL at which data transitions from STALE to UNAVAILABLE
UNAVAILABLE_RATIO = 3.0


@dataclass
class FreshnessRecord:
    """Freshness status for a single modality."""
    modality: str
    last_updated_epoch: Optional[float]   # Unix timestamp of last update
    ttl_seconds: int
    status: str                           # FRESH / AGING / STALE / UNAVAILABLE
    age_seconds: Optional[float]          # None if no record
    confidence_penalty: float             # 0.0 = no penalty, 1.0 = full penalty

    def to_dict(self) -> dict:
        return {
            "modality": self.modality,
            "last_updated_epoch": self.last_updated_epoch,
            "ttl_seconds": self.ttl_seconds,
            "status": self.status,
            "age_seconds": round(self.age_seconds, 1) if self.age_seconds is not None else None,
            "confidence_penalty": round(self.confidence_penalty, 4),
        }


class DataFreshnessEngine:
    """
    Tracks last-update timestamps per modality and computes freshness status.

    Usage:
        engine = DataFreshnessEngine()
        engine.record_update('imd')          # called after successful ingestion
        fr = engine.get_freshness('imd')     # → FreshnessRecord(status='FRESH', ...)
    """

    def __init__(self) -> None:
        self._last_updated: Dict[str, float] = {}

    def record_update(self, modality: str) -> None:
        """Record that modality was successfully updated right now."""
        self._last_updated[modality] = time.time()
        logger.debug(f"[FRESHNESS] Recorded update for modality: {modality}")

    def get_freshness(
        self,
        modality: str,
        last_updated_epoch: Optional[float] = None
    ) -> FreshnessRecord:
        """
        Compute freshness for a modality.

        Args:
            modality: Modality name (imd, ncs, iot, satellite, etc.)
            last_updated_epoch: Override timestamp. If None, uses internal record.

        Returns:
            FreshnessRecord with status and confidence_penalty.
        """
        ttl = DEFAULT_TTL_SECONDS.get(modality, 900)
        epoch = last_updated_epoch or self._last_updated.get(modality)

        if epoch is None:
            return FreshnessRecord(
                modality=modality,
                last_updated_epoch=None,
                ttl_seconds=ttl,
                status=UNAVAILABLE,
                age_seconds=None,
                confidence_penalty=1.0
            )

        age = time.time() - epoch
        aging_threshold = ttl * AGING_RATIO
        unavailable_threshold = ttl * UNAVAILABLE_RATIO

        if age >= unavailable_threshold:
            status = UNAVAILABLE
            penalty = 1.0
        elif age >= ttl:
            status = STALE
            penalty = 0.5
        elif age >= aging_threshold:
            # Linear interpolation from 0.0 to 0.3 across the AGING window
            aging_window = ttl - aging_threshold
            if aging_window > 0:
                penalty = ((age - aging_threshold) / aging_window) * 0.3
            else:
                penalty = 0.0
            status = AGING
        else:
            status = FRESH
            penalty = 0.0

        return FreshnessRecord(
            modality=modality,
            last_updated_epoch=epoch,
            ttl_seconds=ttl,
            status=status,
            age_seconds=age,
            confidence_penalty=penalty
        )

    def get_all_freshness(
        self,
        last_updated_map: Optional[Dict[str, float]] = None
    ) -> Dict[str, FreshnessRecord]:
        """
        Return freshness for all known modalities.

        Args:
            last_updated_map: Optional override timestamps per modality.
        """
        result = {}
        for modality in DEFAULT_TTL_SECONDS:
            epoch = None
            if last_updated_map:
                epoch = last_updated_map.get(modality)
            result[modality] = self.get_freshness(modality, last_updated_epoch=epoch)
        return result

    def compute_aggregate_confidence_penalty(
        self,
        modalities: List[str]
    ) -> float:
        """
        Weighted average confidence penalty across the requested modalities.
        Returns 0.0 (no penalty) to 1.0 (full penalty).
        """
        if not modalities:
            return 0.0
        penalties = [self.get_freshness(m).confidence_penalty for m in modalities]
        return min(1.0, sum(penalties) / len(penalties))

    def get_summary(self) -> Dict[str, str]:
        """Returns a dict of modality → freshness status string."""
        return {m: self.get_freshness(m).status for m in DEFAULT_TTL_SECONDS}


# Global singleton used across PAHAD services
FRESHNESS_ENGINE = DataFreshnessEngine()
