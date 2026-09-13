"""
engine/pahad_sectors.py
=======================
PAHAD Phase 4 — GSI Meso-Scale Critical Sector Registry
-------------------------------------------------------
Structured repository of Geological Survey of India (GSI) 1:10,000
and 1:5,000 critical hillslope monitoring corridors across all 8
North-Eastern Region (NER) states.

States Covered:
  1. Sikkim
  2. Mizoram
  3. Nagaland
  4. Arunachal Pradesh
  5. Manipur
  6. Meghalaya
  7. Assam
  8. Tripura

Methods:
  - list_sectors(state_filter: str = None) -> list[dict]
  - get_sector(sector_id: str) -> dict | None
  - query_nearby(lat: float, lon: float, radius_km: float = 25.0) -> list[dict]

Author : PARVAT NETRA / PAHAD Engineering Team
Data   : [HISTORICAL] GSI National Landslide Susceptibility Mapping (NLSM)
"""

from __future__ import annotations

import math
from typing import List, Dict, Any, Optional

GSI_CRITICAL_SECTORS: List[Dict[str, Any]] = [
    # ---------------- SIKKIM ----------------
    {
        "sector_id": "SK-NH10-KM48",
        "name": "NH-10 Km 48 (29th Mile Sector)",
        "state": "Sikkim",
        "district": "Kalimpong-Sikkim Border",
        "corridor": "National Highway 10",
        "lat": 27.3300,
        "lon": 88.6100,
        "elevation_m": 485,
        "geology": "Daling Group quartz-chlorite phyllites and schists",
        "hazard_rating": "EXTREME",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["Piezometer", "Inclinometer", "CCTV", "Rain Gauge"],
    },
    {
        "sector_id": "SK-SINGTAM-01",
        "name": "Singtam Teesta Basin Toe-Scour Zone",
        "state": "Sikkim",
        "district": "Gangtok",
        "corridor": "NH-10 / Teesta River Gorge",
        "lat": 27.2340,
        "lon": 88.4980,
        "elevation_m": 350,
        "geology": "Daling quartzites and sheared fault gouge",
        "hazard_rating": "VERY_HIGH",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["CWC Radar Gauge", "Tiltmeter"],
    },
    {
        "sector_id": "SK-DIKCHU-01",
        "name": "Dikchu Hydro Sector Bluffs",
        "state": "Sikkim",
        "district": "North Sikkim",
        "corridor": "North Sikkim Highway",
        "lat": 27.3820,
        "lon": 88.5830,
        "elevation_m": 620,
        "geology": "Biotite gneiss with steep dip slope",
        "hazard_rating": "HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["InSAR Reflector", "Rain Gauge"],
    },
    {
        "sector_id": "SK-MANGAN-01",
        "name": "Mangan Relict Landslide Complex",
        "state": "Sikkim",
        "district": "Mangan",
        "corridor": "Mangan-Chungthang Road",
        "lat": 27.5020,
        "lon": 88.5280,
        "elevation_m": 950,
        "geology": "Chungthang Formation calc-silicates and marbles",
        "hazard_rating": "VERY_HIGH",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["Extensometer", "Inclinometer"],
    },

    # ---------------- MIZORAM ----------------
    {
        "sector_id": "MZ-HUNTHAR-01",
        "name": "Aizawl NH-6 Hunthar Veng Slump",
        "state": "Mizoram",
        "district": "Aizawl",
        "corridor": "NH-06 / Western Arterial",
        "lat": 23.7420,
        "lon": 92.7080,
        "elevation_m": 880,
        "geology": "Surma Group interbedded siltstone and fissile clay",
        "hazard_rating": "EXTREME",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["Borehole Piezometer", "GNSS Station"],
    },
    {
        "sector_id": "MZ-SAIRANG-01",
        "name": "Sairang Railway Terminal Ridge",
        "state": "Mizoram",
        "district": "Aizawl",
        "corridor": "Bairabi-Sairang Rail Spur",
        "lat": 23.8050,
        "lon": 92.6590,
        "elevation_m": 420,
        "geology": "Tipam sandstone with thick residual overburden",
        "hazard_rating": "HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Corner Reflectors", "Tension Crack Gauges"],
    },
    {
        "sector_id": "MZ-KOLASIB-01",
        "name": "Kolasib Sinking Carriageway",
        "state": "Mizoram",
        "district": "Kolasib",
        "corridor": "NH-306 Silchar-Aizawl Link",
        "lat": 24.2250,
        "lon": 92.6780,
        "elevation_m": 590,
        "geology": "Upper Bhuban sandstone and siltstone",
        "hazard_rating": "VERY_HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Rain Gauge", "Tiltmeter"],
    },

    # ---------------- NAGALAND ----------------
    {
        "sector_id": "NL-PAGALA-01",
        "name": "Kohima NH-29 Pagala Pahar",
        "state": "Nagaland",
        "district": "Kohima",
        "corridor": "NH-29 Dimapur-Kohima Lifeline",
        "lat": 25.6880,
        "lon": 93.9850,
        "elevation_m": 1240,
        "geology": "Disang Group intensely crushed splintery shale",
        "hazard_rating": "EXTREME",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["InSAR Corner Reflectors", "Inclinometer", "CCTV"],
    },
    {
        "sector_id": "NL-DZUDZA-01",
        "name": "Dzüdza River Bridge Bluffs",
        "state": "Nagaland",
        "district": "Kohima",
        "corridor": "NH-29 Km 15",
        "lat": 25.6700,
        "lon": 94.0200,
        "elevation_m": 1100,
        "geology": "Barail massive sandstone overlying weak Disang shales",
        "hazard_rating": "VERY_HIGH",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["Tiltmeter", "Crack Aperture Sensors"],
    },
    {
        "sector_id": "NL-PIPHEMA-01",
        "name": "Piphema Sinking Zone",
        "state": "Nagaland",
        "district": "Chümoukedima",
        "corridor": "NH-29",
        "lat": 25.7560,
        "lon": 93.9120,
        "elevation_m": 680,
        "geology": "Disang shale colluvium with high clay fraction",
        "hazard_rating": "HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Rain Gauge", "Pore Pressure Transducer"],
    },

    # ---------------- ARUNACHAL PRADESH ----------------
    {
        "sector_id": "AR-BHALUK-01",
        "name": "Bhalukpong-Tawang Axis Km 32",
        "state": "Arunachal Pradesh",
        "district": "West Kameng",
        "corridor": "Tawang Strategic Highway",
        "lat": 27.0120,
        "lon": 92.6450,
        "elevation_m": 840,
        "geology": "Siwalik sandstones and Main Boundary Thrust (MBT) shear",
        "hazard_rating": "EXTREME",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["BRO Geo-Sensors", "Automated Weather Station"],
    },
    {
        "sector_id": "AR-PASIGHAT-01",
        "name": "Pasighat Siang River Scour Escarpment",
        "state": "Arunachal Pradesh",
        "district": "East Siang",
        "corridor": "NH-515 / Siang Valley",
        "lat": 28.0670,
        "lon": 95.3260,
        "elevation_m": 155,
        "geology": "Unconsolidated river terraces and boulder gravels",
        "hazard_rating": "VERY_HIGH",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["Hydrometric Radar", "Drone Survey Targets"],
    },
    {
        "sector_id": "AR-SELA-01",
        "name": "Sela Pass North Approach Km 8",
        "state": "Arunachal Pradesh",
        "district": "Tawang",
        "corridor": "NH-13",
        "lat": 27.5050,
        "lon": 92.1020,
        "elevation_m": 3950,
        "geology": "Permafrost-degraded granitic gneiss and moraine scree",
        "hazard_rating": "HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Temperature Sensors", "GNSS Rover"],
    },

    # ---------------- MANIPUR ----------------
    {
        "sector_id": "MN-TUPUL-01",
        "name": "Noney Tupul Railway Corridor",
        "state": "Manipur",
        "district": "Noney",
        "corridor": "Jiribam-Imphal Railway",
        "lat": 24.8180,
        "lon": 93.6350,
        "elevation_m": 540,
        "geology": "Disang flysch formation sheared claystone and siltstone",
        "hazard_rating": "EXTREME",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["InSAR In-situ Station", "Piezometers", "Tiltmeters"],
    },
    {
        "sector_id": "MN-JIRIBAM-01",
        "name": "Imphal-Jiribam NH-37 Km 78",
        "state": "Manipur",
        "district": "Tamenglong",
        "corridor": "NH-37 Lifeline",
        "lat": 24.8020,
        "lon": 93.4210,
        "elevation_m": 610,
        "geology": "Barail Formation layered shale and sandstone",
        "hazard_rating": "VERY_HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Automated Rain Gauge", "Crackmeter"],
    },

    # ---------------- MEGHALAYA ----------------
    {
        "sector_id": "ML-SONAPUR-01",
        "name": "Sonapur Tunnel NH-06",
        "state": "Meghalaya",
        "district": "East Jaintia Hills",
        "corridor": "NH-06 Barak Valley Lifeline",
        "lat": 25.1050,
        "lon": 92.3620,
        "elevation_m": 310,
        "geology": "Barail sandstone with interbedded coal and shale seams",
        "hazard_rating": "EXTREME",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["CCTV Camera", "InSAR Reflector", "Water Level Radar"],
    },
    {
        "sector_id": "ML-CHERRA-01",
        "name": "Cherrapunji South Escarpment",
        "state": "Meghalaya",
        "district": "East Khasi Hills",
        "corridor": "Sohra-Shella Corridor",
        "lat": 25.2750,
        "lon": 91.7320,
        "elevation_m": 1280,
        "geology": "Karstified Sylhet limestone and Therria sandstone",
        "hazard_rating": "HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Pluviometer", "Seismic Micro-tremor"],
    },

    # ---------------- ASSAM ----------------
    {
        "sector_id": "AS-DIMA-01",
        "name": "Dima Hasao Hill Railway Corridor Km 42",
        "state": "Assam",
        "district": "Dima Hasao",
        "corridor": "Lumding-Badarpur Hill Section",
        "lat": 25.1780,
        "lon": 93.0230,
        "elevation_m": 480,
        "geology": "Surma Group unconsolidated argillaceous sediments",
        "hazard_rating": "EXTREME",
        "monitoring_tier": "TIER_1_REALTIME_IOT",
        "instrumentation": ["Track Inclinometer", "Borehole Piezometer"],
    },
    {
        "sector_id": "AS-GUWAHATI-01",
        "name": "Guwahati Narakasur Hills",
        "state": "Assam",
        "district": "Kamrup Metropolitan",
        "corridor": "Guwahati Urban Rim",
        "lat": 26.1420,
        "lon": 91.7760,
        "elevation_m": 190,
        "geology": "Precambrian granite gneiss with deeply weathered saprolite",
        "hazard_rating": "HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Urban Rain Gauge", "Tension Wire Sensor"],
    },

    # ---------------- TRIPURA ----------------
    {
        "sector_id": "TR-BARAMURA-01",
        "name": "Baramura Hill Range NH-08",
        "state": "Tripura",
        "district": "Khowai",
        "corridor": "NH-08 National Corridor",
        "lat": 23.8820,
        "lon": 91.5640,
        "elevation_m": 260,
        "geology": "Bhuban Formation folded anticlinal shale-sandstone",
        "hazard_rating": "HIGH",
        "monitoring_tier": "TIER_2_INSAR_PERIODIC",
        "instrumentation": ["Rain Gauge", "Tiltmeter"],
    },
]


