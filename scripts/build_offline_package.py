# -*- coding: utf-8 -*-
"""
scripts/build_offline_package.py
================================
PARVAT NETRA • Offline Core Geospatial Package Builder
Generates a lightweight, self-contained GeoJSON vector feature collection
(static/data/offline_core_package.json) encompassing:
  1. NER Administrative Outlines (8 states: SK, AS, ML, AR, NL, MN, MZ, TR)
  2. Strategic Mountain Corridors (NH-10, NH-717A, NH-29, NH-6, NH-102, NH-37, NH-8, Bhalukpong-Tawang)
  3. Himalayan Rivers (Teesta, Rangeet, Brahmaputra, Barak)
  4. 18 Critical PAHAD Monitoring Sectors
  5. Designated Evacuation Shelters
  6. Historical Landslide Scars & Ground Truth Points
  7. Key Settlement / Operational Hubs
"""

import json
import os
import csv
import hashlib
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "offline_core_package.json")
CACHE_FILE = os.path.join(BASE_DIR, "static", "pahad_offline_cache.json")
HIST_CSV = os.path.join(BASE_DIR, "data", "raw", "historical_landslides_ner.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. State Boundary Polygons (approximate simplified bounding polygons for 8 NER states)
STATE_BOUNDARIES = [
    {
        "state": "Sikkim",
        "iso": "IN-SK",
        "capital": "Gangtok",
        "coordinates": [
            [88.01, 27.08], [88.20, 27.15], [88.55, 27.10], [88.85, 27.20],
            [88.92, 27.45], [88.75, 27.85], [88.60, 28.12], [88.40, 28.00],
            [88.05, 27.75], [88.01, 27.08]
        ]
    },
    {
        "state": "Meghalaya",
        "iso": "IN-ML",
        "capital": "Shillong",
        "coordinates": [
            [89.85, 25.10], [91.80, 25.10], [92.80, 25.15], [92.75, 25.75],
            [91.85, 26.05], [90.50, 25.95], [89.85, 25.50], [89.85, 25.10]
        ]
    },
    {
        "state": "Assam",
        "iso": "IN-AS",
        "capital": "Dispur",
        "coordinates": [
            [89.70, 26.00], [90.50, 26.30], [92.00, 26.70], [93.50, 26.80],
            [95.50, 27.50], [95.90, 27.20], [94.50, 26.20], [93.00, 24.80],
            [92.50, 24.50], [92.00, 25.00], [90.50, 25.50], [89.70, 26.00]
        ]
    },
    {
        "state": "Arunachal Pradesh",
        "iso": "IN-AR",
        "capital": "Itanagar",
        "coordinates": [
            [91.60, 27.30], [92.10, 27.90], [93.50, 28.60], [95.00, 29.00],
            [96.80, 28.30], [97.40, 28.00], [96.00, 27.00], [94.00, 27.20],
            [92.00, 26.90], [91.60, 27.30]
        ]
    },
    {
        "state": "Nagaland",
        "iso": "IN-NL",
        "capital": "Kohima",
        "coordinates": [
            [93.30, 25.50], [93.70, 25.60], [94.50, 26.20], [95.20, 26.90],
            [95.30, 26.50], [94.80, 25.70], [94.20, 25.20], [93.30, 25.50]
        ]
    },
    {
        "state": "Manipur",
        "iso": "IN-MN",
        "capital": "Imphal",
        "coordinates": [
            [93.05, 24.00], [93.40, 24.20], [93.70, 25.40], [94.50, 25.60],
            [94.60, 24.80], [94.30, 23.80], [93.20, 23.90], [93.05, 24.00]
        ]
    },
    {
        "state": "Mizoram",
        "iso": "IN-MZ",
        "capital": "Aizawl",
        "coordinates": [
            [92.25, 22.00], [92.60, 22.10], [93.30, 22.40], [93.40, 23.80],
            [93.00, 24.40], [92.50, 24.20], [92.30, 23.20], [92.25, 22.00]
        ]
    },
    {
        "state": "Tripura",
        "iso": "IN-TR",
        "capital": "Agartala",
        "coordinates": [
            [91.15, 23.00], [91.50, 23.20], [92.20, 24.00], [92.30, 24.50],
            [92.00, 24.40], [91.30, 23.80], [91.15, 23.00]
        ]
    }
]

# 2. Strategic Mountain Corridors (Highway Polylines)
HIGHWAY_CORRIDORS = [
    {
        "name": "NH-10 Sikkim Lifeline Corridor",
        "highway_ref": "NH-10",
        "state": "Sikkim & West Bengal",
        "priority": "CRITICAL_LIFELINE",
        "coordinates": [
            [88.42, 26.78], [88.50, 26.90], [88.48, 27.05], [88.45, 27.12],
            [88.50, 27.18], [88.52, 27.23], [88.61, 27.33]
        ]
    },
    {
        "name": "NH-717A Strategic Alternative Bypass",
        "highway_ref": "NH-717A",
        "state": "Sikkim & West Bengal",
        "priority": "STRATEGIC_BYPASS",
        "coordinates": [
            [88.60, 26.85], [88.65, 27.02], [88.68, 27.15], [88.63, 27.24],
            [88.61, 27.33]
        ]
    },
    {
        "name": "NH-29 Dimapur-Kohima Corridor",
        "highway_ref": "NH-29",
        "state": "Nagaland",
        "priority": "STATE_LIFELINE",
        "coordinates": [
            [93.72, 25.90], [93.82, 25.80], [93.95, 25.72], [94.11, 25.68]
        ]
    },
    {
        "name": "NH-6 Shillong-Jowai-Silchar Corridor",
        "highway_ref": "NH-6",
        "state": "Meghalaya & Assam",
        "priority": "REGIONAL_TRUNK",
        "coordinates": [
            [91.89, 25.58], [92.20, 25.45], [92.40, 25.20], [92.78, 24.83]
        ]
    },
    {
        "name": "NH-37 / Jiribam-Imphal Corridor",
        "highway_ref": "NH-37",
        "state": "Manipur",
        "priority": "STRATEGIC_LIFELINE",
        "coordinates": [
            [93.12, 24.80], [93.42, 24.81], [93.64, 24.82], [93.94, 24.81]
        ]
    },
    {
        "name": "NH-13 Bhalukpong-Tawang Military Axis",
        "highway_ref": "NH-13",
        "state": "Arunachal Pradesh",
        "priority": "DEFENSE_CORRIDOR",
        "coordinates": [
            [92.65, 27.01], [92.50, 27.25], [92.25, 27.45], [91.86, 27.59]
        ]
    },
    {
        "name": "NH-8 Agartala-Dharmanagar Arterial",
        "highway_ref": "NH-8",
        "state": "Tripura",
        "priority": "STATE_LIFELINE",
        "coordinates": [
            [91.28, 23.83], [91.65, 23.95], [92.00, 24.15], [92.17, 24.38]
        ]
    }
]

# 3. Himalayan Rivers
RIVERS = [
    {
        "name": "Teesta River",
        "basin": "Brahmaputra Basin (Sikkim)",
        "coordinates": [
            [88.58, 27.85], [88.58, 27.38], [88.50, 27.23], [88.45, 27.12],
            [88.48, 26.90]
        ]
    },
    {
        "name": "Rangeet River",
        "basin": "Teesta Sub-Basin",
        "coordinates": [
            [88.25, 27.35], [88.35, 27.20], [88.45, 27.12]
        ]
    },
    {
        "name": "Brahmaputra River (Main Stem)",
        "basin": "Brahmaputra Basin",
        "coordinates": [
            [95.50, 27.50], [94.00, 26.90], [92.80, 26.60], [91.75, 26.18],
            [90.50, 26.10]
        ]
    },
    {
        "name": "Barak River",
        "basin": "Meghna Basin (Assam/Manipur)",
        "coordinates": [
            [93.50, 25.10], [93.10, 24.90], [92.80, 24.83], [92.50, 24.85]
        ]
    }
]

features = []

# Add State Boundaries
for b in STATE_BOUNDARIES:
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [b["coordinates"]]
        },
        "properties": {
            "layer_group": "ADMIN_BOUNDARIES",
            "category": "boundary",
            "name": b["state"],
            "iso": b["iso"],
            "capital": b["capital"],
            "fill_color": "#1E293B",
            "stroke_color": "#38BDF8",
            "stroke_width": 1.5,
            "opacity": 0.4,
            "provenance": "[HISTORICAL]"
        }
    })

