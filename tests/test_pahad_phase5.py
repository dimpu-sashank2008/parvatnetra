"""
tests/test_pahad_phase5.py
===========================
PAHAD Phase 5 Unit & Integration Tests
----------------------------------------
Tests:
  01  Prioritization math ranks single-access isolated routes higher than redundant secondary corridors
  02  Staged rescue forces are correctly mapped to their respective NER states
  03  Priority score formula clamps ETA at 0.5 hours to prevent division by zero
  04  GET /api/pahad/response-prioritization -> HTTP 200 + valid priority_queue
  05  GET /api/pahad/regional-overview -> HTTP 200 + 8-state breakdown + highest CRI
  06  Missing or empty parameters return safe fallbacks without 500 errors
  07  index.html contains #btn-pahad-regional-drawer and #pahad-regional-drawer DOM elements
  08  index.html contains authority guardrail for regional intelligence drawer
"""

import sys
import os
import unittest
import json

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_prioritization import (
    EmergencyResponsePrioritizer,
    CRITICALITY_WEIGHTS,
    RESCUE_FORCE_MAPPING,
)
from app import app


class TestPrioritizationEngine(unittest.TestCase):
    """Tests 01, 02, 03: Response Prioritisation Algorithm."""

    def setUp(self):
        self.prioritizer = EmergencyResponsePrioritizer()

    def test_01_single_access_ranked_higher_than_secondary(self):
        """Single-access isolated route ranks higher than redundant secondary corridor given identical pop and CRI."""
        # Route 1: Single Access (weight 2.5)
        r_isolated = {
            "sector_id": "SEC-ISOLATED",
            "name": "Isolated Pass Corridor",
            "state": "Sikkim",
            "population_at_risk": 20000,
            "cri_score": 80.0,
            "road_criticality": "STRATEGIC_SINGLE_ACCESS",
            "eta_hours": 1.0,
        }
        # Route 2: Secondary Bypass (weight 1.2)
        r_secondary = {
            "sector_id": "SEC-SECONDARY",
            "name": "Secondary Bypass Route",
            "state": "Sikkim",
            "population_at_risk": 20000,
            "cri_score": 80.0,
            "road_criticality": "STATE_HIGHWAY_SECONDARY",
            "eta_hours": 1.0,
        }

        ranked = self.prioritizer.rank_active_sectors([r_secondary, r_isolated])
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["sector_id"], "SEC-ISOLATED")
        self.assertEqual(ranked[1]["sector_id"], "SEC-SECONDARY")
        self.assertGreater(ranked[0]["priority_score"], ranked[1]["priority_score"])
        # Theoretical: (20000 * 0.8 * 2.5) / 1.0 = 40000 vs (20000 * 0.8 * 1.2) / 1.0 = 19200
        self.assertEqual(ranked[0]["priority_score"], 40000.0)
        self.assertEqual(ranked[1]["priority_score"], 19200.0)
        print(f"\n[PASS] Test 01: Single-access route ({ranked[0]['priority_score']}) ranked over secondary ({ranked[1]['priority_score']}).")

    def test_02_rescue_forces_mapped_correctly(self):
        """Rescue forces correctly mapped across all 8 NER states."""
        expected_forces = {
            "Sikkim": "BRO Project Swastik / NDRF 2nd Bn",
            "Mizoram": "BRO Project Pushpak / SDRF Aizawl",
            "Nagaland": "BRO Project Sewak / SDRF Kohima",
            "Arunachal Pradesh": "BRO Project Vartak / NDRF 12th Bn",
            "Assam": "SDRF Guwahati / NDRF 1st Bn",
            "Meghalaya": "SDRF Shillong",
            "Manipur": "BRO Project Sewak / NDRF 12th Bn",
            "Tripura": "SDRF Agartala",
        }

        test_sectors = [
            {"sector_id": f"TEST-{st[:3].upper()}", "state": st, "population_at_risk": 5000, "cri_score": 70.0}
            for st in expected_forces.keys()
        ]

        ranked = self.prioritizer.rank_active_sectors(test_sectors)
        for r in ranked:
            st = r["state"]
            self.assertEqual(
                r["assigned_rescue_force"],
                expected_forces[st],
                f"Incorrect rescue force for {st}: {r['assigned_rescue_force']}"
            )
        print(f"\n[PASS] Test 02: All 8 NER state rescue forces verified.")

    def test_03_eta_clamping_prevents_zero_division(self):
        """ETA <= 0.0 is clamped at 0.5 hours to prevent division by zero or infinite priority."""
        score_zero_eta = self.prioritizer.calculate_priority_score(
            population_at_risk=10000,
            cri=80.0,
            road_criticality="NATIONAL_HIGHWAY_ARTERIAL",
            eta_hours=0.0,
        )
        score_half_eta = self.prioritizer.calculate_priority_score(
            population_at_risk=10000,
            cri=80.0,
            road_criticality="NATIONAL_HIGHWAY_ARTERIAL",
            eta_hours=0.5,
        )
        self.assertEqual(score_zero_eta, score_half_eta)
        self.assertGreater(score_zero_eta, 0.0)
        print(f"\n[PASS] Test 03: ETA clamping at 0.5h verified: score={score_zero_eta}.")


