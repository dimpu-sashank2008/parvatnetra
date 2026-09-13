# -*- coding: utf-8 -*-
"""
engine/pahad_events.py
======================
PARVAT NETRA • PAHAD AI Landslide Event Observation Data Model
--------------------------------------------------------------
Defines the strict observation schema for landslide event prediction,
distinguishing:
  1. Geotechnical Stability (Factor of Safety - FoS)
  2. Landslide Event Probability (P(Event | Horizon))
  3. Composite Risk Index (CRI = Hazard + Vulnerability/Exposure)

Event label convention:
  0 = No documented slope failure within observation window
  1 = Verified landslide / mass movement failure event

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union



# Explicit Visual Evidence Taxonomy & Statuses
EVIDENCE_TYPE_BEFORE_AFTER_PHOTO = "BEFORE_AFTER_PHOTO"
EVIDENCE_TYPE_FIELD_PHOTO = "FIELD_PHOTO"
EVIDENCE_TYPE_FIELD_VIDEO = "FIELD_VIDEO"
EVIDENCE_TYPE_SATELLITE_IMAGERY = "SATELLITE_IMAGERY"
EVIDENCE_TYPE_INSAR_DEFORMATION = "INSAR_DEFORMATION"
EVIDENCE_TYPE_GEOTECHNICAL_SKETCH = "GEOTECHNICAL_SKETCH"

VALID_EVIDENCE_TYPES = {
    EVIDENCE_TYPE_BEFORE_AFTER_PHOTO,
    EVIDENCE_TYPE_FIELD_PHOTO,
    EVIDENCE_TYPE_FIELD_VIDEO,
    EVIDENCE_TYPE_SATELLITE_IMAGERY,
    EVIDENCE_TYPE_INSAR_DEFORMATION,
    EVIDENCE_TYPE_GEOTECHNICAL_SKETCH,
}

STATUS_VERIFIED = "VERIFIED"
STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
STATUS_PENDING = "PENDING"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_DEMO_QUARANTINED = "DEMO_QUARANTINED"

VALID_VERIFICATION_STATUSES = {
    STATUS_VERIFIED,
    STATUS_NOT_AVAILABLE,
    STATUS_PENDING,
    STATUS_UNVERIFIED,
    STATUS_DEMO_QUARANTINED,
}


@dataclass
class VisualEvidenceRecord:
    """
    Provenance-controlled visual and remote sensing evidence layer for historical events.
    Enforces strict verification status, archive traceability, and zero-fabrication.
    """
    evidence_id: str
    event_id: str
    evidence_type: str
    title: str
    description: str
    source_reference: str
    source_url: Optional[str] = None
    capture_date: Optional[str] = None
    verification_status: str = STATUS_NOT_AVAILABLE
    provenance: str = "[HISTORICAL]"
    sha256_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.verification_status not in VALID_VERIFICATION_STATUSES:
            raise ValueError(f"Invalid verification_status: {self.verification_status}. Must be one of {VALID_VERIFICATION_STATUSES}")
        if self.evidence_type not in VALID_EVIDENCE_TYPES:
            raise ValueError(f"Invalid evidence_type: {self.evidence_type}. Must be one of {VALID_EVIDENCE_TYPES}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LandslideEventObservation:
    """
    Unified temporal event observation schema for PAHAD AI event-prediction models.
    Encapsulates static terrain, hydrometeorological triggers, in-situ geotechnics,
    seismic excitation, satellite vegetation, historical susceptibility, and physical state.
    """
    # Identification & Ground Truth Label
    sector_id: str
    timestamp: str  # ISO 8601 observation timestamp
    event_label: int  # 0 = No event, 1 = Documented landslide failure
    event_start: Optional[str] = None  # Exact failure timestamp if known
    event_window: str = "6h"  # Prediction target window (e.g., '1h', '3h', '6h', '12h', '24h', '48h')

    # Meteorological Triggers
    rainfall_1h: float = 0.0      # Current 1h rainfall accumulation (mm)
    rainfall_6h: float = 0.0      # 6h accumulation (mm)
    rainfall_24h: float = 0.0     # 24h accumulation (mm)
    rainfall_72h: float = 0.0     # 72h accumulation (mm)
    API_3d: float = 0.0           # 3-day Antecedent Precipitation Index (mm)
    API_7d: float = 0.0           # 7-day Antecedent Precipitation Index (mm)
    API_30d: float = 0.0          # 30-day Antecedent Precipitation Index (mm)

    # In-Situ Geotechnical Telemetry
    soil_moisture: float = 0.35   # Volumetric Water Content (m^3/m^3)
    pore_pressure: float = 8.5    # Piezometer pore-water pressure (kPa)
    tilt: float = 0.45            # Inclinometer/tilt deflection (degrees)
    ground_displacement: float = 1.2  # Borehole cumulative displacement (mm)

    # Seismic Excitation
    seismic_magnitude: float = 0.0       # Richter magnitude
    seismic_distance: float = 999.0      # Epicentral distance (km)
    seismic_trigger_score: float = 0.0   # Attenuated shaking proxy (0.0 to 1.0)

    # Static Geospatial & Terrain Attributes
    elevation: float = 540.0             # Altitude from DEM (meters)
    slope: float = 38.0                  # Slope angle (degrees)
    aspect: float = 215.0                # Aspect (degrees clockwise from North)
    curvature: float = -0.04             # Planform/profile curvature

    # Remote Sensing & Vegetation
    NDVI: float = 0.65                   # Normalized Difference Vegetation Index
    NDVI_change: float = -0.04           # Temporal delta (current - previous NDVI)

    # History, Exposure & Disturbance
    historical_landslide_density: float = 0.012  # Historical events per km^2
    road_criticality: float = 0.70               # Strategic corridor importance (0.0 - 1.0)
    population_exposure: int = 850               # Local exposed population count

    # Physical Model & Composite Risk (Distinct from Event Probability!)
    FoS: float = 1.25                    # Infinite slope Factor of Safety (Mohr-Coulomb)
    CRI: float = 45.0                    # Composite Risk Index (0 - 100)

    # Provenance & Audit Metadata
    source: str = "GSI / IMD / Copernicus / In-Situ Sensor Telemetry"
    provenance: str = "[HISTORICAL]"     # [LIVE], [CACHED], [HISTORICAL], [SIMULATED], [DEMO]

    # Additional Temporal Trend & Rate-of-Change Features
    rainfall_accumulation_3h: float = 0.0
    rainfall_intensity_3h: float = 0.0     # mm/hr over 3h window
    rainfall_acceleration: float = 0.0      # dI/dt (rainfall rate delta)
    soil_moisture_trend_24h: float = 0.0    # Delta soil moisture over 24h
    pore_pressure_trend_24h: float = 0.0    # Delta pore pressure over 24h
    tilt_rate_24h: float = 0.0              # Degrees per 24h
    displacement_velocity_24h: float = 0.0  # mm/day rate
    seismic_recency_hours: float = 999.0    # Hours since latest significant seismic event
    static_susceptibility: float = 0.50     # GSI static susceptibility rating (0.0 - 1.0)

    # Spatial grouping for GroupKFold validation
    geographic_group: str = "teesta_corridor"

    # Linked Visual & Remote Sensing Evidence Layer (Zero-Fabrication)
    visual_evidence: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        # Ensure event_label is strictly binary (0 or 1)
        if self.event_label not in (0, 1):
            raise ValueError(f"event_label must be explicitly 0 or 1, got: {self.event_label}")
        
        # Derive trend features if not explicitly supplied
        if self.rainfall_intensity_3h == 0.0 and self.rainfall_6h > 0.0:
            self.rainfall_intensity_3h = round(self.rainfall_6h / 6.0, 2)
        if self.rainfall_accumulation_3h == 0.0:
            self.rainfall_accumulation_3h = round((self.rainfall_1h + self.rainfall_6h) / 2.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Converts observation record to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LandslideEventObservation:
        """Constructs observation from dictionary with fallback defaults."""
        fields_set = set(cls.__dataclass_fields__.keys())
        filtered = {k: v for k, v in data.items() if k in fields_set}
        return cls(**filtered)

    def to_feature_vector(self) -> Dict[str, float]:
        """
        Extracts numerical model feature vector for statistical classifiers.
        Excludes metadata, identifiers, and the target label to strictly prevent leakage.
        """
        return {
            "rainfall_1h": float(self.rainfall_1h),
            "rainfall_6h": float(self.rainfall_6h),
            "rainfall_24h": float(self.rainfall_24h),
            "rainfall_72h": float(self.rainfall_72h),
            "API_3d": float(self.API_3d),
            "API_7d": float(self.API_7d),
            "API_30d": float(self.API_30d),
            "rainfall_accumulation_3h": float(self.rainfall_accumulation_3h),
            "rainfall_intensity_3h": float(self.rainfall_intensity_3h),
            "rainfall_acceleration": float(self.rainfall_acceleration),
            "soil_moisture": float(self.soil_moisture),
            "soil_moisture_trend_24h": float(self.soil_moisture_trend_24h),
            "pore_pressure": float(self.pore_pressure),
            "pore_pressure_trend_24h": float(self.pore_pressure_trend_24h),
            "tilt": float(self.tilt),
            "tilt_rate_24h": float(self.tilt_rate_24h),
            "ground_displacement": float(self.ground_displacement),
            "displacement_velocity_24h": float(self.displacement_velocity_24h),
            "seismic_magnitude": float(self.seismic_magnitude),
            "seismic_distance": float(self.seismic_distance),
            "seismic_trigger_score": float(self.seismic_trigger_score),
            "seismic_recency_hours": float(self.seismic_recency_hours),
            "elevation": float(self.elevation),
            "slope": float(self.slope),
            "aspect": float(self.aspect),
            "curvature": float(self.curvature),
            "NDVI": float(self.NDVI),
            "NDVI_change": float(self.NDVI_change),
            "historical_landslide_density": float(self.historical_landslide_density),
            "static_susceptibility": float(self.static_susceptibility),
            "road_criticality": float(self.road_criticality),
            "population_exposure": float(self.population_exposure),
            "FoS": float(self.FoS),
            "CRI": float(self.CRI)
        }


# Schema definitions and supported forecast horizons
SUPPORTED_FORECAST_HORIZONS: List[int] = [1, 3, 6, 12, 24, 48]

EVENT_FEATURE_COLUMNS: List[str] = [
    "rainfall_1h", "rainfall_6h", "rainfall_24h", "rainfall_72h",
    "API_3d", "API_7d", "API_30d",
    "rainfall_accumulation_3h", "rainfall_intensity_3h", "rainfall_acceleration",
    "soil_moisture", "soil_moisture_trend_24h",
    "pore_pressure", "pore_pressure_trend_24h",
    "tilt", "tilt_rate_24h",
    "ground_displacement", "displacement_velocity_24h",
    "seismic_magnitude", "seismic_distance", "seismic_trigger_score", "seismic_recency_hours",
    "elevation", "slope", "aspect", "curvature",
    "NDVI", "NDVI_change",
    "historical_landslide_density", "static_susceptibility",
    "road_criticality", "population_exposure",
    "FoS", "CRI"
]
