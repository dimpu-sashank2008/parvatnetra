# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- AI Situation Report (SitRep) & Adaptive VTI Notification Matrix Test Suite
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Validates:
1. AISitRepGenerator multi-source natural language synthesis and 0-100 VTI scoring.
2. 4-tier Adaptive Notification & Siren Matrix (Normal, Elevated, High, Critical).
3. Live REST API endpoints (/api/ai/sitrep and /api/ai/evaluate-vti).
4. HTML dashboard markup for #ai-sitrep-card and #emergency-lockdown-banner.
"""

import os
import time
import json
import unittest
import urllib.request
import urllib.error

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_URL = "http://127.0.0.1:8080"


class MockAlertBus:
    def __init__(self):
        self.broadcasts = []

    def broadcast(self, event_name, payload):
        self.broadcasts.append({"event": event_name, "payload": payload})


class TestAISitRepAndVTIMatrix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO_ROOT, "templates", "index.html"), "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    # =========================================================================
    # TASK 1: AI SitRep Generator & VTI Calculation
    # =========================================================================
    def test_01_vti_scoring_and_tiers(self):
        """Test continuous 0-100 VTI scale and 4 tier classifications."""
        from services.ai_sitrep import AISitRepGenerator

        gen = AISitRepGenerator()

        # Normal condition
        vti_normal = gen.calculate_vti(fos=1.8, tau_b=500.0, rainfall_24h=10.0, crack_aperture=0.0)
        self.assertLessEqual(vti_normal, 40.0)
        self.assertEqual(gen.get_vti_tier(vti_normal), "NORMAL")

        # Elevated condition
        vti_elevated = gen.calculate_vti(fos=1.1, tau_b=2600.0, rainfall_24h=70.0, crack_aperture=15.0)
        self.assertTrue(40.0 < vti_elevated <= 70.0)
        self.assertEqual(gen.get_vti_tier(vti_elevated), "ELEVATED")

        # High condition
        vti_high = gen.calculate_vti(fos=0.95, tau_b=4000.0, rainfall_24h=100.0, crack_aperture=25.0)
        self.assertTrue(70.0 < vti_high <= 90.0)
        self.assertEqual(gen.get_vti_tier(vti_high), "HIGH")

        # Critical condition
        vti_critical = gen.calculate_vti(fos=0.74, tau_b=5400.0, rainfall_24h=130.0, crack_aperture=38.0)
        self.assertGreater(vti_critical, 90.0)
        self.assertEqual(gen.get_vti_tier(vti_critical), "CRITICAL")

    def test_02_sitrep_natural_language_synthesis(self):
        """Test executive SitRep natural language synthesis contains key telemetry."""
        from services.ai_sitrep import AI_SITREP_SERVICE

        report = AI_SITREP_SERVICE.generate_situation_report()
        self.assertEqual(report["status"], "SUCCESS")
        self.assertIn("executive_briefing", report)
        self.assertIn("vti_score", report)
        self.assertIn("vti_tier", report)
        self.assertIn("metrics", report)

        briefing = report["executive_briefing"]
        self.assertIn("NH-10", briefing)
        self.assertIn("rainfall", briefing.lower())
        self.assertIn("scour", briefing.lower())
        self.assertIn("fos", briefing.lower())

    # =========================================================================
    # TASK 2: Adaptive Notification & Siren Matrix
    # =========================================================================
    def test_03_adaptive_matrix_tiers(self):
        """Test all 4 tiers of the adaptive triage matrix via AutonomousAITriageEngine."""
        from services.ai_triage import AutonomousAITriageEngine

        mock_bus = MockAlertBus()
        engine = AutonomousAITriageEngine(alert_bus=mock_bus)

        # Tier 1: Normal (0-40) -> PASSIVE_LOGGING
        normal_metrics = {"fos": 1.7, "tau_b": 600.0, "rainfall_24h_mm": 15.0, "crack_aperture_mm": 0.0}
        res_normal = engine.execute_autonomous_triage(override_metrics=normal_metrics)
        self.assertEqual(res_normal["action"], "PASSIVE_LOGGING")
        self.assertEqual(res_normal["vti_tier"], "NORMAL")

        # Tier 2: Elevated (41-70) -> CITIZEN_ADVISORY_DISPATCHED
        elevated_metrics = {"fos": 1.1, "tau_b": 2600.0, "rainfall_24h_mm": 70.0, "crack_aperture_mm": 15.0}
        res_elevated = engine.execute_autonomous_triage(override_metrics=elevated_metrics)
        self.assertEqual(res_elevated["action"], "CITIZEN_ADVISORY_DISPATCHED")
        self.assertEqual(res_elevated["vti_tier"], "ELEVATED")
        # Check advisory broadcasted to mock bus
        advisory_events = [b for b in mock_bus.broadcasts if b["event"] == "citizen_advisory"]
        self.assertTrue(len(advisory_events) > 0)

        # Tier 3: High (71-90) -> SAR_DEVICES_FLAGGED
        high_metrics = {"fos": 0.95, "tau_b": 4000.0, "rainfall_24h_mm": 100.0, "crack_aperture_mm": 25.0}
        res_high = engine.execute_autonomous_triage(override_metrics=high_metrics)
        self.assertEqual(res_high["action"], "SAR_DEVICES_FLAGGED")
        self.assertEqual(res_high["vti_tier"], "HIGH")
        sar_events = [b for b in mock_bus.broadcasts if b["event"] == "sar_alert"]
        self.assertTrue(len(sar_events) > 0)

        # Tier 4: Critical (91-100) -> BROADCAST_DISPATCHED
        critical_metrics = {"fos": 0.74, "tau_b": 5400.0, "rainfall_24h_mm": 130.0, "crack_aperture_mm": 38.0}
        res_crit = engine.execute_autonomous_triage(override_metrics=critical_metrics, force=True)
        self.assertEqual(res_crit["action"], "BROADCAST_DISPATCHED")
        self.assertEqual(res_crit["vti_tier"], "CRITICAL")
        broadcast_events = [b for b in mock_bus.broadcasts if b["event"] == "ai_autonomous_broadcast"]
        self.assertTrue(len(broadcast_events) > 0)

    # =========================================================================
    # TASK 3: REST API Integration Endpoints
    # =========================================================================
    def test_04_rest_api_sitrep(self):
        """Test /api/ai/sitrep endpoint returns valid SitRep JSON."""
        url = f"{BASE_URL}/api/ai/sitrep"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as res:
                self.assertEqual(res.status, 200)
                data = json.loads(res.read().decode("utf-8"))
                self.assertEqual(data["status"], "SUCCESS")
                self.assertIn("executive_briefing", data)
                self.assertIn("vti_score", data)
                self.assertIn("vti_tier", data)
                self.assertIn("metrics", data)
        except urllib.error.URLError as e:
            self.fail(f"Could not connect to {url}: {e}")

    def test_05_rest_api_evaluate_vti(self):
        """Test /api/ai/evaluate-vti endpoint returns valid execution status."""
        url = f"{BASE_URL}/api/ai/evaluate-vti"
        payload = {
            "fos": 1.25,
            "river_scour_tau_b": 2200.0,
            "rainfall_24h": 65.0,
            "crack_aperture_mm": 12.0
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                self.assertEqual(res.status, 200)
                data = json.loads(res.read().decode("utf-8"))
                self.assertEqual(data["status"], "SUCCESS")
                self.assertIn("result", data)
                self.assertIn("vti_score", data["result"])
                self.assertIn("action", data["result"])
        except urllib.error.URLError as e:
            self.fail(f"Could not connect to {url}: {e}")

    # =========================================================================
    # TASK 4: DOM Elements in index.html
    # =========================================================================
    def test_06_dashboard_sitrep_and_lockdown_markup(self):
        """Verify SitRep widget and emergency lockdown banner exist in templates/index.html."""
        # Lockdown banner
        self.assertIn('id="emergency-lockdown-banner"', self.index_html)
        self.assertIn('id="lockdown-banner-dispatch-id"', self.index_html)
        self.assertIn('id="lockdown-banner-msg"', self.index_html)

        # SitRep card & elements
        self.assertIn('id="ai-sitrep-card"', self.index_html)
        self.assertIn('id="ai-sitrep-badge"', self.index_html)
        self.assertIn('id="ai-sitrep-vti"', self.index_html)
        self.assertIn('id="ai-sitrep-text"', self.index_html)
        self.assertIn('id="ai-sitrep-timestamp"', self.index_html)

        # Telemetry pills
        self.assertIn('id="ai-sitrep-imd"', self.index_html)
        self.assertIn('id="ai-sitrep-cwc"', self.index_html)
        self.assertIn('id="ai-sitrep-insar"', self.index_html)
        self.assertIn('id="ai-sitrep-cv"', self.index_html)
        self.assertIn('id="ai-sitrep-fos"', self.index_html)

        # JS functions
        self.assertIn('function fetchAISitRep', self.index_html)
        self.assertIn('window.fetchAISitRep', self.index_html)


if __name__ == "__main__":
    unittest.main()
