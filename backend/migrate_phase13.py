#!/usr/bin/env python3
"""
PARVAT NETRA -- Database Migration: Phase 13
Creates tables for:
  1. bypass_corridors (Strategic alternate routes around NH-10 with LineString geometry)
  2. critical_habitations (Settlements vulnerable to isolation with Point geometry)
Creates GIST spatial indexes and seeds initial benchmarks.
"""

import os
import sys
import psycopg2

# Reconfigure stdout/stderr to UTF-8 on Windows
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


def run_migration():
    load_env()
    db_url = os.environ.get('NEON_DB_URL') or os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("NEON_DB_URL environment variable is missing.")

    print("Connecting to Neon PostGIS database...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1. Table: bypass_corridors
    print("Creating table `bypass_corridors`...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bypass_corridors (
            route_id SERIAL PRIMARY KEY,
            corridor_code TEXT NOT NULL,
            name TEXT NOT NULL,
            via_settlements TEXT NOT NULL,
            surface_type TEXT CHECK (surface_type IN ('PAVED_DOUBLE_LANE', 'SINGLE_LANE_METALLIC', 'UNPAVED_HAZARDOUS')),
            max_tonnage_tonnes NUMERIC DEFAULT 15.0,
            length_km NUMERIC NOT NULL,
            normal_duration_hrs NUMERIC NOT NULL,
            status TEXT DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CONGESTED', 'CLOSED_SECONDARY_SLIDE')),
            geom GEOMETRY(LineString, 4326)
        );
    """)

    # GIST spatial index for bypass_corridors
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_bypass_corridors_geom 
        ON bypass_corridors USING GIST(geom);
    """)

    # 2. Table: critical_habitations
    print("Creating table `critical_habitations`...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS critical_habitations (
            habitation_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            district TEXT NOT NULL,
            population INTEGER NOT NULL,
            primary_road_id INTEGER REFERENCES lifeline_roads(road_id),
            has_functional_phc BOOLEAN DEFAULT TRUE,
            has_helipad BOOLEAN DEFAULT FALSE,
            grain_reserve_days INTEGER DEFAULT 14,
            fuel_reserve_days INTEGER DEFAULT 7,
            isolation_status TEXT DEFAULT 'NORMAL' CHECK (isolation_status IN ('NORMAL', 'THREATENED', 'ISOLATED_AIR_ONLY')),
            geom GEOMETRY(Point, 4326)
        );
    """)

    # GIST spatial index for critical_habitations
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_critical_habitations_geom 
        ON critical_habitations USING GIST(geom);
    """)

    # 3. Seed bypass_corridors
    print("Seeding strategic bypass corridors...")
    cur.execute("SELECT COUNT(*) FROM bypass_corridors;")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO bypass_corridors (
                corridor_code, name, via_settlements, surface_type,
                max_tonnage_tonnes, length_km, normal_duration_hrs, status, geom
            ) VALUES
            (
                'BYPASS-LAVA',
                'Lava - Gorubathan Corridor',
                'Damdim - Gorubathan - Lava - Algarah - Rangpo',
                'SINGLE_LANE_METALLIC',
                12.0,
                84.5,
                4.5,
                'OPEN',
                ST_GeomFromText('LINESTRING(88.62 26.90, 88.70 26.98, 88.66 27.08, 88.58 27.14, 88.53 27.20)', 4326)
            ),
            (
                'BYPASS-MUNGPOO',
                'Mungpoo Secondary Ridge',
                'Rongpo - Mungpoo - Jorebungalow',
                'UNPAVED_HAZARDOUS',
                5.0,
                42.0,
                3.2,
                'CONGESTED',
                ST_GeomFromText('LINESTRING(88.42 26.98, 88.40 27.05, 88.44 27.12, 88.50 27.18)', 4326)
            );
        """)
        print("  -> Seeded 2 bypass corridors (Lava & Mungpoo).")
    else:
        print("  -> Bypass corridors already seeded.")

    # 4. Seed critical_habitations
    print("Seeding critical habitations...")
    cur.execute("SELECT COUNT(*) FROM critical_habitations;")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO critical_habitations (
                name, district, population, primary_road_id,
                has_functional_phc, has_helipad, grain_reserve_days, fuel_reserve_days,
                isolation_status, geom
            ) VALUES
            (
                'Singtam Transit Hub',
                'Pakyong',
                8500,
                1,
                TRUE,
                FALSE,
                12,
                5,
                'NORMAL',
                ST_GeomFromText('POINT(88.50 27.15)', 4326)
            ),
            (
                'Dikchu River Settlement',
                'Gangtok',
                4200,
                1,
                TRUE,
                FALSE,
                6,
                3,
                'NORMAL',
                ST_GeomFromText('POINT(88.55 27.25)', 4326)
            ),
            (
                'Chungthang Sub-Divisional Base',
                'Mangan',
                6100,
                1,
                TRUE,
                TRUE,
                4,
                2,
                'NORMAL',
                ST_GeomFromText('POINT(88.64 27.60)', 4326)
            );
        """)
        print("  -> Seeded 3 critical habitations (Singtam, Dikchu, Chungthang).")
    else:
        print("  -> Critical habitations already seeded.")

    conn.commit()
    cur.close()
    conn.close()
    print("Migration Phase 13 completed successfully!")


if __name__ == "__main__":
    run_migration()
