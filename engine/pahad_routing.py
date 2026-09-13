"""
engine/pahad_routing.py
=======================
PAHAD Phase 6 — Road Connectivity, Dynamic Bypass Routing & Resilient Logistics
--------------------------------------------------------------------------------
Manages monitored arterial highway corridors across the 8 NER states, computes
gross vehicle weight (GVW) tiered emergency bypass routes around severed
landslide sectors, and provides proximity search for geocoded emergency shelters.

Key Operational Formulations:
  - Route Eligibility: vehicle_weight_tons <= max_gvw_tons
  - Route Sorting: sorted ascending by transit delay_minutes
  - Proximity Calculation: Spherical Haversine distance in kilometres

Author : PARVAT NETRA / PAHAD Engineering Team
Data   : [SIMULATED] BRO & NHIDCL Highway Logistics Matrix v6
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# =============================================================================
# MONITORED ARTERIAL HIGHWAY CORRIDORS
# =============================================================================

MONITORED_CORRIDORS: List[Dict[str, Any]] = [
    {
        "corridor_id": "SK-NH10",
        "name": "NH-10 (Siliguri – Gangtok Lifeline)",
        "state": "Sikkim",
        "status": "SEVERED_BLOCKED",
        "blockage_point": "Km 48 (29th Mile Sector)",
        "blockage_cause": "High precipitation pore pressure and Teesta River toe scour",
        "affected_length_km": 4.2,
        "traffic_impact": "CRITICAL_LIFELINE_ISOLATION",
        "jurisdiction": "BRO Project Swastik / Sikkim PWD",
    },
    {
        "corridor_id": "SK-NSH",
        "name": "North Sikkim Highway (Mangan – Chungthang)",
        "state": "Sikkim",
        "status": "SEVERED_BLOCKED",
        "blockage_point": "Dikchu-Sankalang Sector",
        "blockage_cause": "Debris flow across multiple hairpin turns",
        "affected_length_km": 6.8,
        "traffic_impact": "DISTRICT_HQ_ISOLATION",
        "jurisdiction": "BRO Project Swastik",
    },
    {
        "corridor_id": "NL-NH29",
        "name": "NH-29 (Dimapur – Kohima – Mao Gate)",
        "state": "Nagaland",
        "status": "SEVERED_BLOCKED",
        "blockage_point": "Pagala Pahar / Dzüdza River Bridge Bluffs",
        "blockage_cause": "Rotational slip in crushed Disang shales",
        "affected_length_km": 3.5,
        "traffic_impact": "STATE_CAPITAL_FREIGHT_DISRUPTION",
        "jurisdiction": "BRO Project Sewak / Nagaland PWD",
    },
    {
        "corridor_id": "ML-NH06",
        "name": "NH-06 (Shillong – Silchar via Sonapur Tunnel)",
        "state": "Meghalaya",
        "status": "SEVERED_BLOCKED",
        "blockage_point": "Sonapur Tunnel Portal Approach",
        "blockage_cause": "Heavy mudflow blocking tunnel entrance portal",
        "affected_length_km": 1.8,
        "traffic_impact": "BARAK_VALLEY_SUPPLY_SEVERED",
        "jurisdiction": "NHIDCL / Meghalaya PWD",
    },
    {
        "corridor_id": "MZ-NH06",
        "name": "NH-06 (Silchar – Aizawl via Hunthar)",
        "state": "Mizoram",
        "status": "SEVERED_BLOCKED",
        "blockage_point": "Hunthar Veng Slump Zone",
        "blockage_cause": "Deep translational creep in Surma siltstone",
        "affected_length_km": 2.1,
        "traffic_impact": "AIZAWL_WESTERN_ARTERIAL_CLOSURE",
        "jurisdiction": "BRO Project Pushpak / Mizoram PWD",
    },
    {
        "corridor_id": "AR-NH13",
        "name": "NH-13 (Trans-Arunachal Highway / Balipara – Tawang Axis)",
        "state": "Arunachal Pradesh",
        "status": "SEVERED_BLOCKED",
        "blockage_point": "Bhalukpong Km 32 & Sela Pass Approaches",
        "blockage_cause": "Rockfall and scree avalanches",
        "affected_length_km": 5.4,
        "traffic_impact": "STRATEGIC_DEFENCE_LINE_DISRUPTED",
        "jurisdiction": "BRO Project Vartak",
    },
    {
        "corridor_id": "MN-NH37",
        "name": "NH-37 (Imphal – Jiribam via Tupul Corridor)",
        "state": "Manipur",
        "status": "SEVERED_BLOCKED",
        "blockage_point": "Noney Tupul Sector Km 78",
        "blockage_cause": "Slope toe failure along railway cutting",
        "affected_length_km": 3.0,
        "traffic_impact": "INTERSTATE_ESSENTIALS_SUPPLY_HALTED",
        "jurisdiction": "BRO Project Sewak / Manipur PWD",
    },
]

# =============================================================================
# BYPASS ROUTE MATRIX WITH GROSS VEHICLE WEIGHT (GVW) RESTRICTIONS
# =============================================================================

BYPASS_MATRIX: Dict[str, List[Dict[str, Any]]] = {
    "SK-NH10": [
        {
            "route_id": "BYP-SK-01",
            "name": "Lava - Gorubathan Axis",
            "via": "Damdim - Gorubathan - Lava - Algarah - Rangpo",
            "max_gvw_tons": 45.0,
            "surface_type": "All-Weather Double-Lane Asphalt",
            "status": "PASSABLE",
            "delay_minutes": 140,
            "distance_km": 112.0,
            "allowed_vehicle_types": ["Heavy Freight Multi-Axle Trucks", "Buses", "Emergency Vehicles", "Light Vehicles"],
            "patrol_unit": "BRO Project Swastik Heavy Traffic Escort",
        },
        {
            "route_id": "BYP-SK-02",
            "name": "Mungpoo - Jorebunglow Route",
            "via": "Rambhi - Mungpoo - 3rd Mile - Jorebunglow - Teesta Valley",
            "max_gvw_tons": 18.5,
            "surface_type": "Single-Lane Intermediate Paved",
            "status": "RESTRICTED",
            "delay_minutes": 95,
            "distance_km": 84.0,
            "allowed_vehicle_types": ["Medium Duty Trucks (<= 18.5T)", "Mini Buses", "Emergency Ambulances", "Light Vehicles"],
            "patrol_unit": "Kalimpong Traffic Police Station",
        },
        {
            "route_id": "BYP-SK-03",
            "name": "Teesta Bazar - Peshok",
            "via": "Teesta Bazar - Peshok Tea Garden - Jorebunglow",
            "max_gvw_tons": 3.5,
            "surface_type": "Steep Hairpin Mountain Track",
            "status": "CAUTION",
            "delay_minutes": 60,
            "distance_km": 62.0,
            "allowed_vehicle_types": ["Emergency Medical Services (EMS)", "Light Civilian Cars (< 3.5T)"],
            "patrol_unit": "Darjeeling Hill Disaster Cell",
        },
    ],
    "SK-NSH": [
        {
            "route_id": "BYP-NSH-01",
            "name": "Dikchu - Sankalang Bailey Bridge Link",
            "via": "Dikchu - Lingdong - Sankalang",
            "max_gvw_tons": 12.0,
            "surface_type": "Single-Lane Bailey Bridge Corridor",
            "status": "RESTRICTED",
            "delay_minutes": 180,
            "distance_km": 78.0,
            "allowed_vehicle_types": ["Light/Medium Supply Trucks (<= 12T)", "Emergency Convoys"],
            "patrol_unit": "BRO 86 RCC / ITBP",
        },
    ],
    "NL-NH29": [
        {
            "route_id": "BYP-NL-01",
            "name": "Niuland - Kohima Heavy Bypass Axis",
            "via": "Niuland - Ghaspani - Zhadima - Kohima North",
            "max_gvw_tons": 35.0,
            "surface_type": "Double-Lane Upgraded Asphalt",
            "status": "PASSABLE",
            "delay_minutes": 110,
            "distance_km": 96.0,
            "allowed_vehicle_types": ["Heavy Freight Trucks (<= 35T)", "Buses", "Emergency Vehicles"],
            "patrol_unit": "BRO Project Sewak Patrol Unit",
        },
        {
            "route_id": "BYP-NL-02",
            "name": "Zhadima - Peducha Link Route",
            "via": "Peducha - Tsiesema - Zhadima",
            "max_gvw_tons": 15.0,
            "surface_type": "Single-Lane Macadam",
            "status": "RESTRICTED",
            "delay_minutes": 75,
            "distance_km": 68.0,
            "allowed_vehicle_types": ["Medium Trucks (<= 15T)", "Light Motor Vehicles"],
            "patrol_unit": "Kohima District Police",
        },
    ],
    "ML-NH06": [
        {
            "route_id": "BYP-ML-01",
            "name": "Umkiang - Rymbai Heavy Haul Bypass",
            "via": "Rymbai - Sutnga - Saipung - Umkiang",
            "max_gvw_tons": 42.0,
            "surface_type": "Heavy Mineral Transport Corridor",
            "status": "PASSABLE",
            "delay_minutes": 130,
            "distance_km": 118.0,
            "allowed_vehicle_types": ["Multi-Axle Petroleum & Food Tankers", "Heavy Freight", "Buses"],
            "patrol_unit": "Meghalaya Police Highway Patrol",
        },
        {
            "route_id": "BYP-ML-02",
            "name": "Khliehriat - Sutnga Rural Arterial",
            "via": "Khliehriat Bypass - Sutnga Ridge",
            "max_gvw_tons": 16.0,
            "surface_type": "Intermediate Single Lane",
            "status": "RESTRICTED",
            "delay_minutes": 85,
            "distance_km": 74.0,
            "allowed_vehicle_types": ["Medium Freight (<= 16T)", "Light Passenger Vehicles"],
            "patrol_unit": "East Jaintia Hills SDRF Post",
        },
    ],
    "MZ-NH06": [
        {
            "route_id": "BYP-MZ-01",
            "name": "Bhairabi - Sairang Freight Route",
            "via": "Bhairabi - Kolasib - Sairang",
            "max_gvw_tons": 40.0,
            "surface_type": "Railway Allied Heavy Corridor",
            "status": "PASSABLE",
            "delay_minutes": 120,
            "distance_km": 104.0,
            "allowed_vehicle_types": ["Heavy Freight Goods Trucks", "Supply Convoys"],
            "patrol_unit": "BRO Project Pushpak Command",
        },
        {
            "route_id": "BYP-MZ-02",
            "name": "Durtlang - Zemabawk Inner Link",
            "via": "Durtlang North - Zemabawk Arterial",
            "max_gvw_tons": 7.5,
            "surface_type": "Steep Urban Link",
            "status": "RESTRICTED",
            "delay_minutes": 50,
            "distance_km": 42.0,
            "allowed_vehicle_types": ["Light Ambulances", "Passenger Cars (< 7.5T)"],
            "patrol_unit": "Aizawl City Police Control",
        },
    ],
    "AR-NH13": [
        {
            "route_id": "BYP-AR-01",
            "name": "OKSRT Axis (Orang - Kalaktang - Shergaon - Rupa - Tenga)",
            "via": "Orang - Rowta - Kalaktang - Rupa - Tenga Valley",
            "max_gvw_tons": 45.0,
            "surface_type": "National Strategic Double-Lane Highway",
            "status": "PASSABLE",
            "delay_minutes": 150,
            "distance_km": 135.0,
            "allowed_vehicle_types": ["Heavy Military & Freight Convoys", "Buses", "Emergency Vehicles"],
            "patrol_unit": "BRO Project Vartak Heavy Regt",
        },
    ],
    "MN-NH37": [
        {
            "route_id": "BYP-MN-01",
            "name": "Old Cachar Road Axis",
            "via": "Jiribam - Khongsang - Noney Old Axis",
            "max_gvw_tons": 22.0,
            "surface_type": "Upgraded Single Lane Bituminous",
            "status": "RESTRICTED",
            "delay_minutes": 160,
            "distance_km": 128.0,
            "allowed_vehicle_types": ["Medium Trucks (<= 22T)", "Emergency Convoys"],
            "patrol_unit": "Manipur Highway Security Force",
        },
    ],
}

BYPASS_ROUTES = BYPASS_MATRIX

# Normalize lookup aliases
CORRIDOR_ALIASES: Dict[str, str] = {
    "NH-10": "SK-NH10",
    "NH10": "SK-NH10",
    "SK-NH-10": "SK-NH10",
    "NORTH SIKKIM HIGHWAY": "SK-NSH",
    "NSH": "SK-NSH",
    "NH-29": "NL-NH29",
    "NH29": "NL-NH29",
    "NH-06-MEGHALAYA": "ML-NH06",
    "ML-NH6": "ML-NH06",
    "NH-06-MIZORAM": "MZ-NH06",
    "MZ-NH6": "MZ-NH06",
    "NH-13": "AR-NH13",
    "NH13": "AR-NH13",
    "NH-37": "MN-NH37",
    "NH37": "MN-NH37",
}

# =============================================================================
# EMERGENCY SHELTERS REGISTRY
# =============================================================================

EMERGENCY_SHELTERS: List[Dict[str, Any]] = [
    {
        "shelter_id": "SHL-SK-01",
        "name": "Rangpo Indoor Mining Stadium Relief Hub",
        "state": "Sikkim",
        "district": "Pakyong",
        "lat": 27.1780,
        "lon": 88.5290,
        "capacity_people": 1200,
        "medical_readiness": "LEVEL_2_TRAUMA_STATION",
        "has_helipad": True,
        "satellite_phone": "+91-3592-240112",
        "contact_officer": "SDRF Sub-Divisional Officer, Rangpo",
    },
    {
        "shelter_id": "SHL-SK-02",
        "name": "Melli Ground Central Evacuation Camp",
        "state": "Sikkim",
        "district": "Namchi",
        "lat": 27.0980,
        "lon": 88.4610,
        "capacity_people": 850,
        "medical_readiness": "FIRST_AID_TRIAGE",
        "has_helipad": False,
        "satellite_phone": "+91-3592-248901",
        "contact_officer": "District Relief Commissioner",
    },
    {
        "shelter_id": "SHL-SK-03",
        "name": "Singtam Community Hall & Emergency Base",
        "state": "Sikkim",
        "district": "Gangtok",
        "lat": 27.2340,
        "lon": 88.4980,
        "capacity_people": 650,
        "medical_readiness": "MOBILE_MEDICAL_UNIT",
        "has_helipad": False,
        "satellite_phone": "+91-3592-234551",
        "contact_officer": "Singtam Municipal Officer",
    },
    {
        "shelter_id": "SHL-SK-04",
        "name": "Gangtok Paljor Stadium Emergency Headquarters",
        "state": "Sikkim",
        "district": "Gangtok",
        "lat": 27.3320,
        "lon": 88.6140,
        "capacity_people": 3500,
        "medical_readiness": "FULL_SURGICAL_HOSPITAL",
        "has_helipad": True,
        "satellite_phone": "+91-3592-202244",
        "contact_officer": "State Disaster Response Commissioner",
    },
    {
        "shelter_id": "SHL-MZ-01",
        "name": "Aizawl Hawla Indoor Stadium Relief Base",
        "state": "Mizoram",
        "district": "Aizawl",
        "lat": 23.7380,
        "lon": 92.7150,
        "capacity_people": 2000,
        "medical_readiness": "DISTRICT_TRAUMA_CENTRE",
        "has_helipad": True,
        "satellite_phone": "+91-389-2342111",
        "contact_officer": "Mizoram Disaster Management Authority",
    },
    {
        "shelter_id": "SHL-NL-01",
        "name": "Kohima Local Ground Emergency Relief Staging Base",
        "state": "Nagaland",
        "district": "Kohima",
        "lat": 25.6690,
        "lon": 94.1080,
        "capacity_people": 2500,
        "medical_readiness": "ARMY_BASE_HOSPITAL",
        "has_helipad": True,
        "satellite_phone": "+91-3862-248102",
        "contact_officer": "Nagaland State Emergency Operations Centre",
    },
    {
        "shelter_id": "SHL-ML-01",
        "name": "Shillong JN Stadium Evacuation Centre",
        "state": "Meghalaya",
        "district": "East Khasi Hills",
        "lat": 25.5780,
        "lon": 91.8920,
        "capacity_people": 3000,
        "medical_readiness": "NEIGRIHMS_TRIAGE",
        "has_helipad": True,
        "satellite_phone": "+91-364-2224010",
        "contact_officer": "Meghalaya SDRF Battalion Commander",
    },
    {
        "shelter_id": "SHL-MN-01",
        "name": "Noney Tupul Railway Relief Complex",
        "state": "Manipur",
        "district": "Noney",
        "lat": 24.8150,
        "lon": 93.6320,
        "capacity_people": 1500,
        "medical_readiness": "MILITARY_FIELD_HOSPITAL",
        "has_helipad": True,
        "satellite_phone": "+91-385-2451101",
        "contact_officer": "Assam Rifles / SDRF Field Officer",
    },
    {
        "shelter_id": "SHL-AR-01",
        "name": "Tawang High-Altitude Evacuation Compound",
        "state": "Arunachal Pradesh",
        "district": "Tawang",
        "lat": 27.5860,
        "lon": 91.8650,
        "capacity_people": 1000,
        "medical_readiness": "ARMY_CIVIL_JOINT_AID",
        "has_helipad": True,
        "satellite_phone": "+91-3794-222220",
        "contact_officer": "District Disaster Management Officer",
    },
    {
        "shelter_id": "SHL-AS-01",
        "name": "Silchar District Sports Stadium Hub",
        "state": "Assam",
        "district": "Cachar",
        "lat": 24.8250,
        "lon": 92.7950,
        "capacity_people": 4000,
        "medical_readiness": "REGIONAL_DISASTER_HUB",
        "has_helipad": True,
        "satellite_phone": "+91-3842-230015",
        "contact_officer": "Cachar District Emergency Officer",
    },
]


class RoadConnectivityRoutingEngine:
    """
    Logistics and bypass routing engine for Himalayan highway corridors.
    Enforces gross vehicle weight restrictions and spherical proximity shelter lookup.
    """

    def __init__(
        self,
        corridors: Optional[List[Dict[str, Any]]] = None,
        bypass_matrix: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        shelters: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.corridors = corridors or MONITORED_CORRIDORS
        self.bypass_matrix = bypass_matrix or BYPASS_MATRIX
        self.shelters = shelters or EMERGENCY_SHELTERS

    def _normalize_corridor_id(self, corridor_id: str) -> str:
        """Resolve aliases or lowercase IDs to standard corridor code."""
        clean = (corridor_id or "").strip().upper()
        if clean in CORRIDOR_ALIASES:
            return CORRIDOR_ALIASES[clean]
        for c in self.corridors:
            if c["corridor_id"].upper() == clean:
                return c["corridor_id"]
        return clean

    def get_corridor_status(self, corridor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List monitored corridors, optionally filtering by specific corridor ID.
        """
        if not corridor_id:
            return list(self.corridors)

        norm_id = self._normalize_corridor_id(corridor_id)
        return [
            c for c in self.corridors
            if c["corridor_id"].upper() == norm_id or norm_id in c["name"].upper()
        ]

    def calculate_bypass(
        self,
        severed_corridor_id: str,
        vehicle_weight_tons: float,
    ) -> Dict[str, Any]:
        """
        Evaluate eligible bypass corridors given severed route and vehicle GVW.

        Parameters
        ----------
        severed_corridor_id : str
            Identifier of blocked highway (e.g. 'SK-NH10', 'NH-10').
        vehicle_weight_tons : float
            Gross Vehicle Weight in metric tonnes.

        Returns
        -------
        dict
            Contains eligible_routes (sorted by delay_minutes ascending),
            ineligible_routes (rejected due to weight capacity), and recommendation.
        """
        norm_id = self._normalize_corridor_id(severed_corridor_id)
        weight = max(0.1, float(vehicle_weight_tons))

        routes = self.bypass_matrix.get(norm_id, [])
        if not routes:
            # Fallback if corridor not in matrix
            return {
                "status": "NO_BYPASS_FOUND",
                "severed_corridor_id": norm_id,
                "vehicle_weight_tons": weight,
                "total_bypass_options": 0,
                "eligible_routes": [],
                "ineligible_routes": [],
                "best_route": None,
                "recommendation": "No registered alternate bypass. Advise vehicle staging at nearest logistics depot.",
            }

        eligible: List[Dict[str, Any]] = []
        ineligible: List[Dict[str, Any]] = []

        for r in routes:
            rec = dict(r)
            max_gvw = float(rec.get("max_gvw_tons", 40.0))
            if weight <= max_gvw:
                rec["weight_clearance"] = "PERMITTED"
                rec["margin_tons"] = round(max_gvw - weight, 2)
                eligible.append(rec)
            else:
                rec["weight_clearance"] = "EXCEEDED_RESTRICTION"
                rec["overweight_tons"] = round(weight - max_gvw, 2)
                rec["rejection_reason"] = f"Vehicle weight {weight}T exceeds route maximum GVW limit {max_gvw}T"
                ineligible.append(rec)

        # Sort eligible routes by lowest delay first
        eligible.sort(key=lambda x: x.get("delay_minutes", 999))

        best = eligible[0] if eligible else None
        if best:
            recommendation = (
                f"Proceed via {best['name']} ({best['via']}). "
                f"Max GVW: {best['max_gvw_tons']}T. Est. Additional Transit Delay: +{best['delay_minutes']} mins."
            )
        else:
            recommendation = (
                f"All bypass routes for {norm_id} have GVW limits below {weight}T. "
                "Hold freight at highway staging checkpoint until civil engineering assessment."
            )

        return {
            "status": "SUCCESS",
            "severed_corridor_id": norm_id,
            "vehicle_weight_tons": weight,
            "total_bypass_options": len(routes),
            "eligible_count": len(eligible),
            "eligible_routes": eligible,
            "ineligible_count": len(ineligible),
            "ineligible_routes": ineligible,
            "best_route": best,
            "recommendation": recommendation,
            "provenance": "[SIMULATED] BRO & NHIDCL Bypass Logistics Matrix v6",
        }

    def find_nearest_shelters(
        self,
        lat: float,
        lon: float,
        limit: int = 3,
        state_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query closest emergency evacuation shelters using spherical Haversine distance.
        """
        target_lat = float(lat)
        target_lon = float(lon)
        lim = max(1, int(limit))

        candidates = self.shelters
        if state_filter:
            sf = state_filter.strip().lower()
            candidates = [s for s in candidates if s.get("state", "").strip().lower() == sf]

        results: List[Dict[str, Any]] = []
        for s in candidates:
            rec = dict(s)
            dist = self._haversine(target_lat, target_lon, float(rec["lat"]), float(rec["lon"]))
            rec["distance_km"] = round(dist, 2)
            results.append(rec)

        results.sort(key=lambda x: x["distance_km"])
        return results[:lim]

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Spherical Haversine formula in kilometres."""
        R = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = (
            math.sin(dp / 2.0) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
        )
        return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
