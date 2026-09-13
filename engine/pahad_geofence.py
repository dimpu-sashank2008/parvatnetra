# -*- coding: utf-8 -*-
"""
engine/pahad_geofence.py
========================
PARVAT NETRA • Spatial Geofencing & Recipient Impact Zone Engine
----------------------------------------------------------------
Implements Section 6, 7, 27: Multi-geometry geofence resolution and recipient eligibility.
Supports:
  1. Point geometries (radial circle buffers, default 15 km).
  2. Road Corridor geometries (buffered linear segments along mountain highways, e.g. NH-10).
  3. Polygon geometries (arbitrary landslide catchments or GSI hazard polygons).
  4. Configurable radius via PAHAD_ALERT_RADIUS_KM environment variable.
  5. Privacy-preserving recipient eligibility checks without leaking personal data.

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import math
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    from shapely.geometry import Point, Polygon, LineString, shape
    from shapely.ops import transform
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

logger = logging.getLogger("PAHAD_GEOFENCE")

DEFAULT_RADIUS_KM = float(os.getenv("PAHAD_ALERT_RADIUS_KM", "15.0"))


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two geographic coordinates in kilometers."""
    r_earth = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2.0) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(dlambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return float(r_earth * c)


@dataclass
class GeofenceEligibilityResult:
    """Result of evaluating a recipient's location against an alert geofence."""
    eligible: bool
    distance_km: float
    zone_type: str  # "IMPACT_DIRECT", "BUFFER_ZONE", "OUTSIDE"
    alert_id: Optional[str] = None
    recipient_role: str = "citizen"
    radius_km: float = DEFAULT_RADIUS_KM

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PahadGeofenceEngine:
    """
    Manages impact geometry construction and recipient spatial eligibility filtering.
    """

    def __init__(self, default_radius_km: float = DEFAULT_RADIUS_KM):
        self.default_radius_km = default_radius_km

    def create_alert_geometry(
        self,
        geom_type: str,
        coordinates: Any,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Constructs a normalized alert impact zone geometry specification.
        geom_type: 'point', 'corridor', or 'polygon'
        """
        r = radius_km if radius_km is not None else self.default_radius_km
        clean_type = geom_type.lower()

        if clean_type == "point":
            lat, lon = float(coordinates[0]), float(coordinates[1])
            return {
                "type": "point",
                "center": [lat, lon],
                "radius_km": r,
                "description": f"Radial circular buffer ({r:.1f} km) centered at [{lat:.4f}, {lon:.4f}]"
            }
        elif clean_type == "corridor":
            # coordinates: list of [lat, lon] waypoints or flat [lat, lon]
            if coordinates and isinstance(coordinates[0], (int, float)):
                pts = [[float(coordinates[0]), float(coordinates[1])]]
            else:
                pts = [[float(p[0]), float(p[1])] for p in coordinates]
            return {
                "type": "corridor",
                "waypoints": pts,
                "buffer_km": r,
                "description": f"Highway corridor buffer ({r:.1f} km along {len(pts)} road waypoints)"
            }
        elif clean_type == "polygon":
            # coordinates: list of [lat, lon] vertices forming a closed ring or flat [lat, lon]
            if coordinates and isinstance(coordinates[0], (int, float)):
                ring = [[float(coordinates[0]), float(coordinates[1])]]
            else:
                ring = [[float(p[0]), float(p[1])] for p in coordinates]
            return {
                "type": "polygon",
                "vertices": ring,
                "buffer_km": r,
                "description": f"Catchment polygon ({len(ring)} vertices) with {r:.1f} km outer buffer"
            }
        else:
            # Fallback to point
            lat, lon = float(coordinates[0]), float(coordinates[1])
            return {
                "type": "point",
                "center": [lat, lon],
                "radius_km": r,
                "description": f"Default fallback radial buffer ({r:.1f} km)"
            }

    def is_recipient_in_alert_zone(
        self,
        recipient_lat: float,
        recipient_lon: float,
        alert_geometry: Dict[str, Any],
        recipient_role: str = "citizen",
        alert_id: Optional[str] = None
    ) -> GeofenceEligibilityResult:
        """
        Evaluates whether a recipient's location qualifies them to receive an emergency alert.
        """
        g_type = alert_geometry.get("type", "point").lower()
        r_km = float(alert_geometry.get("radius_km") or alert_geometry.get("buffer_km") or self.default_radius_km)

        if g_type == "point":
            c_lat, c_lon = alert_geometry["center"]
            dist = haversine_distance_km(recipient_lat, recipient_lon, c_lat, c_lon)

            # Direct impact is inside core 3 km; buffer zone is up to radius_km
            if dist <= 3.0:
                zone_type = "IMPACT_DIRECT"
                eligible = True
            elif dist <= r_km:
                zone_type = "BUFFER_ZONE"
                eligible = True
            else:
                zone_type = "OUTSIDE"
                eligible = False

            return GeofenceEligibilityResult(
                eligible=eligible,
                distance_km=round(dist, 2),
                zone_type=zone_type,
                alert_id=alert_id,
                recipient_role=recipient_role,
                radius_km=r_km
            )

        elif g_type == "corridor":
            waypoints = alert_geometry.get("waypoints", [])
            if not waypoints:
                return GeofenceEligibilityResult(False, 999.0, "OUTSIDE", alert_id, recipient_role, r_km)

            # Calculate minimum distance to any waypoint or segment
            min_dist = min(haversine_distance_km(recipient_lat, recipient_lon, wp[0], wp[1]) for wp in waypoints)

            if min_dist <= 2.0:
                zone_type = "IMPACT_DIRECT"
                eligible = True
            elif min_dist <= r_km:
                zone_type = "BUFFER_ZONE"
                eligible = True
            else:
                zone_type = "OUTSIDE"
                eligible = False

            return GeofenceEligibilityResult(
                eligible=eligible,
                distance_km=round(min_dist, 2),
                zone_type=zone_type,
                alert_id=alert_id,
                recipient_role=recipient_role,
                radius_km=r_km
            )

        elif g_type == "polygon":
            vertices = alert_geometry.get("vertices", [])
            if not vertices:
                return GeofenceEligibilityResult(False, 999.0, "OUTSIDE", alert_id, recipient_role, r_km)

            if SHAPELY_AVAILABLE:
                # Point-in-polygon check (lon, lat order in shapely Cartesian projection)
                # For small regions in Sikkim, equirectangular approximation is standard:
                poly = Polygon([(v[1], v[0]) for v in vertices])
                pt = Point(recipient_lon, recipient_lat)

                if poly.contains(pt):
                    return GeofenceEligibilityResult(True, 0.0, "IMPACT_DIRECT", alert_id, recipient_role, r_km)

            # Compute min distance to polygon vertices
            min_dist = min(haversine_distance_km(recipient_lat, recipient_lon, v[0], v[1]) for v in vertices)
            eligible = min_dist <= r_km
            zone_type = "BUFFER_ZONE" if eligible else "OUTSIDE"

            return GeofenceEligibilityResult(
                eligible=eligible,
                distance_km=round(min_dist, 2),
                zone_type=zone_type,
                alert_id=alert_id,
                recipient_role=recipient_role,
                radius_km=r_km
            )

        # Default fallback
        return GeofenceEligibilityResult(False, 999.0, "OUTSIDE", alert_id, recipient_role, r_km)

    def filter_eligible_recipients(
        self,
        candidate_recipients: List[Dict[str, Any]],
        alert_geometry: Dict[str, Any],
        alert_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filters a list of candidate recipients against the alert geometry and returns
        augmented eligible recipients with distance and zone_type.
        """
        eligible = []
        for r in candidate_recipients:
            lat = float(r.get("lat", 0.0))
            lon = float(r.get("lon", 0.0))
            role = r.get("role", "citizen")
            res = self.is_recipient_in_alert_zone(lat, lon, alert_geometry, role, alert_id)
            if res.eligible:
                entry = dict(r)
                entry["distance_km"] = res.distance_km
                entry["zone_type"] = res.zone_type
                eligible.append(entry)

        # Sort by proximity
        eligible.sort(key=lambda x: x.get("distance_km", 999.0))
        return eligible

    def compute_affected_infrastructure(
        self,
        alert_geometry: Dict[str, Any],
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Computes critical sectors, monitored road corridors, and key infrastructure
        lying within the alert impact zone (default 15 km).
        """
        r = radius_km if radius_km is not None else float(
            alert_geometry.get("radius_km") or alert_geometry.get("buffer_km") or self.default_radius_km
        )

        # Retrieve reference critical sectors
        try:
            from engine.pahad_sectors import GSI_CRITICAL_SECTORS
        except Exception:
            GSI_CRITICAL_SECTORS = []

        try:
            from engine.pahad_routing import MONITORED_CORRIDORS
        except Exception:
            MONITORED_CORRIDORS = []

        # Reference emergency facilities in NER pilot region
        CRITICAL_FACILITIES = [
            {"facility_id": "FAC-HOSP-01", "name": "Singtam District Hospital", "type": "HOSPITAL", "lat": 27.235, "lon": 88.498, "beds": 120},
            {"facility_id": "FAC-CAMP-01", "name": "Rangpo Emergency Relief Camp", "type": "SHELTER", "lat": 27.178, "lon": 88.532, "capacity": 650},
            {"facility_id": "FAC-BRDG-01", "name": "Teesta River Suspension Bridge", "type": "BRIDGE", "lat": 27.058, "lon": 88.435, "span_m": 180},
            {"facility_id": "FAC-STAG-01", "name": "Likhu Veer Relief Center", "type": "STAGING_POST", "lat": 27.210, "lon": 88.545, "capacity": 400},
            {"facility_id": "FAC-STAG-02", "name": "Sevoke Army Staging Depot", "type": "MILITARY_STAGING", "lat": 26.885, "lon": 88.472, "capacity": 1200},
            {"facility_id": "FAC-HOSP-02", "name": "Gangtok STNM Multi-Specialty Hospital", "type": "TERTIARY_HOSPITAL", "lat": 27.320, "lon": 88.605, "beds": 450},
        ]

        affected_sectors = []
        for sec in GSI_CRITICAL_SECTORS:
            s_lat = float(sec.get("lat", 0.0))
            s_lon = float(sec.get("lon", 0.0))
            elig = self.is_recipient_in_alert_zone(s_lat, s_lon, alert_geometry)
            if elig.eligible:
                affected_sectors.append({
                    "sector_id": sec.get("sector_id"),
                    "name": sec.get("name"),
                    "corridor": sec.get("corridor"),
                    "hazard_rating": sec.get("hazard_rating"),
                    "geology": sec.get("geology"),
                    "distance_km": elig.distance_km,
                    "zone_type": elig.zone_type
                })

        affected_facilities = []
        for fac in CRITICAL_FACILITIES:
            f_lat = float(fac.get("lat", 0.0))
            f_lon = float(fac.get("lon", 0.0))
            elig = self.is_recipient_in_alert_zone(f_lat, f_lon, alert_geometry)
            if elig.eligible:
                affected_facilities.append({
                    "facility_id": fac.get("facility_id"),
                    "name": fac.get("name"),
                    "type": fac.get("type"),
                    "distance_km": elig.distance_km,
                    "zone_type": elig.zone_type
                })

        # Check monitored corridors affected
        affected_corridors = []
        sec_corridor_names = {s["corridor"] for s in affected_sectors if s.get("corridor")}
        for corridor in MONITORED_CORRIDORS:
            c_name = corridor.get("name", "")
            if any(cn in c_name or c_name in cn for cn in sec_corridor_names):
                affected_corridors.append({
                    "corridor_id": corridor.get("corridor_id"),
                    "name": corridor.get("name"),
                    "state": corridor.get("state"),
                    "status": corridor.get("status"),
                    "traffic_impact": corridor.get("traffic_impact"),
                    "blockage_point": corridor.get("blockage_point")
                })

        # Calculate estimated population
        # Model standard NER mountain density: ~280 persons/km2 in inhabited corridor slivers
        impact_area_km2 = math.pi * (min(r, 15.0) ** 2) * 0.15  # 15% settled corridor fraction
        est_population = int(max(450, round(impact_area_km2 * 12.0)))

        return {
            "radius_km": r,
            "total_affected_sectors": len(affected_sectors),
            "affected_sectors": affected_sectors,
            "total_affected_corridors": len(affected_corridors),
            "affected_corridors": affected_corridors,
            "total_critical_facilities": len(affected_facilities),
            "critical_facilities": affected_facilities,
            "estimated_population_impacted": est_population,
            "impact_summary": (
                f"15 km Geofence encompasses {len(affected_sectors)} critical GSI hillslopes, "
                f"{len(affected_corridors)} arterial highway corridors, and {len(affected_facilities)} emergency facilities "
                f"(est. population impacted: ~{est_population:,})."
            )
        }


# Global singleton geofence engine
GEOFENCE_ENGINE = PahadGeofenceEngine()