class TestPhase5Endpoints(unittest.TestCase):
    """Tests 04, 05, 06: REST API endpoints."""

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_04_get_response_prioritization_success(self):
        """GET /api/pahad/response-prioritization -> HTTP 200 + valid ranked queue."""
        resp = self.client.get("/api/pahad/response-prioritization")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("priority_queue", data)
        self.assertGreaterEqual(len(data["priority_queue"]), 1)

        top = data["priority_queue"][0]
        self.assertIn("priority_score", top)
        self.assertIn("assigned_rescue_force", top)
        self.assertIn("evacuation_advisory", top)
        self.assertEqual(top["priority_rank"], 1)
        print(f"\n[PASS] Test 04: /api/pahad/response-prioritization -> 200 OK (Top: {top['name']}, Score: {top['priority_score']})")

    def test_05_get_regional_overview_success(self):
        """GET /api/pahad/regional-overview -> HTTP 200 + 8-state breakdown + highest CRI."""
        resp = self.client.get("/api/pahad/regional-overview")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["states_monitored"], 8)
        self.assertIn("state_summaries", data)
        self.assertGreater(data["highest_active_cri"], 0.0)

        # Check all 8 NER states are represented
        for st in ("Sikkim", "Mizoram", "Nagaland", "Arunachal Pradesh", "Manipur", "Meghalaya", "Assam", "Tripura"):
            self.assertIn(st, data["state_summaries"])
            summary = data["state_summaries"][st]
            self.assertIn("highest_cri", summary)
            self.assertIn("assigned_rescue_force", summary)
        print(f"\n[PASS] Test 05: /api/pahad/regional-overview -> 200 OK (8 states, Highest CRI: {data['highest_active_cri']})")

    def test_06_state_filter_and_safe_fallbacks(self):
        """Filtering by state works, and non-existent states return safe empty queues."""
        resp_sk = self.client.get("/api/pahad/response-prioritization?state=Sikkim")
        self.assertEqual(resp_sk.status_code, 200)
        data_sk = json.loads(resp_sk.data)
        self.assertTrue(all(s["state"] == "Sikkim" for s in data_sk["priority_queue"]))

        resp_invalid = self.client.get("/api/pahad/response-prioritization?state=NonExistentState")
        self.assertEqual(resp_invalid.status_code, 200)
        data_inv = json.loads(resp_invalid.data)
        self.assertEqual(data_inv["total_evaluated"], 0)
        self.assertEqual(len(data_inv["priority_queue"]), 0)
        print("\n[PASS] Test 06: State filtering and non-existent fallback return HTTP 200 safely.")


class TestRegionalDrawerDOM(unittest.TestCase):
    """Tests 07, 08: Frontend template DOM elements and authority guardrail."""

    def setUp(self):
        with open("templates/index.html", "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_07_drawer_dom_elements_present(self):
        """index.html contains required button, drawer container, grid, and table elements."""
        self.assertIn('id="btn-pahad-regional-drawer"', self.html)
        self.assertIn('togglePahadRegionalDrawer()', self.html)
        self.assertIn('id="pahad-regional-drawer"', self.html)
        self.assertIn('id="pahad-ner-states-grid"', self.html)
        self.assertIn('id="pahad-prioritization-tbody"', self.html)
        self.assertIn('id="btn-simulate-insar"', self.html)
        self.assertIn('simulatePahadInSarCreep()', self.html)
        print("\n[PASS] Test 07: All Regional Drawer DOM components present in index.html.")

    def test_08_authority_guardrail_present(self):
        """index.html script contains authority-check guardrails so drawer is never exposed to citizen mode."""
        self.assertIn("currentPortalMode === 'citizen'", self.html)
        self.assertIn("Regional Drawer blocked: Authority role required", self.html)
        print("\n[PASS] Test 08: Citizen mode authority guardrail verified in client script.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
