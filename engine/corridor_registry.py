# -*- coding: utf-8 -*-
"""
engine/corridor_registry.py
===========================
PARVAT NETRA • PAHAD AI — Himalayan Transportation Corridor Registry
---------------------------------------------------------------------
Authoritative registry of critical mountain highway, railway, and settlement
corridors monitored for hillslope failure, debris flow, and structural compromise.

Lifecycle Statuses:
  - CANDIDATE           : Initial risk assessment identification
  - SURVEYED            : On-site geotechnical and LiDAR/topographic survey completed
  - APPROVED            : Competent authority sanction for sensor deployment
  - DEPLOYMENT_PENDING  : Sensor hardware allocated, awaiting physical installation
  - DEPLOYED            : Instrumentation anchored and connected to edge concentrators
  - VALIDATED           : End-to-end corridor telemetry and early warning verified
"""

from __future__ import annotations

import os
import json
import sqlite3
import logging
import threading
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("CORRIDOR_REGISTRY")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Status Constants
STATUS_CANDIDATE = "CANDIDATE"
STATUS_SURVEYED = "SURVEYED"
STATUS_APPROVED = "APPROVED"
STATUS_DEPLOYMENT_PENDING = "DEPLOYMENT_PENDING"
STATUS_DEPLOYED = "DEPLOYED"
STATUS_VALIDATED = "VALIDATED"

VALID_CORRIDOR_STATUSES = {
    STATUS_CANDIDATE,
    STATUS_SURVEYED,
    STATUS_APPROVED,
    STATUS_DEPLOYMENT_PENDING,
    STATUS_DEPLOYED,
    STATUS_VALIDATED
}

# Strict Status Transition Graph
ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    STATUS_CANDIDATE: [STATUS_SURVEYED, STATUS_CANDIDATE],
    STATUS_SURVEYED: [STATUS_APPROVED, STATUS_CANDIDATE],
    STATUS_APPROVED: [STATUS_DEPLOYMENT_PENDING, STATUS_SURVEYED],
    STATUS_DEPLOYMENT_PENDING: [STATUS_DEPLOYED, STATUS_APPROVED],
    STATUS_DEPLOYED: [STATUS_VALIDATED, STATUS_DEPLOYMENT_PENDING],
    STATUS_VALIDATED: [STATUS_DEPLOYED]
}


@dataclass
class CorridorDefinition:
    corridor_id: str
    name: str
    state: str
    district: str
    road: str
    kilometre_marker: str
    geometry: Dict[str, Any]
    elevation: float
    slope: float
    risk: str
    sensor_sites: List[Dict[str, Any]] = field(default_factory=list)
    gateway_sites: List[Dict[str, Any]] = field(default_factory=list)
    weather_sources: List[str] = field(default_factory=list)
    evacuation_routes: List[Dict[str, Any]] = field(default_factory=list)
    status: str = STATUS_CANDIDATE
    last_survey_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Seed Himalayan Transportation Corridors
