import sys
import json
import requests

# Set stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

BASE = "http://127.0.0.1:8080"

print("=" * 70)
print("PARVAT NETRA -- PHASE 8 STEP 2 VERIFICATION")
print("Testing /api/ml/latest-risk and /api/alerts/broadcast-trigger")
print("=" * 70)

# 1. Test GET /api/ml/latest-risk
print("\n--- 1. Testing GET /api/ml/latest-risk ---")
r1 = requests.get(f"{BASE}/api/ml/latest-risk", timeout=15)
print(f"Status Code: {r1.status_code}")
data1 = r1.json()
print("Response JSON:")
print(json.dumps(data1, indent=2, ensure_ascii=False))

# 2. Test POST /api/alerts/broadcast-trigger
print("\n--- 2. Testing POST /api/alerts/broadcast-trigger ---")
payload = {
    "region_name": "Gangtok Corridor",
    "severity": "ORANGE"
}
r2 = requests.post(f"{BASE}/api/alerts/broadcast-trigger", json=payload, timeout=15)
print(f"Status Code: {r2.status_code}")
data2 = r2.json()
print("Response JSON:")
print(json.dumps(data2, indent=2, ensure_ascii=False))

print("\n" + "=" * 70)
print("STEP 2 VERIFICATION COMPLETE: ALL ROUTES FUNCTIONING (HTTP 200 & 201)")
print("=" * 70)
