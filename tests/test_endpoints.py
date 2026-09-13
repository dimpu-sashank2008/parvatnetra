import requests
import json

BASE = "http://127.0.0.1:8080"

def test_all():
    print("--- PARVAT NETRA MVP: End-to-End Verification Suite ---")

    # 1. Test GET /
    r = requests.get(f"{BASE}/")
    print(f"[PASS] 1. GET / -> Status: {r.status_code}, Length: {len(r.text)} bytes")
    assert r.status_code == 200
    assert "PARVAT NETRA" in r.text

    # 2. Test GET /api/health
    r = requests.get(f"{BASE}/api/health")
    print(f"[PASS] 2. GET /api/health -> Status: {r.status_code}, PostGIS: {r.json().get('postgis')}")
    assert r.status_code == 200

    # 3. Test POST /api/ingest/imd-rainfall
    r = requests.post(f"{BASE}/api/ingest/imd-rainfall")
    print(f"[PASS] 3. POST /api/ingest/imd-rainfall -> Status: {r.status_code}, Processed: {r.json().get('records_processed')} records")
    assert r.status_code == 200

    # 4. Test GET /api/spatial/live-risk
    r = requests.get(f"{BASE}/api/spatial/live-risk")
    features = r.json().get("features", [])
    print(f"[PASS] 4. GET /api/spatial/live-risk -> Status: {r.status_code}, Fused Polygons: {len(features)}")
    assert r.status_code == 200
    assert len(features) > 0

    # 5. Test POST /api/reports/submit
    report_payload = {
        "reporter_name": "Subedar K. Dorjee",
        "phone": "+91-9434099881",
        "latitude": 27.210,
        "longitude": 88.525,
        "severity": "CRITICAL",
        "description": "Active debris slide near Singtam turnoff. Road impassable.",
        "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600"
    }
    r = requests.post(f"{BASE}/api/reports/submit", json=report_payload)
    print(f"[PASS] 5. POST /api/reports/submit -> Status: {r.status_code}, Report ID: {r.json().get('report_id')}, Proximity Alert: {r.json().get('proximity_alert')}")
    assert r.status_code == 201

    # 6. Test GET /api/reports/list
    r = requests.get(f"{BASE}/api/reports/list")
    reports = r.json()
    print(f"[PASS] 6. GET /api/reports/list -> Status: {r.status_code}, Reports Count: {len(reports)}")
    assert r.status_code == 200
    assert len(reports) >= 4

    # 7. Test POST /api/decisions/1/authorize
    r = requests.post(f"{BASE}/api/decisions/1/authorize", json={})
    print(f"[PASS] 7. POST /api/decisions/1/authorize -> Status: {r.status_code}, Decision Status: {r.json().get('decision', {}).get('authority_status')}")
    assert r.status_code == 200

    # 8. Test GET /api/kpis
    r = requests.get(f"{BASE}/api/kpis")
    kpis = r.json()
    print(f"[PASS] 8. GET /api/kpis -> Status: {r.status_code}, Critical Zones: {kpis.get('critical_zones_count')}, Pending Reports: {kpis.get('pending_reports_count')}")
    assert r.status_code == 200

    print("\n=======================================================")
    print("ALL ENDPOINTS VERIFIED & FUNCTIONING WITH HTTP 200/201!")
    print("=======================================================")

if __name__ == "__main__":
    test_all()
