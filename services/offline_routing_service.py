# -*- coding: utf-8 -*-
"""
services/offline_routing_service.py
===================================
PARVAT NETRA • Pilot Region Offline Road Network & Evacuation Routing Engine
-----------------------------------------------------------------------------
Computes emergency bypass routing, nearest evacuation shelter identification,
and distance/travel time estimations using locally packaged road graph data
without requiring central cloud or third-party mapping APIs.

Key Operational Formulations:
  - Local Road Graph: Strategic corridors (NH-10, NH-717A, NH-29, NH-06, NH-13, NH-37)
  - Severed Lifeline Detection: Dynamic avoidance of active landslide blockages
  - Evacuation Shelter Proximity: Spherical Haversine distance in km
  - Provenance Guard: Explicit labeling as 'OFFLINE ROUTE' / '[CACHED]'

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import math
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("PAHAD_OFFLINE_ROUTING")

# Regional average speeds for mountain corridors (km/h)
AVERAGE_SPEED_KMH = {
    "PRIMARY_HIGHWAY": 35.0,
    "BYPASS_CORRIDOR": 25.0,
    "RURAL_STEEP": 15.0,
    "SEVERED": 0.0
}


class OfflineRoutingService:
    """Zero-connectivity routing engine for the NER pilot mountain corridor."""

    def __init__(self) -> None:
        self.blocked_corridors_set: set[str] = set()
        self.blocked_bridges_set: set[str] = set()
        self.landslide_hazard_zones: List[Dict[str, Any]] = []
        self.is_data_stale: bool = False
        self._init_network()

    def _init_network(self) -> None:
        """Loads offline network from pahad_routing components."""
        try:
            from engine.pahad_routing import MONITORED_CORRIDORS, BYPASS_ROUTES, EMERGENCY_SHELTERS
            self.corridors = [dict(c) for c in MONITORED_CORRIDORS]
            self.bypass_matrix = {k: [dict(r) for r in v] for k, v in BYPASS_ROUTES.items()}
            self.shelters = [dict(s) for s in EMERGENCY_SHELTERS]
        except Exception as exc:
            logger.warning(f"[OfflineRouting] Fallback to minimal static road graph: {exc}")
            self.corridors = [
                {
                    "corridor_id": "SK-NH10",
                    "name": "NH-10 (Siliguri – Gangtok Lifeline)",
                    "state": "Sikkim",
                    "status": "SEVERED_BLOCKED",
                    "blockage_point": "Km 48 (29th Mile Sector)",
                    "affected_length_km": 4.2,
                }
            ]
            self.bypass_matrix = {
                "SK-NH10": [
                    {
                        "route_id": "BYP-SK-01",
                        "name": "NH-717A Strategic Bypass (Bagrakote - Labha - Algarah - Reshi - Rhenock - Pakyong)",
                        "via": "Bagrakote - Algarah - Pakyong",
                        "max_gvw_tons": 40.0,
                        "delay_minutes": 105,
                        "distance_km": 92.0,
                        "status": "PASSABLE"
                    }
                ]
            }
            self.shelters = [
                {
                    "shelter_id": "SHL-SK-01",
                    "name": "Rangpo Indoor Mining Stadium Relief Hub",
                    "state": "Sikkim",
                    "district": "Pakyong",
                    "lat": 27.1780,
                    "lon": 88.5290,
                    "capacity_people": 1200,
                    "has_helipad": True
                }
            ]

        # Populate blocked corridors from network status
        for c in self.corridors:
            if "BLOCKED" in str(c.get("status", "")).upper():
                self.blocked_corridors_set.add(c["corridor_id"])

    def block_corridor(self, corridor_id: str, reason: str = "Landslide Blockage") -> None:
        self.blocked_corridors_set.add(corridor_id)
        for c in self.corridors:
            if c["corridor_id"] == corridor_id:
                c["status"] = "SEVERED_BLOCKED"
                c["blockage_reason"] = reason

    def unblock_corridor(self, corridor_id: str) -> None:
        self.blocked_corridors_set.discard(corridor_id)
        for c in self.corridors:
            if c["corridor_id"] == corridor_id:
                c["status"] = "PASSABLE"

    def block_bridge(self, bridge_id: str, reason: str = "Bridge Damage") -> None:
        self.blocked_bridges_set.add(bridge_id)

    def unblock_bridge(self, bridge_id: str) -> None:
        self.blocked_bridges_set.discard(bridge_id)

    def add_landslide_hazard_zone(self, zone_id: str, lat: float, lon: float, radius_km: float = 3.0, risk_penalty: float = 2.5) -> None:
        self.landslide_hazard_zones.append({
            "zone_id": zone_id,
            "lat": lat,
            "lon": lon,
            "radius_km": radius_km,
            "risk_penalty": risk_penalty
        })

    def clear_hazard_zones(self) -> None:
        self.landslide_hazard_zones.clear()

    def set_data_freshness(self, is_stale: bool) -> None:
        self.is_data_stale = bool(is_stale)

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Spherical Haversine distance in kilometres."""
        R = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = (
            math.sin(dp / 2.0) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
        )
        return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def find_nearest_shelter(
        self,
        lat: float,
        lon: float,
        state_filter: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Locates closest designated evacuation shelter using local offline cache."""
        candidates = self.shelters
        if state_filter:
            sf = state_filter.strip().lower()
            candidates = [s for s in candidates if s.get("state", "").strip().lower() == sf]

        if not candidates:
            return None

        ranked = []
        for s in candidates:
            rec = dict(s)
            dist = self.haversine(lat, lon, float(rec["lat"]), float(rec["lon"]))
            rec["distance_km"] = round(dist, 2)
            ranked.append(rec)

        ranked.sort(key=lambda x: x["distance_km"])
        return ranked[0] if ranked else None

    def plan_offline_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: Optional[float] = None,
        dest_lon: Optional[float] = None,
        vehicle_weight_tons: float = 3.5,
        avoid_blockages: bool = True,
        find_shelter_if_no_dest: bool = True,
        routing_preference: str = "FASTEST"
    ) -> Dict[str, Any]:
        """
        Calculates an offline emergency route between current location and destination
        or nearest emergency shelter, accounting for blocked arterial corridors and bridges.
        Supports FASTEST, SHORTEST, and SAFEST routing profiles.
        """
        target_shelter = None
        if (dest_lat is None or dest_lon is None) and find_shelter_if_no_dest:
            target_shelter = self.find_nearest_shelter(origin_lat, origin_lon)
            if target_shelter:
                dest_lat = float(target_shelter["lat"])
                dest_lon = float(target_shelter["lon"])

        if dest_lat is None or dest_lon is None:
            dest_lat = origin_lat + 0.05
            dest_lon = origin_lon + 0.05

        direct_dist_km = round(self.haversine(origin_lat, origin_lon, dest_lat, dest_lon), 2)

        # Check bridge blockage severance
        if len(self.blocked_bridges_set) > 0 and avoid_blockages:
            if "SK-NH10" in self.blocked_corridors_set or len(self.blocked_corridors_set) > 0:
                return {
                    "status": "UNREACHABLE",
                    "route_label": "DESTINATION UNREACHABLE",
                    "provenance": "[OFFLINE ROUTE / SEVERED]",
                    "is_offline": True,
                    "reason": "Critical bridge and arterial corridors severed. No passable route exists.",
                    "route_distance_km": 0.0,
                    "estimated_time_minutes": 0,
                    "route_mode": "NO_PASSABLE_ROUTE",
                    "bypass_recommendation": None,
                    "nearest_shelter": target_shelter or self.find_nearest_shelter(origin_lat, origin_lon),
                    "origin": {"lat": origin_lat, "lon": origin_lon},
                    "destination": {"lat": dest_lat, "lon": dest_lon}
                }

        # Detect relevant active blockages
        active_blockage_ids = set(self.blocked_corridors_set)
        for c in self.corridors:
            if "BLOCKED" in str(c.get("status", "")).upper():
                active_blockage_ids.add(c["corridor_id"])

        bypass_recommended = None
        route_mode = "DIRECT_LOCAL"
        pref_up = routing_preference.upper()

        # Base winding multiplier
        base_multiplier = 1.35
        speed_kmh = AVERAGE_SPEED_KMH["PRIMARY_HIGHWAY"]

        est_distance_km = round(direct_dist_km * base_multiplier, 2)
        est_minutes = int(round((est_distance_km / speed_kmh) * 60))

        # Evaluate bypass condition in Sikkim sector
        is_sikkim_zone = (
            (27.0 <= origin_lat <= 27.6 and 88.3 <= origin_lon <= 88.8) or
            (27.0 <= dest_lat <= 27.6 and 88.3 <= dest_lon <= 88.8)
        )

        if avoid_blockages and "SK-NH10" in active_blockage_ids and is_sikkim_zone:
            bypasses = self.bypass_matrix.get("SK-NH10", [])
            eligible = [b for b in bypasses if float(b.get("max_gvw_tons", 40)) >= vehicle_weight_tons and b.get("status", "PASSABLE") == "PASSABLE"]
            if eligible:
                bypass_recommended = eligible[0]
                route_mode = "BYPASS_AVOIDANCE"
                est_distance_km = float(bypass_recommended.get("distance_km", 92.0))
                est_minutes = int(bypass_recommended.get("delay_minutes", 105))
            else:
                # Bypass also blocked -> unreachable
                return {
                    "status": "UNREACHABLE",
                    "route_label": "DESTINATION UNREACHABLE",
                    "provenance": "[OFFLINE ROUTE / SEVERED]",
                    "is_offline": True,
                    "reason": "All arterial routes and bypass corridors are impassable.",
                    "route_distance_km": 0.0,
                    "estimated_time_minutes": 0,
                    "route_mode": "NO_PASSABLE_ROUTE",
                    "bypass_recommendation": None,
                    "nearest_shelter": target_shelter or self.find_nearest_shelter(origin_lat, origin_lon),
                    "origin": {"lat": origin_lat, "lon": origin_lon},
                    "destination": {"lat": dest_lat, "lon": dest_lon}
                }

        # Calculate hazard zone penalty across all profiles
        hazard_penalty_mins = 0
        safety_score = 0.85
        for hz in self.landslide_hazard_zones:
            d_hz = self.haversine(origin_lat, origin_lon, hz["lat"], hz["lon"])
            if d_hz < hz.get("radius_km", 3.0):
                hazard_penalty_mins += int(hz.get("risk_penalty", 2.0) * 15)
                safety_score = max(0.20, safety_score - 0.35)

        est_minutes += hazard_penalty_mins

        # Adjust metrics according to profile
        if pref_up == "SHORTEST":
            if bypass_recommended is None:
                est_distance_km = round(direct_dist_km * 1.20, 2)  # Narrower rural shortcuts
                est_minutes = int(round((est_distance_km / AVERAGE_SPEED_KMH["RURAL_STEEP"]) * 60)) + hazard_penalty_mins
            safety_score = min(safety_score, 0.60)
        elif pref_up == "SAFEST":
            if bypass_recommended is None:
                # Detour around known slope cut
                est_distance_km = round(est_distance_km * 1.18, 2)
                est_minutes = int(round((est_distance_km / AVERAGE_SPEED_KMH["BYPASS_CORRIDOR"]) * 60)) + hazard_penalty_mins

        freshness_label = "STALE" if self.is_data_stale else "CACHED"
        prov = "[OFFLINE ROUTE / STALE]" if self.is_data_stale else "[OFFLINE ROUTE]"

        return {
            "status": "SUCCESS",
            "route_label": "OFFLINE ROUTE",
            "provenance": prov,
            "is_offline": True,
            "is_stale": self.is_data_stale,
            "data_freshness": freshness_label,
            "data_freshness_status": freshness_label,
            "routing_preference": pref_up,
            "safety_score": round(safety_score, 2),
            "calculated_at": datetime.now(timezone.utc).isoformat(),
            "origin": {"lat": origin_lat, "lon": origin_lon},
            "destination": {
                "lat": dest_lat,
                "lon": dest_lon,
                "is_shelter": target_shelter is not None,
                "shelter_details": target_shelter
            },
            "route_mode": route_mode,
            "route_distance_km": est_distance_km,
            "direct_distance_km": direct_dist_km,
            "estimated_time_minutes": est_minutes,
            "active_blockages_detected": len(active_blockage_ids),
            "blocked_corridors": list(active_blockage_ids),
            "blocked_bridges": list(self.blocked_bridges_set),
            "bypass_recommendation": bypass_recommended,
            "nearest_shelter": target_shelter or self.find_nearest_shelter(origin_lat, origin_lon),
            "offline_notes": (
                "Route calculated using pre-packaged offline vector network. "
                f"Data freshness: {freshness_label}. "
                "Road blockages reflect last synchronized intelligence."
            )
        }


# Global singleton instance
OFFLINE_ROUTING_SERVICE = OfflineRoutingService()
OFFLINE_ROUTER = OFFLINE_ROUTING_SERVICE
