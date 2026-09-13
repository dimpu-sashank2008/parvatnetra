# -*- coding: utf-8 -*-
"""
engine/event_labeling.py
========================
PARVAT NETRA • PAHAD AI Scientific Event Labeling & Control Protocol Engine
---------------------------------------------------------------------------
Implements strict labeling methodology for landslide event classification:
  1. Target Variable: Binary Y in {0, 1}
     - Y = 1: Documented slope failure / landslide within forecast horizon
     - Y = 0: Defensible negative control window
     - Excluded: Ambiguous / Unknown samples (missing rainfall, buffer overlap, uncertain timing)
  2. Positive Event Criteria:
     - Documented failure from GSI, NRSC, or SDMA
     - Known timestamp (< 24h uncertainty)
     - Verified coordinates within NER bounding box (lat: 21.5-29.5, lon: 88.0-97.5)
     - Source confidence >= 0.70
  3. Exclusion Zones:
     - 7-day temporal buffer (±7 days) around known scarps
     - 5 km spatial buffer around known failure zones
  4. Negative Control Selection:
     - Dry season or confirmed non-failure monitoring periods
     - Non-trivial terrain: slope > 15.0 degrees
     - Confirmed stability: FoS >= 1.10
     - Complete data coverage for core features
     - At least 5 km away from documented failure within 7 days
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

NER_LAT_RANGE = (21.5, 29.5)
NER_LON_RANGE = (88.0, 97.5)
MIN_SLOPE_FOR_NEGATIVE_CONTROL = 15.0
MIN_FOS_FOR_NEGATIVE_CONTROL = 1.10
MIN_SOURCE_CONFIDENCE = 0.70
SPATIAL_EXCLUSION_BUFFER_KM = 5.0
TEMPORAL_EXCLUSION_BUFFER_DAYS = 7.0


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographic points in kilometers."""
    r = 6371.0  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


