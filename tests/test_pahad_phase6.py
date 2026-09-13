"""
tests/test_pahad_phase6.py
===========================
PAHAD Phase 6 Unit & Integration Tests
----------------------------------------
Tests:
  01  Bypass calculation rejects heavy trucks (> 18.5T) on light-capacity routes while permitting them on 45T Lava axis
  02  Light vehicles (e.g., 2.5T EMS) are permitted on all 3 bypasses and sorted by lowest delay first
  03  Severed corridor status accurately reports monitored highways and blockage points
  04  Proximity shelter search returns valid nearest locations ordered by spherical Haversine distance
  05  Offline cache JSON exists, parses, and contains required emergency contacts & sector registry
  06  GET /api/pahad/routing/status -> HTTP 200 + corridor array
  07  POST /api/pahad/routing/calculate-bypass -> HTTP 200 + eligible routes
  08  GET /api/pahad/shelters (proximity & state filter) -> HTTP 200
  09  POST /api/pahad/routing/calculate-bypass with missing corridor_id -> HTTP 400
  10  Non-existent corridor returns NO_BYPASS_FOUND gracefully without 500
"""

import sys
import os
import unittest
import json

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_routing import (
    RoadConnectivityRoutingEngine,
    MONITORED_CORRIDORS,
    BYPASS_MATRIX,
    EMERGENCY_SHELTERS,
)
from app import app


class TestBypassRoutingEngine(unittest.TestCase):
    """Tests 01, 02, 03, 04, 05: Routing engine logic and offline asset."""

    def setUp(self):
        self.engine = RoadConnectivityRoutingEngine()

    def test_01_heavy_truck_gvw_filtering(self):
        """Bypass calculation rejects heavy trucks (> 18.5T) on light routes (Mungpoo/Peshok) while permitting 45T Lava."""
        # 32.0 Ton Freight Truck on severed NH-10
        res = self.engine.calculate_bypass(severed_corridor_id="SK-NH10", vehicle_weight_tons=32.0)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["eligible_count"], 1)
        self.assertEqual(res["ineligible_count"], 2)

        eligible_names = [r["name"] for r in res["eligible_routes"]]
        ineligible_names = [r["name"] for r in res["ineligible_routes"]]

        self.assertIn("Lava - Gorubathan Axis", eligible_names)
        self.assertIn("Mungpoo - Jorebunglow Route", ineligible_names)
        self.assertIn("Teesta Bazar - Peshok", ineligible_names)

        # Verify rejection reasons
        mungpoo = next(r for r in res["ineligible_routes"] if "Mungpoo" in r["name"])
        self.assertEqual(mungpoo["weight_clearance"], "EXCEEDED_RESTRICTION")
        self.assertGreater(mungpoo["overweight_tons"], 0.0)
        print(f"\n[PASS] Test 01: 32T truck permitted only on Lava (45T); rejected from Mungpoo (18.5T) & Peshok (3.5T).")

    def test_02_light_ems_permitted_on_all_and_sorted_by_delay(self):
        """Light vehicles (< 3.5T) permitted on all bypasses and sorted ascending by transit delay."""
        res = self.engine.calculate_bypass(severed_corridor_id="SK-NH10", vehicle_weight_tons=2.5)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["eligible_count"], 3)
        self.assertEqual(res["ineligible_count"], 0)

        # Verify sorted ascending by delay
        delays = [r["delay_minutes"] for r in res["eligible_routes"]]
        self.assertEqual(delays, sorted(delays))
        # Peshok (+60 mins) should be #1 recommendation
        self.assertEqual(res["best_route"]["name"], "Teesta Bazar - Peshok")
        self.assertEqual(res["best_route"]["delay_minutes"], 60)
        print(f"\n[PASS] Test 02: 2.5T EMS vehicle eligible for all 3 routes; fastest is {res['best_route']['name']} (+60m).")

    def test_03_corridor_status_reporting(self):
        """Severed corridor status accurately reports monitored highways and blockage points."""
        corridors = self.engine.get_corridor_status()
        self.assertGreaterEqual(len(corridors), 5)

        nh10 = self.engine.get_corridor_status("SK-NH10")
        self.assertEqual(len(nh10), 1)
        self.assertEqual(nh10[0]["corridor_id"], "SK-NH10")
        self.assertEqual(nh10[0]["status"], "SEVERED_BLOCKED")
        self.assertIn("Km 48", nh10[0]["blockage_point"])
        print(f"\n[PASS] Test 03: Corridor status verified for {nh10[0]['name']}: {nh10[0]['status']}")

    def test_04_proximity_shelters_ordered_by_distance(self):
        """Proximity shelter search returns valid nearest locations ordered by Haversine distance."""
        # Query near Rangpo border (27.17, 88.52)
        shelters = self.engine.find_nearest_shelters(lat=27.1700, lon=88.5200, limit=3)
        self.assertEqual(len(shelters), 3)

        # Distances must be sorted ascending
        dists = [s["distance_km"] for s in shelters]
        self.assertEqual(dists, sorted(dists))

        nearest = shelters[0]
        self.assertEqual(nearest["shelter_id"], "SHL-SK-01")
        self.assertLess(nearest["distance_km"], 2.0)
        self.assertIn("medical_readiness", nearest)
        print(f"\n[PASS] Test 04: Nearest shelter to Rangpo is {nearest['name']} ({nearest['distance_km']} km).")

    def test_05_offline_cache_structure(self):
        """Offline cache JSON exists, parses, and contains emergency contacts & sector registry."""
        cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "pahad_offline_cache.json")
        self.assertTrue(os.path.exists(cache_path), f"Missing cache file: {cache_path}")

        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["schema_version"], "1.0.0")
        self.assertIn("critical_sectors", data)
        self.assertIn("monitored_corridors", data)
        self.assertIn("bypass_routes", data)
        self.assertIn("emergency_shelters", data)
        self.assertIn("emergency_contacts", data)
        self.assertIn("ndrf_control_room_24x7", data["emergency_contacts"])
        self.assertIn("bro_swastik_dispatch", data["emergency_contacts"])
        print(f"\n[PASS] Test 05: Offline resilience cache JSON verified ({len(data['emergency_shelters'])} shelters, {len(data['emergency_contacts'])} emergency hotlines).")