class CriticalSectorRegistry:
    """
    GSI Meso-scale Critical Landslide Corridor Registry for the 8 NER States.
    Provides query filtering and Haversine proximity searches.
    """

    def __init__(self, sectors: Optional[List[Dict[str, Any]]] = None) -> None:
        self._sectors = sectors or GSI_CRITICAL_SECTORS

    def list_sectors(self, state_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all sectors, optionally filtering by state (case-insensitive).
        """
        if not state_filter:
            return list(self._sectors)

        filt = state_filter.strip().lower()
        return [
            s for s in self._sectors
            if s.get("state", "").strip().lower() == filt
        ]

    def get_sector(self, sector_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve single sector by ID (e.g., 'SK-NH10-KM48').
        """
        sec_id_norm = sector_id.strip().upper()
        for s in self._sectors:
            if s.get("sector_id", "").upper() == sec_id_norm:
                return dict(s)
        return None

    def query_nearby(
        self,
        lat: float,
        lon: float,
        radius_km: float = 25.0,
    ) -> List[Dict[str, Any]]:
        """
        Query sectors within radius_km using the Haversine spherical formula.
        Returns list sorted ascending by distance_km.
        """
        target_lat, target_lon = float(lat), float(lon)
        matches: List[Dict[str, Any]] = []

        for s in self._sectors:
            s_lat = float(s["lat"])
            s_lon = float(s["lon"])
            dist = self._haversine_distance(target_lat, target_lon, s_lat, s_lon)
            if dist <= radius_km:
                record = dict(s)
                record["distance_km"] = round(dist, 2)
                matches.append(record)

        matches.sort(key=lambda x: x["distance_km"])
        return matches

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine spherical distance in kilometres."""
        R = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = (
            math.sin(dp / 2.0) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
        )
        return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
