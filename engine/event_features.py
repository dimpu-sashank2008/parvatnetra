# -*- coding: utf-8 -*-
"""
engine/event_features.py
========================
PARVAT NETRA • PAHAD AI Multi-Modal Feature Registry & Missing Data Strategy
----------------------------------------------------------------------------
Defines the scientific feature grouping, provenance tracking, and missing-data
imputation strategy for the PAHAD Landslide Event Prediction Model.

Feature Groups:
  1. Rainfall & Hydrology
  2. Terrain & Geomorphology
  3. Vegetation & Land Cover
  4. Susceptibility & Geology
  5. Infrastructure & Disturbance
  6. Geotechnical & Telemetry
  7. Satellite / InSAR
  8. Seismic & Dynamic

Provenance Flags:
  - [LIVE]: Real-time authenticated sensor or API telemetry.
  - [HISTORICAL]: Archival record from GSI/IMD/Copernicus historical catalog.
  - [CACHED]: Last known valid reading cached due to telemetry disruption.
  - [SIMULATED]: Statistically/physically realistic simulation for demonstration.
  - [MISSING]: Feature value unavailable; imputed via training split median.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple, Set

# Provenance status flags
VALID_PROVENANCE_FLAGS: Set[str] = {"[LIVE]", "[HISTORICAL]", "[CACHED]", "[SIMULATED]", "[MISSING]"}

# 8 Scientific Feature Groups
FEATURE_GROUPS: Dict[str, List[str]] = {
    "rainfall_and_hydrology": [
        "rainfall_1h", "rainfall_3h", "rainfall_accumulation_3h", "rainfall_intensity_3h",
        "rainfall_6h", "rainfall_12h", "rainfall_24h", "rainfall_72h",
        "rainfall_acceleration", "API_3d", "API_7d", "API_30d",
        "soil_moisture", "pore_pressure"
    ],
    "terrain_and_geomorphology": [
        "slope", "elevation", "aspect", "curvature",
        "topographic_wetness_index", "stream_power_index"
    ],
    "vegetation_and_land_cover": [
        "NDVI", "NDVI_change", "land_use_class", "forest_canopy_loss"
    ],
    "susceptibility_and_geology": [
        "lithology_code", "geological_structure_distance_m",
        "historical_landslide_density", "fault_distance_m",
        "static_susceptibility"
    ],
    "infrastructure_and_disturbance": [
        "road_cut_distance_m", "cut_slope_height_m", "drainage_density",
        "road_criticality", "population_exposure"
    ],
    "geotechnical_and_telemetry": [
        "pore_pressure", "pore_pressure_trend_24h",
        "ground_displacement", "displacement_velocity_24h",
        "tilt", "tilt_rate_24h", "soil_moisture_trend_24h",
        "vibration_g", "FoS"
    ],
    "satellite_and_insar": [
        "insar_los_velocity_mm_yr", "insar_coherence", "coherence_loss_30d"
    ],
    "seismic_and_dynamic": [
        "seismic_magnitude", "seismic_distance", "seismic_trigger_score",
        "seismic_recency_hours", "pga_g", "seismic_intensity_mmi",
        "recent_earthquake_count_7d"
    ]
}

# Pre-computed training split (real_train.csv) feature medians for leakage-safe imputation
# These values are derived strictly from the training partition and never from test data.
TRAINING_SPLIT_MEDIANS: Dict[str, float] = {
    "rainfall_1h": 0.0,
    "rainfall_6h": 5.2,
    "rainfall_24h": 22.0,
    "rainfall_72h": 65.0,
    "rainfall_accumulation_3h": 2.5,
    "rainfall_intensity_3h": 0.85,
    "rainfall_acceleration": 0.02,
    "API_3d": 18.5,
    "API_7d": 42.0,
    "API_30d": 145.0,
    "soil_moisture": 0.36,
    "soil_moisture_trend_24h": 0.015,
    "pore_pressure": 9.2,
    "pore_pressure_trend_24h": 0.50,
    "tilt": 0.52,
    "tilt_rate_24h": 0.03,
    "ground_displacement": 1.45,
    "displacement_velocity_24h": 0.25,
    "seismic_magnitude": 0.0,
    "seismic_distance": 999.0,
    "seismic_trigger_score": 0.0,
    "seismic_recency_hours": 999.0,
    "elevation": 720.0,
    "slope": 34.0,
    "aspect": 195.0,
    "curvature": -0.02,
    "NDVI": 0.62,
    "NDVI_change": -0.02,
    "historical_landslide_density": 0.010,
    "static_susceptibility": 0.55,
    "road_criticality": 0.65,
    "population_exposure": 750.0,
    "FoS": 1.22,
    "CRI": 52.0
}


@dataclass
class FeatureItem:
    """Represents a single feature value with provenance and metadata."""
    name: str
    value: float
    provenance: str = "[HISTORICAL]"  # [LIVE], [HISTORICAL], [CACHED], [SIMULATED], [MISSING]
    group: str = "rainfall_and_hydrology"
    is_imputed: bool = False
    source: str = "IMD / GSI"


class EventFeatureExtractor:
    """
    Extracts, standardizes, and audits feature vectors for landslide event modeling.
    Enforces strict missing-data handling without data leakage.
    """

    def __init__(self, training_medians: Optional[Dict[str, float]] = None):
        self.medians = training_medians or TRAINING_SPLIT_MEDIANS

    def get_feature_group(self, feature_name: str) -> str:
        """Finds which of the 8 feature groups a feature belongs to."""
        for group, features in FEATURE_GROUPS.items():
            if feature_name in features:
                return group
        return "other"

    def process_raw_features(
        self,
        raw_dict: Dict[str, Any],
        provenance_hints: Optional[Dict[str, str]] = None
    ) -> Tuple[Dict[str, float], Dict[str, str], float]:
        """
        Processes an input feature dictionary:
          1. Validates values.
          2. Replaces missing / None / NaN values with training split medians.
          3. Tracks per-feature provenance badges.
          4. Computes overall data completeness score (0.0 to 1.0).

        Returns:
          - clean_features: Dict[str, float]
          - provenance_map: Dict[str, str]
          - completeness_score: float (percentage of non-missing features)
        """
        clean_features: Dict[str, float] = {}
        provenance_map: Dict[str, str] = {}
        provenance_hints = provenance_hints or {}

        total_features = len(self.medians)
        available_count = 0

        for col, median_val in self.medians.items():
            val = raw_dict.get(col)
            hint_prov = provenance_hints.get(col)

            if val is None or val == "" or (isinstance(val, float) and (val != val or val == float("inf"))):
                # Feature is missing -> impute with training split median
                clean_features[col] = float(median_val)
                provenance_map[col] = "[MISSING]"
            else:
                try:
                    num_val = float(val)
                    clean_features[col] = num_val
                    available_count += 1
                    # Use hint if valid, else default to [HISTORICAL] or [LIVE]
                    if hint_prov in VALID_PROVENANCE_FLAGS:
                        provenance_map[col] = hint_prov
                    else:
                        provenance_map[col] = "[LIVE]" if raw_dict.get("is_live", False) else "[HISTORICAL]"
                except (ValueError, TypeError):
                    clean_features[col] = float(median_val)
                    provenance_map[col] = "[MISSING]"

        completeness = float(available_count / total_features) if total_features > 0 else 1.0
        return clean_features, provenance_map, round(completeness, 3)

    def summarize_provenance(self, provenance_map: Dict[str, str]) -> Dict[str, int]:
        """Returns breakdown count of features across provenance categories."""
        counts = {p: 0 for p in VALID_PROVENANCE_FLAGS}
        for prov in provenance_map.values():
            if prov in counts:
                counts[prov] += 1
        return counts
