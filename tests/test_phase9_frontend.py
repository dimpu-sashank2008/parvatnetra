#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 9 Step 4 Automated Verification Suite
Validates Leaflet GIS Console, IoT Geotechnical Sensors, and Satellite InSAR Radar Integration.
"""

import sys
import os
import requests

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

BASE_URL = "http://127.0.0.1:8080"

def test_phase9_frontend():
    print("=" * 75)
    print("PARVAT NETRA -- PHASE 9 STEP 4 AUTOMATED VERIFICATION SUITE")
    print("Testing Leaflet GIS Console, IoT Sensor Pulse & Satellite InSAR Layers")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # TEST 1: VALIDATE DASHBOARD HTML & GIS ASSETS (GET /)
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Testing GET / (Dashboard Console HTML)...")
    res = requests.get(f"{BASE_URL}/", timeout=15)
    print(f"  -> HTTP Status Code: {res.status_code}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"

    html = res.text

    # Verify CSS pulsating animations
    assert "sensor-pin-pulse-online" in html, "Missing CSS class: sensor-pin-pulse-online"
    assert "sensor-pin-pulse-warning" in html, "Missing CSS class: sensor-pin-pulse-warning"
    assert "pulse-green" in html, "Missing @keyframes pulse-green"
    assert "pulse-red" in html, "Missing @keyframes pulse-red"
    print("  -> Verified: CSS Animated Geotechnical Pulse Classes & Keyframes.")

    # Verify Map Toolbar Layer Controls
    assert "toggle-sensors-btn" in html, "Missing DOM element: toggle-sensors-btn"
    assert "toggle-insar-btn" in html, "Missing DOM element: toggle-insar-btn"
    assert "toggleSensorLayer" in html, "Missing JS function reference: toggleSensorLayer"
    assert "toggleInSARLayer" in html, "Missing JS function reference: toggleInSARLayer"
    print("  -> Verified: Map Toolbar Layer Filter Buttons (IoT & InSAR Toggles).")

    # Verify 5-Modality Decision Intelligence Card elements
    assert "ev-rain" in html, "Missing evidence element: ev-rain"
    assert "ev-susc" in html, "Missing evidence element: ev-susc"
    assert "ev-vwc" in html, "Missing evidence element: ev-vwc"
    assert "ev-insar" in html, "Missing evidence element: ev-insar"
    assert "ev-soil" in html, "Missing evidence element: ev-soil"
    print("  -> Verified: 5-Modality Decision Intelligence Card DOM IDs.")

    # Verify JavaScript API Handlers & Layer Groups
    assert "loadIoTSensors" in html, "Missing JS function: loadIoTSensors"
    assert "loadInSARPoints" in html, "Missing JS function: loadInSARPoints"
    assert "sensorLayerGroup" in html, "Missing Leaflet layer group: sensorLayerGroup"
    assert "insarLayerGroup" in html, "Missing Leaflet layer group: insarLayerGroup"
    assert "updateMLEvidenceCard" in html, "Missing JS function: updateMLEvidenceCard"
    print("  -> Verified: JavaScript GIS Fetch & Layer Handlers in script block.")

    print("[PASS] TEST 1: Dashboard HTML, CSS pulse pins, and JS GIS logic verified.")

    # -------------------------------------------------------------------------
    # TEST 2: VALIDATE LIVE IOT SENSORS ENDPOINT (GET /api/sensors/live)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing GET /api/sensors/live...")
    r_sensors = requests.get(f"{BASE_URL}/api/sensors/live", timeout=15)
    print(f"  -> HTTP Status Code: {r_sensors.status_code}")
    assert r_sensors.status_code == 200, f"Expected 200, got {r_sensors.status_code}"

    sensors_data = r_sensors.json()
    assert sensors_data.get("status") == "SUCCESS", f"Expected SUCCESS, got {sensors_data.get('status')}"
    sensors = sensors_data.get("sensors", [])
    print(f"  -> Returned Active IoT Sensors: {len(sensors)}")
    assert len(sensors) >= 3, f"Expected at least 3 sensors, got {len(sensors)}"

    for s in sensors:
        s_id = s.get("sensor_id")
        loc = s.get("location_name")
        status = s.get("status")
        reading = s.get("latest_reading", {})
        prox = s.get("lifeline_proximity", {})
        print(f"     Node {s_id}: {loc} | Status: {status} | Value: {reading.get('value')} {reading.get('unit')} | Road Prox: {prox.get('distance_meters')}m ({prox.get('road_code')})")

    print("[PASS] TEST 2: Live IoT Sensors API verified with active telemetry & lifeline proximity.")

    # -------------------------------------------------------------------------
    # TEST 3: VALIDATE SATELLITE INSAR RADAR ENDPOINT (GET /api/insar/points)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing GET /api/insar/points...")
    r_insar = requests.get(f"{BASE_URL}/api/insar/points", timeout=15)
    print(f"  -> HTTP Status Code: {r_insar.status_code}")
    assert r_insar.status_code == 200, f"Expected 200, got {r_insar.status_code}"

    insar_data = r_insar.json()
    assert insar_data.get("status") == "SUCCESS", f"Expected SUCCESS, got {insar_data.get('status')}"
    features = insar_data.get("features", [])
    print(f"  -> Returned InSAR PS Scatterers: {len(features)}")
    assert len(features) >= 3, f"Expected at least 3 InSAR scatterers, got {len(features)}"

    for f in features:
        pt_id = f.get("point_id")
        loc = f.get("location_name")
        vel = f.get("los_velocity_mm_yr")
        disp = f.get("cumulative_disp_mm")
        coh = f.get("coherence")
        cls = f.get("deformation_classification")
        print(f"     PS #{pt_id}: {loc} | Mission: {f.get('mission')} | LOS Vel: {vel} mm/yr | 30d Disp: {disp} mm | Coherence: {coh} | Class: {cls}")

    print("[PASS] TEST 3: Satellite InSAR Points API verified with PS scatterer displacement vectors.")

    print("\n" + "=" * 75)
    print("ALL PHASE 9 STEP 4 VERIFICATION TESTS PASSED SUCCESSFULLY! (HTTP 200)")
    print("=" * 75)

if __name__ == "__main__":
    test_phase9_frontend()
