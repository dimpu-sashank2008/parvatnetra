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
conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
cur = conn.cursor()

# 1. Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS early_warning_broadcasts (
    alert_id SERIAL PRIMARY KEY,
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity TEXT CHECK (severity IN ('YELLOW', 'ORANGE', 'RED')),
    region_name TEXT NOT NULL,
    cap_event TEXT NOT NULL,
    message_en TEXT NOT NULL,
    message_hi TEXT NOT NULL,
    channels TEXT[] DEFAULT ARRAY['SMS', 'CELL_BROADCAST', 'APP_PUSH'],
    status TEXT DEFAULT 'DISPATCHED'
);
""")
conn.commit()

# 2. Inspect columns
cur.execute("""
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'early_warning_broadcasts'
ORDER BY ordinal_position;
""")
cols = cur.fetchall()
print("EARLY_WARNING_BROADCASTS SCHEMA:")
for c in cols:
    print(f"  - {c['column_name']}: {c['data_type']} (nullable: {c['is_nullable']})")

cur.close()
conn.close()
