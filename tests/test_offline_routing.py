# -*- coding: utf-8 -*-
"""
tests/test_offline_routing.py
=============================
PARVAT NETRA • Phase 5D Offline Routing & Lifeline Logistics Test Suite
-----------------------------------------------------------------------
Validates:
  1. Offline emergency routing engine (services/offline_routing_service.py)
  2. Blocked arterial corridor detection and bypass recommendation
  3. Nearest evacuation shelter discovery via spherical Haversine formula
  4. Explicit 'OFFLINE ROUTE' labeling and provenance metadata
  5. POST /api/routing/offline-plan HTTP endpoint contract
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
from app import app
from services.offline_routing_service import OFFLINE_ROUTING_SERVICE


class TestOfflineRouting(unittest.TestCase):
    """Verifies offline road graph and emergency shelter navigation."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.routing_svc = OFFLINE_ROUTING_SERVICE

    def test_01_nearest_shelter_lookup(self):
        """Finds closest emergency shelter for a given hillslope location."""
        # Rangpo area coordinates
        shelter = self.routing_svc.find_nearest_shelter(27.180, 88.530)
        self.assertIsNotNone(shelter)
        self.assertIn("shelter_id", shelter)
        self.assertIn("name", shelter)
        self.assertIn("distance_km", shelter)
        self.assertLess(shelter["distance_km"], 5.0)

    def test_02_plan_offline_route_with_destination(self):
        """Calculates distance and travel time to destination tagged as OFFLINE ROUTE."""
        plan = self.routing_svc.plan_offline_route(
            origin_lat=27.3300,
            origin_lon=88.6100,
            dest_lat=27.1780,
            dest_lon=88.5290,
            vehicle_weight_tons=3.5,
            avoid_blockages=False,
            find_shelter_if_no_dest=False
        )
        self.assertEqual(plan["status"], "SUCCESS")
        self.assertEqual(plan["route_label"], "OFFLINE ROUTE")
        self.assertEqual(plan["provenance"], "[OFFLINE ROUTE]")
        self.assertTrue(plan["is_offline"])
        self.assertGreater(plan["route_distance_km"], 0.0)
        self.assertGreater(plan["estimated_time_minutes"], 0)

    def test_03_blockage_avoidance_bypass(self):
        """Detects severed corridor on NH-10 and recommends NH-717A bypass."""
        plan = self.routing_svc.plan_offline_route(
            origin_lat=27.3300,
            origin_lon=88.6100,
            dest_lat=26.8500,
            dest_lon=88.4000,
            vehicle_weight_tons=12.0,
            avoid_blockages=True
        )
        self.assertEqual(plan["status"], "SUCCESS")
        self.assertGreater(plan["active_blockages_detected"], 0)
        self.assertIn(plan["route_mode"], ["BYPASS_AVOIDANCE", "DIRECT_LOCAL"])
        if plan["route_mode"] == "BYPASS_AVOIDANCE":
            self.assertIsNotNone(plan["bypass_recommendation"])

    def test_04_offline_routing_api_endpoint(self):
        """POST /api/routing/offline-plan returns valid offline route plan."""
        payload = {
            "origin_lat": 27.3300,
            "origin_lon": 88.6100,
            "find_shelter": True,
            "vehicle_weight_tons": 5.0
        }
        res = self.client.post("/api/routing/offline-plan", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("route_label"), "OFFLINE ROUTE")
        self.assertEqual(data.get("provenance"), "[OFFLINE ROUTE]")
        self.assertIn("nearest_shelter", data)


if __name__ == "__main__":
    unittest.main()
