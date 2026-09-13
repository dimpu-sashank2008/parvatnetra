#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 8 Automated Verification Suite
Tests Full-Stack Loop Closure & Automated Early Warnings (Problem Statement ID: 26001).

Verifies:
1. GET /api/ml/latest-risk returns HTTP 200 with non-empty ML risk evaluations and road exposure data.
2. POST /api/alerts/broadcast-trigger writes bilingual broadcast to early_warning_broadcasts and returns HTTP 201.
"""

import sys
import json
import requests

# Reconfigure stdout/stderr to UTF-8 for Devanagari / Hindi characters on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

BASE_URL = "http://127.0.0.1:8080"

def test_phase8():
    print("=" * 70)
    print("PARVAT NETRA -- PHASE 8 AUTOMATED VERIFICATION SUITE")
    print("Testing ML Routing, Road Exposure, and Common Alerting Protocol (CAP)")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # TEST 1: GET /api/ml/latest-risk
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Testing GET /api/ml/latest-risk...")
    endpoint_ml = f"{BASE_URL}/api/ml/latest-risk"
    try:
        r1 = requests.get(endpoint_ml, timeout=15)
    except requests.exceptions.ConnectionError as ce:
        print(f"[FAIL] Could not connect to Flask server at {BASE_URL}: {ce}")
        sys.exit(1)

    print(f"  -> HTTP Status Code: {r1.status_code}")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {r1.text}"

    data1 = r1.json()
    assert data1.get("status") == "SUCCESS", f"Status should be SUCCESS, got {data1.get('status')}"
    evaluations = data1.get("evaluations", [])
    print(f"  -> Returned Evaluations: {len(evaluations)} regions")
    assert len(evaluations) > 0, "Evaluations list must not be empty"

    for ev in evaluations:
        region = ev.get("region_name")
        risk_idx = ev.get("risk_index")
        sev = ev.get("severity")
        road = ev.get("lifeline_road", {})
        explain = ev.get("explainability", {})

        print(f"\n     Region: {region} | Risk Index: {risk_idx} | Severity: {sev}")
        print(f"     Lifeline Road: {road.get('road_code')} ({road.get('road_name')})")
        print(f"     Connectivity Status: {road.get('connectivity_status')}")
        print(f"     Road Exposed: {road.get('is_exposed')}")
        print(f"     Explainability: {explain.get('why')}")

        assert region, "region_name must be present"
        assert risk_idx is not None, "risk_index must be present"
        assert sev in ("GREEN", "YELLOW", "ORANGE", "RED"), f"Invalid severity: {sev}"
        assert road.get("road_code") == "NH-10", f"Expected road NH-10, got {road.get('road_code')}"
        assert road.get("is_exposed") is True, f"NH-10 should intersect buffer for {region}"
        assert "Debris Blockage" in road.get("connectivity_status"), "Connectivity status must reflect risk"
        assert explain.get("why"), "Multimodal explainability 'why' string must be present"

    print("\n[PASS] TEST 1: GET /api/ml/latest-risk verified with road exposure and explainability.")

    # -------------------------------------------------------------------------
    # TEST 2: POST /api/alerts/broadcast-trigger
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing POST /api/alerts/broadcast-trigger...")
    endpoint_alert = f"{BASE_URL}/api/alerts/broadcast-trigger"
    alert_payload = {
        "region_name": "Gangtok Corridor",
        "severity": "ORANGE"
    }
    r2 = requests.post(endpoint_alert, json=alert_payload, timeout=15)
    print(f"  -> HTTP Status Code: {r2.status_code}")
    assert r2.status_code == 201, f"Expected 201, got {r2.status_code}: {r2.text}"

    data2 = r2.json()
    assert data2.get("status") == "SUCCESS", f"Status should be SUCCESS, got {data2.get('status')}"
    alert = data2.get("alert", {})
    assert alert, "Alert payload must not be empty"

    alert_id = alert.get("alert_id")
    region_name = alert.get("region_name")
    severity = alert.get("severity")
    msg_en = alert.get("message_en")
    msg_hi = alert.get("message_hi")
    channels = alert.get("channels")
    status = alert.get("status")

    print(f"  -> Dispatched Alert ID: #{alert_id}")
    print(f"  -> Region: {region_name} | Severity: {severity} | Status: {status}")
    print(f"  -> Channels: {channels}")
    print(f"  -> English Message: {msg_en}")
    print(f"  -> Hindi Message: {msg_hi}")

    assert alert_id is not None and alert_id > 0, "Alert ID must be a positive integer"
    assert region_name == "Gangtok Corridor", f"Region mismatch: {region_name}"
    assert severity == "ORANGE", f"Severity mismatch: {severity}"
    assert "WARNING:" in msg_en, "English message must follow NDMA CAP warning format"
    assert "Gangtok Corridor" in msg_en, "English message must contain region name"
    assert "चेतावनी:" in msg_hi, "Hindi message must follow NDMA CAP warning format"
    assert "Gangtok Corridor" in msg_hi, "Hindi message must contain region name"
    assert "SMS" in channels and "CELL_BROADCAST" in channels, "Channels must include SMS and CELL_BROADCAST"
    assert status == "DISPATCHED", f"Status must be DISPATCHED, got {status}"

    print("\n[PASS] TEST 2: POST /api/alerts/broadcast-trigger successfully generated bilingual CAP alert.")

    print("\n" + "=" * 70)
    print("ALL PHASE 8 VERIFICATION TESTS PASSED SUCCESSFULLY! (HTTP 200 & HTTP 201)")
    print("=" * 70)

if __name__ == "__main__":
    test_phase8()
