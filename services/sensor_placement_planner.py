# -*- coding: utf-8 -*-
"""
services/sensor_placement_planner.py
====================================
PARVAT NETRA • PAHAD AI — Geotechnical Sensor Placement Multi-Criteria Planner
-------------------------------------------------------------------------------
Evaluates and ranks prospective borehole, surface tilt, and precipitation sensor
locations along Himalayan mountain corridors using multi-criteria decision analysis (MCDA).

Criteria Evaluated:
  1. Slope Steepness & Geometry (30° - 60° critical failure band)
  2. Plan/Profile Curvature (flow convergence vs planar runoff)
  3. Historical Landslide Inventory (GSI records & recorded scarps)
  4. Transportation Corridor Criticality (strategic lifeline vs feeder)
  5. Downslope Population & Asset Exposure
  6. Rainfall Anomaly & Catchment Drainage Index
  7. Toe Erosion Proximity (Teesta, Ijei, Jatinga riverbeds)
  8. LoRa RF Propagation Visibility & Solar Insolation Access

Data Honesty Invariant:
  All scores and priority ranks are algorithmic heuristics and must be labeled:
  - is_scientifically_final: False
  - recommendation_basis: "ESTIMATED"
  - provenance: "MODELLED"
"""

from __future__ import annotations

import math
import logging
from typing import Dict, Any, List, Optional
from engine.corridor_registry import CORRIDOR_REGISTRY

logger = logging.getLogger("SENSOR_PLACEMENT_PLANNER")

# Normalized Evaluation Criteria Weights (Sum = 1.0)
CRITERIA_WEIGHTS = {
    "slope_gradient": 0.20,
    "historical_inventory": 0.18,
    "toe_erosion_proximity": 0.15,
    "rainfall_catchment": 0.12,
    "corridor_criticality": 0.12,
    "downslope_exposure": 0.10,
    "terrain_curvature": 0.08,
    "solar_accessibility": 0.05
}


