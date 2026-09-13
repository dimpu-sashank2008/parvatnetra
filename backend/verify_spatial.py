#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 8 Step 1 Spatial Verification Script
Verifies spatial road intersections and lifeline protection on Neon PostGIS.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# UTF-8 encoding safeguard for Windows console
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

def verify_spatial():
    load_env()
    db_url = os.environ.get("NEON_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        print("[ERROR] NEON_DB_URL not configured.")
        sys.exit(1)

    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    cur = conn.cursor()

    print("=" * 75)
    print("PARVAT NETRA -- STEP 1: SPATIAL ROAD INTERSECTIONS & LIFELINE PROTECTION")
    print("=" * 75)

    # 1. Verify table and index
    cur.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'lifeline_roads';
    """)
    indexes = cur.fetchall()
    print("\n[INFO] Lifeline Roads Indexes:")
    for idx in indexes:
        print(f"  - {idx['indexname']}: {idx['indexdef']}")

    # 2. Verify NH-10 Record
    cur.execute("""
        SELECT road_id, road_code, name, importance, ST_AsText(geom) AS geom_wkt
        FROM lifeline_roads
        WHERE road_code = 'NH-10';
    """)
    nh10 = cur.fetchone()
    print("\n[INFO] Seeded Lifeline Route:")
    print(f"  - ID: {nh10['road_id']} | Code: {nh10['road_code']} | Name: {nh10['name']}")
    print(f"  - Classification: {nh10['importance']}")
    print(f"  - LineString: {nh10['geom_wkt']}")

    # 3. Spatial Intersection Query with static_terrain
    print("\n[QUERY 1] Intersecting static_terrain with 500m NH-10 Buffer:")
    cur.execute("""
        SELECT 
            t.id,
            t.region_name,
            t.slope_angle::float AS slope,
            t.soil_type,
            r.road_code,
            ROUND(ST_Distance(t.geom::geography, r.geom::geography)::numeric, 2) AS distance_m,
            ST_DWithin(t.geom::geography, r.geom::geography, 500) AS within_500m,
            ST_Intersects(t.geom, ST_Buffer(r.geom::geography, 500)::geometry) AS intersects_500m
        FROM static_terrain t
        CROSS JOIN lifeline_roads r
        WHERE r.road_code = 'NH-10'
        ORDER BY t.id;
    """)
    terrain_rows = cur.fetchall()
    for row in terrain_rows:
        status = "CRITICAL INTERSECTION (Within 500m)" if row['within_500m'] else "SAFE"
        print(f"  * Region #{row['id']} [{row['region_name']}]:")
        print(f"      Slope: {row['slope']}° | Soil: {row['soil_type']}")
        print(f"      Distance to NH-10: {row['distance_m']}m | 500m Buffer Intersection: {row['intersects_500m']}")
        print(f"      Exposure Status: {status}")

    # 4. Spatial Intersection Query with hazard_zones
    print("\n[QUERY 2] Intersecting hazard_zones with 500m NH-10 Buffer:")
    cur.execute("""
        SELECT 
            h.zone_id,
            h.zone_name,
            h.district,
            h.susceptibility_level,
            r.road_code,
            ROUND(ST_Distance(h.geom::geography, r.geom::geography)::numeric, 2) AS distance_m,
            ST_DWithin(h.geom::geography, r.geom::geography, 500) AS within_500m,
            ST_Intersects(h.geom, ST_Buffer(r.geom::geography, 500)::geometry) AS intersects_500m
        FROM hazard_zones h
        CROSS JOIN lifeline_roads r
        WHERE r.road_code = 'NH-10'
        ORDER BY h.zone_id;
    """)
    zone_rows = cur.fetchall()
    for z in zone_rows:
        status = "INTERSECTING NH-10 CORRIDOR" if z['within_500m'] else "CLEAR OF CORRIDOR"
        print(f"  * Zone #{z['zone_id']} [{z['zone_name']} - {z['district']}]:")
        print(f"      Susceptibility: {z['susceptibility_level']}")
        print(f"      Distance to NH-10: {z['distance_m']}m | Within 500m: {z['within_500m']}")
        print(f"      Exposure Status: {status}")

    print("\n" + "=" * 75)
    print("STEP 1 SPATIAL INTERSECTION VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 75)

    cur.close()
    conn.close()

if __name__ == "__main__":
    verify_spatial()
