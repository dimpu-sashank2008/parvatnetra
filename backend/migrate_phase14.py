#!/usr/bin/env python3
"""
PARVAT NETRA -- Database Migration: Phase 14
Creates or updates tables for:
  1. field_reports (Citizen/official crowdsourced incident reports with CV crack triage and Point geometry)
Creates GIST spatial index on geom, B-Tree index on cluster_id, and seeds 3 benchmark incident reports.
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

    try:
        # 1. Ensure table field_reports exists
        print("Ensuring table 'field_reports' exists with Phase 14 schema...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS field_reports (
                report_id SERIAL PRIMARY KEY,
                reporter_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                latitude NUMERIC NOT NULL,
                longitude NUMERIC NOT NULL,
                cv_crack_type TEXT,
                cv_confidence_pct NUMERIC,
                cv_aperture_mm NUMERIC,
                triage_priority TEXT,
                cluster_id INTEGER DEFAULT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                geom GEOMETRY(Point, 4326)
            );
        """)

        # Add missing columns if field_reports was already created previously
        columns_to_add = [
            ("cv_crack_type", "TEXT CHECK (cv_crack_type IN ('TENSION_CRACK', 'ROAD_SUBSIDENCE', 'DEBRIS_CONE', 'NONE_DETECTED'))"),
            ("cv_confidence_pct", "NUMERIC"),
            ("cv_aperture_mm", "NUMERIC"),
            ("triage_priority", "TEXT CHECK (triage_priority IN ('IMMEDIATE_CLOSURE', 'INSPECT_24H', 'MONITOR', 'UNVERIFIED'))"),
            ("cluster_id", "INTEGER DEFAULT NULL"),
            ("submitted_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("geom", "GEOMETRY(Point, 4326)")
        ]

        for col_name, col_def in columns_to_add:
            cur.execute("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'field_reports' AND column_name = %s;
            """, (col_name,))
            if not cur.fetchone():
                print(f"Adding column '{col_name}' to field_reports...")
                cur.execute(f"ALTER TABLE field_reports ADD COLUMN {col_name} {col_def};")

        # If geom is NULL for any older rows, populate from latitude/longitude
        cur.execute("""
            UPDATE field_reports 
            SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
            WHERE geom IS NULL AND latitude IS NOT NULL AND longitude IS NOT NULL;
        """)

        # 2. Indexes
        print("Creating GIST spatial index and B-Tree cluster index...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_field_reports_geom 
            ON field_reports USING GIST (geom);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_field_reports_cluster_id 
            ON field_reports (cluster_id);
        """)

        # 3. Seed 3 High-Fidelity Incident Benchmarks along NH-10
        print("Seeding 3 high-fidelity benchmark field reports along NH-10...")
        seeds = [
            (
                'Constable Tashi Lepcha',
                '9800112233',
                'CRITICAL',
                'Transverse asphalt fissure opening across Singtam road cut section',
                'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600',
                27.151,
                88.498,
                'TENSION_CRACK',
                94.2,
                45.0,
                'IMMEDIATE_CLOSURE'
            ),
            (
                'Pemba Bhutia (Panchayat)',
                '9800223344',
                'CRITICAL',
                'Deep fissure widening on edge of road near Singtam',
                'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600',
                27.152,
                88.499,
                'TENSION_CRACK',
                91.0,
                40.0,
                'IMMEDIATE_CLOSURE'
            ),
            (
                'Driver Rajesh Gurung',
                '9800334455',
                'MODERATE',
                'Minor gravel slide blocking inner mountain lane at 29th Mile',
                'https://images.unsplash.com/photo-1517649763962-0c623266ddc0?w=600',
                27.081,
                88.472,
                'DEBRIS_CONE',
                87.5,
                12.0,
                'INSPECT_24H'
            )
        ]

        for s in seeds:
            cur.execute("""
                SELECT report_id FROM field_reports 
                WHERE reporter_name = %s AND phone = %s;
            """, (s[0], s[1]))
            existing = cur.fetchone()
            if not existing:
                cur.execute("""
                    INSERT INTO field_reports (
                        reporter_name, phone, severity, description, image_url,
                        latitude, longitude, cv_crack_type, cv_confidence_pct,
                        cv_aperture_mm, triage_priority, geom
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    );
                """, (
                    s[0], s[1], s[2], s[3], s[4],
                    s[5], s[6], s[7], s[8],
                    s[9], s[10], s[6], s[5]
                ))
            else:
                # Update with Phase 14 benchmark parameters
                cur.execute("""
                    UPDATE field_reports SET
                        severity = %s,
                        description = %s,
                        image_url = %s,
                        latitude = %s,
                        longitude = %s,
                        cv_crack_type = %s,
                        cv_confidence_pct = %s,
                        cv_aperture_mm = %s,
                        triage_priority = %s,
                        geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    WHERE report_id = %s;
                """, (
                    s[2], s[3], s[4], s[5], s[6],
                    s[7], s[8], s[9], s[10],
                    s[6], s[5], existing[0]
                ))

        conn.commit()

        # Verification count
        cur.execute("SELECT COUNT(*) FROM field_reports;")
        count = cur.fetchone()[0]
        print(f"[SUCCESS] Phase 14 migration complete. Total field reports in database: {count}")

        # List seeded reports
        cur.execute("""
            SELECT report_id, reporter_name, severity, cv_crack_type, cv_aperture_mm, triage_priority 
            FROM field_reports 
            WHERE reporter_name IN ('Constable Tashi Lepcha', 'Pemba Bhutia (Panchayat)', 'Driver Rajesh Gurung')
            ORDER BY report_id;
        """)
        rows = cur.fetchall()
        print("Seeded Benchmarks:")
        for r in rows:
            print(f"  ID #{r[0]}: {r[1]} | {r[2]} | {r[3]} | {r[4]} mm | {r[5]}")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    run_migration()
