# -*- coding: utf-8 -*-
"""
engine/pahad_corroboration.py
=============================
PARVAT NETRA • PAHAD AI — Multi-Source Independent Corroboration Engine
-----------------------------------------------------------------------
Enforces the strict multi-modal independent corroboration rule:
Never recommend or trigger high-severity early warnings on a single sensor
or model anomaly. Multiple parameters from the same physical source DO NOT
count as independent evidence.

Authoritative Independence Groups:
  1. PHYSICS           : Mohr-Coulomb limit equilibrium Factor of Safety (FoS)
  2. METEOROLOGY       : AWS/IMD rainfall intensity & antecedent threshold exceedance
  3. CLASSIFIER        : PAHAD ML calibrated event probability model
  4. IN_SITU_TELEMETRY : Borehole piezometer, MEMS inclinometer, tiltmeter
  5. EARTH_OBSERVATION : Sentinel-1 InSAR LOS ground deformation, NDVI anomaly
  6. SEISMOLOGY        : NCS/USGS peak ground acceleration & seismic triggers
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger("PAHAD_CORROBORATION")

# 6 Mutually Independent Signal Groups
GROUP_PHYSICS = "PHYSICS"
GROUP_METEOROLOGY = "METEOROLOGY"
GROUP_CLASSIFIER = "CLASSIFIER"
GROUP_IN_SITU = "IN_SITU_TELEMETRY"
GROUP_EARTH_OBSERVATION = "EARTH_OBSERVATION"
GROUP_SEISMOLOGY = "SEISMOLOGY"

VALID_INDEPENDENCE_GROUPS = {
    GROUP_PHYSICS,
    GROUP_METEOROLOGY,
    GROUP_CLASSIFIER,
    GROUP_IN_SITU,
    GROUP_EARTH_OBSERVATION,
    GROUP_SEISMOLOGY
}


@dataclass
class CorroborationSignal:
    signal_name: str
    value: Any
    quality: str
    source: str
    independence_group: str
    is_abnormal: bool
    threshold_info: str
    confidence_weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CorroborationEngine:
    """Evaluates multi-source evidence ensuring strict independence of confirming signals."""

    def evaluate_signals(self, observation_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts signals, maps each to its unique independence group, evaluates abnormality,
        and determines multi-group corroboration agreement.
        """
        signals: List[CorroborationSignal] = []

        # 1. PHYSICS GROUP: FoS
        if "fos" in observation_bundle and observation_bundle["fos"] is not None:
            fos_val = float(observation_bundle["fos"])
            abnormal = fos_val < 1.25  # Limit equilibrium threshold
            signals.append(CorroborationSignal(
                signal_name="factor_of_safety",
                value=fos_val,
                quality=observation_bundle.get("fos_quality", "GOOD"),
                source="INFINITE_SLOPE_PHYSICS_ENGINE",
                independence_group=GROUP_PHYSICS,
                is_abnormal=abnormal,
                threshold_info="FoS < 1.25 indicates limit equilibrium shear instability",
                confidence_weight=1.0
            ))

        # 2. METEOROLOGY GROUP: Rainfall Intensity / Antecedent
        rain_24h = observation_bundle.get("rain_24h_mm")
        rain_int = observation_bundle.get("rain_intensity_mmh")
        if rain_24h is not None or rain_int is not None:
            r24 = float(rain_24h or 0.0)
            rint = float(rain_int or 0.0)
            abnormal = (r24 >= 80.0) or (rint >= 25.0)
            signals.append(CorroborationSignal(
                signal_name="precipitation_threshold",
                value={"rain_24h_mm": r24, "rain_intensity_mmh": rint},
                quality=observation_bundle.get("weather_quality", "GOOD"),
                source=observation_bundle.get("weather_source", "IMD_AWS_STATION"),
                independence_group=GROUP_METEOROLOGY,
                is_abnormal=abnormal,
                threshold_info="Rainfall >= 80mm/24h or >= 25mm/h triggers geotechnical saturation",
                confidence_weight=0.9
            ))

        # 3. CLASSIFIER GROUP: ML Event Probability
        if "event_probability" in observation_bundle and observation_bundle["event_probability"] is not None:
            prob = float(observation_bundle["event_probability"])
            abnormal = prob >= 0.65
            signals.append(CorroborationSignal(
                signal_name="event_probability_ml",
                value=prob,
                quality=observation_bundle.get("model_quality", "GOOD"),
                source="PAHAD_GBDT_CLASSIFIER_V3",
                independence_group=GROUP_CLASSIFIER,
                is_abnormal=abnormal,
                threshold_info="Calibrated failure probability >= 0.65",
                confidence_weight=0.95
            ))

        # 4. IN-SITU TELEMETRY GROUP: Piezometer / Inclinometer / Tilt
        in_situ_abnormal = False
        in_situ_details = {}
        if "pore_pressure_kpa" in observation_bundle and observation_bundle["pore_pressure_kpa"] is not None:
            pp = float(observation_bundle["pore_pressure_kpa"])
            in_situ_details["pore_pressure_kpa"] = pp
            if pp >= 45.0:
                in_situ_abnormal = True

        if "tilt_deg" in observation_bundle and observation_bundle["tilt_deg"] is not None:
            tilt = float(observation_bundle["tilt_deg"])
            in_situ_details["tilt_deg"] = tilt
            if tilt >= 0.50:
                in_situ_abnormal = True

        if "displacement_rate_mm_h" in observation_bundle and observation_bundle["displacement_rate_mm_h"] is not None:
            disp = float(observation_bundle["displacement_rate_mm_h"])
            in_situ_details["displacement_rate_mm_h"] = disp
            if disp >= 2.0:
                in_situ_abnormal = True

        if in_situ_details:
            signals.append(CorroborationSignal(
                signal_name="in_situ_sensor_array",
                value=in_situ_details,
                quality=observation_bundle.get("sensor_quality", "GOOD"),
                source="CORRIDOR_LORA_BOREHOLE_ARRAY",
                independence_group=GROUP_IN_SITU,
                is_abnormal=in_situ_abnormal,
                threshold_info="Pore pressure >= 45kPa, Tilt >= 0.5°, or Inclinometer >= 2mm/h",
                confidence_weight=1.0
            ))

        # 5. EARTH OBSERVATION GROUP: InSAR / NDVI
        if "insar_velocity_mm_yr" in observation_bundle and observation_bundle["insar_velocity_mm_yr"] is not None:
            insar = float(observation_bundle["insar_velocity_mm_yr"])
            abnormal = abs(insar) >= 20.0
            signals.append(CorroborationSignal(
                signal_name="satellite_insar_deformation",
                value=insar,
                quality=observation_bundle.get("eo_quality", "GOOD"),
                source="SENTINEL_1_SAR_CATALOG",
                independence_group=GROUP_EARTH_OBSERVATION,
                is_abnormal=abnormal,
                threshold_info="InSAR Line-of-Sight velocity >= 20mm/yr",
                confidence_weight=0.85
            ))

        # 6. SEISMOLOGY GROUP: Earthquakes
        if "seismic_pga_g" in observation_bundle and observation_bundle["seismic_pga_g"] is not None:
            pga = float(observation_bundle["seismic_pga_g"])
            abnormal = pga >= 0.08  # 0.08g ground acceleration
            signals.append(CorroborationSignal(
                signal_name="seismic_pga_trigger",
                value=pga,
                quality=observation_bundle.get("seismic_quality", "GOOD"),
                source="NCS_USGS_EARTHQUAKE_FEED",
                independence_group=GROUP_SEISMOLOGY,
                is_abnormal=abnormal,
                threshold_info="Peak Ground Acceleration (PGA) >= 0.08g",
                confidence_weight=0.9
            ))

        # Count DISTINCT independent groups confirming anomaly
        abnormal_groups: Set[str] = set()
        normal_groups: Set[str] = set()
        dominant_drivers: List[str] = []

        for s in signals:
            if s.is_abnormal:
                abnormal_groups.add(s.independence_group)
                dominant_drivers.append(f"{s.independence_group}:{s.signal_name}")
            else:
                normal_groups.add(s.independence_group)

        # Multi-Group Corroboration Rule: Requires >= 2 DISTINCT independent groups
        distinct_count = len(abnormal_groups)
        is_corroborated = distinct_count >= 2

        # Corroboration agreement score (0.0 to 1.0)
        total_groups_present = len(abnormal_groups.union(normal_groups))
        agreement_ratio = round(distinct_count / max(1, total_groups_present), 2)

        return {
            "is_corroborated": is_corroborated,
            "independent_groups_count": distinct_count,
            "participating_abnormal_groups": sorted(list(abnormal_groups)),
            "all_present_groups": sorted(list(abnormal_groups.union(normal_groups))),
            "agreement_ratio": agreement_ratio,
            "dominant_drivers": dominant_drivers,
            "signals": [s.to_dict() for s in signals],
            "recommendation": (
                "CORROBORATED_HAZARD" if is_corroborated
                else "UNCONFIRMED_ANOMALY" if distinct_count == 1
                else "EQUILIBRIUM"
            )
        }


PAHAD_CORROBORATION = CorroborationEngine()
