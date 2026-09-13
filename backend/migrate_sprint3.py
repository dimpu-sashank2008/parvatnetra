#!/usr/bin/env python3
"""
PARVAT NETRA -- Sprint 3 Database Migration
Adds HCII columns to critical_habitations and IRC gradient/curve columns to bypass_corridors.
Seeds/Upserts the 4 key GLOF-exposed settlements.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# ASCII-safe stdout on Windows
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


def get_db_connection():
    load_env()
    db_url = os.environ.get('NEON_DB_URL') or os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("NEON_DB_URL is missing in environment.")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor, connect_timeout=20)


def migrate_sprint3():
    print("=" * 70)
    print("PARVAT NETRA -- Sprint 3 Database Migration")
    print("=" * 70)

    conn = get_db_connection()
    with conn.cursor() as cur:
        # 1. Update critical_habitations table schema
        print("\n[1] Updating critical_habitations schema...")
        cur.execute("""
            ALTER TABLE critical_habitations
            ADD COLUMN IF NOT EXISTS critical_patients INT DEFAULT 0,
            ADD COLUMN IF NOT EXISTS bed_capacity INT DEFAULT 10,
            ADD COLUMN IF NOT EXISTS helipad_operational_fraction NUMERIC DEFAULT 1.0,
            ADD COLUMN IF NOT EXISTS hcii_score NUMERIC DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS hcii_tier TEXT DEFAULT 'STABLE_RESERVES';
        """)

        # Relax / update isolation_status check constraint to support all tiers
        cur.execute("""
            ALTER TABLE critical_habitations 
            DROP CONSTRAINT IF EXISTS critical_habitations_isolation_status_check;

            ALTER TABLE critical_habitations 
            ADD CONSTRAINT critical_habitations_isolation_status_check 
            CHECK (isolation_status IN (
                'NORMAL', 'THREATENED', 'ISOLATED_AIR_ONLY', 
                'CRITICAL_AIR_DROP_REQUIRED', 'ACUTE_SHORTAGE_THREATENED', 
                'MONITORED_WATCH', 'STABLE_RESERVES'
            ));
        """)

        # 2. Update bypass_corridors schema
        print("\n[2] Updating bypass_corridors schema...")
        cur.execute("""
            ALTER TABLE bypass_corridors
            ADD COLUMN IF NOT EXISTS ruling_gradient_pct NUMERIC DEFAULT 5.0,
            ADD COLUMN IF NOT EXISTS min_curve_radius_m NUMERIC DEFAULT 50.0;
        """)

        # 3. Update bypass corridor parameters for Lava and Mungpoo
        print("\n[3] Synchronizing bypass corridor parameters...")
        cur.execute("""
            UPDATE bypass_corridors
            SET max_tonnage_tonnes = 45.0,
                ruling_gradient_pct = 4.8,
                min_curve_radius_m = 100.0,
                status = 'OPEN'
            WHERE corridor_code = 'BYPASS-LAVA';

            UPDATE bypass_corridors
            SET max_tonnage_tonnes = 18.5,
                ruling_gradient_pct = 7.5,
                min_curve_radius_m = 75.0,
                status = 'OPEN'
            WHERE corridor_code = 'BYPASS-MUNGPOO';
        """)

        # 4. Upsert the 4 GLOF-exposed settlements
        print("\n[4] Seeding/Upserting 4 key GLOF-exposed critical habitations...")
        settlements = [
            {
                "name": "Chungthang Sub-Divisional Base",
                "district": "Mangan",
                "population": 6100,
                "primary_road_id": 1,
                "has_functional_phc": True,
                "has_helipad": True,
                "grain_reserve_days": 4,
                "fuel_reserve_days": 2,
                "critical_patients": 8,
                "bed_capacity": 10,
                "helipad_operational_fraction": 1.0,
                "hcii_score": 66.0,
                "hcii_tier": "ACUTE_SHORTAGE_THREATENED",
                "isolation_status": "ISOLATED_AIR_ONLY",
                "lon": 88.6465,
                "lat": 27.6039
            },
            {
                "name": "Dikchu River Settlement",
                "district": "Gangtok",
                "population": 4200,
                "primary_road_id": 1,
                "has_functional_phc": True,
                "has_helipad": False,
                "grain_reserve_days": 6,
                "fuel_reserve_days": 3,
                "critical_patients": 4,
                "bed_capacity": 8,
                "helipad_operational_fraction": 0.0,
                "hcii_score": 65.5,
                "hcii_tier": "ACUTE_SHORTAGE_THREATENED",
                "isolation_status": "THREATENED",
                "lon": 88.5200,
                "lat": 27.3800
            },
            {
                "name": "Mangan District HQ",
                "district": "Mangan",
                "population": 6800,
                "primary_road_id": 1,
                "has_functional_phc": True,
                "has_helipad": True,
                "grain_reserve_days": 9,
                "fuel_reserve_days": 6,
                "critical_patients": 5,
                "bed_capacity": 25,
                "helipad_operational_fraction": 1.0,
                "hcii_score": 28.0,
                "hcii_tier": "MONITORED_WATCH",
                "isolation_status": "NORMAL",
                "lon": 88.5300,
                "lat": 27.5000
            },
            {
                "name": "Dzongu Indigenous Reserve",
                "district": "Mangan",
                "population": 3200,
                "primary_road_id": 1,
                "has_functional_phc": False,
                "has_helipad": False,
                "grain_reserve_days": 3,
                "fuel_reserve_days": 1,
                "critical_patients": 6,
                "bed_capacity": 6,
                "helipad_operational_fraction": 0.0,
                "hcii_score": 91.5,
                "hcii_tier": "CRITICAL_AIR_DROP_REQUIRED",
                "isolation_status": "THREATENED",
                "lon": 88.5400,
                "lat": 27.5300
            }
        ]

        for s in settlements:
            cur.execute("""
                SELECT habitation_id FROM critical_habitations
                WHERE name = %(name)s;
            """, {"name": s["name"]})
            existing = cur.fetchone()

            if existing:
                cur.execute("""
                    UPDATE critical_habitations
                    SET district = %(district)s,
                        population = %(population)s,
                        primary_road_id = %(primary_road_id)s,
                        has_functional_phc = %(has_functional_phc)s,
                        has_helipad = %(has_helipad)s,
                        grain_reserve_days = %(grain_reserve_days)s,
                        fuel_reserve_days = %(fuel_reserve_days)s,
                        critical_patients = %(critical_patients)s,
                        bed_capacity = %(bed_capacity)s,
                        helipad_operational_fraction = %(helipad_operational_fraction)s,
                        hcii_score = %(hcii_score)s,
                        hcii_tier = %(hcii_tier)s,
                        isolation_status = %(isolation_status)s,
                        geom = ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
                    WHERE habitation_id = %(hid)s;
                """, {**s, "hid": existing["habitation_id"]})
                print(f"  [UPDATED] {s['name']} (ID: {existing['habitation_id']}) -> HCII: {s['hcii_score']} [{s['hcii_tier']}]")
            else:
                cur.execute("""
                    INSERT INTO critical_habitations (
                        name, district, population, primary_road_id,
                        has_functional_phc, has_helipad, grain_reserve_days, fuel_reserve_days,
                        critical_patients, bed_capacity, helipad_operational_fraction,
                        hcii_score, hcii_tier, isolation_status, geom
                    ) VALUES (
                        %(name)s, %(district)s, %(population)s, %(primary_road_id)s,
                        %(has_functional_phc)s, %(has_helipad)s, %(grain_reserve_days)s, %(fuel_reserve_days)s,
                        %(critical_patients)s, %(bed_capacity)s, %(helipad_operational_fraction)s,
                        %(hcii_score)s, %(hcii_tier)s, %(isolation_status)s,
                        ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
                    );
                """, s)
                print(f"  [INSERTED] {s['name']} -> HCII: {s['hcii_score']} [{s['hcii_tier']}]")

        conn.commit()
    conn.close()
    print("\n[SUCCESS] Sprint 3 Database Migration Complete.")


if __name__ == "__main__":
    migrate_sprint3()
