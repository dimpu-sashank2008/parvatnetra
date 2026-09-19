"""
scripts/ingest_live_observations.py
=====================================
PAHAD LSTM Private Training — Live Data Ingestion
--------------------------------------------------
Pulls real-time weather (Open-Meteo) and seismic (USGS FDSN) observations
for the 8 NER PAHAD monitoring sectors and appends them to pahad_observations.db.

This enriches the training dataset with genuinely live telemetry before
the private LSTM model training run.

Data Provenance : [LIVE] Open-Meteo (free, no key required)
                  [LIVE] USGS FDSNws (free, no key required)
Usage           : python scripts/ingest_live_observations.py
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [INGEST] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DB_PATH = "data/observations/pahad_observations.db"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
USGS_FDSN_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# NER monitoring sectors with representative coordinates
NER_SECTORS = [
    {"sector_id": "SK-SINGTAM-01", "lat": 27.23, "lon": 88.50, "name": "Sikkim Teesta Corridor"},
    {"sector_id": "SK-MANGAN-01", "lat": 27.51, "lon": 88.53, "name": "Sikkim North Corridor"},
    {"sector_id": "MN-NONEY-01", "lat": 24.75, "lon": 93.48, "name": "Manipur Tupul Corridor"},
    {"sector_id": "MZ-AIZAWL-MELTHUM", "lat": 23.73, "lon": 92.72, "name": "Mizoram Aizawl Basin"},
    {"sector_id": "ML-MAWSYNRAM-01", "lat": 25.30, "lon": 91.58, "name": "Meghalaya Plateau"},
    {"sector_id": "AR-ITANAGAR-01", "lat": 27.09, "lon": 93.62, "name": "Arunachal Papum Corridor"},
    {"sector_id": "AS-DIMA-HASAO-01", "lat": 25.10, "lon": 93.00, "name": "Assam Barak Valley"},
    {"sector_id": "NL-PHEK-01", "lat": 25.68, "lon": 94.47, "name": "Nagaland Kohima Corridor"},
]

WEATHER_VARIABLES = [
    "precipitation",
    "precipitation_probability",
    "rain",
    "soil_moisture_0_to_1cm",
    "soil_moisture_1_to_3cm",
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "et0_fao_evapotranspiration",
    "surface_pressure",
]


def _safe_get(url: str, params: dict, timeout: int = 15) -> Optional[dict]:
    """HTTP GET with retry on transient errors."""
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as exc:
            if attempt < 2:
                log.warning("Attempt %d failed: %s — retrying…", attempt + 1, exc)
                time.sleep(2 ** attempt)
            else:
                log.error("All attempts failed for %s: %s", url, exc)
                return None


def fetch_weather(sector: dict) -> list[dict]:
    """Fetch current hourly weather for a sector (last 24h)."""
    params = {
        "latitude": sector["lat"],
        "longitude": sector["lon"],
        "hourly": ",".join(WEATHER_VARIABLES),
        "past_days": 2,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }
    data = _safe_get(OPEN_METEO_URL, params)
    if not data:
        return []

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    records = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for i, ts in enumerate(times):
        for var in WEATHER_VARIABLES:
            val = hourly.get(var, [None] * len(times))[i]
            if val is None:
                continue
            records.append({
                "id": str(uuid.uuid4()),
                "sector_id": sector["sector_id"],
                "timestamp": ts.replace("T", " ") + ":00",
                "feature": var,
                "value": float(val),
                "unit": _unit_for(var),
                "source": "open-meteo-live",
                "quality": "LIVE",
                "provenance": "[LIVE] Open-Meteo free API — no API key required",
                "ingested_at": now_iso,
                "extra": json.dumps({"lat": sector["lat"], "lon": sector["lon"]}),
            })
    return records


def fetch_seismic(sector: dict) -> list[dict]:
    """Fetch recent M≥2 earthquakes within 150 km of sector (last 7 days)."""
    params = {
        "format": "geojson",
        "latitude": sector["lat"],
        "longitude": sector["lon"],
        "maxradiuskm": 150,
        "minmagnitude": 2.0,
        "starttime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "orderby": "time",
        "limit": 20,
    }
    # Calculate starttime as 7 days ago
    from datetime import timedelta
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    params["starttime"] = seven_days_ago.strftime("%Y-%m-%dT%H:%M:%S")

    data = _safe_get(USGS_FDSN_URL, params)
    if not data:
        return []

    records = []
    now_iso = datetime.now(timezone.utc).isoformat()
    features = data.get("features", [])

    for feat in features:
        props = feat.get("properties", {})
        coords = feat.get("geometry", {}).get("coordinates", [None, None, None])
        mag = props.get("mag")
        if mag is None:
            continue
        ts_ms = props.get("time", 0)
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        dist_km = _haversine(sector["lat"], sector["lon"], coords[1] or 0, coords[0] or 0)

        records.append({
            "id": str(uuid.uuid4()),
            "sector_id": sector["sector_id"],
            "timestamp": ts,
            "feature": "seismic_magnitude",
            "value": float(mag),
            "unit": "Mw",
            "source": "usgs-fdsn",
            "quality": "LIVE",
            "provenance": "[LIVE] USGS FDSNws earthquake catalog",
            "ingested_at": now_iso,
            "extra": json.dumps({
                "depth_km": coords[2],
                "distance_km": round(dist_km, 1),
                "place": props.get("place", ""),
            }),
        })
        records.append({
            "id": str(uuid.uuid4()),
            "sector_id": sector["sector_id"],
            "timestamp": ts,
            "feature": "seismic_distance_km",
            "value": round(dist_km, 1),
            "unit": "km",
            "source": "usgs-fdsn",
            "quality": "LIVE",
            "provenance": "[LIVE] USGS FDSNws earthquake catalog",
            "ingested_at": now_iso,
            "extra": json.dumps({"lat": coords[1], "lon": coords[0]}),
        })

    return records


def _unit_for(var: str) -> str:
    units = {
        "precipitation": "mm",
        "precipitation_probability": "%",
        "rain": "mm",
        "soil_moisture_0_to_1cm": "m3/m3",
        "soil_moisture_1_to_3cm": "m3/m3",
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "wind_speed_10m": "km/h",
        "wind_direction_10m": "°",
        "et0_fao_evapotranspiration": "mm",
        "surface_pressure": "hPa",
    }
    return units.get(var, "")


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def insert_records(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Upsert observation records (skip duplicates by sector+timestamp+feature)."""
    if not records:
        return 0
    cur = conn.cursor()
    inserted = 0
    for rec in records:
        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO observations
                  (id, sector_id, timestamp, feature, value, unit,
                   source, quality, provenance, ingested_at, extra)
                VALUES
                  (:id, :sector_id, :timestamp, :feature, :value, :unit,
                   :source, :quality, :provenance, :ingested_at, :extra)
                """,
                rec,
            )
            inserted += cur.rowcount
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    return inserted


def main() -> None:
    log.info("=== PAHAD LSTM Private Training — Live Observation Ingestion ===")
    log.info("Connecting to: %s", DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    total_inserted = 0
    for sector in NER_SECTORS:
        log.info("Fetching sector: %s (%s)", sector["sector_id"], sector["name"])

        weather_recs = fetch_weather(sector)
        seismic_recs = fetch_seismic(sector)

        w_count = insert_records(conn, weather_recs)
        s_count = insert_records(conn, seismic_recs)
        total_inserted += w_count + s_count

        log.info(
            "  → Weather: %d new rows | Seismic: %d new rows",
            w_count, s_count
        )
        time.sleep(0.5)  # Be polite to free APIs

    conn.close()
    log.info("Ingestion complete. Total new rows inserted: %d", total_inserted)
    log.info("Database: %s", DB_PATH)


if __name__ == "__main__":
    main()
