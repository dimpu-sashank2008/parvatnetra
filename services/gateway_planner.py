# -*- coding: utf-8 -*-
"""
services/gateway_planner.py
===========================
PARVAT NETRA • PAHAD AI — Gateway Placement & RF Line-of-Sight Planner
----------------------------------------------------------------------
Calculates topographic elevation clearance, distance, 1st Fresnel zone clearance,
and power/backhaul feasibility for Himalayan edge concentrator gateway locations.

Data Honesty Invariant:
  All radio propagation assessments are based on idealized optical/geometric
  models and must be labeled:
  - los_verdict: "ESTIMATED"
  - requires_rf_field_survey: True
  - provenance: "MODELLED"
  Field confirmation requires on-site testing via `scripts/test_radio_link.py`.
"""

from __future__ import annotations

import math
import logging
from typing import Dict, Any, List, Optional
from engine.corridor_registry import CORRIDOR_REGISTRY

logger = logging.getLogger("GATEWAY_PLANNER")


class GatewayPlanner:
    """Evaluates RF line-of-sight propagation, backhaul resilience, and coverage for edge gateways."""

    def __init__(self, default_frequency_mhz: float = 868.0):
        self.frequency_mhz = default_frequency_mhz

    def calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine great-circle distance between two decimal degree points."""
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2 +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 3)

    def calculate_fresnel_radius_m(self, distance_km: float, freq_mhz: Optional[float] = None) -> float:
        """
        Calculates maximum 1st Fresnel zone radius at path midpoint (meters):
        R1 = 8.656 * sqrt(D / f_GHz)
        """
        freq = (freq_mhz or self.frequency_mhz) / 1000.0  # Convert to GHz
        if distance_km <= 0 or freq <= 0:
            return 0.0
        return round(8.656 * math.sqrt(distance_km / freq), 2)

    def evaluate_node_link(self, gateway: Dict[str, Any], node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates geometric link budget and line-of-sight between an edge gateway and a sensor node.
        """
        gw_lat = float(gateway.get("latitude", 0.0))
        gw_lon = float(gateway.get("longitude", 0.0))
        gw_elev = float(gateway.get("elevation_m", 750.0))
        gw_mast = float(gateway.get("mast_height_m", 12.0))
        total_gw_elev = gw_elev + gw_mast

        node_lat = float(node.get("latitude", 0.0))
        node_lon = float(node.get("longitude", 0.0))
        node_elev = float(node.get("elevation_m", 680.0))
        node_mast = float(node.get("mast_height_m", 2.0))
        total_node_elev = node_elev + node_mast

        dist_km = self.calculate_distance_km(gw_lat, gw_lon, node_lat, node_lon)
        fresnel_r1_m = self.calculate_fresnel_radius_m(dist_km, self.frequency_mhz)
        elev_diff_m = total_gw_elev - total_node_elev

        # Free Space Path Loss (FSPL) in dB: FSPL = 32.44 + 20*log10(d_km) + 20*log10(f_MHz)
        if dist_km > 0:
            fspl_db = round(32.44 + 20.0 * math.log10(dist_km) + 20.0 * math.log10(self.frequency_mhz), 1)
        else:
            fspl_db = 0.0

        # Estimated LOS verdict based on Himalayan ridge geometry
        if dist_km <= 3.5 and elev_diff_m >= 15.0:
            los_verdict = "ESTIMATED_CLEAR"
            expected_rssi_band = "-75 dBm to -95 dBm"
            link_margin = "ADEQUATE"
        elif dist_km <= 6.0 and elev_diff_m >= -10.0:
            los_verdict = "MARGINAL"
            expected_rssi_band = "-96 dBm to -115 dBm"
            link_margin = "CRITICAL"
        else:
            los_verdict = "ESTIMATED_OBSTRUCTED"
            expected_rssi_band = "< -118 dBm"
            link_margin = "INSUFFICIENT"

        return {
            "node_id": node.get("site_id") or node.get("target_device_id", "UNKNOWN-NODE"),
            "distance_km": dist_km,
            "elevation_diff_m": round(elev_diff_m, 1),
            "fresnel_radius_1st_m": fresnel_r1_m,
            "free_space_path_loss_db": fspl_db,
            "estimated_los": los_verdict,
            "expected_rssi_band": expected_rssi_band,
            "link_margin": link_margin,
            "los_verdict": "ESTIMATED",
            "requires_rf_field_survey": True,
            "provenance": "MODELLED"
        }

    def plan_corridor_gateways(self, corridor_id: str) -> Dict[str, Any]:
        """
        Evaluates all gateway positions for a monitored corridor against its sensor sites.
        """
        corridor = CORRIDOR_REGISTRY.get_corridor(corridor_id)
        if not corridor:
            raise KeyError(f"Corridor {corridor_id} not found")

        gw_sites = corridor.gateway_sites
        sensor_sites = corridor.sensor_sites

        gateway_evaluations = []
        for gw in gw_sites:
            links = []
            clear_count = 0
            for sn in sensor_sites:
                eval_res = self.evaluate_node_link(gw, sn)
                links.append(eval_res)
                if eval_res["estimated_los"] == "ESTIMATED_CLEAR":
                    clear_count += 1

            gateway_evaluations.append({
                "gateway_id": gw.get("gateway_id"),
                "name": gw.get("name"),
                "latitude": gw.get("latitude"),
                "longitude": gw.get("longitude"),
                "elevation_m": gw.get("elevation_m"),
                "backhaul": gw.get("backhaul", "4G_LTE"),
                "node_links": links,
                "coverage_ratio": round(clear_count / max(1, len(sensor_sites)), 2)
            })

        return {
            "corridor_id": corridor_id,
            "gateway_count": len(gw_sites),
            "sensor_nodes_count": len(sensor_sites),
            "gateway_plans": gateway_evaluations,
            "planning_verdict": "ESTIMATED",
            "requires_rf_field_survey": True,
            "provenance": "MODELLED"
        }


GATEWAY_PLANNER = GatewayPlanner()
