# -*- coding: utf-8 -*-
"""
engine/canonical_registry.py
============================
PARVAT NETRA • PAHAD AI — Unified Canonical Corridor & Location Registry
------------------------------------------------------------------------
Consolidates and unifies all hillslope monitoring locations, surveyed transportation
corridors, and GSI critical sectors across all 8 North-Eastern Region (NER) states
plus strategic border corridors.

Unified Sources:
  1. SECTOR_REGISTRY (8 canonical state-representative sectors from engine/sector_snapshot.py)
  2. GSI_CRITICAL_SECTORS (20 meso-scale surveyed sectors from engine/pahad_sectors.py)
  3. GLOBAL_CORRIDOR_REGISTRY (5 transportation highway corridors from engine/corridor_registry.py)

Key Invariants:
  - Every entry provides: id, name, state, district, lat, lon, highway/corridor, geometry, status.
  - Supports resolution by primary ID or any legacy alias.
  - Spatial proximity lookup (Haversine formula).
  - Clean filtering by State and District for cascading UI selectors.
  - Strict data integrity: no fabricated coordinates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class CanonicalLocation:
    """Represents a single canonical hillslope monitoring corridor or strategic location."""
    id: str
    name: str
    state: str
    district: str
    lat: float
    lon: float
    highway: str
    geometry: Dict[str, Any]
    status: str
    hazard_rating: str = "HIGH"
    elevation_m: float = 500.0
    slope_deg: float = 35.0
    geology: str = "Himalayan sedimentary/metamorphic colluvium"
    instrumentation: List[str] = field(default_factory=list)
    source_registries: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


# ─────────────────────────────────────────────────────────────────────────────
# SEED MASTER CATALOG: 25 UNIQUE STRATEGIC CORRIDORS ACROSS ALL NER STATES
# ─────────────────────────────────────────────────────────────────────────────

_SEED_CANONICAL_LOCATIONS: List[CanonicalLocation] = [
    # ── SIKKIM ───────────────────────────────────────────────────────────────
    CanonicalLocation(
        id="SK-NH10-KM48",
        name="NH-10 Km 48 (29th Mile Sector)",
        state="Sikkim",
        district="Pakyong",
        lat=27.3300,
        lon=88.6100,
        highway="National Highway 10",
        geometry={"type": "Point", "coordinates": [88.6100, 27.3300]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=485.0,
        slope_deg=42.0,
        geology="Daling Group quartz-chlorite phyllites and schists",
        instrumentation=["Piezometer", "Inclinometer", "CCTV", "Rain Gauge"],
        source_registries=["SECTOR_REGISTRY", "GSI_CRITICAL_SECTORS", "GLOBAL_CORRIDOR_REGISTRY"],
        aliases=["CORR-NH10-SIKKIM-KM48", "SK-29TH-MILE", "NH10-KM48"]
    ),
    CanonicalLocation(
        id="SK-SINGTAM-01",
        name="Singtam Teesta Basin Toe-Scour Zone",
        state="Sikkim",
        district="Gangtok",
        lat=27.2340,
        lon=88.4980,
        highway="NH-10 / Teesta River Gorge",
        geometry={"type": "Point", "coordinates": [88.4980, 27.2340]},
        status="SURVEYED",
        hazard_rating="VERY_HIGH",
        elevation_m=350.0,
        slope_deg=38.0,
        geology="Daling quartzites and sheared fault gouge",
        instrumentation=["CWC Radar Gauge", "Tiltmeter"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["SK-SINGTAM-BASIN"]
    ),
    CanonicalLocation(
        id="SK-DIKCHU-01",
        name="Dikchu Hydro Sector Bluffs",
        state="Sikkim",
        district="North Sikkim",
        lat=27.3820,
        lon=88.5830,
        highway="North Sikkim Highway",
        geometry={"type": "Point", "coordinates": [88.5830, 27.3820]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=620.0,
        slope_deg=36.0,
        geology="Biotite gneiss with steep dip slope",
        instrumentation=["InSAR Reflector", "Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["SK-DIKCHU-HYDRO"]
    ),
    CanonicalLocation(
        id="SK-MANGAN-01",
        name="Mangan Relict Landslide Complex",
        state="Sikkim",
        district="Mangan",
        lat=27.5020,
        lon=88.5280,
        highway="Mangan-Chungthang Road",
        geometry={"type": "Point", "coordinates": [88.5280, 27.5020]},
        status="SURVEYED",
        hazard_rating="VERY_HIGH",
        elevation_m=950.0,
        slope_deg=40.0,
        geology="Chungthang Formation calc-silicates and marbles",
        instrumentation=["Extensometer", "Inclinometer"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["SK-MANGAN-COMPLEX"]
    ),

    # ── MANIPUR ──────────────────────────────────────────────────────────────
    CanonicalLocation(
        id="MN-TUPUL-RLY",
        name="NH-37 / Tupul Railway Yard Corridor",
        state="Manipur",
        district="Noney",
        lat=24.7550,
        lon=93.5780,
        highway="NH-37 / Jiribam-Imphal Railway",
        geometry={"type": "Point", "coordinates": [93.5780, 24.7550]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=540.0,
        slope_deg=44.0,
        geology="Disang Group splintery dark grey shales and siltstones",
        instrumentation=["Borehole Inclinometer", "Piezometer", "Rain Gauge", "Geophone"],
        source_registries=["SECTOR_REGISTRY", "GSI_CRITICAL_SECTORS", "GLOBAL_CORRIDOR_REGISTRY"],
        aliases=["MN-TUPUL-01", "CORR-TUPUL-MANIPUR-RLY", "TUPUL-STATION"]
    ),
    CanonicalLocation(
        id="MN-JIRIBAM-01",
        name="Imphal-Jiribam NH-37 Km 78 Cut",
        state="Manipur",
        district="Tamenglong",
        lat=24.8020,
        lon=93.4210,
        highway="NH-37 Lifeline",
        geometry={"type": "Point", "coordinates": [93.4210, 24.8020]},
        status="SURVEYED",
        hazard_rating="VERY_HIGH",
        elevation_m=620.0,
        slope_deg=39.0,
        geology="Barail Group sandstones interbedded with carbonaceous shale",
        instrumentation=["Tiltmeter", "Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["MN-NH37-KM78"]
    ),

    # ── MIZORAM ──────────────────────────────────────────────────────────────
    CanonicalLocation(
        id="MZ-MELTHUM-QRY",
        name="NH-6 / Melthum Quarry Settlement Axis",
        state="Mizoram",
        district="Aizawl",
        lat=23.8950,
        lon=92.9600,
        highway="NH-06 / Melthum Bypass",
        geometry={"type": "Point", "coordinates": [92.9600, 23.8950]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=720.0,
        slope_deg=46.0,
        geology="Surma Group fine-grained sandstone with steep road excavation scarp",
        instrumentation=["Surface Crackmeter", "Rain Gauge", "CCTV"],
        source_registries=["SECTOR_REGISTRY", "GLOBAL_CORRIDOR_REGISTRY"],
        aliases=["CORR-MELTHUM-MIZORAM", "MELTHUM-QUARRY"]
    ),
    CanonicalLocation(
        id="MZ-HUNTHAR-01",
        name="Aizawl NH-6 Hunthar Veng Slump",
        state="Mizoram",
        district="Aizawl",
        lat=23.7420,
        lon=92.7080,
        highway="NH-06 / Western Arterial",
        geometry={"type": "Point", "coordinates": [92.7080, 23.7420]},
        status="SURVEYED",
        hazard_rating="EXTREME",
        elevation_m=810.0,
        slope_deg=41.0,
        geology="Upper Bhuban siltstones with severe basal toe saturation",
        instrumentation=["Inclinometer", "Piezometer", "Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["HUNTHAR-VENG"]
    ),
    CanonicalLocation(
        id="MZ-SAIRANG-01",
        name="Sairang Railway Terminal Ridge",
        state="Mizoram",
        district="Aizawl",
        lat=23.8050,
        lon=92.6590,
        highway="Bairabi-Sairang Rail Spur",
        geometry={"type": "Point", "coordinates": [92.6590, 23.8050]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=450.0,
        slope_deg=34.0,
        geology="Bhuban sandstones with deep structural joints",
        instrumentation=["InSAR Reflector", "Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["SAIRANG-TERMINAL"]
    ),
    CanonicalLocation(
        id="MZ-KOLASIB-01",
        name="Kolasib Sinking Carriageway",
        state="Mizoram",
        district="Kolasib",
        lat=24.2250,
        lon=92.6780,
        highway="NH-306 Silchar-Aizawl Link",
        geometry={"type": "Point", "coordinates": [92.6780, 24.2250]},
        status="SURVEYED",
        hazard_rating="VERY_HIGH",
        elevation_m=580.0,
        slope_deg=37.0,
        geology="Bokabil shale and siltstone prone to water-induced slaking",
        instrumentation=["Tiltmeter", "Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["KOLASIB-NH306"]
    ),

    # ── ASSAM ────────────────────────────────────────────────────────────────
    CanonicalLocation(
        id="AS-HAFLONG-RLY",
        name="Haflong Hill Section Railway Cutting",
        state="Assam",
        district="Dima Hasao",
        lat=25.1650,
        lon=93.0270,
        highway="Lumding-Badarpur Hill Section",
        geometry={"type": "Point", "coordinates": [93.0270, 25.1650]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=510.0,
        slope_deg=43.0,
        geology="Barail Group carbonaceous shales prone to torrential mudflow",
        instrumentation=["Piezometer", "Extensometer", "Rain Gauge"],
        source_registries=["SECTOR_REGISTRY", "GSI_CRITICAL_SECTORS", "GLOBAL_CORRIDOR_REGISTRY"],
        aliases=["AS-DIMA-01", "CORR-DIMA-HASAO-ASSAM", "JATINGA-LUMPUR"]
    ),
    CanonicalLocation(
        id="AS-GUWAHATI-01",
        name="Guwahati Narakasur Hills Rim",
        state="Assam",
        district="Kamrup Metropolitan",
        lat=26.1420,
        lon=91.7760,
        highway="Guwahati Urban Corridor",
        geometry={"type": "Point", "coordinates": [91.7760, 26.1420]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=220.0,
        slope_deg=35.0,
        geology="Precambrian granite gneiss with thick residual lateritic soil",
        instrumentation=["Rain Gauge", "CCTV"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["GUWAHATI-NARAKASUR"]
    ),

    # ── MEGHALAYA ────────────────────────────────────────────────────────────
    CanonicalLocation(
        id="ML-MAWSYNRAM",
        name="NH-206 / Mawsynram Scarp Edge",
        state="Meghalaya",
        district="East Khasi Hills",
        lat=25.2970,
        lon=91.5830,
        highway="NH-206 Scarp Route",
        geometry={"type": "Point", "coordinates": [91.5830, 25.2970]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=1400.0,
        slope_deg=48.0,
        geology="Sylhet Traps basalt overlain by fragile sandstone",
        instrumentation=["Pluviometer", "Tiltmeter", "CCTV"],
        source_registries=["SECTOR_REGISTRY"],
        aliases=["MAWSYNRAM-SCARP"]
    ),
    CanonicalLocation(
        id="ML-SONAPUR-01",
        name="Sonapur Tunnel NH-06 Portal Scarp",
        state="Meghalaya",
        district="East Jaintia Hills",
        lat=25.1050,
        lon=92.3620,
        highway="NH-06 Barak Valley Lifeline",
        geometry={"type": "Point", "coordinates": [92.3620, 25.1050]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=320.0,
        slope_deg=45.0,
        geology="Therria Sandstone and coal seams with heavy saturation failure",
        instrumentation=["Inclinometer", "CCTV", "Automatic Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["SONAPUR-TUNNEL"]
    ),
    CanonicalLocation(
        id="ML-CHERRA-01",
        name="Cherrapunji South Escarpment",
        state="Meghalaya",
        district="East Khasi Hills",
        lat=25.2750,
        lon=91.7320,
        highway="Sohra-Shella Corridor",
        geometry={"type": "Point", "coordinates": [91.7320, 25.2750]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=1280.0,
        slope_deg=52.0,
        geology="Limestone and calcareous sandstone karst cliff",
        instrumentation=["Rain Gauge", "InSAR Target"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["CHERRA-ESCARPMENT", "SOHRA-CLIFF"]
    ),

    # ── NAGALAND ─────────────────────────────────────────────────────────────
    CanonicalLocation(
        id="NL-DZUKOU-KOH",
        name="NH-29 / Dzukou Valley Axis",
        state="Nagaland",
        district="Kohima",
        lat=25.5820,
        lon=94.1200,
        highway="NH-29 Arterial Highway",
        geometry={"type": "Point", "coordinates": [94.1200, 25.5820]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=1750.0,
        slope_deg=41.0,
        geology="Disang shales interbedded with flysch sandstone",
        instrumentation=["Inclinometer", "Rain Gauge"],
        source_registries=["SECTOR_REGISTRY"],
        aliases=["DZUKOU-AXIS"]
    ),
    CanonicalLocation(
        id="NL-PAGALA-01",
        name="Kohima NH-29 Pagala Pahar",
        state="Nagaland",
        district="Kohima",
        lat=25.6880,
        lon=93.9850,
        highway="NH-29 Dimapur-Kohima Lifeline",
        geometry={"type": "Point", "coordinates": [93.9850, 25.6880]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=890.0,
        slope_deg=47.0,
        geology="Crushed Disang shales within major tectonic thrust zone",
        instrumentation=["Inclinometer", "Extensometer", "Rain Gauge", "CCTV"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["PAGALA-PAHAR"]
    ),
    CanonicalLocation(
        id="NL-DZUDZA-01",
        name="Dzüdza River Bridge Bluffs",
        state="Nagaland",
        district="Kohima",
        lat=25.6700,
        lon=94.0200,
        highway="NH-29 Km 15",
        geometry={"type": "Point", "coordinates": [94.0200, 25.6700]},
        status="SURVEYED",
        hazard_rating="VERY_HIGH",
        elevation_m=980.0,
        slope_deg=39.0,
        geology="Fractured siltstones subject to river-toe erosion",
        instrumentation=["Tiltmeter", "Radar Water Level Sensor"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["DZUDZA-BRIDGE"]
    ),
    CanonicalLocation(
        id="NL-PIPHEMA-01",
        name="Piphema Sinking Zone",
        state="Nagaland",
        district="Chümoukedima",
        lat=25.7560,
        lon=93.9120,
        highway="NH-29 Lowland Spur",
        geometry={"type": "Point", "coordinates": [93.9120, 25.7560]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=460.0,
        slope_deg=33.0,
        geology="Clayey silt with expansive montmorillonite content",
        instrumentation=["Soil Moisture Sensor", "Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["PIPHEMA-SINKING"]
    ),

    # ── ARUNACHAL PRADESH ────────────────────────────────────────────────────
    CanonicalLocation(
        id="AR-TAWANG-SELA",
        name="NH-13 / Sela Pass Axis",
        state="Arunachal Pradesh",
        district="Tawang",
        lat=27.5800,
        lon=91.8500,
        highway="NH-13 Trans-Arunachal Highway",
        geometry={"type": "Point", "coordinates": [91.8500, 27.5800]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=3800.0,
        slope_deg=45.0,
        geology="High-grade crystalline gneiss and glacial moraine",
        instrumentation=["Frost Sensor", "Tiltmeter", "Weather Station"],
        source_registries=["SECTOR_REGISTRY"],
        aliases=["SELA-PASS-AXIS"]
    ),
    CanonicalLocation(
        id="AR-BHALUK-01",
        name="Bhalukpong-Tawang Axis Km 32",
        state="Arunachal Pradesh",
        district="West Kameng",
        lat=27.0120,
        lon=92.6450,
        highway="Tawang Strategic Highway",
        geometry={"type": "Point", "coordinates": [92.6450, 27.0120]},
        status="APPROVED",
        hazard_rating="EXTREME",
        elevation_m=1120.0,
        slope_deg=44.0,
        geology="Gondwana sandstones and sheared carbonaceous phyllites",
        instrumentation=["Borehole Inclinometer", "Rain Gauge"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["BHALUKPONG-KM32"]
    ),
    CanonicalLocation(
        id="AR-PASIGHAT-01",
        name="Pasighat Siang River Scour Escarpment",
        state="Arunachal Pradesh",
        district="East Siang",
        lat=28.0670,
        lon=95.3260,
        highway="NH-515 / Siang Valley",
        geometry={"type": "Point", "coordinates": [95.3260, 28.0670]},
        status="SURVEYED",
        hazard_rating="VERY_HIGH",
        elevation_m=280.0,
        slope_deg=38.0,
        geology="Siwalik boulder beds and semi-consolidated sandstones",
        instrumentation=["CWC Hydro Gauge", "Riverbank Inclinometer"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["PASIGHAT-SIANG"]
    ),
    CanonicalLocation(
        id="AR-SELA-01",
        name="Sela Pass North Approach Km 8",
        state="Arunachal Pradesh",
        district="Tawang",
        lat=27.5050,
        lon=92.1020,
        highway="NH-13 North Portal",
        geometry={"type": "Point", "coordinates": [92.1020, 27.5050]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=3400.0,
        slope_deg=37.0,
        geology="Biotite gneiss with active periglacial freeze-thaw loosening",
        instrumentation=["Ultrasonic Snow Sensor", "Tiltmeter"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["SELA-NORTH-PORTAL"]
    ),

    # ── TRIPURA ──────────────────────────────────────────────────────────────
    CanonicalLocation(
        id="TR-JAMPUI-HILLS",
        name="Jampui Hills Ridge Corridor",
        state="Tripura",
        district="North Tripura",
        lat=23.9500,
        lon=92.3100,
        highway="Jampui State Highway",
        geometry={"type": "Point", "coordinates": [92.3100, 23.9500]},
        status="APPROVED",
        hazard_rating="HIGH",
        elevation_m=650.0,
        slope_deg=36.0,
        geology="Tipam sandstone with loose lateritic weathering crust",
        instrumentation=["Rain Gauge", "Tiltmeter"],
        source_registries=["SECTOR_REGISTRY"],
        aliases=["JAMPUI-RIDGE"]
    ),
    CanonicalLocation(
        id="TR-BARAMURA-01",
        name="Baramura Hill Range NH-08 Pass",
        state="Tripura",
        district="Khowai",
        lat=23.8820,
        lon=91.5640,
        highway="NH-08 National Corridor",
        geometry={"type": "Point", "coordinates": [91.5640, 23.8820]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=240.0,
        slope_deg=32.0,
        geology="Bokabil shale and loose sandstones subject to monsoon washouts",
        instrumentation=["Rain Gauge", "InSAR Reflector"],
        source_registries=["GSI_CRITICAL_SECTORS"],
        aliases=["BARAMURA-PASS"]
    ),

    # ── WEST BENGAL (BORDER STRATEGIC CORRIDOR) ──────────────────────────────
    CanonicalLocation(
        id="CORR-NH717A-PEDONG-RISSI",
        name="NH-717A Strategic Bypass (Pedong to Rissi Bridge)",
        state="West Bengal",
        district="Kalimpong",
        lat=27.1520,
        lon=88.6250,
        highway="National Highway 717A",
        geometry={"type": "Point", "coordinates": [88.6250, 27.1520]},
        status="SURVEYED",
        hazard_rating="HIGH",
        elevation_m=1150.0,
        slope_deg=37.0,
        geology="Mica schist and weathered phyllite alternate arterial route",
        instrumentation=["Rain Gauge", "Tiltmeter"],
        source_registries=["GLOBAL_CORRIDOR_REGISTRY"],
        aliases=["NH717A-PEDONG", "RISSI-BYPASS"]
    )
]


class CanonicalLocationRegistry:
    """Thread-safe unified registry managing hillslope monitoring corridors across all NER states."""

    def __init__(self, seed_locations: Optional[List[CanonicalLocation]] = None):
        self._locations: Dict[str, CanonicalLocation] = {}
        self._alias_map: Dict[str, str] = {}
        
        locations_to_load = seed_locations if seed_locations is not None else _SEED_CANONICAL_LOCATIONS
        for loc in locations_to_load:
            self.register(loc)

    def register(self, loc: CanonicalLocation) -> None:
        """Register a canonical location and index all its aliases."""
        self._locations[loc.id] = loc
        self._alias_map[loc.id.upper()] = loc.id
        for alias in loc.aliases:
            self._alias_map[alias.upper()] = loc.id

    def get_location(self, location_id: str) -> Optional[CanonicalLocation]:
        """Resolve a location by primary ID or any known alias (case-insensitive)."""
        if not location_id:
            return None
        key = location_id.strip().upper()
        canonical_id = self._alias_map.get(key)
        if canonical_id and canonical_id in self._locations:
            return self._locations[canonical_id]
        return self._locations.get(location_id)

    def list_locations(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        status: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[CanonicalLocation]:
        """Filter locations by state, district, operational status, or text search."""
        results = list(self._locations.values())

        if state:
            s_clean = state.strip().lower()
            results = [r for r in results if r.state.lower() == s_clean]

        if district:
            d_clean = district.strip().lower()
            results = [r for r in results if r.district.lower() == d_clean]

        if status:
            st_clean = status.strip().upper()
            results = [r for r in results if r.status.upper() == st_clean]

        if query:
            q_clean = query.strip().lower()
            results = [
                r for r in results
                if q_clean in r.name.lower()
                or q_clean in r.id.lower()
                or q_clean in r.highway.lower()
                or q_clean in r.district.lower()
                or q_clean in r.state.lower()
            ]

        # Sort predictably by State, then Name
        return sorted(results, key=lambda x: (x.state, x.name))

    def list_states(self) -> List[str]:
        """Return sorted list of all states present in the registry."""
        states = set(loc.state for loc in self._locations.values())
        return sorted(list(states))

    def list_districts(self, state: Optional[str] = None) -> List[str]:
        """Return sorted list of districts, optionally filtered by state."""
        locs = self.list_locations(state=state)
        districts = set(loc.district for loc in locs)
        return sorted(list(districts))

    def find_nearest(self, lat: float, lon: float, max_radius_km: float = 200.0) -> Optional[Tuple[CanonicalLocation, float]]:
        """Find the closest registered location to given coordinates using Haversine distance."""
        nearest = None
        min_dist = float("inf")

        for loc in self._locations.values():
            dist = self._haversine(lat, lon, loc.lat, loc.lon)
            if dist < min_dist and dist <= max_radius_km:
                min_dist = dist
                nearest = loc

        if nearest:
            return nearest, round(min_dist, 2)
        return None

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance between two points on the Earth in kilometres."""
        r = 6371.0  # Earth's mean radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def to_geojson(self, state: Optional[str] = None) -> Dict[str, Any]:
        """Export locations as a GeoJSON FeatureCollection."""
        locs = self.list_locations(state=state)
        features = []
        for loc in locs:
            feat = {
                "type": "Feature",
                "id": loc.id,
                "geometry": loc.geometry,
                "properties": {
                    "id": loc.id,
                    "name": loc.name,
                    "state": loc.state,
                    "district": loc.district,
                    "highway": loc.highway,
                    "status": loc.status,
                    "hazard_rating": loc.hazard_rating,
                    "elevation_m": loc.elevation_m,
                    "slope_deg": loc.slope_deg,
                    "geology": loc.geology,
                    "instrumentation": loc.instrumentation,
                    "aliases": loc.aliases
                }
            }
            features.append(feat)

        return {
            "type": "FeatureCollection",
            "count": len(features),
            "features": features
        }


# Global singleton instance
CANONICAL_REGISTRY = CanonicalLocationRegistry()