class SensorPlacementPlanner:
    """Geotechnical site recommendation engine for in-situ instrument arrays."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or CRITERIA_WEIGHTS

    def score_slope(self, slope_deg: float) -> float:
        """
        Critical slope response:
        < 15°: Stable / flat (0.1)
        15° - 30°: Moderate hazard (0.4)
        30° - 50°: Highest shear failure initiation band (0.95 - 1.0)
        > 50°: Steep rockfall / cliff face, low colluvium retention (0.75)
        """
        if slope_deg < 15.0:
            return 0.15
        elif slope_deg <= 30.0:
            return 0.2 + (slope_deg - 15.0) / 15.0 * 0.4
        elif slope_deg <= 48.0:
            return 0.6 + (slope_deg - 30.0) / 18.0 * 0.4
        else:
            return max(0.6, 1.0 - (slope_deg - 48.0) / 30.0 * 0.3)

    def score_curvature(self, curvature_val: float) -> float:
        """Negative curvature (hollows/concave) concentrates pore water."""
        if curvature_val < -0.05:
            return 0.95  # Concave water-gathering hollow
        elif curvature_val > 0.05:
            return 0.30  # Convex nose / shedding
        return 0.60     # Planar slope

    def score_proximity_to_river(self, distance_m: float) -> float:
        """Proximity to actively cutting Himalayan riverbed increases toe unloading."""
        if distance_m <= 50.0:
            return 1.0
        elif distance_m <= 200.0:
            return 0.8
        elif distance_m <= 500.0:
            return 0.5
        elif distance_m <= 1000.0:
            return 0.25
        return 0.05

    def evaluate_candidate_site(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes composite multi-criteria suitability score for a prospective sensor site.
        """
        slope = float(candidate.get("slope_deg", 35.0))
        curvature = float(candidate.get("curvature", -0.02))
        hist_events = int(candidate.get("historical_events_count", 2))
        river_dist = float(candidate.get("river_distance_m", 150.0))
        rainfall_idx = float(candidate.get("catchment_rainfall_mm", 120.0))
        traffic_importance = candidate.get("corridor_criticality", "HIGH")
        population_downslope = int(candidate.get("population_exposed", 150))
        solar_hours = float(candidate.get("solar_insolation_hours", 4.5))

        # Sub-scores (0.0 to 1.0)
        s_slope = self.score_slope(slope)
        s_curv = self.score_curvature(curvature)
        s_hist = min(1.0, hist_events / 4.0)
        s_river = self.score_proximity_to_river(river_dist)
        s_rain = min(1.0, rainfall_idx / 250.0)
        
        crit_map = {"CRITICAL": 1.0, "HIGH": 0.8, "MODERATE": 0.5, "LOW": 0.2}
        s_crit = crit_map.get(traffic_importance.upper(), 0.6)
        s_pop = min(1.0, population_downslope / 300.0)
        s_solar = min(1.0, solar_hours / 6.0)

        composite_score = (
            s_slope * self.weights["slope_gradient"] +
            s_hist * self.weights["historical_inventory"] +
            s_river * self.weights["toe_erosion_proximity"] +
            s_rain * self.weights["rainfall_catchment"] +
            s_crit * self.weights["corridor_criticality"] +
            s_pop * self.weights["downslope_exposure"] +
            s_curv * self.weights["terrain_curvature"] +
            s_solar * self.weights["solar_accessibility"]
        )

        composite_score = round(composite_score, 4)

        # Rationalized Primary Recommendation Reason
        reasons = []
        if s_slope >= 0.85:
            reasons.append(f"Steep failure-prone slope gradient ({slope:.1f}°)")
        if s_river >= 0.8:
            reasons.append(f"Immediate toe erosion hazard ({river_dist:.0f}m from river)")
        if s_hist >= 0.7:
            reasons.append(f"Recorded historical reactivation frequency ({hist_events} occurrences)")
        if s_pop >= 0.6:
            reasons.append(f"High downslope settlement exposure ({population_downslope} persons)")
        if not reasons:
            reasons.append("Moderate overall composite hazard profile")

        # Instrument Recommendations
        instrument_package = []
        if slope >= 38.0 and s_river >= 0.7:
            instrument_package.extend(["piezometer", "inclinometer"])
        if curvature < -0.02 or s_rain >= 0.7:
            instrument_package.append("soil_moisture")
        if candidate.get("engineered_structure", False):
            instrument_package.extend(["tilt", "crack_sensor"])
        if not instrument_package:
            instrument_package.append("tilt")

        return {
            "site_id": candidate.get("site_id", "SITE-CANDIDATE"),
            "name": candidate.get("name", "Unnamed Slope Bench"),
            "latitude": candidate.get("latitude"),
            "longitude": candidate.get("longitude"),
            "composite_score": composite_score,
            "recommended_instruments": list(dict.fromkeys(instrument_package)),
            "primary_rationale": "; ".join(reasons),
            "sub_scores": {
                "slope": round(s_slope, 2),
                "historical": round(s_hist, 2),
                "river_proximity": round(s_river, 2),
                "rainfall": round(s_rain, 2),
                "criticality": round(s_crit, 2),
                "population": round(s_pop, 2),
                "curvature": round(s_curv, 2),
                "solar": round(s_solar, 2)
            },
            "recommendation_basis": "ESTIMATED",
            "is_scientifically_final": False,
            "provenance": "MODELLED"
        }

    def rank_sites_for_corridor(
        self,
        corridor_id: str,
        additional_candidates: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ranks all candidate sites for a specified corridor in descending order of composite score.
        """
        corridor = CORRIDOR_REGISTRY.get_corridor(corridor_id)
        candidates = list(additional_candidates or [])

        # Include registered sensor sites from corridor definition as baseline candidates
        if corridor:
            for s in corridor.sensor_sites:
                candidates.append({
                    "site_id": s.get("site_id"),
                    "name": s.get("name"),
                    "latitude": s.get("latitude"),
                    "longitude": s.get("longitude"),
                    "slope_deg": corridor.slope,
                    "historical_events_count": 3 if corridor.risk == "CRITICAL" else 1,
                    "river_distance_m": 80.0 if "Teesta" in corridor.name or "Ijei" in corridor.name else 250.0,
                    "corridor_criticality": corridor.risk,
                    "population_exposed": 220 if corridor.risk == "CRITICAL" else 90
                })

        evaluated = [self.evaluate_candidate_site(c) for c in candidates]
        evaluated.sort(key=lambda x: x["composite_score"], reverse=True)

        for rank, item in enumerate(evaluated, start=1):
            item["priority_rank"] = rank

        return evaluated


SENSOR_PLACEMENT_PLANNER = SensorPlacementPlanner()
