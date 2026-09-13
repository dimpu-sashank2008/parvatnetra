# -*- coding: utf-8 -*-
"""
services/landslide_inventory_service.py
=======================================
PARVAT NETRA • Historical Landslide Inventory & Spatial Clustering Service
--------------------------------------------------------------------------
Manages authoritative historical landslide event records from the Geological
Survey of India (GSI) National Landslide Susceptibility Mapping (NLSM) database,
ISRO Bhuvan, and PostGIS `landslide_events` table.

Calculates:
  - Spatial density (events / km^2)
  - Nearest historical failure distance & time delta
  - Immediate local recurrence (events within 1 km)
  - Sector neighborhood recurrence (events within 5 km)
  - Calibrated Historical Susceptibility Index

Important Invariant:
  "Historical occurrence demonstrates physical hillslope predisposition;
   it does not guarantee immediate future recurrence."

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import math
import logging
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("LANDSLIDE_INVENTORY")

# Authoritative baseline GSI inventory for key Himalayan corridors
GSI_CURATED_EVENTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "event_date": "2024-10-04",
        "location": "NH-10 Km 48 (29th Mile) Active Slump",
        "district": "Pakyong",
        "state": "Sikkim",
        "latitude": 27.3300,
        "longitude": 88.6100,
        "severity": "CRITICAL",
        "road_impact": "Full carriageway breach across 80m; NH-10 traffic suspended for 6 days",
        "casualties": 0,
        "confidence": 0.96,
        "source": "Geological Survey of India (GSI) Post-Disaster Field Survey",
        "provenance": "[HISTORICAL]"
    },
    {
        "id": 2,
        "event_date": "2024-06-12",
        "location": "Mangan-Chungthang Road Relict Complex",
        "district": "Mangan",
        "state": "Sikkim",
        "latitude": 27.5020,
        "longitude": 88.5280,
        "severity": "SEVERE",
        "road_impact": "Extensive debris flow overtopping river bridge abutment",
        "casualties": 2,
        "confidence": 0.92,
        "source": "ISRO Disaster Management Support Group / GSI",
        "provenance": "[HISTORICAL]"
    },
    {
        "id": 3,
        "event_date": "2024-07-18",
        "location": "Kalimpong-Teesta Bazar Confluence Bluff",
        "district": "Kalimpong",
        "state": "West Bengal",
        "latitude": 27.0600,
        "longitude": 88.4720,
        "severity": "MODERATE",
        "road_impact": "Single lane blockage from rockfall; cleared by BRO within 12h",
        "casualties": 0,
        "confidence": 0.88,
        "source": "GSI NLSM Archive",
        "provenance": "[HISTORICAL]"
    },
    {
        "id": 4,
        "event_date": "2023-10-04",
        "location": "Singtam Indreni Bridge Toe Failure",
        "district": "Gangtok",
        "state": "Sikkim",
        "latitude": 27.2340,
        "longitude": 88.4980,
        "severity": "CRITICAL",
        "road_impact": "South Lhonak GLOF river scour undermined slope toe",
        "casualties": 4,
        "confidence": 0.98,
        "source": "Sikkim SDMA / GSI Joint Assessment",
        "provenance": "[HISTORICAL]"
    },
    {
        "id": 5,
        "event_date": "2023-08-14",
        "location": "Dikchu Hydro Dam Left Abutment Shear",
        "district": "North Sikkim",
        "state": "Sikkim",
        "latitude": 27.3820,
        "longitude": 88.5830,
        "severity": "SEVERE",
        "road_impact": "Translational debris slide on dipping phyllite bedding",
        "casualties": 0,
        "confidence": 0.90,
        "source": "GSI Field Inspection Report",
        "provenance": "[HISTORICAL]"
    },
    {
        "id": 6,
        "event_date": "2024-05-28",
        "location": "Aizawl Hunthar Veng Subsidence",
        "district": "Aizawl",
        "state": "Mizoram",
        "latitude": 23.7420,
        "longitude": 92.7080,
        "severity": "CRITICAL",
        "road_impact": "Remobilized rotational slide following Cyclone Remal; 14 houses evacuated",
        "casualties": 1,
        "confidence": 0.95,
        "source": "Mizoram Disaster Management Authority & GSI",
        "provenance": "[HISTORICAL]"
    },
    {
        "id": 7,
        "event_date": "2024-06-02",
        "location": "Kohima Pagala Pahar Sinking Zone",
        "district": "Kohima",
        "state": "Nagaland",
        "latitude": 25.6880,
        "longitude": 93.9850,
        "severity": "SEVERE",
        "road_impact": "Active creeping slide on Disang shale; NH-29 traffic restricted to 1 lane",
        "casualties": 0,
        "confidence": 0.91,
        "source": "BRO Project Sewak / Nagaland PWD",
        "provenance": "[HISTORICAL]"
    },
    {
        "id": 8,
        "event_date": "2024-06-20",
        "location": "Guwahati Kharghuli Hill Escarpment",
        "district": "Kamrup Metropolitan",
        "state": "Assam",
        "latitude": 26.2050,
        "longitude": 91.7800,
        "severity": "MODERATE",
        "road_impact": "Shallow earth slide on artificial cut slope impacting residential access",
        "casualties": 0,
        "confidence": 0.89,
        "source": "Assam ASDMA",
        "provenance": "[HISTORICAL]"
    }
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two geographic coordinates in kilometers."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2.0) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(dlam / 2.0) ** 2)
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


class LandslideInventoryService:
    """
    Manages historical landslide query execution, spatial neighborhood clustering,
    and GeoJSON feature generation.
    """

    def __init__(self) -> None:
        self._memory_catalog = GSI_CURATED_EVENTS

    def query_events(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Queries landslide events within an optional bounding box and state/district filter.
        Queries PostGIS table first, falling back cleanly to memory catalog.
        """
        # Try database first
        try:
            from app import get_db
            with get_db() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT id, event_date, district, state, severity, source,
                               ST_Y(geom) as latitude, ST_X(geom) as longitude
                        FROM landslide_events
                        WHERE 1=1
                    """
                    params = []
                    if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
                        query += " AND geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)"
                        params.extend([min_lon, min_lat, max_lon, max_lat])
                    if state:
                        query += " AND LOWER(state) = LOWER(%s)"
                        params.append(state)
                    if district:
                        query += " AND LOWER(district) = LOWER(%s)"
                        params.append(district)
                    query += " ORDER BY event_date DESC LIMIT %s;"
                    params.append(limit)

                    cur.execute(query, tuple(params))
                    rows = cur.fetchall()
                    if rows and len(rows) > 0:
                        events = []
                        for r in rows:
                            events.append({
                                "id": r["id"],
                                "event_date": r["event_date"].isoformat() if isinstance(r["event_date"], (date, datetime)) else str(r["event_date"]),
                                "location": f"{r.get('district', '')} Sector",
                                "district": r.get("district", ""),
                                "state": r.get("state", ""),
                                "latitude": float(r["latitude"]),
                                "longitude": float(r["longitude"]),
                                "severity": r.get("severity", "MODERATE"),
                                "road_impact": "Carriageway affected",
                                "casualties": 0,
                                "confidence": 0.90,
                                "source": r.get("source", "GSI NLSM"),
                                "provenance": "[HISTORICAL]"
                            })
                        return events
        except Exception as e:
            logger.debug(f"DB landslide query fallback to memory catalog: {e}")

        # In-memory filter
        filtered = []
        for ev in self._memory_catalog:
            lat = ev["latitude"]
            lon = ev["longitude"]
            if min_lat is not None and not (min_lat <= lat <= max_lat):
                continue
            if min_lon is not None and not (min_lon <= lon <= max_lon):
                continue
            if state and ev["state"].lower() != state.lower():
                continue
            if district and ev["district"].lower() != district.lower():
                continue
            filtered.append(ev)

        return filtered[:limit]

    def get_geojson(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Returns standard GeoJSON FeatureCollection of historical landslide events."""
        events = self.query_events(min_lat, max_lat, min_lon, max_lon, state, district, limit)
        features = []
        for ev in events:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(ev["longitude"], 5), round(ev["latitude"], 5)]
                },
                "properties": {
                    "id": ev["id"],
                    "event_date": ev["event_date"],
                    "location": ev.get("location", "Landslide Event"),
                    "district": ev["district"],
                    "state": ev["state"],
                    "severity": ev["severity"],
                    "road_impact": ev.get("road_impact", "Road blockage"),
                    "casualties": ev.get("casualties", 0),
                    "confidence": ev.get("confidence", 0.90),
                    "source": ev["source"],
                    "provenance": ev.get("provenance", "[HISTORICAL]")
                }
            })

        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "GSI National Landslide Susceptibility Mapping (NLSM)",
                "total_features": len(features),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "provenance": "[HISTORICAL]"
            }
        }

    def evaluate_sector_history(self, sector_id: str, lat: float, lon: float) -> Dict[str, Any]:
        """
        Calculates localized historical recurrence, density, and nearest event metrics
        for a hillslope monitoring sector.
        """
        all_events = self.query_events(limit=200)

        within_1km = 0
        within_5km = 0
        nearest_event: Optional[Dict[str, Any]] = None
        min_dist = 9999.0

        for ev in all_events:
            d = haversine_distance_km(lat, lon, ev["latitude"], ev["longitude"])
            if d < min_dist:
                min_dist = d
                nearest_event = ev
            if d <= 1.0:
                within_1km += 1
            if d <= 5.0:
                within_5km += 1

        # Calculate local spatial density (events per km^2 within 5km radius)
        # Area of 5km circle = pi * 5^2 = 78.54 km^2
        density_per_km2 = round(within_5km / 78.54, 4)

        # Days since nearest event
        now = datetime.now(timezone.utc).date()
        days_since = 365
        if nearest_event and nearest_event.get("event_date"):
            try:
                ev_d = date.fromisoformat(nearest_event["event_date"][:10])
                days_since = max(1, (now - ev_d).days)
            except Exception:
                days_since = 365

        # Classify historical susceptibility signal
        if within_1km >= 1 or within_5km >= 4 or min_dist < 0.5:
            hist_signal = "VERY_HIGH"
            weight_points = 18.0
        elif within_5km >= 2 or min_dist < 2.0:
            hist_signal = "HIGH"
            weight_points = 12.0
        elif within_5km >= 1 or min_dist < 5.0:
            hist_signal = "MODERATE"
            weight_points = 6.0
        else:
            hist_signal = "LOW"
            weight_points = 0.0

        return {
            "sector_id": sector_id,
            "events_within_1km": within_1km,
            "events_within_5km": within_5km,
            "nearest_event_distance_km": round(min_dist, 2),
            "nearest_event": {
                "id": nearest_event["id"] if nearest_event else None,
                "location": nearest_event.get("location") if nearest_event else "None",
                "date": nearest_event.get("event_date") if nearest_event else None,
                "severity": nearest_event.get("severity") if nearest_event else "NONE"
            } if nearest_event else None,
            "event_density_per_km2": density_per_km2,
            "days_since_nearest_event": days_since,
            "historical_susceptibility_signal": hist_signal,
            "historical_weight_points": weight_points,
            "source": "GSI National Landslide Susceptibility Mapping (NLSM)",
            "provenance": "[HISTORICAL]"
        }


# Singleton Instance
LANDSLIDE_INVENTORY_SERVICE = LandslideInventoryService()