SEED_CORRIDORS: List[CorridorDefinition] = [
    CorridorDefinition(
        corridor_id="CORR-NH10-SIKKIM-KM48",
        name="NH-10 Teesta Gorge Corridor (Km 48 Pakyong)",
        state="Sikkim",
        district="Pakyong",
        road="NH-10",
        kilometre_marker="Km 48.200",
        geometry={
            "type": "LineString",
            "coordinates": [
                [88.5821, 27.2410],
                [88.5954, 27.2485],
                [88.6100, 27.3300],
                [88.6180, 27.3390]
            ]
        },
        elevation=680.0,
        slope=42.5,
        risk="CRITICAL",
        sensor_sites=[
            {
                "site_id": "SITE-NH10-PIEZ-01",
                "name": "Km 48 Escarpment Toe Borehole",
                "sensor_type": "piezometer",
                "latitude": 27.3300,
                "longitude": 88.6100,
                "target_depth_m": 18.5,
                "target_device_id": "SN-PIEZ-NH10-01"
            },
            {
                "site_id": "SITE-NH10-TILT-01",
                "name": "Km 48 Retaining Wall Crest",
                "sensor_type": "tilt",
                "latitude": 27.3305,
                "longitude": 88.6102,
                "target_depth_m": 0.0,
                "target_device_id": "SN-TILT-NH10-01"
            },
            {
                "site_id": "SITE-NH10-RAIN-01",
                "name": "Km 48 BRO Staging Yard Met Mast",
                "sensor_type": "rain_gauge",
                "latitude": 27.3292,
                "longitude": 88.6091,
                "target_depth_m": 2.0,
                "target_device_id": "SN-RAIN-NH10-01"
            }
        ],
        gateway_sites=[
            {
                "gateway_id": "GW-NH10-SINGTAM-01",
                "name": "Singtam Ridge Concentrator Mast",
                "latitude": 27.3320,
                "longitude": 88.6145,
                "elevation_m": 790.0,
                "mast_height_m": 12.0,
                "backhaul": "4G_LTE_FALLBACK_SATELLITE"
            }
        ],
        weather_sources=["IMD_RANGPO", "IMD_GANGTOK_AWS", "OPEN_METEO"],
        evacuation_routes=[
            {
                "route_id": "EVAC-NH10-ALT-NH717A",
                "name": "NH-717A Rorathang-Pakhyong Bypass",
                "type": "SAFEST",
                "destination": "Gangtok South Staging Area"
            }
        ],
        status=STATUS_APPROVED,
        last_survey_date="2026-08-15"
    ),
    CorridorDefinition(
        corridor_id="CORR-TUPUL-MANIPUR-RLY",
        name="Jiribam-Imphal Railway Section (Tupul Station Scarp)",
        state="Manipur",
        district="Noney",
        road="Jiribam-Imphal Railway Alignment",
        kilometre_marker="Ch 52.600",
        geometry={
            "type": "LineString",
            "coordinates": [
                [93.5650, 24.7480],
                [93.5780, 24.7550],
                [93.5890, 24.7620]
            ]
        },
        elevation=540.0,
        slope=48.0,
        risk="CRITICAL",
        sensor_sites=[
            {
                "site_id": "SITE-TUPUL-INCL-01",
                "name": "Ijei River Valley Cut Slope Borehole",
                "sensor_type": "inclinometer",
                "latitude": 24.7550,
                "longitude": 93.5780,
                "target_depth_m": 25.0,
                "target_device_id": "SN-INCL-TUPUL-01"
            },
            {
                "site_id": "SITE-TUPUL-PIEZ-01",
                "name": "Railway Embankment Toe Piezometer",
                "sensor_type": "piezometer",
                "latitude": 24.7548,
                "longitude": 93.5776,
                "target_depth_m": 15.0,
                "target_device_id": "SN-PIEZ-TUPUL-01"
            }
        ],
        gateway_sites=[
            {
                "gateway_id": "GW-TUPUL-STN-01",
                "name": "Tupul Railway Station Control Tower",
                "latitude": 24.7570,
                "longitude": 93.5805,
                "elevation_m": 595.0,
                "mast_height_m": 15.0,
                "backhaul": "OFC_RAILTEL_LORA"
            }
        ],
        weather_sources=["IMD_NONEY", "OPEN_METEO"],
        evacuation_routes=[
            {
                "route_id": "EVAC-TUPUL-NH37",
                "name": "NH-37 Imphal Old Road Bypass",
                "type": "SAFEST",
                "destination": "Noney District HQ"
            }
        ],
        status=STATUS_APPROVED,
        last_survey_date="2026-07-28"
    ),
    CorridorDefinition(
        corridor_id="CORR-MELTHUM-MIZORAM",
        name="Melthum Quarry Hillside Settlement Corridor",
        state="Mizoram",
        district="Aizawl",
        road="Aizawl-Lunglei State Highway",
        kilometre_marker="Km 12.400",
        geometry={
            "type": "LineString",
            "coordinates": [
                [92.9520, 23.8890],
                [92.9600, 23.8950],
                [92.9680, 23.9010]
            ]
        },
        elevation=910.0,
        slope=46.2,
        risk="HIGH",
        sensor_sites=[
            {
                "site_id": "SITE-MELTHUM-CRACK-01",
                "name": "Upper Quarry Scarp Joint Extensometer",
                "sensor_type": "crack_sensor",
                "latitude": 23.8950,
                "longitude": 92.9600,
                "target_depth_m": 0.0,
                "target_device_id": "SN-CRACK-MELTHUM-01"
            },
            {
                "site_id": "SITE-MELTHUM-TILT-01",
                "name": "Residential Terrace Foundation Anchor",
                "sensor_type": "tilt",
                "latitude": 23.8955,
                "longitude": 92.9608,
                "target_depth_m": 0.0,
                "target_device_id": "SN-TILT-MELTHUM-01"
            }
        ],
        gateway_sites=[
            {
                "gateway_id": "GW-MELTHUM-WATER-01",
                "name": "Aizawl PHE Water Reservoir Mast",
                "latitude": 23.8980,
                "longitude": 92.9630,
                "elevation_m": 965.0,
                "mast_height_m": 10.0,
                "backhaul": "4G_LTE"
            }
        ],
        weather_sources=["IMD_AIZAWL", "OPEN_METEO"],
        evacuation_routes=[
            {
                "route_id": "EVAC-MELTHUM-UPPER",
                "name": "Kulikawn Hill Crest Access Road",
                "type": "SAFEST",
                "destination": "Kulikawn Hospital Safe Staging"
            }
        ],
        status=STATUS_APPROVED,
        last_survey_date="2026-06-20"
    ),
    CorridorDefinition(
        corridor_id="CORR-NH717A-PEDONG-RISSI",
        name="NH-717A Strategic Bypass (Pedong to Rissi Bridge)",
        state="West Bengal",
        district="Kalimpong",
        road="NH-717A",
        kilometre_marker="Km 34.100",
        geometry={
            "type": "LineString",
            "coordinates": [
                [88.6010, 27.1450],
                [88.6150, 27.1580],
                [88.6300, 27.1700]
            ]
        },
        elevation=1150.0,
        slope=38.0,
        risk="HIGH",
        sensor_sites=[
            {
                "site_id": "SITE-PEDONG-SOIL-01",
                "name": "Rissi River High Bluff Slope",
                "sensor_type": "soil_moisture",
                "latitude": 27.1580,
                "longitude": 88.6150,
                "target_depth_m": 1.5,
                "target_device_id": "SN-SOIL-PEDONG-01"
            }
        ],
        gateway_sites=[
            {
                "gateway_id": "GW-PEDONG-POLICE-01",
                "name": "Pedong Border Post Communications Tower",
                "latitude": 27.1520,
                "longitude": 88.6130,
                "elevation_m": 1240.0,
                "mast_height_m": 18.0,
                "backhaul": "BSNL_FIBER_LORA"
            }
        ],
        weather_sources=["IMD_KALIMPONG", "OPEN_METEO"],
        evacuation_routes=[
            {
                "route_id": "EVAC-PEDONG-ALGARAH",
                "name": "Algarah Ridge Route",
                "type": "SAFEST",
                "destination": "Algarah BRO Camp"
            }
        ],
        status=STATUS_SURVEYED,
        last_survey_date="2026-05-12"
    ),
    CorridorDefinition(
        corridor_id="CORR-DIMA-HASAO-ASSAM",
        name="Lumding-Badarpur Railway Cutting (Jatinga Valley)",
        state="Assam",
        district="Dima Hasao",
        road="NFR Lumding-Badarpur Hill Section",
        kilometre_marker="Km 118.500",
        geometry={
            "type": "LineString",
            "coordinates": [
                [93.0150, 25.1500],
                [93.0270, 25.1650],
                [93.0390, 25.1800]
            ]
        },
        elevation=410.0,
        slope=41.0,
        risk="HIGH",
        sensor_sites=[
            {
                "site_id": "SITE-DIMA-INCL-01",
                "name": "Jatinga River Embankment Cut",
                "sensor_type": "inclinometer",
                "latitude": 25.1650,
                "longitude": 93.0270,
                "target_depth_m": 20.0,
                "target_device_id": "SN-INCL-DIMA-01"
            }
        ],
        gateway_sites=[
            {
                "gateway_id": "GW-HAFLONG-HILL-01",
                "name": "New Haflong Signal Cabin Tower",
                "latitude": 25.1710,
                "longitude": 93.0320,
                "elevation_m": 510.0,
                "mast_height_m": 15.0,
                "backhaul": "RAILTEL_OFC"
            }
        ],
        weather_sources=["IMD_SILCHAR", "OPEN_METEO"],
        evacuation_routes=[
            {
                "route_id": "EVAC-HAFLONG-HIGHWAY",
                "name": "Haflong Hill Bypass",
                "type": "SAFEST",
                "destination": "Haflong Civil Hospital"
            }
        ],
        status=STATUS_SURVEYED,
        last_survey_date="2026-04-18"
    )
]