# Add Highway Corridors
for h in HIGHWAY_CORRIDORS:
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": h["coordinates"]
        },
        "properties": {
            "layer_group": "ROADS",
            "category": "corridor",
            "name": h["name"],
            "highway_ref": h["highway_ref"],
            "state": h["state"],
            "priority": h["priority"],
            "stroke_color": "#F59E0B",
            "stroke_width": 2.5,
            "provenance": "[HISTORICAL]"
        }
    })

# Add Rivers
for r in RIVERS:
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": r["coordinates"]
        },
        "properties": {
            "layer_group": "HYDROLOGY",
            "category": "river",
            "name": r["name"],
            "basin": r["basin"],
            "stroke_color": "#06B6D4",
            "stroke_width": 2.0,
            "provenance": "[HISTORICAL]"
        }
    })

# Add Critical Sectors & Shelters from pahad_offline_cache.json if available
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache_data = json.load(f)

    # 18 Critical Sectors
    for s in cache_data.get("critical_sectors", []):
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [s["lon"], s["lat"]]
            },
            "properties": {
                "layer_group": "PAHAD_SECTORS",
                "category": "critical_sector",
                "sector_id": s.get("sector_id"),
                "name": s.get("name"),
                "state": s.get("state"),
                "district": s.get("district"),
                "corridor": s.get("corridor"),
                "elevation_m": s.get("elevation_m"),
                "hazard_rating": s.get("hazard_rating"),
                "monitoring_tier": s.get("monitoring_tier"),
                "instrumentation": s.get("instrumentation", []),
                "provenance": "[CACHED]"
            }
        })

    # Emergency Shelters
    shelters_list = cache_data.get("emergency_shelters", cache_data.get("shelters", []))
    for shl in shelters_list:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [shl["lon"], shl["lat"]]
            },
            "properties": {
                "layer_group": "SHELTERS",
                "category": "shelter",
                "shelter_id": shl.get("shelter_id"),
                "name": shl.get("name"),
                "state": shl.get("state"),
                "district": shl.get("district"),
                "capacity_people": shl.get("capacity_people"),
                "medical_readiness": shl.get("medical_readiness"),
                "has_helipad": shl.get("has_helipad", False),
                "satellite_phone": shl.get("satellite_phone"),
                "contact_officer": shl.get("contact_officer"),
                "provenance": "[CACHED]"
            }
        })

