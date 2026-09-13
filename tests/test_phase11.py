#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 11 Automated Verification Suite
Validates Deep Learning Multi-Spectral Landslide Detection, PostGIS Scars Persistence,
REST APIs, 4-Language Indigenous CAP Alerting Matrix, and Web Speech Audio Synthesis.
"""

import sys
import os
import json
import requests

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.dl_landslide_detector import get_db_connection, MultiSpectralLandslideDetector

BASE_URL = "http://127.0.0.1:8080"

def test_phase11():
    print("=" * 80)
    print("PARVAT NETRA -- PHASE 11 AUTOMATED VERIFICATION SUITE")
    print("Deep Learning Multi-Spectral Landslide Detection & Indigenous Voice Broadcast")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PART 1: DL LANDSLIDE DETECTION ENGINE & POSTGIS PERSISTENCE
    # -------------------------------------------------------------------------
    print("\n[PART 1] Running Multi-Spectral U-Net Landslide Detection Pipeline...")
    conn = get_db_connection()
    detector = MultiSpectralLandslideDetector(conn)
    scars = detector.run_detection_pipeline()

    print(f"  -> Detected AI Scar Clusters: {len(scars)}")
    assert len(scars) >= 3, f"Expected at least 3 detected scars, got {len(scars)}"

    blocked_count = 0
    for s in scars:
        print(f"     Scar #{s['scar_id']}: {s['corridor_name']}")
        print(f"       Area: {s['area_sq_m']} m2 | Conf: {s['confidence_pct']}% | NH-10 Blocked: {s['is_road_blocked']}")
        assert s["area_sq_m"] > 1000.0, f"Area should be realistic, got {s['area_sq_m']}"
        assert 70.0 <= s["confidence_pct"] <= 100.0, f"Confidence out of bounds: {s['confidence_pct']}"
        assert s["geojson"]["type"] == "Polygon", f"Expected Polygon GeoJSON, got {s['geojson']['type']}"
        if s["is_road_blocked"]:
            blocked_count += 1

    assert blocked_count >= 1, "Expected at least 1 scar intersecting/blocking lifeline road NH-10"

    # Verify directly in PostGIS
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM ai_detected_scars;")
        db_count = cur.fetchone()[0]
    conn.close()

    print(f"  -> PostGIS Table `ai_detected_scars` Verified: {db_count} records.")
    assert db_count >= 3, f"Expected >= 3 records in DB, found {db_count}"
    print("[PASS] PART 1: DL Landslide Detection Engine & PostGIS Persistence Verified.")

    # -------------------------------------------------------------------------
    # PART 2: REST ENDPOINT GET /api/satellite/detected-scars
    # -------------------------------------------------------------------------
    print("\n[PART 2] Testing GET /api/satellite/detected-scars...")
    r1 = requests.get(f"{BASE_URL}/api/satellite/detected-scars", timeout=15)
    print(f"  -> HTTP Status Code: {r1.status_code}")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {r1.text}"

    data1 = r1.json()
    assert data1.get("status") == "SUCCESS", f"Expected SUCCESS, got {data1.get('status')}"
    api_scars = data1.get("scars", [])
    print(f"  -> Returned Scars: {len(api_scars)}")
    assert len(api_scars) >= 3, f"Expected >= 3 scars from API, got {len(api_scars)}"

    for scar in api_scars:
        geom = scar.get("geometry", {})
        assert geom.get("type") == "Polygon", f"Invalid geometry type: {geom.get('type')}"
        coords = geom.get("coordinates", [[]])[0]
        assert len(coords) >= 4, f"Polygon must have at least 4 coordinate vertices, got {len(coords)}"
        print(f"     Verified: {scar['corridor_name']} | Conf: {scar['confidence_pct']}% | Blocked: {scar['is_road_blocked']}")

    print("[PASS] PART 2: GET /api/satellite/detected-scars verified with GeoJSON polygons.")

    # -------------------------------------------------------------------------
    # PART 3: 4-LANGUAGE INDIGENOUS CAP BROADCAST DISPATCHER
    # -------------------------------------------------------------------------
    print("\n[PART 3] Testing POST /api/alerts/broadcast-trigger (4-Language Indigenous Matrix)...")
    payload = {
        "region_name": "Rangpo Scarp (NH-10 Km 48)",
        "severity": "RED"
    }
    r2 = requests.post(f"{BASE_URL}/api/alerts/broadcast-trigger", json=payload, timeout=15)
    print(f"  -> HTTP Status Code: {r2.status_code}")
    assert r2.status_code == 201, f"Expected 201, got {r2.status_code}: {r2.text}"

    data2 = r2.json()
    assert data2.get("status") == "SUCCESS", f"Expected SUCCESS, got {data2.get('status')}"
    alert = data2.get("alert", {})

    print(f"  -> Dispatched Alert ID: #{alert.get('alert_id')}")
    print(f"  -> Region: {alert.get('region_name')} | Severity: {alert.get('severity')}")
    print(f"  -> Voice Synthesizer Text: {alert.get('voice_text')}")

    # Validate English message
    msg_en = alert.get("message_en", "")
    print(f"     [EN]: {msg_en}")
    assert "WARNING" in msg_en and "Rangpo Scarp" in msg_en, "Invalid English CAP message"

    # Validate Hindi message
    msg_hi = alert.get("message_hi", "")
    print(f"     [HI]: {msg_hi}")
    assert "चेतावनी" in msg_hi and "Rangpo Scarp" in msg_hi, "Invalid Hindi CAP message"

    # Validate Nepali message
    msg_ne = alert.get("message_ne", "")
    print(f"     [NE]: {msg_ne}")
    assert "पहिरोको" in msg_ne and "Rangpo Scarp" in msg_ne, "Invalid Nepali CAP message"

    # Validate Assamese message
    msg_as = alert.get("message_as", "")
    print(f"     [AS]: {msg_as}")
    assert "ভূমিস্খলনৰ" in msg_as and "Rangpo Scarp" in msg_as, "Invalid Assamese CAP message"

    assert alert.get("voice_text"), "Voice text field must not be empty"

    print("[PASS] PART 3: 4-Language Indigenous Alert Matrix (EN, HI, NE, AS) successfully dispatched.")

    # -------------------------------------------------------------------------
    # PART 4: FRONTEND GIS ASSETS & WEB SPEECH INTEGRATION (GET /)
    # -------------------------------------------------------------------------
    print("\n[PART 4] Testing GET / (GIS Console & Web Speech Integration)...")
    r3 = requests.get(f"{BASE_URL}/", timeout=15)
    print(f"  -> HTTP Status Code: {r3.status_code}")
    assert r3.status_code == 200, f"Expected 200, got {r3.status_code}"

    html = r3.text

    # Verify AI Scars Layer UI & handlers
    assert "toggle-scars-btn" in html, "Missing DOM element: toggle-scars-btn"
    assert "toggleScarsLayer" in html, "Missing JS function: toggleScarsLayer"
    assert "loadAISatelliteScars" in html, "Missing JS function: loadAISatelliteScars"
    assert "scarsLayerGroup" in html, "Missing Leaflet layer group: scarsLayerGroup"
    print("  -> Verified: Leaflet AI Scars Layer, Toggle Button, and Ingestion Handler.")

    # Verify 4-Language Modal and Web Speech elements
    assert "cap-text-ne" in html, "Missing Nepali alert DOM element: cap-text-ne"
    assert "cap-text-as" in html, "Missing Assamese alert DOM element: cap-text-as"
    assert "btn-play-voice" in html, "Missing voice play button: btn-play-voice"
    assert "playVoiceAlert" in html, "Missing JS function: playVoiceAlert"
    assert "speechSynthesis" in html, "Missing Web Speech API call: speechSynthesis"
    assert "SpeechSynthesisUtterance" in html, "Missing SpeechSynthesisUtterance constructor"
    print("  -> Verified: 4-Language Modal Cards & Web Speech API Voice Synthesizer.")

    print("[PASS] PART 4: Frontend GIS Console & Indigenous Audio Broadcast Integration Verified.")

    print("\n" + "=" * 80)
    print("ALL PHASE 11 AUTOMATED VERIFICATION TESTS PASSED SUCCESSFULLY! (HTTP 200 & 201)")
    print("=" * 80)

if __name__ == "__main__":
    test_phase11()
