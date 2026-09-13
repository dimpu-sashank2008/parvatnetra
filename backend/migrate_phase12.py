#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 12 Database Migration
Creates PostGIS tables for River Hydrology (teesta_waterways) & Anthropogenic Hill Cuts (anthropogenic_cuts),
creates GIST indexes, seeds initial corridor benchmarks, and expands ml_risk_scores schema.
"""

import os
import sys
import psycopg2

# Reconfigure stdout for Windows cp1252
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def get_db_connection():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    neon_url = os.environ.get("NEON_DB_URL")
    if not neon_url and os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "NEON_DB_URL=" in line:
                    neon_url = line.split("NEON_DB_URL=", 1)[1].strip()
                    break

    if not neon_url:
        raise ValueError("NEON_DB_URL not found in environment or .env file.")

    return psycopg2.connect(neon_url)


def migrate_phase12():
    print("=" * 75)
    print("PARVAT NETRA -- PHASE 12 DATABASE MIGRATION")
    print("Hydrological Toe Erosion & Anthropogenic Hill Cuts Schemas")
    print("=" * 75)

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Create table teesta_waterways
    print("\n[STEP 1] Creating table `teesta_waterways`...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teesta_waterways (
            river_id SERIAL PRIMARY KEY,
            reach_name TEXT NOT NULL,
            water_level_m NUMERIC NOT NULL,
            danger_level_m NUMERIC NOT NULL,
            discharge_cusecs NUMERIC NOT NULL,
            scour_risk_level TEXT CHECK (scour_risk_level IN ('LOW', 'MODERATE', 'CRITICAL')),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            geom GEOMETRY(LineString, 4326)
        );
        CREATE INDEX IF NOT EXISTS idx_teesta_waterways_geom ON teesta_waterways USING GIST(geom);
    """)
    print("  -> Table `teesta_waterways` and GIST index created.")

    # 2. Create table anthropogenic_cuts
    print("\n[STEP 2] Creating table `anthropogenic_cuts`...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS anthropogenic_cuts (
            cut_id SERIAL PRIMARY KEY,
            location_name TEXT NOT NULL,
            corridor TEXT NOT NULL,
            cut_angle_deg NUMERIC NOT NULL,
            height_meters NUMERIC NOT NULL,
            has_retaining_wall BOOLEAN DEFAULT FALSE,
            activity_type TEXT CHECK (activity_type IN ('ROAD_WIDENING', 'TERRACED_BUILDING', 'QUARRYING', 'UNREGULATED_EXCAVATION')),
            destabilization_index NUMERIC CHECK (destabilization_index >= 0 AND destabilization_index <= 100),
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            geom GEOMETRY(Point, 4326)
        );
        CREATE INDEX IF NOT EXISTS idx_anthropogenic_cuts_geom ON anthropogenic_cuts USING GIST(geom);
    """)
    print("  -> Table `anthropogenic_cuts` and GIST index created.")

    # 3. Expand ml_risk_scores with Phase 12 audit columns
    print("\n[STEP 3] Expanding `ml_risk_scores` schema...")
    cur.execute("""
        ALTER TABLE ml_risk_scores ADD COLUMN IF NOT EXISTS toe_scour_factor NUMERIC DEFAULT 0;
        ALTER TABLE ml_risk_scores ADD COLUMN IF NOT EXISTS anthro_cut_factor NUMERIC DEFAULT 1.0;
    """)
    print("  -> Added `toe_scour_factor` and `anthro_cut_factor` columns.")

    # 4. Seed Benchmarks in teesta_waterways
    print("\n[STEP 4] Seeding `teesta_waterways` reach benchmark...")
    cur.execute("DELETE FROM teesta_waterways;")
    cur.execute("""
        INSERT INTO teesta_waterways (reach_name, water_level_m, danger_level_m, discharge_cusecs, scour_risk_level, geom)
        VALUES (
            'Teesta Gorge Arterial Reach (Melli - Singtam)',
            218.4,
            220.0,
            42500,
            'CRITICAL',
            ST_GeomFromText('LINESTRING(88.45 27.02, 88.48 27.10, 88.50 27.15, 88.52 27.22)', 4326)
        ) RETURNING river_id, reach_name, water_level_m, scour_risk_level;
    """)
    r_row = cur.fetchone()
    print(f"  -> Seeded Reach #{r_row[0]}: {r_row[1]} | Water Level: {r_row[2]}m | Scour: {r_row[3]}")

    # 5. Seed Benchmarks in anthropogenic_cuts
    print("\n[STEP 5] Seeding `anthropogenic_cuts` excavation benchmarks...")
    cur.execute("DELETE FROM anthropogenic_cuts;")
    cur.execute("""
        INSERT INTO anthropogenic_cuts (location_name, corridor, cut_angle_deg, height_meters, has_retaining_wall, activity_type, destabilization_index, geom)
        VALUES 
        (
            '29th Mile Road Widening Bench',
            'NH-10 Km 29',
            68.5,
            18.0,
            FALSE,
            'ROAD_WIDENING',
            84.5,
            ST_GeomFromText('POINT(88.47 27.08)', 4326)
        ),
        (
            'Singtam Quarry & Benching Zone',
            'NH-10 Singtam Bypass',
            62.0,
            14.0,
            FALSE,
            'UNREGULATED_EXCAVATION',
            76.0,
            ST_GeomFromText('POINT(88.51 27.16)', 4326)
        )
        RETURNING cut_id, location_name, cut_angle_deg, activity_type;
    """)
    cuts_rows = cur.fetchall()
    for c in cuts_rows:
        print(f"  -> Seeded Cut #{c[0]}: {c[1]} | Cut Angle: {c[2]} deg | Activity: {c[3]}")

    conn.commit()
    cur.close()
    conn.close()
    print("\n" + "=" * 75)
    print("PHASE 12 DATABASE MIGRATION COMPLETED SUCCESSFULLY")
    print("=" * 75)


if __name__ == "__main__":
    migrate_phase12()