class TestPhase6Endpoints(unittest.TestCase):
    """Tests 06, 07, 08, 09, 10: Flask REST API endpoints."""

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_06_get_routing_status_success(self):
        """GET /api/pahad/routing/status -> HTTP 200 + corridor array."""
        resp = self.client.get("/api/pahad/routing/status")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("corridors", data)
        self.assertGreaterEqual(len(data["corridors"]), 5)
        print(f"\n[PASS] Test 06: /api/pahad/routing/status -> 200 OK ({data['total_corridors']} monitored corridors)")

    def test_07_post_calculate_bypass_success(self):
        """POST /api/pahad/routing/calculate-bypass with 25T truck -> HTTP 200."""
        payload = {
            "corridor_id": "SK-NH10",
            "vehicle_weight_tons": 25.0,
        }
        resp = self.client.post(
            "/api/pahad/routing/calculate-bypass",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("eligible_routes", data)
        self.assertEqual(len(data["eligible_routes"]), 1)
        self.assertEqual(data["eligible_routes"][0]["name"], "Lava - Gorubathan Axis")
        print(f"\n[PASS] Test 07: /api/pahad/routing/calculate-bypass -> 200 OK (25T permitted on Lava)")

    def test_08_get_shelters_queries(self):
        """GET /api/pahad/shelters supports proximity search and state filtering."""
        # 1. Proximity
        resp_prox = self.client.get("/api/pahad/shelters?lat=27.17&lon=88.50&limit=2")
        self.assertEqual(resp_prox.status_code, 200)
        data_prox = json.loads(resp_prox.data)
        self.assertEqual(data_prox["query_type"], "PROXIMITY")
        self.assertEqual(len(data_prox["shelters"]), 2)

        # 2. State filter
        resp_st = self.client.get("/api/pahad/shelters?state=Sikkim")
        self.assertEqual(resp_st.status_code, 200)
        data_st = json.loads(resp_st.data)
        self.assertEqual(data_st["query_type"], "STATE_FILTER")
        self.assertTrue(all(s["state"] == "Sikkim" for s in data_st["shelters"]))
        print("\n[PASS] Test 08: /api/pahad/shelters -> 200 OK (Proximity & State filter verified)")

    def test_09_calculate_bypass_missing_corridor_returns_400(self):
        """POST /api/pahad/routing/calculate-bypass without corridor_id -> HTTP 400."""
        resp = self.client.post(
            "/api/pahad/routing/calculate-bypass",
            data=json.dumps({"vehicle_weight_tons": 15.0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ERROR")
        print("\n[PASS] Test 09: Missing corridor_id correctly returns HTTP 400.")

    def test_10_unknown_corridor_returns_no_bypass_found(self):
        """Unknown corridor returns NO_BYPASS_FOUND status gracefully without crashing."""
        resp = self.client.post(
            "/api/pahad/routing/calculate-bypass",
            data=json.dumps({"corridor_id": "UNKNOWN-CORRIDOR-99", "vehicle_weight_tons": 5.0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "NO_BYPASS_FOUND")
        self.assertEqual(data["eligible_routes"], [])
        print("\n[PASS] Test 10: Unknown corridor handled gracefully with NO_BYPASS_FOUND.")

    # -------------------------------------------------------------------------
    # PHASE 7 FRONTEND & GIS MAP INTEGRATION TESTS
    # -------------------------------------------------------------------------

    def test_11_citizen_bypass_calculator_dom(self):
        """Verify Citizen Mode Active Corridor Bypass & Safe Shelter Finder DOM elements."""
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        required_ids = [
            "citizen-bypass-calculator-card",
            "citizen-corridor-select",
            "citizen-vehicle-weight-select",
            "citizen-vehicle-weight-input",
            "btn-citizen-calc-bypass",
            "citizen-bypass-results-box",
            "citizen-bypass-recommendation-banner",
            "citizen-bypass-routes-list",
            "citizen-shelters-list",
            "citizen-bypass-count-badge",
        ]
        for elem_id in required_ids:
            self.assertIn(f'id="{elem_id}"', html, f"Missing DOM element: {elem_id}")
        print("\n[PASS] Test 11: All Citizen Bypass & Shelter Finder DOM elements verified in index.html.")

    def test_12_authority_gsi_insar_toggle_dom(self):
        """Verify Authority Mode GSI Critical Sectors & InSAR toggle button and LCP item."""
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="btn-toggle-gsi-insar"', html)
        self.assertIn('id="lbl-toggle-gsi-insar"', html)
        self.assertIn('id="lc-toggle-gsi-insar"', html)
        self.assertIn('toggleGsiInSarOverlay()', html)
        print("\n[PASS] Test 12: Authority GSI InSAR overlay toggle buttons verified in index.html.")

    def test_13_client_side_javascript_functions(self):
        """Verify that required client JavaScript functions are declared and exposed."""
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        import re
        required_fns = [
            "calculateCitizenBypassAndShelters",
            "drawCitizenBypassOnMap",
            "highlightBypassRouteOnMap",
            "centerMapOnCoords",
            "toggleGsiInSarOverlay",
            "onCitizenWeightPresetChange",
        ]
        for fn in required_fns:
            pattern = rf'function\s+{fn}\s*\('
            self.assertTrue(re.search(pattern, html), f"Missing JS function: {fn}")
            self.assertIn(f'window.{fn} = {fn}', html, f"Function not exposed to window: {fn}")
        print("\n[PASS] Test 13: All 6 client-side JavaScript functions verified in index.html.")

    def test_14_32t_vehicle_bypass_calculation(self):
        """Verify 32T vehicle bypass calculation: Lava eligible, Mungpoo/Peshok rejected."""
        resp = self.client.post(
            "/api/pahad/routing/calculate-bypass",
            data=json.dumps({"corridor_id": "SK-NH10", "vehicle_weight_tons": 32.0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")

        eligible = data.get("eligible_routes", [])
        ineligible = data.get("ineligible_routes", [])

        # Lava 45T must be eligible
        eligible_names = [r["name"] for r in eligible]
        self.assertTrue(any("Lava" in name for name in eligible_names), "Lava Axis should be eligible for 32T")

        # Mungpoo (18.5T) and Peshok (3.5T) must be ineligible
        ineligible_names = [r["name"] for r in ineligible]
        self.assertTrue(any("Mungpoo" in name for name in ineligible_names), "Mungpoo route should be rejected for 32T")
        self.assertTrue(any("Peshok" in name for name in ineligible_names), "Peshok route should be rejected for 32T")

        # Verify explicit rejection reasons
        for r in ineligible:
            self.assertIn("rejection_reason", r)
            self.assertIn("exceeds route maximum GVW limit", r["rejection_reason"])

        print(f"\n[PASS] Test 14: 32T vehicle bypass verified (1 eligible [Lava], {len(ineligible)} rejected with explicit reasons).")

    def test_15_shelters_proximity_query(self):
        """Verify /api/pahad/shelters proximity query returns closest 3 shelters with medical readiness."""
        resp = self.client.get("/api/pahad/shelters?lat=27.17&lon=88.50&limit=3")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        shelters = data.get("shelters", [])
        self.assertEqual(len(shelters), 3)

        for s in shelters:
            self.assertIn("name", s)
            self.assertIn("distance_km", s)
            self.assertIn("medical_readiness", s)
            self.assertIn("capacity_people", s)

        print(f"\n[PASS] Test 15: Top 3 shelters returned (Closest: {shelters[0]['name']}, {shelters[0]['distance_km']} km, Medical: {shelters[0]['medical_readiness']}).")


if __name__ == "__main__":
    unittest.main(verbosity=2)
