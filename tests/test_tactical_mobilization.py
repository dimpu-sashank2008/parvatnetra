# -*- coding: utf-8 -*-
"""
tests/test_tactical_mobilization.py
===================================
Verifies the Tactical Commander SitRep & Resource Mobilization Engine:
  1. Resource scaling across risk levels (CRITICAL, HIGH, ELEVATED, NORMAL)
  2. NDRF / SDRF search and rescue personnel & equipment calculation
  3. BRO Task Force heavy machinery & Bailey bridge staging
  4. Medical triage capacity & shelter beds allocation
  5. REST API contracts for /api/tactical/briefing and /api/tactical/dispatch-plan
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json

from app import app
from services.ai_sitrep import AI_SITREP_SERVICE


class TestTacticalMobilization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_mobilization_critical_tier(self):
        """Verify Priority 1 Critical dispatch when threat >= 90 or FoS <= 0.8."""
        plan = AI_SITREP_SERVICE.generate_tactical_mobilization_plan(
            sector_id="SK-NH10-KM48",
            vti_score=94.5,
            fos=0.62,
            population_exposed=1500
        )
        self.assertEqual(plan["priority_tier"], "PRIORITY_1_CRITICAL")
        self.assertEqual(plan["transit_directive"], "IMMEDIATE_MANDATORY_EVACUATION")
        self.assertEqual(plan["ndrf_sdrf"]["rescue_battalions"], 4)
        self.assertEqual(plan["ndrf_sdrf"]["deployed_personnel"], 160)
        self.assertEqual(plan["ndrf_sdrf"]["canine_search_teams"], 4)
        self.assertEqual(plan["ndrf_sdrf"]["deep_acoustic_life_detectors"], 6)
        self.assertEqual(plan["bro_infrastructure"]["tracked_excavators_20ton"], 8)
        self.assertEqual(plan["bro_infrastructure"]["bailey_bridge_spans_feet"], 200)
        self.assertTrue(plan["aerial_support"]["heli_recon_requested"])
        self.assertGreaterEqual(plan["medical_and_shelter"]["field_hospital_beds"], 600)

    def test_mobilization_high_tier(self):
        """Verify Priority 2 High dispatch when threat >= 70 or FoS < 1.0."""
        plan = AI_SITREP_SERVICE.generate_tactical_mobilization_plan(
            sector_id="MN-NONEY-01",
            vti_score=78.0,
            fos=0.92,
            population_exposed=1000
        )
        self.assertEqual(plan["priority_tier"], "PRIORITY_2_HIGH")
        self.assertEqual(plan["transit_directive"], "CONTROLLED_ONE_WAY_DETOUR")
        self.assertEqual(plan["ndrf_sdrf"]["rescue_battalions"], 2)
        self.assertEqual(plan["ndrf_sdrf"]["deployed_personnel"], 80)
        self.assertEqual(plan["bro_infrastructure"]["tracked_excavators_20ton"], 4)
        self.assertEqual(plan["bro_infrastructure"]["bailey_bridge_spans_feet"], 80)

    def test_mobilization_normal_tier(self):
        """Verify Priority 4 Normal tier when hillslopes are in stable equilibrium."""
        plan = AI_SITREP_SERVICE.generate_tactical_mobilization_plan(
            sector_id="CTRL-SK-DRY-01",
            vti_score=14.0,
            fos=1.85,
            population_exposed=500
        )
        self.assertEqual(plan["priority_tier"], "PRIORITY_4_NORMAL")
        self.assertEqual(plan["transit_directive"], "UNRESTRICTED_MOUNTAIN_TRANSIT")
        self.assertEqual(plan["ndrf_sdrf"]["deployed_personnel"], 0)
        self.assertEqual(plan["bro_infrastructure"]["bailey_bridge_spans_feet"], 0)
        self.assertFalse(plan["aerial_support"]["heli_recon_requested"])

    def test_api_tactical_briefing(self):
        """Verify GET /api/tactical/briefing endpoint returns 200 and schema."""
        res = self.client.get("/api/tactical/briefing?sector_id=SK-NH10-KM48")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["sector_id"], "SK-NH10-KM48")
        self.assertIn("sitrep", data)
        self.assertIn("vti_score", data)
        self.assertIn("mobilization_plan", data)
        mob = data["mobilization_plan"]
        self.assertIn("ndrf_sdrf", mob)
        self.assertIn("bro_infrastructure", mob)
        self.assertIn("medical_and_shelter", mob)

    def test_api_tactical_dispatch_plan(self):
        """Verify POST /api/tactical/dispatch-plan endpoint returns 200 and schema."""
        payload = {
            "sector_id": "MZ-AIZAWL-MELTHUM",
            "vti_score": 92.0,
            "fos": 0.58,
            "population_exposed": 2000
        }
        res = self.client.post("/api/tactical/dispatch-plan", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["sector_id"], "MZ-AIZAWL-MELTHUM")
        self.assertIn("dispatch_plan", data)
        dp = data["dispatch_plan"]
        self.assertEqual(dp["priority_tier"], "PRIORITY_1_CRITICAL")
        self.assertEqual(dp["bro_infrastructure"]["tracked_excavators_20ton"], 8)


if __name__ == "__main__":
    unittest.main()
