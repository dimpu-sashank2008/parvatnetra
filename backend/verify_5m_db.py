import os
import psycopg2
from psycopg2.extras import RealDictCursor

def load_env(filepath='.env'):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()
conn = psycopg2.connect(os.environ['NEON_DB_URL'], cursor_factory=RealDictCursor)
cur = conn.cursor()
cur.execute("""
    SELECT id, region_name, risk_index, severity_label, slope_factor, rain_factor, vwc_factor, insar_factor, soil_multiplier, explainability_why 
    FROM ml_risk_scores 
    ORDER BY id DESC 
    LIMIT 2;
""")
rows = cur.fetchall()
for r in rows:
    print(dict(r))
cur.close()
conn.close()
