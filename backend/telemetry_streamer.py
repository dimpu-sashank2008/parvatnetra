#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 9 Step 2: Geotechnical Telemetry Streamer
Simulates realistic in-situ geotechnical telemetry responses (Volumetric Water Content,
Borehole Tilt/Inclinometer shear) coupled to antecedent rainfall infiltration.
"""

import os
import sys
import random
from datetime import datetime
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

class GeotechnicalTelemetryStreamer:
    def __init__(self):
        load_env()
        self.db_url = os.environ.get("NEON_DB_URL") or os.environ.get("DATABASE_URL")
        if not self.db_url:
            print("[ERROR] NEON_DB_URL not configured.")
            sys.exit(1)

    def get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def fetch_regional_rainfall(self):
        """Fetches latest observed rainfall for monitored districts."""
        rainfall_map = {}
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT district, MAX(rainfall_mm)::float AS rain_mm
                    FROM raw_rainfall
                    GROUP BY district;
                """)
                for row in cur.fetchall():
                    rainfall_map[row['district'].lower()] = float(row['rain_mm'])
        return rainfall_map

    def fetch_sensors(self):
        """Fetches all registered IoT sensors."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT sensor_id, sensor_type, location_name, district, battery_pct, status,
                           ST_AsText(geom) AS geom_wkt
                    FROM iot_sensors
                    ORDER BY sensor_id;
                """)
                return cur.fetchall()

    def stream_cycle(self):
        """Runs a complete telemetry acquisition & infiltration simulation cycle."""
        print("=" * 76)
        print("PARVAT NETRA -- GEOTECHNICAL TELEMETRY STREAMER CYCLE")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')} | Provenance: [SIMULATED]")
        print("=" * 76)

        rainfall_map = self.fetch_regional_rainfall()
        sensors = self.fetch_sensors()
        readings_generated = []

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                for s in sensors:
                    s_id = s['sensor_id']
                    s_type = s['sensor_type']
                    loc = s['location_name']
                    dist = s['district']
                    curr_batt = s['battery_pct']

                    district_key = dist.lower()
                    rain_mm = rainfall_map.get(district_key, 50.0)

                    if s_type == 'SOIL_MOISTURE_VWC':
                        # Volumetric Water Content calculation based on rainfall infiltration
                        # Base dry VWC ~32%. When rain > 50mm, saturation increases into 48-56%
                        variation = round(random.uniform(-0.8, 0.8), 2)
                        if rain_mm > 50.0:
                            # Elevated moisture zone
                            calculated_vwc = round(32.0 + ((rain_mm - 30.0) * 0.72) + variation, 1)
                            calculated_vwc = max(48.2, min(56.4, calculated_vwc))
                        else:
                            calculated_vwc = round(32.0 + (rain_mm * 0.25) + variation, 1)

                        value = calculated_vwc
                        unit = '% VWC'
                        is_critical = (value >= 50.0)

                    elif s_type == 'TILT_INCLINOMETER':
                        # Borehole shear displacement simulation (2.8 to 4.2 deg)
                        value = round(random.uniform(2.85, 4.15), 2)
                        unit = 'deg'
                        is_critical = (value >= 3.0)

                    else:
                        # Generic sensor fallback
                        value = round(rain_mm, 1)
                        unit = 'mm'
                        is_critical = False

                    # Determine new sensor status
                    new_status = 'WARNING' if is_critical else 'ONLINE'

                    # Simulate battery degradation (decrement slightly, floor at 85%)
                    new_battery = max(85, curr_batt - (1 if random.random() < 0.3 else 0))

                    # 1. Insert telemetry reading
                    cur.execute("""
                        INSERT INTO sensor_telemetry (sensor_id, value, unit, is_critical)
                        VALUES (%s, %s, %s, %s)
                        RETURNING reading_id, recorded_at;
                    """, (s_id, value, unit, is_critical))
                    telemetry_row = cur.fetchone()

                    # 2. Update sensor status and battery
                    cur.execute("""
                        UPDATE iot_sensors
                        SET status = %s, battery_pct = %s
                        WHERE sensor_id = %s;
                    """, (new_status, new_battery, s_id))

                    readings_generated.append({
                        "reading_id": telemetry_row['reading_id'],
                        "sensor_id": s_id,
                        "sensor_type": s_type,
                        "location_name": loc,
                        "district": dist,
                        "value": value,
                        "unit": unit,
                        "is_critical": is_critical,
                        "status": new_status,
                        "battery_pct": new_battery,
                        "rainfall_ref_mm": rain_mm
                    })

                conn.commit()

        # Display clean structured ASCII console report
        for r in readings_generated:
            crit_flag = "CRITICAL EXCEEDANCE" if r['is_critical'] else "NORMAL"
            status_flag = f"[{r['status']}]"
            print(f"\n  * Node {r['sensor_id']} ({r['sensor_type']}):")
            print(f"      Location     : {r['location_name']}, {r['district']}")
            print(f"      Rainfall Ref : {r['rainfall_ref_mm']:.1f} mm")
            print(f"      Observation  : {r['value']} {r['unit']} ({crit_flag})")
            print(f"      Node Health  : {status_flag} | Battery: {r['battery_pct']}%")

        print("\n" + "=" * 76)
        print(f"Successfully generated and committed {len(readings_generated)} sensor telemetry readings.")
        print("=" * 76 + "\n")
        return readings_generated

if __name__ == "__main__":
    streamer = GeotechnicalTelemetryStreamer()
    streamer.stream_cycle()
