#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 9 Step 2 Automated Test Suite
Tests Geotechnical Telemetry Streaming, Live Sensor Hardware API, and Satellite InSAR Points.
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

from backend.telemetry_streamer import GeotechnicalTelemetryStreamer

BASE_URL = "http://127.0.0.1:8080"

def test_telemetry():
    print("=" * 75)
    print("PARVAT NETRA -- PHASE 9 STEP 2 AUTOMATED TEST SUITE")
    print("Testing In-Situ Geotechnical Telemetry & Satellite PS-InSAR Endpoints")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # PART 1: TRIGGER TELEMETRY STREAMER CYCLE
    # -------------------------------------------------------------------------
    print("\n[PART 1] Triggering Telemetry Streamer Acquisition Cycle...")
    streamer = GeotechnicalTelemetryStreamer()
    stream_results = streamer.stream_cycle()
    assert len(stream_results) == 3, f"Expected 3 sensor telemetry readings, got {len(stream_results)}"
    print(f"[PASS] Streamer cycle successfully generated {len(stream_results)} in-situ readings.")

    # -------------------------------------------------------------------------
    # PART 2: TEST GET /api/sensors/live
    # -------------------------------------------------------------------------
    print("\n[PART 2] Testing GET /api/sensors/live...")
    r1 = requests.get(f"{BASE_URL}/api/sensors/live", timeout=15)
    print(f"  -> HTTP Status Code: {r1.status_code}")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {r1.text}"

    data1 = r1.json()
    assert data1.get("status") == "SUCCESS", f"Expected SUCCESS status, got {data1.get('status')}"
    sensors = data1.get("sensors", [])
    print(f"  -> Returned Sensors: {len(sensors)}")
    assert len(sensors) == 3, f"Expected 3 registered IoT sensor nodes, got {len(sensors)}"

    for s in sensors:
        s_id = s.get("sensor_id")
        s_type = s.get("sensor_type")
        loc = s.get("location_name")
        dist = s.get("district")
        status = s.get("status")
        reading = s.get("latest_reading", {})
        prox = s.get("lifeline_proximity", {})

        print(f"\n     Sensor Node: {s_id} ({s_type})")
        print(f"     Location: {loc}, {dist} | Node Status: {status} | Battery: {s.get('battery_pct')}%")
        print(f"     Latest Telemetry: {reading.get('value')} {reading.get('unit')} (Critical: {reading.get('is_critical')})")
        print(f"     Recorded At: {reading.get('recorded_at')}")
        print(f"     Distance to {prox.get('road_code')}: {prox.get('distance_meters')}m (Within 1km: {prox.get('is_within_1000m')})")

        assert s_id in ('IOT-SK-VWC-01', 'IOT-SK-TILT-02', 'IOT-SK-VWC-03'), f"Unexpected sensor_id: {s_id}"
        assert reading.get("value") is not None, "Reading value must not be None"
        assert reading.get("unit") in ('% VWC', 'deg'), f"Unexpected unit: {reading.get('unit')}"
        assert prox.get("road_code") == 'NH-10', f"Expected NH-10 proximity, got {prox.get('road_code')}"
        assert prox.get("distance_meters") is not None, "Distance to road must be calculated"

    print("\n[PASS] PART 2: /api/sensors/live verified with latest telemetry & road proximity.")

    # -------------------------------------------------------------------------
    # PART 3: TEST GET /api/insar/points
    # -------------------------------------------------------------------------
    print("\n[PART 3] Testing GET /api/insar/points...")
    r2 = requests.get(f"{BASE_URL}/api/insar/points", timeout=15)
    print(f"  -> HTTP Status Code: {r2.status_code}")
    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}: {r2.text}"

    data2 = r2.json()
    assert data2.get("status") == "SUCCESS", f"Expected SUCCESS status, got {data2.get('status')}"
    features = data2.get("features", [])
    print(f"  -> Returned InSAR PS Points: {len(features)}")
    assert len(features) == 3, f"Expected 3 Persistent Scatterer radar points, got {len(features)}"

    for f in features:
        pt_id = f.get("point_id")
        loc = f.get("location_name")
        vel = f.get("los_velocity_mm_yr")
        disp = f.get("cumulative_disp_mm")
        coh = f.get("coherence")
        cls = f.get("deformation_classification")
        geom = f.get("geometry", {})

        print(f"\n     Point #{pt_id}: {loc} ({f.get('district')})")
        print(f"     Mission: {f.get('mission')} | Coherence: {coh}")
        print(f"     LOS Velocity: {vel} mm/yr | 30d Cumulative: {disp} mm")
        print(f"     Deformation Classification: {cls}")
        print(f"     GeoJSON Coordinates: {geom.get('coordinates')}")

        assert vel is not None, "LOS velocity must be present"
        assert disp is not None, "Cumulative displacement must be present"
        assert coh is not None and 0.0 <= coh <= 1.0, f"Invalid coherence: {coh}"
        assert geom.get("type") == "Point", f"Expected Point geometry, got {geom.get('type')}"
        assert len(geom.get("coordinates", [])) == 2, "Coordinates must be [lon, lat]"

    print("\n[PASS] PART 3: /api/insar/points verified with GeoJSON radar scatterer features.")

    print("\n" + "=" * 75)
    print("ALL PHASE 9 STEP 2 TESTS PASSED SUCCESSFULLY! (HTTP 200)")
    print("=" * 75)

if __name__ == "__main__":
    test_telemetry()
