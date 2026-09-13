import os
import sys
import psycopg2

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

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("Upgrading ml_risk_scores table schema with 5-modality audit columns...")
cur.execute("""
    ALTER TABLE ml_risk_scores 
    ADD COLUMN IF NOT EXISTS slope_factor NUMERIC,
    ADD COLUMN IF NOT EXISTS rain_factor NUMERIC,
    ADD COLUMN IF NOT EXISTS vwc_factor NUMERIC,
    ADD COLUMN IF NOT EXISTS insar_factor NUMERIC,
    ADD COLUMN IF NOT EXISTS soil_multiplier NUMERIC,
    ADD COLUMN IF NOT EXISTS explainability_why TEXT;
""")
conn.commit()

cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'ml_risk_scores'
    ORDER BY ordinal_position;
""")
cols = cur.fetchall()
print("ml_risk_scores columns:")
for col in cols:
    print(f"  - {col[0]}: {col[1]}")

cur.close()
conn.close()
print("ml_risk_scores table upgraded successfully.")
