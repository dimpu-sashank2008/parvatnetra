#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 9 Step 1 Verification Script
Verifies IoT Sensors, Sensor Telemetry, and InSAR Satellite Deformation on Neon PostGIS.
Queries:
1. Sensors within 1,000 meters of lifeline_roads (NH-10).
2. InSAR observation points exhibiting high creep rate (los_velocity_mm_yr < -15.0).
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# UTF-8 for console output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def load_env(filepath='.env'):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

def verify():
    load_env()
    db_url = os.environ.get("NEON_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        print("[ERROR] NEON_DB_URL not configured.")
        sys.exit(1)

    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    cur = conn.cursor()

    print("=" * 78)
    print("PARVAT NETRA -- PHASE 9 STEP 1: IOT SENSORS & INSAR DEFORMATION VERIFICATION")
    print("=" * 78)

    # -------------------------------------------------------------------------
    # 1. VERIFY TABLES & GIST INDEXES
    # -------------------------------------------------------------------------
    print("\n[PART 1] Verifying GIST Spatial Indexes in Catalog:")
    cur.execute("""
        SELECT tablename, indexname, indexdef
        FROM pg_indexes
        WHERE tablename IN ('iot_sensors', 'sensor_telemetry', 'insar_deformation')
        ORDER BY tablename, indexname;
    """)
    indexes = cur.fetchall()
    for idx in indexes:
        print(f"  • Table: {idx['tablename']:<20} | Index: {idx['indexname']:<25}")
        print(f"    Definition: {idx['indexdef']}")

    # -------------------------------------------------------------------------
    # 2. QUERY: SENSORS WITHIN 1,000 METERS OF LIFELINE ROADS (NH-10)
    # -------------------------------------------------------------------------
    print("\n[PART 2] Spatial Proximity: IoT Sensors within 1,000m of NH-10 Corridor:")
    cur.execute("""
        SELECT 
            s.sensor_id,
            s.sensor_type,
            s.location_name,
            s.district,
            s.depth_meters::float AS depth_m,
            s.battery_pct,
            s.status AS sensor_status,
            t.value::float AS telemetry_val,
            t.unit AS telemetry_unit,
            t.is_critical,
            r.road_code,
            r.name AS road_name,
            ROUND(ST_Distance(s.geom::geography, r.geom::geography)::numeric, 2) AS distance_to_nh10_m,
            ST_DWithin(s.geom::geography, r.geom::geography, 1000) AS is_within_1000m
        FROM iot_sensors s
        CROSS JOIN lifeline_roads r
        LEFT JOIN LATERAL (
            SELECT value, unit, is_critical, recorded_at
            FROM sensor_telemetry
            WHERE sensor_id = s.sensor_id
            ORDER BY recorded_at DESC, reading_id DESC
            LIMIT 1
        ) t ON true
        WHERE r.road_code = 'NH-10'
        ORDER BY distance_to_nh10_m ASC;
    """)
    sensor_rows = cur.fetchall()

    for s in sensor_rows:
        prox_badge = "🔴 WITHIN 1KM ARTERIAL CORRIDOR" if s['is_within_1000m'] else "🟢 PERIPHERAL / UPPER CATCHMENT"
        crit_badge = "⚠️ CRITICAL EXCEEDANCE" if s['is_critical'] else "NORMAL"
        print(f"\n  📡 Node: {s['sensor_id']} ({s['sensor_type']})")
        print(f"     Location: {s['location_name']}, {s['district']}")
        print(f"     Latest Telemetry: {s['telemetry_val']} {s['telemetry_unit']} [{crit_badge}]")
        print(f"     Battery: {s['battery_pct']}% | Status: {s['sensor_status']}")
        print(f"     Distance to {s['road_code']}: {s['distance_to_nh10_m']} meters")
        print(f"     Spatial Flag: {prox_badge}")

    # -------------------------------------------------------------------------
    # 3. QUERY: INSAR SATELLITE DEFORMATION HIGH-CREEP RATE (< -15.0 mm/yr)
    # -------------------------------------------------------------------------
    print("\n[PART 3] Satellite Radar Interferometry: PS-InSAR High Creep Points (LOS Velocity < -15.0 mm/yr):")
    cur.execute("""
        SELECT 
            point_id,
            mission,
            location_name,
            district,
            los_velocity_mm_yr::float AS los_vel_mm_yr,
            cumulative_disp_mm::float AS cum_disp_mm,
            coherence::float AS coherence,
            last_pass_date,
            ST_AsText(geom) AS geom_wkt,
            CASE 
                WHEN los_velocity_mm_yr < -20.0 THEN 'CRITICAL ACCELERATION'
                WHEN los_velocity_mm_yr < -15.0 THEN 'SEVERE CREEP SUBSIDENCE'
                ELSE 'MODERATE / STABLE'
            END AS hazard_rating
        FROM insar_deformation
        WHERE los_velocity_mm_yr < -15.0
        ORDER BY los_velocity_mm_yr ASC;
    """)
    insar_rows = cur.fetchall()

    for p in insar_rows:
        print(f"\n  🛰️ PS-InSAR Point #{p['point_id']} [{p['location_name']}, {p['district']}]:")
        print(f"     Mission: {p['mission']} | Last Pass: {p['last_pass_date']}")
        print(f"     LOS Deformation Velocity: {p['los_vel_mm_yr']:.1f} mm/year")
        print(f"     30-Day Cumulative Displacement: {p['cum_disp_mm']:.1f} mm")
        print(f"     Interferometric Coherence (γ): {p['coherence']:.2f}")
        print(f"     Deformation Classification: {p['hazard_rating']}")
        print(f"     Coordinates: {p['geom_wkt']}")

    print("\n" + "=" * 78)
    print("PHASE 9 STEP 1 VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 78)

    cur.close()
    conn.close()

if __name__ == "__main__":
    verify()
