import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# UTF-8 for console
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

load_env()
db_url = os.environ.get("NEON_DB_URL") or os.environ.get("DATABASE_URL")
if not db_url:
    print("[ERROR] NEON_DB_URL not configured.")
    sys.exit(1)

conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
cur = conn.cursor()

print("=" * 75)
print("PARVAT NETRA -- PHASE 9 STEP 1: IOT & INSAR DATABASE MIGRATION")
print("=" * 75)

# --- 1. DDL: iot_sensors ---
print("\n[DDL 1] Creating iot_sensors table & GIST index...")
cur.execute("""
CREATE TABLE IF NOT EXISTS iot_sensors (
    sensor_id TEXT PRIMARY KEY,
    sensor_type TEXT CHECK (sensor_type IN ('SOIL_MOISTURE_VWC', 'PORE_PRESSURE', 'TILT_INCLINOMETER', 'RAIN_GAUGE')),
    location_name TEXT NOT NULL,
    district TEXT NOT NULL,
    depth_meters NUMERIC DEFAULT 1.0,
    battery_pct INTEGER DEFAULT 100,
    status TEXT DEFAULT 'ONLINE' CHECK (status IN ('ONLINE', 'WARNING', 'OFFLINE')),
    geom GEOMETRY(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_iot_sensors_geom ON iot_sensors USING GIST (geom);
""")
conn.commit()

# --- 2. DDL: sensor_telemetry ---
print("[DDL 2] Creating sensor_telemetry table...")
cur.execute("""
CREATE TABLE IF NOT EXISTS sensor_telemetry (
    reading_id SERIAL PRIMARY KEY,
    sensor_id TEXT REFERENCES iot_sensors(sensor_id) ON DELETE CASCADE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value NUMERIC NOT NULL,
    unit TEXT NOT NULL,
    is_critical BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_sensor_telemetry_sensor_id ON sensor_telemetry (sensor_id);
CREATE INDEX IF NOT EXISTS idx_sensor_telemetry_recorded_at ON sensor_telemetry (recorded_at DESC);
""")
conn.commit()

# --- 3. DDL: insar_deformation ---
print("[DDL 3] Creating insar_deformation table & GIST index...")
cur.execute("""
CREATE TABLE IF NOT EXISTS insar_deformation (
    point_id SERIAL PRIMARY KEY,
    mission TEXT DEFAULT 'SENTINEL-1',
    location_name TEXT NOT NULL,
    district TEXT NOT NULL,
    los_velocity_mm_yr NUMERIC NOT NULL,
    cumulative_disp_mm NUMERIC NOT NULL,
    coherence NUMERIC CHECK (coherence >= 0.0 AND coherence <= 1.0),
    last_pass_date DATE DEFAULT CURRENT_DATE,
    geom GEOMETRY(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_insar_deformation_geom ON insar_deformation USING GIST (geom);
""")
conn.commit()

# --- 4. SEED: iot_sensors ---
print("\n[SEED 1] Seeding iot_sensors benchmarks...")
sensors = [
    ('IOT-SK-VWC-01', 'SOIL_MOISTURE_VWC', 'Singtam Hill Cut Section', 'Pakyong', 1.5, 96, 'ONLINE', 'POINT(88.49 27.15)'),
    ('IOT-SK-TILT-02', 'TILT_INCLINOMETER', 'Rangpo Toll Bridge Slope', 'Pakyong', 2.0, 92, 'WARNING', 'POINT(88.53 27.20)'),
    ('IOT-SK-VWC-03', 'SOIL_MOISTURE_VWC', 'Tathangchen Upper Catchment', 'Gangtok', 1.0, 99, 'ONLINE', 'POINT(88.62 27.34)')
]

for s_id, s_type, loc, dist, depth, batt, status, geom_wkt in sensors:
    cur.execute("""
        INSERT INTO iot_sensors (sensor_id, sensor_type, location_name, district, depth_meters, battery_pct, status, geom)
        VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
        ON CONFLICT (sensor_id) DO UPDATE SET
            sensor_type = EXCLUDED.sensor_type,
            location_name = EXCLUDED.location_name,
            district = EXCLUDED.district,
            depth_meters = EXCLUDED.depth_meters,
            geom = EXCLUDED.geom;
    """, (s_id, s_type, loc, dist, depth, batt, status, geom_wkt))
conn.commit()

# --- 5. SEED: insar_deformation ---
print("[SEED 2] Seeding insar_deformation Persistent Scatterer (PS-InSAR) benchmarks...")
insar_points = [
    ('Singtam Active Scarp', 'Pakyong', -18.4, -6.2, 0.88, 'POINT(88.495 27.155)'),
    ('Rangpo Creep Zone', 'Pakyong', -24.1, -9.8, 0.91, 'POINT(88.528 27.202)'),
    ('Gangtok Ridge Crest', 'Gangtok', -4.2, -1.1, 0.95, 'POINT(88.618 27.338)')
]

# Clean previously seeded points with same location_names to keep seed clean & idempotent
for loc, dist, los_vel, cum_disp, coh, geom_wkt in insar_points:
    cur.execute("DELETE FROM insar_deformation WHERE location_name = %s;", (loc,))
    cur.execute("""
        INSERT INTO insar_deformation (mission, location_name, district, los_velocity_mm_yr, cumulative_disp_mm, coherence, geom)
        VALUES ('SENTINEL-1', %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326));
    """, (loc, dist, los_vel, cum_disp, coh, geom_wkt))
conn.commit()

# --- 6. SEED: sensor_telemetry ---
print("[SEED 3] Seeding initial baseline sensor_telemetry...")
telemetry_data = [
    ('IOT-SK-VWC-01', 48.2, '% VWC', False),
    ('IOT-SK-TILT-02', 3.8, 'deg', True),
    ('IOT-SK-VWC-03', 38.0, '% VWC', False)
]

for s_id, val, unit, is_crit in telemetry_data:
    cur.execute("""
        INSERT INTO sensor_telemetry (sensor_id, value, unit, is_critical)
        VALUES (%s, %s, %s, %s);
    """, (s_id, val, unit, is_crit))
conn.commit()

print("\n[SUCCESS] Migration and seeding executed successfully.")

cur.close()
conn.close()