class CorridorRegistry:
    """Thread-safe persistent registry of monitored transportation and settlement corridors."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
        self._seed_default_corridors()

    def _get_conn(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS corridors (
                        corridor_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        state TEXT NOT NULL,
                        district TEXT NOT NULL,
                        road TEXT NOT NULL,
                        kilometre_marker TEXT NOT NULL,
                        geometry TEXT NOT NULL,
                        elevation REAL NOT NULL,
                        slope REAL NOT NULL,
                        risk TEXT NOT NULL,
                        sensor_sites TEXT NOT NULL,
                        gateway_sites TEXT NOT NULL,
                        weather_sources TEXT NOT NULL,
                        evacuation_routes TEXT NOT NULL,
                        status TEXT NOT NULL,
                        last_survey_date TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_corridors_status ON corridors(status)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_corridors_state ON corridors(state)")
                conn.commit()
            finally:
                conn.close()

    def _seed_default_corridors(self) -> None:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM corridors")
                count = cur.fetchone()[0]
                if count == 0:
                    now = datetime.now(timezone.utc).isoformat()
                    for c in SEED_CORRIDORS:
                        cur.execute("""
                            INSERT INTO corridors (
                                corridor_id, name, state, district, road, kilometre_marker,
                                geometry, elevation, slope, risk, sensor_sites, gateway_sites,
                                weather_sources, evacuation_routes, status, last_survey_date,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            c.corridor_id, c.name, c.state, c.district, c.road, c.kilometre_marker,
                            json.dumps(c.geometry), c.elevation, c.slope, c.risk,
                            json.dumps(c.sensor_sites), json.dumps(c.gateway_sites),
                            json.dumps(c.weather_sources), json.dumps(c.evacuation_routes),
                            c.status, c.last_survey_date, now, now
                        ))
                    conn.commit()
                    logger.info(f"Seeded {len(SEED_CORRIDORS)} Himalayan corridors into registry.")
            finally:
                conn.close()

    def register_corridor(self, corridor: CorridorDefinition) -> CorridorDefinition:
        """Inserts or replaces a corridor definition."""
        if corridor.status not in VALID_CORRIDOR_STATUSES:
            raise ValueError(f"Invalid corridor status: {corridor.status}. Must be one of {VALID_CORRIDOR_STATUSES}")

        now = datetime.now(timezone.utc).isoformat()
        if not corridor.created_at:
            corridor.created_at = now
        corridor.updated_at = now

        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO corridors (
                        corridor_id, name, state, district, road, kilometre_marker,
                        geometry, elevation, slope, risk, sensor_sites, gateway_sites,
                        weather_sources, evacuation_routes, status, last_survey_date,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    corridor.corridor_id, corridor.name, corridor.state, corridor.district,
                    corridor.road, corridor.kilometre_marker, json.dumps(corridor.geometry),
                    corridor.elevation, corridor.slope, corridor.risk,
                    json.dumps(corridor.sensor_sites), json.dumps(corridor.gateway_sites),
                    json.dumps(corridor.weather_sources), json.dumps(corridor.evacuation_routes),
                    corridor.status, corridor.last_survey_date, corridor.created_at, corridor.updated_at
                ))
                conn.commit()
                return corridor
            finally:
                conn.close()

    def get_corridor(self, corridor_id: str) -> Optional[CorridorDefinition]:
        """Retrieves a single corridor by its ID."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT corridor_id, name, state, district, road, kilometre_marker,
                           geometry, elevation, slope, risk, sensor_sites, gateway_sites,
                           weather_sources, evacuation_routes, status, last_survey_date,
                           created_at, updated_at
                    FROM corridors WHERE corridor_id = ?
                """, (corridor_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_corridor(row)
            finally:
                conn.close()

    def list_corridors(self, status: Optional[str] = None) -> List[CorridorDefinition]:
        """Lists all registered corridors, optionally filtered by lifecycle status."""
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                if status:
                    cur.execute("""
                        SELECT corridor_id, name, state, district, road, kilometre_marker,
                               geometry, elevation, slope, risk, sensor_sites, gateway_sites,
                               weather_sources, evacuation_routes, status, last_survey_date,
                               created_at, updated_at
                        FROM corridors WHERE status = ?
                        ORDER BY corridor_id ASC
                    """, (status,))
                else:
                    cur.execute("""
                        SELECT corridor_id, name, state, district, road, kilometre_marker,
                               geometry, elevation, slope, risk, sensor_sites, gateway_sites,
                               weather_sources, evacuation_routes, status, last_survey_date,
                               created_at, updated_at
                        FROM corridors
                        ORDER BY corridor_id ASC
                    """)
                rows = cur.fetchall()
                return [self._row_to_corridor(r) for r in rows]
            finally:
                conn.close()

    def update_status(self, corridor_id: str, new_status: str, justification: str = "") -> CorridorDefinition:
        """Transitions corridor status adhering to strict lifecycle progression rules."""
        if new_status not in VALID_CORRIDOR_STATUSES:
            raise ValueError(f"Unknown corridor status: {new_status}")

        corridor = self.get_corridor(corridor_id)
        if not corridor:
            raise KeyError(f"Corridor {corridor_id} not found in registry")

        allowed = ALLOWED_TRANSITIONS.get(corridor.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Illegal corridor status transition from {corridor.status} to {new_status}. "
                f"Permitted next states: {allowed}"
            )

        corridor.status = new_status
        corridor.updated_at = datetime.now(timezone.utc).isoformat()
        self.register_corridor(corridor)
        logger.info(f"Corridor {corridor_id} transitioned to {new_status}. Reason: {justification}")
        return corridor

    def get_sensor_sites(self, corridor_id: str) -> List[Dict[str, Any]]:
        corridor = self.get_corridor(corridor_id)
        return corridor.sensor_sites if corridor else []

    def get_gateway_sites(self, corridor_id: str) -> List[Dict[str, Any]]:
        corridor = self.get_corridor(corridor_id)
        return corridor.gateway_sites if corridor else []

    def get_evacuation_routes(self, corridor_id: str) -> List[Dict[str, Any]]:
        corridor = self.get_corridor(corridor_id)
        return corridor.evacuation_routes if corridor else []

    def summary(self) -> Dict[str, Any]:
        all_corr = self.list_corridors()
        by_status: Dict[str, int] = {}
        by_risk: Dict[str, int] = {}
        total_sensor_sites = 0
        total_gateway_sites = 0

        for c in all_corr:
            by_status[c.status] = by_status.get(c.status, 0) + 1
            by_risk[c.risk] = by_risk.get(c.risk, 0) + 1
            total_sensor_sites += len(c.sensor_sites)
            total_gateway_sites += len(c.gateway_sites)

        return {
            "total_corridors": len(all_corr),
            "by_status": by_status,
            "by_risk": by_risk,
            "total_sensor_sites": total_sensor_sites,
            "total_gateway_sites": total_gateway_sites,
            "validation_state": "FIELD_VALIDATION_READY"
        }

    def _row_to_corridor(self, row: tuple) -> CorridorDefinition:
        return CorridorDefinition(
            corridor_id=row[0],
            name=row[1],
            state=row[2],
            district=row[3],
            road=row[4],
            kilometre_marker=row[5],
            geometry=json.loads(row[6]),
            elevation=float(row[7]),
            slope=float(row[8]),
            risk=row[9],
            sensor_sites=json.loads(row[10]),
            gateway_sites=json.loads(row[11]),
            weather_sources=json.loads(row[12]),
            evacuation_routes=json.loads(row[13]),
            status=row[14],
            last_survey_date=row[15],
            created_at=row[16],
            updated_at=row[17]
        )


CORRIDOR_REGISTRY = CorridorRegistry()
GLOBAL_CORRIDOR_REGISTRY = CORRIDOR_REGISTRY
