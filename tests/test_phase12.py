#!/usr/bin/env python3
"""
PARVAT NETRA -- Phase 12 Automated Verification Suite
Validates PostGIS Schemas for River Hydrology (teesta_waterways) and Anthropogenic Hill Cuts,
Spatial Distance Joins and Risk Fusion Modifiers in risk_engine.py,
REST Endpoints (/api/hydrology/teesta-status, /api/terrain/anthropogenic-cuts, /api/ml/latest-risk),
and Frontend Dashboard Layer Toggles in templates/index.html.
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

from backend.risk_engine import get_db_connection, run_risk_fusion_pipeline

BASE_URL = "http://127.0.0.1:8080"


def test_phase12():
    print("=" * 80)
    print("PARVAT NETRA -- PHASE 12 AUTOMATED VERIFICATION SUITE")
    print("Anthropogenic Hill-Cutting & Teesta River Toe Erosion Monitoring")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PART 1: POSTGIS SCHEMAS & GIST SPATIAL INDEXES
    # -------------------------------------------------------------------------
    print("\n[PART 1] Verifying PostGIS Database Schemas & GIST Indexes...")
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Check teesta_waterways
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'teesta_waterways';
        """)
        tw_cols = {row["column_name"]: row["data_type"] for row in cur.fetchall()}
        assert "river_id" in tw_cols, "Missing river_id in teesta_waterways"
        assert "reach_name" in tw_cols, "Missing reach_name in teesta_waterways"
        assert "water_level_m" in tw_cols, "Missing water_level_m in teesta_waterways"
        assert "scour_risk_level" in tw_cols, "Missing scour_risk_level in teesta_waterways"
        assert "geom" in tw_cols, "Missing geom in teesta_waterways"

        # Check anthropogenic_cuts
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'anthropogenic_cuts';
        """)
        ac_cols = {row["column_name"]: row["data_type"] for row in cur.fetchall()}
        assert "cut_id" in ac_cols, "Missing cut_id in anthropogenic_cuts"
        assert "location_name" in ac_cols, "Missing location_name in anthropogenic_cuts"
        assert "cut_angle_deg" in ac_cols, "Missing cut_angle_deg in anthropogenic_cuts"
        assert "has_retaining_wall" in ac_cols, "Missing has_retaining_wall in anthropogenic_cuts"
        assert "destabilization_index" in ac_cols, "Missing destabilization_index in anthropogenic_cuts"
        assert "geom" in ac_cols, "Missing geom in anthropogenic_cuts"

        # Check GIST indexes
        cur.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename IN ('teesta_waterways', 'anthropogenic_cuts');
        """)
        indexes = [row["indexname"] for row in cur.fetchall()]
        print(f"  -> Found Indexes: {indexes}")
        assert any("teesta" in idx for idx in indexes), "Missing GIST index on teesta_waterways"
        assert any("anthro" in idx for idx in indexes), "Missing GIST index on anthropogenic_cuts"

        # Check seeded data
        cur.execute("SELECT COUNT(*) AS count FROM teesta_waterways;")
        tw_count = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) AS count FROM anthropogenic_cuts;")
        ac_count = cur.fetchone()["count"]
        print(f"  -> Seeded Teesta Waterways: {tw_count} reach(es)")
        print(f"  -> Seeded Anthropogenic Cuts: {ac_count} site(s)")
        assert tw_count >= 1, f"Expected >= 1 waterway reach, found {tw_count}"
        assert ac_count >= 2, f"Expected >= 2 hill cut sites, found {ac_count}"

    conn.close()
    print("[PASS] PART 1: PostGIS Database Schemas & GIST Indexes Verified.")

    # -------------------------------------------------------------------------
    # PART 2: UPGRADED RISK FUSION ENGINE WITH TOE SCOUR & HILL CUT MODIFIERS
    # -------------------------------------------------------------------------
    print("\n[PART 2] Running Upgraded Risk Fusion Pipeline...")
    results = run_risk_fusion_pipeline()
    print(f"  -> Evaluated Regions: {len(results)}")
    assert len(results) >= 2, f"Expected >= 2 evaluated regions, got {len(results)}"

    teesta_res = next((r for r in results if "Teesta" in r["region_name"]), None)
    assert teesta_res is not None, "Teesta Valley region evaluation missing"
    print(f"  -> Teesta Valley Evaluation:")
    print(f"     Base Fused Score: {teesta_res['base_fused_score']}")
    print(f"     Toe Scour Surge: +{teesta_res['toe_scour_surge']} (River Dist: {teesta_res['river_distance_m']}m)")
    print(f"     Anthro Cut Multiplier: {teesta_res['anthro_cut_multiplier']}x (Cut Dist: {teesta_res['cut_distance_m']}m)")
    print(f"     Final Risk Score: {teesta_res['final_risk_score']} [{teesta_res['severity_label']}]")
    print(f"     Why: {teesta_res['explainability_why']}")

    assert teesta_res["toe_scour_surge"] == 12.0, f"Expected +12.0 toe scour surge, got {teesta_res['toe_scour_surge']}"
    assert teesta_res["anthro_cut_multiplier"] == 1.15, f"Expected 1.15 anthro cut multiplier, got {teesta_res['anthro_cut_multiplier']}"
    assert teesta_res["severity_label"] == "RED", f"Expected RED severity, got {teesta_res['severity_label']}"
    assert "Teesta River Hydraulic Surge (+12.0)" in teesta_res["explainability_why"], "Missing Teesta hydraulic surge in explainability"
    assert "Anthro Hill Cut Destabilization (1.15x)" in teesta_res["explainability_why"], "Missing Anthro cut in explainability"

    # Verify Gangtok Corridor does NOT have these modifiers
    gangtok_res = next((r for r in results if "Gangtok" in r["region_name"]), None)
    if gangtok_res:
        print(f"  -> Gangtok Corridor Evaluation:")
        print(f"     Toe Scour Surge: +{gangtok_res['toe_scour_surge']}")
        print(f"     Anthro Cut Multiplier: {gangtok_res['anthro_cut_multiplier']}x")
        assert gangtok_res["toe_scour_surge"] == 0.0, "Gangtok should not trigger Teesta surge"
        assert gangtok_res["anthro_cut_multiplier"] == 1.0, "Gangtok should not trigger hill cut multiplier"

    print("[PASS] PART 2: Risk Fusion Engine Modifiers & Spatial Joins Verified.")

    # -------------------------------------------------------------------------
    # PART 3: REST ENDPOINT GET /api/hydrology/teesta-status
    # -------------------------------------------------------------------------
    print("\n[PART 3] Testing GET /api/hydrology/teesta-status...")
    r1 = requests.get(f"{BASE_URL}/api/hydrology/teesta-status", timeout=15)
    print(f"  -> HTTP Status Code: {r1.status_code}")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {r1.text}"

    data1 = r1.json()
    assert data1.get("status") == "SUCCESS", f"Expected SUCCESS, got {data1.get('status')}"
    reaches = data1.get("reaches", [])
    print(f"  -> Returned Reaches: {len(reaches)}")
    assert len(reaches) >= 1, f"Expected >= 1 reach, got {len(reaches)}"

    for reach in reaches:
        geom = reach.get("geometry", {})
        assert geom.get("type") == "LineString", f"Expected LineString, got {geom.get('type')}"
        coords = geom.get("coordinates", [])
        assert len(coords) >= 2, f"LineString must have at least 2 points, got {len(coords)}"
        assert reach.get("water_level_m") is not None, "Missing water_level_m"
        assert reach.get("scour_risk_level") in ("LOW", "MODERATE", "HIGH", "CRITICAL"), f"Invalid scour level: {reach.get('scour_risk_level')}"
        print(f"     Reach: {reach['reach_name']} | Level: {reach['water_level_m']}m | Scour: {reach['scour_risk_level']}")

    print("[PASS] PART 3: GET /api/hydrology/teesta-status verified with GeoJSON LineString.")

    # -------------------------------------------------------------------------
    # PART 4: REST ENDPOINT GET /api/terrain/anthropogenic-cuts
    # -------------------------------------------------------------------------
    print("\n[PART 4] Testing GET /api/terrain/anthropogenic-cuts...")
    r2 = requests.get(f"{BASE_URL}/api/terrain/anthropogenic-cuts", timeout=15)
    print(f"  -> HTTP Status Code: {r2.status_code}")
    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}: {r2.text}"

    data2 = r2.json()
    cuts = data2.get("cuts", [])
    print(f"  -> Returned Cuts: {len(cuts)}")
    assert len(cuts) >= 2, f"Expected >= 2 cuts, got {len(cuts)}"

    for cut in cuts:
        geom = cut.get("geometry", {})
        assert geom.get("type") == "Point", f"Expected Point, got {geom.get('type')}"
        coords = geom.get("coordinates", [])
        assert len(coords) == 2, f"Point must have [lon, lat], got {coords}"
        assert cut.get("cut_angle_deg") is not None, "Missing cut_angle_deg"
        assert cut.get("destabilization_index") is not None, "Missing destabilization_index"
        print(f"     Cut: {cut['location_name']} ({cut['corridor']}) | Angle: {cut['cut_angle_deg']} deg | Retaining Wall: {cut['has_retaining_wall']} | Index: {cut['destabilization_index']}")

    print("[PASS] PART 4: GET /api/terrain/anthropogenic-cuts verified with GeoJSON Points.")

    # -------------------------------------------------------------------------
    # PART 5: REST ENDPOINT GET /api/ml/latest-risk WITH PHASE 12 FACTORS
    # -------------------------------------------------------------------------
    print("\n[PART 5] Testing GET /api/ml/latest-risk (Evaluating Phase 12 Modifiers)...")
    r3 = requests.get(f"{BASE_URL}/api/ml/latest-risk", timeout=15)
    print(f"  -> HTTP Status Code: {r3.status_code}")
    assert r3.status_code == 200, f"Expected 200, got {r3.status_code}: {r3.text}"

    data3 = r3.json()
    evals = data3.get("evaluations", [])
    tv_eval = next((e for e in evals if "Teesta" in e["region_name"]), None)
    assert tv_eval is not None, "Teesta Valley evaluation missing from latest-risk"
    print(f"  -> Teesta Valley Latest Risk: {tv_eval['risk_index']}/100 [{tv_eval['severity']}]")
    print(f"     Toe Scour Factor: {tv_eval.get('toe_scour_factor')}")
    print(f"     Anthro Cut Factor: {tv_eval.get('anthro_cut_factor')}")
    assert tv_eval.get("toe_scour_factor") == 12.0, f"Expected 12.0, got {tv_eval.get('toe_scour_factor')}"
    assert tv_eval.get("anthro_cut_factor") == 1.15, f"Expected 1.15, got {tv_eval.get('anthro_cut_factor')}"
    print("[PASS] PART 5: GET /api/ml/latest-risk Phase 12 factors verified.")

    # -------------------------------------------------------------------------
    # PART 6: FRONTEND DASHBOARD WIRING & MARKUP
    # -------------------------------------------------------------------------
    print("\n[PART 6] Verifying Frontend Dashboard Layer Controls & Handlers...")
    r4 = requests.get(f"{BASE_URL}/", timeout=15)
    assert r4.status_code == 200, f"Expected 200, got {r4.status_code}"
    html = r4.text

    assert "toggle-river-btn" in html, "Missing toggle-river-btn in index.html"
    assert "toggle-cuts-btn" in html, "Missing toggle-cuts-btn in index.html"
    assert "loadTeestaRiver" in html, "Missing loadTeestaRiver in index.html"
    assert "loadAnthropogenicCuts" in html, "Missing loadAnthropogenicCuts in index.html"
    assert "toggleRiverLayer" in html, "Missing toggleRiverLayer in index.html"
    assert "toggleCutsLayer" in html, "Missing toggleCutsLayer in index.html"
    assert "row-toe-scour" in html, "Missing row-toe-scour in index.html"
    assert "row-anthro-cut" in html, "Missing row-anthro-cut in index.html"
    print("  -> Found all 8 frontend buttons, layer groups, and card elements in DOM.")
    print("[PASS] PART 6: Frontend Dashboard Layer Controls & Handlers Verified.")

    print("\n" + "=" * 80)
    print(">>> ALL PHASE 12 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6 PARTS) <<<")
    print("=" * 80)


if __name__ == "__main__":
    test_phase12()
