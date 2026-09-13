"""
engine/pahad_prioritization.py
==============================
PAHAD Phase 5 — Emergency Response Prioritisation Engine
---------------------------------------------------------
Evaluates GSI critical slope sectors and computes actionable
emergency response priority rankings for civil defence, BRO,
and NDRF staged deployment.

Mathematical Formulation:
  Priority Score = (Population_At_Risk * (CRI / 100.0) * Road_Criticality_Weight) / max(ETA_Hours, 0.5)

Road Criticality Weights:
  - STRATEGIC_SINGLE_ACCESS    : 2.5 (Lifeline route, no alternate bypass)
  - NATIONAL_HIGHWAY_ARTERIAL  : 1.8 (Primary freight and passenger corridor)
  - STATE_HIGHWAY_SECONDARY    : 1.2 (Alternate bypass corridor exists)
  - RURAL_LINK                 : 1.0 (Local village feeder road)

Staged Rescue Forces (NER Operational Architecture):
  - Sikkim           : BRO Project Swastik / NDRF 2nd Bn
  - Mizoram          : BRO Project Pushpak / SDRF Aizawl
  - Nagaland         : BRO Project Sewak / SDRF Kohima
  - Arunachal Pradesh: BRO Project Vartak / NDRF 12th Bn
  - Assam            : SDRF Guwahati / NDRF 1st Bn
  - Meghalaya        : SDRF Shillong
  - Manipur          : BRO Project Sewak / NDRF 12th Bn
  - Tripura          : SDRF Agartala

Author : PARVAT NETRA / PAHAD Engineering Team
Data   : [SIMULATED] Multi-Agency Disaster Response Matrix v5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

CRITICALITY_WEIGHTS: Dict[str, float] = {
    "STRATEGIC_SINGLE_ACCESS": 2.5,
    "NATIONAL_HIGHWAY_ARTERIAL": 1.8,
    "STATE_HIGHWAY_SECONDARY": 1.2,
    "RURAL_LINK": 1.0,
}

RESCUE_FORCE_MAPPING: Dict[str, str] = {
    "Sikkim": "BRO Project Swastik / NDRF 2nd Bn",
    "Mizoram": "BRO Project Pushpak / SDRF Aizawl",
    "Nagaland": "BRO Project Sewak / SDRF Kohima",
    "Arunachal Pradesh": "BRO Project Vartak / NDRF 12th Bn",
    "Assam": "SDRF Guwahati / NDRF 1st Bn",
    "Meghalaya": "SDRF Shillong",
    "Manipur": "BRO Project Sewak / NDRF 12th Bn",
    "Tripura": "SDRF Agartala",
}

DEFAULT_RESCUE_FORCE = "NDRF Regional Response Centre / State SDRF"

# Default baseline corridor risk profiles
DEFAULT_CORRIDOR_METRICS: Dict[str, Dict[str, Any]] = {
    "SK-NH10-KM48": {
        "population_at_risk": 32000,
        "cri_score": 88.5,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 0.8,
    },
    "SK-SINGTAM-01": {
        "population_at_risk": 18000,
        "cri_score": 76.0,
        "road_criticality": "NATIONAL_HIGHWAY_ARTERIAL",
        "eta_hours": 1.2,
    },
    "SK-DIKCHU-01": {
        "population_at_risk": 8500,
        "cri_score": 65.0,
        "road_criticality": "STATE_HIGHWAY_SECONDARY",
        "eta_hours": 1.8,
    },
    "SK-MANGAN-01": {
        "population_at_risk": 14000,
        "cri_score": 79.0,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 2.2,
    },
    "MZ-HUNTHAR-01": {
        "population_at_risk": 28000,
        "cri_score": 85.0,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 0.9,
    },
    "MZ-SAIRANG-01": {
        "population_at_risk": 11000,
        "cri_score": 68.0,
        "road_criticality": "STATE_HIGHWAY_SECONDARY",
        "eta_hours": 1.5,
    },
    "MZ-KOLASIB-01": {
        "population_at_risk": 16000,
        "cri_score": 74.0,
        "road_criticality": "NATIONAL_HIGHWAY_ARTERIAL",
        "eta_hours": 1.6,
    },
    "NL-PAGALA-01": {
        "population_at_risk": 35000,
        "cri_score": 87.0,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 1.0,
    },
    "NL-DZUDZA-01": {
        "population_at_risk": 19000,
        "cri_score": 78.0,
        "road_criticality": "NATIONAL_HIGHWAY_ARTERIAL",
        "eta_hours": 1.4,
    },
    "NL-PIPHEMA-01": {
        "population_at_risk": 12000,
        "cri_score": 64.0,
        "road_criticality": "STATE_HIGHWAY_SECONDARY",
        "eta_hours": 1.6,
    },
    "AR-BHALUK-01": {
        "population_at_risk": 22000,
        "cri_score": 86.0,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 1.5,
    },
    "AR-PASIGHAT-01": {
        "population_at_risk": 15000,
        "cri_score": 73.0,
        "road_criticality": "NATIONAL_HIGHWAY_ARTERIAL",
        "eta_hours": 1.8,
    },
    "AR-SELA-01": {
        "population_at_risk": 9000,
        "cri_score": 67.0,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 3.0,
    },
    "MN-TUPUL-01": {
        "population_at_risk": 24000,
        "cri_score": 84.0,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 1.4,
    },
    "MN-JIRIBAM-01": {
        "population_at_risk": 17000,
        "cri_score": 72.0,
        "road_criticality": "NATIONAL_HIGHWAY_ARTERIAL",
        "eta_hours": 2.0,
    },
    "ML-SONAPUR-01": {
        "population_at_risk": 31000,
        "cri_score": 86.5,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 1.1,
    },
    "ML-CHERRA-01": {
        "population_at_risk": 13000,
        "cri_score": 69.0,
        "road_criticality": "STATE_HIGHWAY_SECONDARY",
        "eta_hours": 1.7,
    },
    "AS-DIMA-01": {
        "population_at_risk": 26000,
        "cri_score": 83.0,
        "road_criticality": "STRATEGIC_SINGLE_ACCESS",
        "eta_hours": 1.6,
    },
    "AS-GUWAHATI-01": {
        "population_at_risk": 45000,
        "cri_score": 62.0,
        "road_criticality": "NATIONAL_HIGHWAY_ARTERIAL",
        "eta_hours": 0.6,
    },
    "TR-BARAMURA-01": {
        "population_at_risk": 14000,
        "cri_score": 66.0,
        "road_criticality": "NATIONAL_HIGHWAY_ARTERIAL",
        "eta_hours": 1.3,
    },
}


class EmergencyResponsePrioritizer:
    """
    Computes emergency response priority scores and tactical dispatches
    for disaster response staging.
    """

    def __init__(
        self,
        criticality_weights: Optional[Dict[str, float]] = None,
        rescue_forces: Optional[Dict[str, str]] = None,
    ) -> None:
        self.weights = criticality_weights or CRITICALITY_WEIGHTS
        self.rescue_forces = rescue_forces or RESCUE_FORCE_MAPPING

    def calculate_priority_score(
        self,
        population_at_risk: float,
        cri: float,
        road_criticality: str,
        eta_hours: float,
    ) -> float:
        """
        Evaluate priority score according to formula:
          Priority = (Population * (CRI / 100.0) * Weight) / max(ETA, 0.5)
        """
        pop = max(0.0, float(population_at_risk))
        cri_norm = max(0.0, min(100.0, float(cri))) / 100.0
        weight = self.weights.get(str(road_criticality).upper(), 1.0)
        eta_clamped = max(float(eta_hours), 0.5)

        score = (pop * cri_norm * weight) / eta_clamped
        return round(score, 2)

    def rank_active_sectors(self, sectors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate and rank list of active sectors in descending order of priority score.
        Enriches records with assigned rescue force and operational advisory.
        """
        ranked: List[Dict[str, Any]] = []

        for s in sectors:
            rec = dict(s)
            sec_id = rec.get("sector_id", "UNKNOWN")
            state = rec.get("state", "Sikkim")

            # Fill defaults if missing
            defaults = DEFAULT_CORRIDOR_METRICS.get(sec_id, {})
            pop = float(rec.get("population_at_risk", defaults.get("population_at_risk", 15000)))
            cri = float(rec.get("cri_score", defaults.get("cri_score", 70.0)))
            crit_type = str(rec.get("road_criticality", defaults.get("road_criticality", "NATIONAL_HIGHWAY_ARTERIAL")))
            eta = float(rec.get("eta_hours", defaults.get("eta_hours", 1.5)))

            score = self.calculate_priority_score(
                population_at_risk=pop,
                cri=cri,
                road_criticality=crit_type,
                eta_hours=eta,
            )

            # Assign staged rescue force
            force = self.rescue_forces.get(state, DEFAULT_RESCUE_FORCE)

            # Operational evacuation advisory
            if score >= 25000.0 or cri >= 85.0:
                advisory = "IMMEDIATE_PREVENTIVE_EVACUATION"
                urgency = "CRITICAL"
            elif score >= 12000.0 or cri >= 70.0:
                advisory = "TRAFFIC_SUSPENSION_AND_STAGING"
                urgency = "HIGH"
            else:
                advisory = "STANDBY_TACTICAL_MONITORING"
                urgency = "MODERATE"

            rec["priority_score"] = score
            rec["population_at_risk"] = int(pop)
            rec["cri_score"] = round(cri, 2)
            rec["road_criticality"] = crit_type
            rec["road_criticality_weight"] = self.weights.get(crit_type.upper(), 1.0)
            rec["eta_hours"] = eta
            rec["assigned_rescue_force"] = force
            rec["evacuation_advisory"] = advisory
            rec["urgency_level"] = urgency

            ranked.append(rec)

        # Sort descending by priority score
        ranked.sort(key=lambda x: x["priority_score"], reverse=True)

        # Assign 1-indexed priority rank
        for idx, item in enumerate(ranked, start=1):
            item["priority_rank"] = idx

        return ranked
