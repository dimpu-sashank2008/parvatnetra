# -*- coding: utf-8 -*-
"""
tests/test_tactical_routing_engine.py
======================================
Verifies the Interactive Multi-Profile Tactical Evacuation Routing Engine:
  1. GET & POST /api/routing/multi-profile evaluates FASTEST, SHORTEST, SAFEST.
  2. POST /api/routing/simulate-severance dynamically blocks & unblocks corridors.
  3. Dynamic rerouting updates corridor statuses without whole-page refresh.
  4. Backward compatibility of /api/routing/safe-route for mobile and dashboard clients.
  5. Evaluator Sandbox (/demo) renders the Master 1-Click Inspection Drill and SVG schematic.
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json

from app import app
from services.offline_routing_service import OFFLINE_ROUTING_SERVICE


class TestTacticalRoutingEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def setUp(self):
        # Reset corridor blockages to a clean baseline before each test
        OFFLINE_ROUTING_SERVICE.unblock_corridor("SK-NH10")

    def tearDown(self):
        # Clean up corridor blockages after each test
        OFFLINE_ROUTING_SERVICE.unblock_corridor("SK-NH10")

    def test_multi_profile_get_success(self):
        """Verify GET /api/routing/multi-profile returns 3 distinct profiles and proper metadata."""
        res = self.client.get("/api/routing/multi-profile?scenario=teesta_sikkim")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("provenance"), "[OFFLINE ROUTE / GRAPH]")
        self.assertEqual(data.get("recommended_profile"), "SAFEST")

        corridors = data.get("corridors", {})
        self.assertIn("FASTEST", corridors)
        self.assertIn("SHORTEST", corridors)
        self.assertIn("SAFEST", corridors)

        # FASTEST profile checks
        fastest = corridors["FASTEST"]
        self.assertGreater(fastest["distance_km"], 0)
        self.assertGreater(fastest["duration_minutes"], 0)
        self.assertIn("checkpoints", fastest)

        # SAFEST profile checks (BRO recommended high-ground bypass)
        safest = corridors["SAFEST"]
        self.assertGreater(safest["safety_score"], 0.8)
        self.assertFalse(safest["is_severed"])
        self.assertGreaterEqual(safest["bridge_gvw_tons"], 40.0)

    def test_multi_profile_post_with_custom_coordinates(self):
        """Verify POST /api/routing/multi-profile accepts custom origin and destination coordinates."""
        payload = {
            "origin_lat": 27.0984,
            "origin_lon": 88.4892,
            "dest_lat": 27.3300,
            "dest_lon": 88.6100,
            "weight_tons": 25.0
        }
        res = self.client.post("/api/routing/multi-profile",
                               json=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        corridors = data.get("corridors", {})
        self.assertIn("SAFEST", corridors)
        self.assertEqual(corridors["SAFEST"]["status"], "ACTIVE_RECOMMENDED")

    def test_simulate_severance_lifecycle(self):
        """Verify POST /api/routing/simulate-severance dynamically severs and clears corridors."""
        # 1. Block corridor SK-NH10
        block_res = self.client.post("/api/routing/simulate-severance",
                                     json={"corridor_id": "SK-NH10", "blocked": True},
                                     content_type="application/json")
        self.assertEqual(block_res.status_code, 200)
        block_data = block_res.get_json()
        self.assertTrue(block_data.get("is_severed"))
        self.assertTrue(block_data.get("blocked"))
        self.assertIn("SEVERED", block_data.get("message"))

        # Verify multi-profile reflects severance
        res_after_block = self.client.get("/api/routing/multi-profile")
        self.assertEqual(res_after_block.status_code, 200)
        data_after = res_after_block.get_json()
        self.assertTrue(data_after.get("is_nh10_severed"))
        self.assertEqual(data_after["corridors"]["FASTEST"]["status"], "IMPASSABLE")
        self.assertTrue(data_after["corridors"]["FASTEST"]["is_severed"])

        # 2. Unblock corridor SK-NH10
        clear_res = self.client.post("/api/routing/simulate-severance",
                                     json={"corridor_id": "SK-NH10", "blocked": False},
                                     content_type="application/json")
        self.assertEqual(clear_res.status_code, 200)
        clear_data = clear_res.get_json()
        self.assertFalse(clear_data.get("is_severed"))
        self.assertFalse(clear_data.get("blocked"))
        self.assertIn("OPEN", clear_data.get("message"))

        # Verify multi-profile reflects restoration
        res_after_clear = self.client.get("/api/routing/multi-profile")
        data_clear = res_after_clear.get_json()
        self.assertFalse(data_clear.get("is_nh10_severed"))
        self.assertFalse(data_clear["corridors"]["FASTEST"]["is_severed"])

    def test_safe_route_backward_compatibility(self):
        """Verify /api/routing/safe-route preserves backward compatibility with mobile and siren callers."""
        res = self.client.get("/api/routing/safe-route?gvw_class=LIGHT_UTILITY")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertEqual(data.get("provenance"), "[LIVE]")
        self.assertIn("primary_corridor", data)
        self.assertIn("recommended_route", data)
        self.assertTrue(data["recommended_route"]["is_safe"])
        self.assertEqual(data["recommended_route"]["status"], "AVAILABLE")

    def test_demo_page_renders_drill_and_schematic(self):
        """Verify /demo template contains the Master Evaluator Drill and Interactive Routing Card."""
        res = self.client.get("/demo")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Master 1-Click Evaluator Drill
        self.assertIn("1-CLICK SIH EVALUATOR DRILL", html)
        self.assertIn("btn-drill-play", html)
        self.assertIn("drill-progress-bar", html)
        self.assertIn("drill-narrative-box", html)
        self.assertIn("pill-drill-1", html)
        self.assertIn("pill-drill-8", html)

        # Tactical Evacuation Routing & Road Graph
        self.assertIn("Tactical Evacuation Routing & Road Graph", html)
        self.assertIn("[OFFLINE ROUTE / GRAPH]", html)
        self.assertIn("tab-route-fastest", html)
        self.assertIn("tab-route-shortest", html)
        self.assertIn("tab-route-safest", html)
        self.assertIn("svg-path-nh10", html)
        self.assertIn("svg-path-nh717a", html)
        self.assertIn("svg-path-ridge", html)
        self.assertIn("btn-toggle-severance", html)


if __name__ == "__main__":
    unittest.main()
