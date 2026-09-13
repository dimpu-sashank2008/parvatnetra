#!/usr/bin/env python3
"""
PARVAT NETRA -- Research Sprint 3 Automated Verification Suite
Pillar 5: Humanitarian Habitation Critical Isolation Index (HCII) &
IRC SP:84 / SP:48 / MoRTH Mountain Freight Routing Cost Function.
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

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.routing_engine import (
    calculate_hcii,
    calculate_effective_gradient,
    calculate_route_cost,
    EmergencyRoutingEngine,
    MORHT_VEHICLE_CLASSES,
    get_db_connection
)

BASE_URL = "http://127.0.0.1:8080"


def test_sprint3_hcii_freight():
    print("=" * 80)
    print("PARVAT NETRA -- SPRINT 3 AUTOMATED VERIFICATION SUITE")
    print("Pillar 5: HCII Isolation Index & IRC SP:84 Mountain Freight Routing")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PART 1: HCII FORMULATION & TIER CLASSIFICATION UNIT TESTS
    # -------------------------------------------------------------------------
    print("\n[PART 1] Validating Standardized HCII Mathematical Formulation...")

    # 1. Chungthang Sub-Divisional Base: Rf=4, Re=2, Patients=8, Beds=10 (Hs=0.8), Ao=1.0
    # Expected HCII = 100 * [ 0.30*(1 - 4/15) + 0.25*(1 - 2/10) + 0.30*0.8 + 0.15*(1 - 1.0) ]
    #                = 100 * [ 0.22 + 0.20 + 0.24 + 0.0 ] = 66.0
    c_score, c_tier, c_bk = calculate_hcii(
        food_reserve_days=4,
        fuel_reserve_days=2,
        critical_patients=8,
        bed_capacity=10,
        helipad_operational_fraction=1.0
    )
    print(f"  -> Chungthang: HCII={c_score} [{c_tier}] | Breakdown: {c_bk['food_term']} + {c_bk['fuel_term']} + {c_bk['health_term']} + {c_bk['airlift_term']}")
    assert abs(c_score - 66.0) < 0.1, f"Expected Chungthang HCII=66.0, got {c_score}"
    assert c_tier == "ACUTE_SHORTAGE_THREATENED", f"Expected ACUTE_SHORTAGE_THREATENED, got {c_tier}"
    assert c_bk["food_term"] == 22.0, f"Expected food_term=22.0, got {c_bk['food_term']}"
    assert c_bk["fuel_term"] == 20.0, f"Expected fuel_term=20.0, got {c_bk['fuel_term']}"
    assert c_bk["health_term"] == 24.0, f"Expected health_term=24.0, got {c_bk['health_term']}"
    assert c_bk["airlift_term"] == 0.0, f"Expected airlift_term=0.0, got {c_bk['airlift_term']}"

    # 2. Dikchu River Settlement: Rf=6, Re=3, Patients=4, Beds=8 (Hs=0.5), Ao=0.0
    # Expected HCII = 100 * [ 0.30*(1 - 6/15) + 0.25*(1 - 3/10) + 0.30*0.5 + 0.15*1.0 ]
    #                = 100 * [ 0.18 + 0.175 + 0.15 + 0.15 ] = 65.5
    d_score, d_tier, d_bk = calculate_hcii(
        food_reserve_days=6,
        fuel_reserve_days=3,
        critical_patients=4,
        bed_capacity=8,
        helipad_operational_fraction=0.0
    )
    print(f"  -> Dikchu: HCII={d_score} [{d_tier}] | Breakdown: {d_bk['food_term']} + {d_bk['fuel_term']} + {d_bk['health_term']} + {d_bk['airlift_term']}")
    assert abs(d_score - 65.5) < 0.1, f"Expected Dikchu HCII=65.5, got {d_score}"
    assert d_tier == "ACUTE_SHORTAGE_THREATENED", f"Expected ACUTE_SHORTAGE_THREATENED, got {d_tier}"

    # 3. Mangan District HQ: Rf=9, Re=6, Patients=5, Beds=25 (Hs=0.2), Ao=1.0
    # Expected HCII = 100 * [ 0.30*(1 - 9/15) + 0.25*(1 - 6/10) + 0.30*0.2 + 0.15*0.0 ]
    #                = 100 * [ 0.12 + 0.10 + 0.06 + 0.0 ] = 28.0
    m_score, m_tier, m_bk = calculate_hcii(
        food_reserve_days=9,
        fuel_reserve_days=6,
        critical_patients=5,
        bed_capacity=25,
        helipad_operational_fraction=1.0
    )
    print(f"  -> Mangan: HCII={m_score} [{m_tier}] | Breakdown: {m_bk['food_term']} + {m_bk['fuel_term']} + {m_bk['health_term']} + {m_bk['airlift_term']}")
    assert abs(m_score - 28.0) < 0.1, f"Expected Mangan HCII=28.0, got {m_score}"
    assert m_tier == "MONITORED_WATCH", f"Expected MONITORED_WATCH, got {m_tier}"

    # 4. Dzongu Indigenous Reserve: Rf=3, Re=1, Patients=6, Beds=6 (Hs=1.0), Ao=0.0
    # Expected HCII = 100 * [ 0.30*(1 - 3/15) + 0.25*(1 - 1/10) + 0.30*1.0 + 0.15*1.0 ]
    #                = 100 * [ 0.24 + 0.225 + 0.30 + 0.15 ] = 91.5
    dz_score, dz_tier, dz_bk = calculate_hcii(
        food_reserve_days=3,
        fuel_reserve_days=1,
        critical_patients=6,
        bed_capacity=6,
        helipad_operational_fraction=0.0
    )
    print(f"  -> Dzongu: HCII={dz_score} [{dz_tier}] | Breakdown: {dz_bk['food_term']} + {dz_bk['fuel_term']} + {dz_bk['health_term']} + {dz_bk['airlift_term']}")
    assert abs(dz_score - 91.5) < 0.1, f"Expected Dzongu HCII=91.5, got {dz_score}"
    assert dz_tier == "CRITICAL_AIR_DROP_REQUIRED", f"Expected CRITICAL_AIR_DROP_REQUIRED, got {dz_tier}"

    print("[PASS] PART 1: HCII Mathematical Formulation & Tiers Verified.")

    # -------------------------------------------------------------------------
    # PART 2: IRC SP:84 MOUNTAIN FREIGHT ROUTING COST FUNCTION
    # -------------------------------------------------------------------------
    print("\n[PART 2] Validating IRC SP:84 Mountain Freight Routing Cost Function...")

    # Curve compensated gradient tests
    # Mungpoo: G=7.5%, R=75m -> comp = 75/75 = 1.0% -> G_eff = 6.5%
    mungpoo_geff = calculate_effective_gradient(nominal_gradient_pct=7.5, curve_radius_m=75.0)
    print(f"  -> Mungpoo Effective Gradient: {mungpoo_geff}% (Ruling: 5.0%)")
    assert mungpoo_geff == 6.5, f"Expected Mungpoo G_eff=6.5, got {mungpoo_geff}"

    # Lava: G=4.8%, R=100m -> comp = 0.75% -> G_eff = max(4.05%, 4.0%) = 4.05%
    lava_geff = calculate_effective_gradient(nominal_gradient_pct=4.8, curve_radius_m=100.0)
    print(f"  -> Lava Effective Gradient: {lava_geff}% (Ruling: 5.0%)")
    assert lava_geff == 4.05, f"Expected Lava G_eff=4.05, got {lava_geff}"

    # Test Light Utility (3.5T) on Mungpoo: no gradient penalty
    cost_light_mungpoo = calculate_route_cost(
        base_duration_hrs=3.2,
        length_km=42.0,
        nominal_gradient_pct=7.5,
        curve_radius_m=75.0,
        gvw_tonnes=3.5,
        max_tonnage_tonnes=18.5
    )
    print(f"  -> Light Utility on Mungpoo: Cost={cost_light_mungpoo['total_route_cost_hrs']}h | P_gradient={cost_light_mungpoo['p_gradient_hrs']}h")
    assert cost_light_mungpoo["p_gradient_hrs"] == 0.0, "Light vehicle should incur zero gradient penalty"
    assert cost_light_mungpoo["total_route_cost_hrs"] < 4.0, "Light vehicle on Mungpoo should complete in < 4.0h"

    # Test Heavy Convoy (40.0T) on Mungpoo: steep gradient penalty + overload
    # P_gradient = 15.0 * (6.5 - 5.0)^2 = 15.0 * 2.25 = 33.75h
    cost_heavy_mungpoo = calculate_route_cost(
        base_duration_hrs=3.2,
        length_km=42.0,
        nominal_gradient_pct=7.5,
        curve_radius_m=75.0,
        gvw_tonnes=40.0,
        max_tonnage_tonnes=18.5
    )
    print(f"  -> Heavy 40T on Mungpoo: Cost={cost_heavy_mungpoo['total_route_cost_hrs']}h | P_gradient={cost_heavy_mungpoo['p_gradient_hrs']}h | P_overload={cost_heavy_mungpoo['p_overload_hrs']}h")
    assert cost_heavy_mungpoo["p_gradient_hrs"] == 33.75, f"Expected P_gradient=33.75h, got {cost_heavy_mungpoo['p_gradient_hrs']}"
    assert cost_heavy_mungpoo["total_route_cost_hrs"] > 35.0, "Heavy vehicle on Mungpoo should be severely penalized (>35h)"

    # Test Heavy Convoy (40.0T) on Lava: G_eff <= 5.0% -> P_gradient = 0.0, max tonnage 45.0T -> P_overload = 0.0
    cost_heavy_lava = calculate_route_cost(
        base_duration_hrs=4.5,
        length_km=84.5,
        nominal_gradient_pct=4.8,
        curve_radius_m=100.0,
        gvw_tonnes=40.0,
        max_tonnage_tonnes=45.0
    )
    print(f"  -> Heavy 40T on Lava: Cost={cost_heavy_lava['total_route_cost_hrs']}h | P_gradient={cost_heavy_lava['p_gradient_hrs']}h | P_overload={cost_heavy_lava['p_overload_hrs']}h")
    assert cost_heavy_lava["p_gradient_hrs"] == 0.0, "Lava corridor should have zero gradient penalty"
    assert cost_heavy_lava["p_overload_hrs"] == 0.0, "Lava corridor supports 45T, zero overload penalty"
    assert cost_heavy_lava["total_route_cost_hrs"] < 5.0, "Heavy vehicle on Lava should complete in < 5.0h"
    assert cost_heavy_lava["total_route_cost_hrs"] < cost_heavy_mungpoo["total_route_cost_hrs"], "Heavy vehicle must prefer Lava over Mungpoo"

    print("[PASS] PART 2: IRC SP:84 Mountain Freight Routing Verified.")

    # -------------------------------------------------------------------------
    # PART 3: ENGINE CYCLE & FLEET MATRIX VALIDATION
    # -------------------------------------------------------------------------
    print("\n[PART 3] Validating EmergencyRoutingEngine Fleet Routing Cycle...")
    engine = EmergencyRoutingEngine()

    # Evaluation for LIGHT_UTILITY
    res_light = engine.run_routing_cycle(gvw_class="LIGHT_UTILITY")
    rec_light = res_light["recommended_detour"]
    print(f"  -> Light Utility Detour: {rec_light['corridor_code']} ({rec_light['name']}) | Cost: {rec_light['route_cost_hrs']}h")
    assert rec_light["corridor_code"] == "BYPASS-MUNGPOO", f"Expected BYPASS-MUNGPOO for Light Utility, got {rec_light['corridor_code']}"

    # Evaluation for MULTI_AXLE_RELIEF_TRAIN
    res_heavy = engine.run_routing_cycle(gvw_class="MULTI_AXLE_RELIEF_TRAIN")
    rec_heavy = res_heavy["recommended_detour"]
    print(f"  -> Heavy Train Detour : {rec_heavy['corridor_code']} ({rec_heavy['name']}) | Cost: {rec_heavy['route_cost_hrs']}h")
    assert rec_heavy["corridor_code"] == "BYPASS-LAVA", f"Expected BYPASS-LAVA for Multi-Axle Train, got {rec_heavy['corridor_code']}"

    # Verify Fleet Matrix contains all classes
    fm = res_heavy["fleet_matrix"]
    for cls_k in MORHT_VEHICLE_CLASSES.keys():
        assert cls_k in fm, f"Missing {cls_k} in fleet_matrix"
        print(f"     Fleet Profile [{cls_k}]: Rec={fm[cls_k]['recommended_corridor']} ({fm[cls_k]['route_cost_hrs']}h)")

    print("[PASS] PART 3: EmergencyRoutingEngine Fleet Routing Cycle Verified.")

    # -------------------------------------------------------------------------
    # PART 4: REST API ENDPOINTS VALIDATION
    # -------------------------------------------------------------------------
    print("\n[PART 4] Testing Live REST Endpoints on Flask Server...")

    # 1. GET /api/humanitarian/isolation-matrix
    r_iso = requests.get(f"{BASE_URL}/api/humanitarian/isolation-matrix", timeout=15)
    print(f"  -> GET /api/humanitarian/isolation-matrix: Status {r_iso.status_code}")
    assert r_iso.status_code == 200, f"Expected 200, got {r_iso.status_code}"
    iso_data = r_iso.json()
    assert iso_data.get("status") == "SUCCESS", "API response status must be SUCCESS"
    habs = iso_data.get("habitations", [])
    assert len(habs) >= 4, f"Expected at least 4 habitations, got {len(habs)}"

    # Check key habitations in response
    names = {h["name"]: h for h in habs}
    for req_name in ["Chungthang Sub-Divisional Base", "Dikchu River Settlement", "Mangan District HQ", "Dzongu Indigenous Reserve"]:
        assert req_name in names, f"Missing settlement {req_name} in API response"
        h_obj = names[req_name]
        assert "hcii_score" in h_obj, f"Missing hcii_score in {req_name}"
        assert "hcii_tier" in h_obj, f"Missing hcii_tier in {req_name}"
        assert "hcii_breakdown" in h_obj, f"Missing hcii_breakdown in {req_name}"
        print(f"     Habitation: {req_name} -> HCII: {h_obj['hcii_score']} [{h_obj['hcii_tier']}] | Channel: {h_obj['evacuation_channel'][:45]}...")

    # 2. GET /api/routing/evacuation-plan with gvw_class query param
    # Light vehicle query
    r_evac_light = requests.get(f"{BASE_URL}/api/routing/evacuation-plan?gvw_class=LIGHT_UTILITY", timeout=15)
    print(f"  -> GET /api/routing/evacuation-plan?gvw_class=LIGHT_UTILITY: Status {r_evac_light.status_code}")
    assert r_evac_light.status_code == 200
    plan_light = r_evac_light.json()
    assert plan_light["recommended_detour"]["corridor_code"] == "BYPASS-MUNGPOO", "Light utility should be routed via Mungpoo"

    # Heavy vehicle query
    r_evac_heavy = requests.get(f"{BASE_URL}/api/routing/evacuation-plan?gvw_class=MULTI_AXLE_RELIEF_TRAIN", timeout=15)
    print(f"  -> GET /api/routing/evacuation-plan?gvw_class=MULTI_AXLE_RELIEF_TRAIN: Status {r_evac_heavy.status_code}")
    assert r_evac_heavy.status_code == 200
    plan_heavy = r_evac_heavy.json()
    assert plan_heavy["recommended_detour"]["corridor_code"] == "BYPASS-LAVA", "Heavy vehicle should be routed via Lava"
    assert "fleet_matrix" in plan_heavy, "Response must include fleet_matrix"

    print("[PASS] PART 4: Live REST Endpoints Verified.")

    # -------------------------------------------------------------------------
    # PART 5: POSTGIS DATABASE PERSISTENCE CHECK
    # -------------------------------------------------------------------------
    print("\n[PART 5] Verifying PostGIS Database Persistence...")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, hcii_score::float, hcii_tier, isolation_status
            FROM critical_habitations
            WHERE name IN ('Chungthang Sub-Divisional Base', 'Dzongu Indigenous Reserve', 'Mangan District HQ', 'Dikchu River Settlement');
        """)
        rows = cur.fetchall()
        assert len(rows) == 4, f"Expected 4 settlements in DB, got {len(rows)}"
        for r in rows:
            print(f"  -> DB Verified: {r['name']} | HCII: {r['hcii_score']} [{r['hcii_tier']}] | Status: [{r['isolation_status']}]")
            assert r["hcii_score"] > 0, f"HCII score in DB should be > 0 for {r['name']}"
    conn.close()
    print("[PASS] PART 5: PostGIS Database Persistence Verified.")

    print("\n" + "=" * 80)
    print("ALL SPRINT 3 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    test_sprint3_hcii_freight()
