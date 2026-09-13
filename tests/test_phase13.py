#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 13 Automated Verification Suite
Validates PostGIS Schemas for Alternate Bypass Corridors & Critical Habitations,
Dynamic Emergency Rerouting Engine & Isolation Triage (routing_engine.py),
REST Endpoints (/api/routing/evacuation-plan & /api/humanitarian/isolation-matrix),
and Frontend Dashboard Layer Toggles & Logistics Status Card (templates/index.html).
"""

import sys
import os
import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.routing_engine import get_db_connection, EmergencyRoutingEngine

BASE_URL = "http://127.0.0.1:8080"


def test_phase13():
    print("=" * 80)
    print("PARVAT NETRA -- PHASE 13 AUTOMATED VERIFICATION SUITE")
    print("Dynamic Emergency Bypass Rerouting & Critical Habitation Isolation Matrix")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PART 1: POSTGIS SCHEMAS & GIST SPATIAL INDEXES
    # -------------------------------------------------------------------------
    print("\n[PART 1] Verifying PostGIS Database Schemas & GIST Indexes...")
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Check bypass_corridors columns
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'bypass_corridors';
        """)
        bc_cols = {row["column_name"]: row["data_type"] for row in cur.fetchall()}
        assert "route_id" in bc_cols, "Missing route_id in bypass_corridors"
        assert "corridor_code" in bc_cols, "Missing corridor_code in bypass_corridors"
        assert "name" in bc_cols, "Missing name in bypass_corridors"
        assert "via_settlements" in bc_cols, "Missing via_settlements in bypass_corridors"
        assert "surface_type" in bc_cols, "Missing surface_type in bypass_corridors"
        assert "max_tonnage_tonnes" in bc_cols, "Missing max_tonnage_tonnes in bypass_corridors"
        assert "length_km" in bc_cols, "Missing length_km in bypass_corridors"
        assert "normal_duration_hrs" in bc_cols, "Missing normal_duration_hrs in bypass_corridors"
        assert "status" in bc_cols, "Missing status in bypass_corridors"
        assert "geom" in bc_cols, "Missing geom in bypass_corridors"

        # Check critical_habitations columns
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'critical_habitations';
        """)
        ch_cols = {row["column_name"]: row["data_type"] for row in cur.fetchall()}
        assert "habitation_id" in ch_cols, "Missing habitation_id in critical_habitations"
        assert "name" in ch_cols, "Missing name in critical_habitations"
        assert "district" in ch_cols, "Missing district in critical_habitations"
        assert "population" in ch_cols, "Missing population in critical_habitations"
        assert "primary_road_id" in ch_cols, "Missing primary_road_id in critical_habitations"
        assert "has_functional_phc" in ch_cols, "Missing has_functional_phc in critical_habitations"
        assert "has_helipad" in ch_cols, "Missing has_helipad in critical_habitations"
        assert "grain_reserve_days" in ch_cols, "Missing grain_reserve_days in critical_habitations"
        assert "fuel_reserve_days" in ch_cols, "Missing fuel_reserve_days in critical_habitations"
        assert "isolation_status" in ch_cols, "Missing isolation_status in critical_habitations"
        assert "geom" in ch_cols, "Missing geom in critical_habitations"

        # Check GIST indexes
        cur.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename IN ('bypass_corridors', 'critical_habitations');
        """)
        indexes = [row["indexname"] for row in cur.fetchall()]
        print(f"  -> Found Indexes: {indexes}")
        assert any("bypass" in idx for idx in indexes), "Missing GIST index on bypass_corridors"
        assert any("habitation" in idx for idx in indexes), "Missing GIST index on critical_habitations"

        # Check seeded entities
        cur.execute("SELECT COUNT(*) AS count FROM bypass_corridors;")
        bc_count = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) AS count FROM critical_habitations;")
        ch_count = cur.fetchone()["count"]
        print(f"  -> Seeded Bypass Corridors: {bc_count} route(s)")
        print(f"  -> Seeded Critical Habitations: {ch_count} settlement(s)")
        assert bc_count >= 2, f"Expected >= 2 bypass corridors, found {bc_count}"
        assert ch_count >= 3, f"Expected >= 3 critical habitations, found {ch_count}"

    conn.close()
    print("[PASS] PART 1: PostGIS Database Schemas & GIST Indexes Verified.")

    # -------------------------------------------------------------------------
    # PART 2: EMERGENCY ROUTING & ISOLATION LOGIC ENGINE
    # -------------------------------------------------------------------------
    print("\n[PART 2] Executing Emergency Routing & Habitation Isolation Engine...")
    engine = EmergencyRoutingEngine()
    cycle = engine.run_routing_cycle()

    primary = cycle["primary_road"]
    rec = cycle["recommended_detour"]
    habs = cycle["habitations"]
    iso = cycle["isolation_summary"]

    print(f"  -> Primary Highway: {primary['road_code']} | Status: [{primary['status']}]")
    print(f"     Driver: {primary['primary_driver']}")
    assert primary["is_blocked"] is True, "NH-10 should be flagged as BLOCKED due to RED risk zones / AI scars"
    assert "BLOCKED" in primary["status"], f"Expected BLOCKED status, got {primary['status']}"

    print(f"  -> Recommended Detour: {rec['corridor_code']} - {rec['name']}")
    print(f"     Delay: +{rec['delay_penalty_hrs']} hrs | Max Tonnage: {rec['max_tonnage_tonnes']}T | Status: {rec['status']}")
    assert rec["status"] == "OPEN", f"Recommended detour should be OPEN, got {rec['status']}"
    assert rec["delay_penalty_hrs"] > 0, "Bypass detour should compute a positive delay penalty"
    assert rec["max_tonnage_tonnes"] >= 10.0, "Recommended detour should support heavy freight"

    print(f"  -> Habitations Evaluated: {len(habs)}")
    print(f"     Summary: {iso['isolated_air_only']} Air-Only | {iso['threatened']} Threatened | {iso['normal']} Normal")
    assert iso["isolated_air_only"] >= 1, f"Expected >= 1 Air-Only isolated settlement, got {iso['isolated_air_only']}"
    assert iso["threatened"] >= 1, f"Expected >= 1 Threatened settlement, got {iso['threatened']}"

    chungthang = next((h for h in habs if "Chungthang" in h["name"]), None)
    assert chungthang is not None, "Chungthang settlement evaluation missing"
    assert chungthang["isolation_status"] == "ISOLATED_AIR_ONLY", f"Chungthang should be ISOLATED_AIR_ONLY, got {chungthang['isolation_status']}"
    assert chungthang["has_helipad"] is True, "Chungthang must have helipad enabled"
    print(f"     Verified Chungthang: [{chungthang['isolation_status']}] -> {chungthang['evacuation_channel']}")

    print("[PASS] PART 2: Emergency Routing & Isolation Logic Engine Verified.")

    # -------------------------------------------------------------------------
    # PART 3: REST ENDPOINT GET /api/routing/evacuation-plan
    # -------------------------------------------------------------------------
    print("\n[PART 3] Testing GET /api/routing/evacuation-plan...")
    r1 = requests.get(f"{BASE_URL}/api/routing/evacuation-plan", timeout=15)
    print(f"  -> HTTP Status Code: {r1.status_code}")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {r1.text}"

    data1 = r1.json()
    assert data1.get("status") == "SUCCESS", f"Expected SUCCESS, got {data1.get('status')}"
    api_primary = data1.get("primary_road", {})
    assert api_primary.get("is_blocked") is True, "API primary road should be marked blocked"

    api_bypasses = data1.get("bypass_routes", [])
    print(f"  -> Returned Bypass Corridors: {len(api_bypasses)}")
    assert len(api_bypasses) >= 2, f"Expected >= 2 bypass routes, got {len(api_bypasses)}"

    for b in api_bypasses:
        geom = b.get("geometry", {})
        assert geom.get("type") == "LineString", f"Expected LineString, got {geom.get('type')}"
        coords = geom.get("coordinates", [])
        assert len(coords) >= 2, f"LineString must contain >= 2 points, got {len(coords)}"
        assert b.get("delay_penalty_hrs") is not None, "Missing delay_penalty_hrs"
        assert b.get("max_tonnage_tonnes") is not None, "Missing max_tonnage_tonnes"
        print(f"     Route: {b['name']} ({b['corridor_code']}) | Length: {b['length_km']} km | Delay: +{b['delay_penalty_hrs']}h")

    print("[PASS] PART 3: GET /api/routing/evacuation-plan verified with GeoJSON LineStrings.")

    # -------------------------------------------------------------------------
    # PART 4: REST ENDPOINT GET /api/humanitarian/isolation-matrix
    # -------------------------------------------------------------------------
    print("\n[PART 4] Testing GET /api/humanitarian/isolation-matrix...")
    r2 = requests.get(f"{BASE_URL}/api/humanitarian/isolation-matrix", timeout=15)
    print(f"  -> HTTP Status Code: {r2.status_code}")
    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}: {r2.text}"

    data2 = r2.json()
    assert data2.get("status") == "SUCCESS", f"Expected SUCCESS, got {data2.get('status')}"
    api_habs = data2.get("habitations", [])
    print(f"  -> Returned Habitations: {len(api_habs)}")
    assert len(api_habs) >= 3, f"Expected >= 3 habitations, got {len(api_habs)}"

    for h in api_habs:
        geom = h.get("geometry", {})
        assert geom.get("type") == "Point", f"Expected Point, got {geom.get('type')}"
        coords = geom.get("coordinates", [])
        assert len(coords) == 2, f"Point must contain [lon, lat], got {coords}"
        assert h.get("isolation_status") in ("NORMAL", "THREATENED", "ISOLATED_AIR_ONLY")
        assert h.get("grain_reserve_days") is not None, "Missing grain_reserve_days"
        assert h.get("fuel_reserve_days") is not None, "Missing fuel_reserve_days"
        print(f"     Habitation: {h['name']} ({h['district']}) | Pop: {h['population']} | Status: [{h['isolation_status']}] | Helipad: {h['has_helipad']}")

    print("[PASS] PART 4: GET /api/humanitarian/isolation-matrix verified with GeoJSON Points.")

    # -------------------------------------------------------------------------
    # PART 5: FRONTEND DASHBOARD WIRING & MARKUP
    # -------------------------------------------------------------------------
    print("\n[PART 5] Verifying Frontend Dashboard Controls & Handlers...")
    r3 = requests.get(f"{BASE_URL}/", timeout=15)
    assert r3.status_code == 200, f"Expected 200, got {r3.status_code}"
    html = r3.text

    assert "toggle-detours-btn" in html, "Missing toggle-detours-btn in index.html"
    assert "toggle-habitations-btn" in html, "Missing toggle-habitations-btn in index.html"
    assert "evac-logistics-card" in html, "Missing evac-logistics-card in index.html"
    assert "loadEvacuationPlan" in html, "Missing loadEvacuationPlan in index.html"
    assert "loadHabitationMatrix" in html, "Missing loadHabitationMatrix in index.html"
    assert "toggleDetoursLayer" in html, "Missing toggleDetoursLayer in index.html"
    assert "toggleHabitationsLayer" in html, "Missing toggleHabitationsLayer in index.html"
    assert "habitation-pulse-isolated" in html, "Missing habitation-pulse-isolated in index.html"
    print("  -> Found all 8 frontend buttons, layer groups, and logistics elements in DOM.")
    print("[PASS] PART 5: Frontend Dashboard Controls & Handlers Verified.")

    print("\n" + "=" * 80)
    print(">>> ALL PHASE 13 AUTOMATED TESTS PASSED SUCCESSFULLY! (5/5 PARTS) <<<")
    print("=" * 80)


if __name__ == "__main__":
    test_phase13()