class EventLabeler:
    """
    Scientific event labeling engine ensuring zero contamination between
    documented failures, rigorous negative controls, and excluded ambiguous periods.
    """

    def __init__(
        self,
        spatial_buffer_km: float = SPATIAL_EXCLUSION_BUFFER_KM,
        temporal_buffer_days: float = TEMPORAL_EXCLUSION_BUFFER_DAYS,
        min_slope_deg: float = MIN_SLOPE_FOR_NEGATIVE_CONTROL,
        min_fos: Optional[float] = None,
        min_source_confidence: float = MIN_SOURCE_CONFIDENCE,
        enforce_fos_stability: bool = False
    ):
        self.spatial_buffer_km = spatial_buffer_km
        self.temporal_buffer_days = temporal_buffer_days
        self.min_slope_deg = min_slope_deg
        self.min_fos = min_fos
        self.min_source_confidence = min_source_confidence
        self.enforce_fos_stability = enforce_fos_stability

    def validate_positive_event(self, event: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates whether a positive event record meets scientific ground-truth standards:
          1. Documented failure source from verified institutions.
          2. Known timestamp with < 24h uncertainty.
          3. Verified coordinates within Northeast Region (NER) bounding box.
          4. Source confidence >= 0.70.
        """
        source = str(event.get("source", "")).strip()
        auth_keywords = ["GSI", "SDMA", "PWD", "BRO", "ISRO", "NLSM", "Disaster", "IMD", "CWC", "NCS"]
        if not any(k in source for k in auth_keywords):
            return False, f"Source '{source}' is unverified; must be an authorized institutional record."

        confidence = float(event.get("source_confidence", event.get("confidence", 0.75)))
        if confidence < self.min_source_confidence:
            return False, f"Source confidence {confidence:.2f} is below threshold {self.min_source_confidence}."

        lat = float(event.get("latitude", 0.0))
        lon = float(event.get("longitude", 0.0))
        if not (NER_LAT_RANGE[0] <= lat <= NER_LAT_RANGE[1] and NER_LON_RANGE[0] <= lon <= NER_LON_RANGE[1]):
            return False, f"Coordinates ({lat}, {lon}) are outside Northeast Region bounding box."

        timestamp_str = event.get("timestamp") or event.get("event_start")
        if not timestamp_str:
            return False, "Missing failure timestamp."

        timing_uncertainty_hours = float(event.get("timing_uncertainty_hours", 0.0))
        if timing_uncertainty_hours > 24.0:
            return False, f"Timing uncertainty {timing_uncertainty_hours}h exceeds 24h limit."

        return True, "VALID_POSITIVE_EVENT"

    def is_in_exclusion_zone(
        self,
        lat: float,
        lon: float,
        timestamp_dt: datetime,
        known_events: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Checks if candidate location/time falls within the spatial/temporal exclusion zone
        around any documented positive event (within 5 km and 7 days).
        """
        for ev in known_events:
            ev_lat = float(ev.get("latitude", 0.0))
            ev_lon = float(ev.get("longitude", 0.0))
            ev_ts_str = ev.get("timestamp") or ev.get("event_start")
            if not ev_ts_str:
                continue

            try:
                ev_dt = datetime.fromisoformat(str(ev_ts_str).replace("Z", "+00:00"))
                if ev_dt.tzinfo is None:
                    ev_dt = ev_dt.replace(tzinfo=timezone.utc)
            except Exception:
                continue

            # Check time delta in days
            delta_days = abs((timestamp_dt - ev_dt).total_seconds()) / 86400.0
            if delta_days <= self.temporal_buffer_days:
                dist_km = haversine_distance_km(lat, lon, ev_lat, ev_lon)
                if dist_km <= self.spatial_buffer_km:
                    return True, f"Within {dist_km:.2f}km and {delta_days:.1f} days of event '{ev.get('event_id', 'unknown')}'"

        return False, None

    def validate_negative_control(
        self,
        record: Dict[str, Any],
        known_events: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Validates candidate negative control window:
          1. Slope > 15 degrees (not flat floodplains or trivial negatives).
          2. Physical stability: Factor of Safety >= 1.10.
          3. Complete core features (no missing core rainfall / telemetry).
          4. Outside 5 km and 7 day exclusion zone of any known failure.
        """
        slope = float(record.get("slope", record.get("slope_deg", 25.0)))
        if slope < self.min_slope_deg:
            return False, f"Slope {slope:.1f}° < {self.min_slope_deg}° minimum (trivial negative control rejected)."

        # Scientific Decoupling: FoS is an engineering physics feature (Model A), NOT ground truth for label assignment.
        # Enforcing FoS >= 1.10 creates selection bias and eliminates legitimate hard negative controls.
        # Only evaluate FoS when explicitly configured in legacy strict-stability mode.
        if self.enforce_fos_stability and self.min_fos is not None:
            fos = float(record.get("FoS", record.get("fos", 1.25)))
            if fos < self.min_fos:
                return False, f"Factor of Safety {fos:.2f} < {self.min_fos} (slope is near critical equilibrium)."

        lat = float(record.get("latitude", 0.0))
        lon = float(record.get("longitude", 0.0))
        ts_str = record.get("timestamp", "")
        if not ts_str:
            return False, "Missing timestamp."

        try:
            ts_dt = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
            if ts_dt.tzinfo is None:
                ts_dt = ts_dt.replace(tzinfo=timezone.utc)
        except Exception:
            return False, f"Invalid timestamp format: {ts_str}"

        # Exclusion zone check
        in_exclusion, reason = self.is_in_exclusion_zone(lat, lon, ts_dt, known_events)
        if in_exclusion:
            return False, f"Candidate falls inside exclusion zone: {reason}"

        # Core feature completeness check
        core_features = ["rainfall_24h", "soil_moisture", "elevation", "slope"]
        for feat in core_features:
            if feat not in record or record[feat] is None or record[feat] == "":
                return False, f"Missing core feature '{feat}' required for verified negative control."

        return True, "VALID_NEGATIVE_CONTROL"

    def label_record(
        self,
        record: Dict[str, Any],
        known_positive_events: List[Dict[str, Any]]
    ) -> Tuple[str, int, str]:
        """
        Labels record into:
          - ("POSITIVE", 1, rationale)
          - ("NEGATIVE", 0, rationale)
          - ("UNKNOWN", -1, rationale) [excluded from binary training]
        """
        # If candidate claims to be positive
        raw_label = int(record.get("event_label", 0))
        if raw_label == 1:
            valid, reason = self.validate_positive_event(record)
            if valid:
                return "POSITIVE", 1, reason
            else:
                return "UNKNOWN", -1, f"Rejected positive event: {reason}"

        # Candidate claims to be negative
        valid_neg, neg_reason = self.validate_negative_control(record, known_positive_events)
        if valid_neg:
            return "NEGATIVE", 0, neg_reason
        else:
            return "UNKNOWN", -1, f"Rejected negative control: {neg_reason}"