# Add Historical Landslides from historical_landslides_ner.csv
if os.path.exists(HIST_CSV):
    with open(HIST_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "layer_group": "HISTORICAL_LANDSLIDES",
                        "category": "landslide_event",
                        "event_id": row["event_id"],
                        "disaster_id": row["disaster_id"],
                        "timestamp": row["timestamp"],
                        "state": row["state"],
                        "district": row["district"],
                        "sector_id": row["sector_id"],
                        "source": row["source"],
                        "rainfall_trigger_mm": float(row["rainfall_trigger_mm"]),
                        "fos": float(row["fos"]),
                        "cri": float(row["cri"]),
                        "provenance": row["provenance"]
                    }
                })
            except Exception:
                continue

# Assemble final package
package_metadata = {
    "package_id": "ner-core-v1",
    "name": "NER Operational Base Map",
    "version": "1.0",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "coverage": "North-Eastern Region of India (8 States)",
    "bounding_box": [87.0, 21.0, 98.0, 30.5],
    "description": "Pre-bundled offline GIS vector package supporting zero-connectivity operational triage.",
    "layers": [
        "ADMIN_BOUNDARIES", "ROADS", "HYDROLOGY", "PAHAD_SECTORS", "SHELTERS", "HISTORICAL_LANDSLIDES"
    ],
    "feature_counts": {
        "admin_boundaries": len(STATE_BOUNDARIES),
        "roads": len(HIGHWAY_CORRIDORS),
        "hydrology": len(RIVERS),
        "sectors": len(cache_data.get("critical_sectors", [])),
        "shelters": len(shelters_list),
        "historical_landslides": 17
    },
    "total_features": len(features)
}

geojson_doc = {
    "type": "FeatureCollection",
    "package_metadata": package_metadata,
    "features": features
}

package_json = json.dumps(geojson_doc, indent=2)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(package_json)

sha256 = hashlib.sha256(package_json.encode("utf-8")).hexdigest()
size_bytes = os.path.getsize(OUTPUT_FILE)

print(f"[OK] Generated {OUTPUT_FILE}")
print(f"     Features: {len(features)}")
print(f"     Size: {size_bytes} bytes ({size_bytes/1024:.1f} KB)")
print(f"     SHA-256: {sha256}")
