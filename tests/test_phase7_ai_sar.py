# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- Phase 7 Unit & Integration Test Suite
Autonomous AI Multi-Source Triage Engine & Offline Last-Known GPS SAR Tracking Cache
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Validates:
1. Autonomous AI Multi-Source Triage Engine convergence decision matrix (FoS, Scour, Rain, Edge CV).
2. Autonomous siren trigger and CAP dispatch without human delay (AI_AUTONOMOUS_BROADCAST).
3. Offline Last-Known GPS Position Tracking Cache (telemetry ping, 120s timeout, 15km geofence).
4. Telemetry REST endpoints: /api/telemetry/ping, /api/telemetry/devices, /api/telemetry/simulate-disconnect.
5. Authority SAR Dashboard integration markup and Leaflet GIS pulsing markers.
"""

import os
import time
import json
import unittest
import urllib.request
import urllib.error

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_URL = "http://127.0.0.1:8080"


class TestPhase7AISAR(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO_ROOT, "templates", "index.html"), "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    # =========================================================================
    # TASK 1: Autonomous AI Multi-Source Triage Engine
    # =========================================================================
    def test_01_ai_triage_convergence_logic(self):
        """Test the 4-source convergence matrix: FoS (<1.0), Scour (>5000Pa), Rain (>120mm), Crack (>30mm)."""
        from services.ai_triage import AutonomousAITriageEngine

        engine = AutonomousAITriageEngine(alert_bus=None)

        # 1. Test All 4 Modalities Breached (100% Convergence)
        all_breached_metrics = {
            "fos": 0.745,             # < 1.0 (Breached)
            "tau_b": 5986.65,          # > 5000 Pa (Breached)
            "rainfall_24h_mm": 142.0,  # > 120 mm (Breached)
            "crack_aperture_mm": 41.5  # > 30 mm (Breached)
        }
        res_full = engine.evaluate_convergence(all_breached_metrics)
        self.assertEqual(res_full["breach_count"], 4)
        self.assertEqual(res_full["convergence_score"], 100.0)
        self.assertTrue(res_full["is_critical_convergence"])
        self.assertEqual(res_full["status"], "CRITICAL_CONVERGENCE")
        self.assertIn("explainability", res_full)
        self.assertIn("why", res_full["explainability"])

        # 2. Test 3 Modalities Breached (75% Convergence - Still Critical)
        three_breached_metrics = {
            "fos": 0.880,              # < 1.0 (Breached)
            "tau_b": 5200.0,           # > 5000 Pa (Breached)
            "rainfall_24h_mm": 135.0,  # > 120 mm (Breached)
            "crack_aperture_mm": 15.0  # <= 30 mm (Safe)
        }
        res_three = engine.evaluate_convergence(three_breached_metrics)
        self.assertEqual(res_three["breach_count"], 3)
        self.assertEqual(res_three["convergence_score"], 75.0)
        self.assertTrue(res_three["is_critical_convergence"])

        # 3. Test Low Risk (1 Modality Breached - Not Critical)
        low_risk_metrics = {
            "fos": 1.45,               # >= 1.0 (Safe)
            "tau_b": 2400.0,           # <= 5000 Pa (Safe)
            "rainfall_24h_mm": 45.0,   # <= 120 mm (Safe)
            "crack_aperture_mm": 35.0  # > 30 mm (Breached)
        }
        res_low = engine.evaluate_convergence(low_risk_metrics)
        self.assertEqual(res_low["breach_count"], 1)
        self.assertEqual(res_low["convergence_score"], 25.0)
        self.assertFalse(res_low["is_critical_convergence"])
        self.assertEqual(res_low["status"], "ELEVATED_WATCH")

        print("[PASS] 1. Autonomous AI multi-source triage convergence matrix verified.")

    def test_02_ai_autonomous_broadcast_execution(self):
        """Test autonomous trigger execution and SSE siren dispatch upon critical convergence."""
        from services.ai_triage import AutonomousAITriageEngine

        class MockAlertBus:
            def __init__(self):
                self.messages = []
            def broadcast(self, event_type, data):
                self.messages.append({"event": event_type, "data": data})

        mock_bus = MockAlertBus()
        engine = AutonomousAITriageEngine(alert_bus=mock_bus)

        # Execute autonomous triage with critical convergence
        crit_metrics = {
            "fos": 0.745,
            "tau_b": 5990.0,
            "rainfall_24h_mm": 140.0,
            "crack_aperture_mm": 42.0,
            "sector": "NH-10 Km 48 (29th Mile Sector)"
        }
        result = engine.execute_autonomous_triage(override_metrics=crit_metrics, force=True)

        self.assertEqual(result["action"], "BROADCAST_DISPATCHED")
        self.assertTrue(result["dispatch_id"].startswith("AI-AUTO-"))

        # Verify broadcast to bus
        self.assertGreaterEqual(len(mock_bus.messages), 1)
        broadcast_types = [m["data"].get("type") for m in mock_bus.messages]
        self.assertIn("AI_AUTONOMOUS_BROADCAST", broadcast_types)
        self.assertIn("AUTHORITY_SIREN_DISPATCH", broadcast_types)

        # Test live REST endpoint /api/ai/triage-status
        req = urllib.request.Request(f"{BASE_URL}/api/ai/triage-status")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "SUCCESS")
            self.assertIn("evaluation", data)
            self.assertIn("convergence_score", data["evaluation"])

        print("[PASS] 2. Autonomous AI broadcast dispatch without human delay verified.")

    # =========================================================================
    # TASK 2: Offline Last-Known GPS Tracking Cache for SAR
    # =========================================================================
    def test_03_sar_tracking_cache_logic(self):
        """Test telemetry ping ingestion, Haversine geofence check, and 120s offline disconnect timeout."""
        from services.sar_tracking import SARTrackingService, calculate_haversine_km

        sar = SARTrackingService()

        # 1. Haversine distance accuracy
        # Km 48 epicenter: 27.2010, 88.5180
        # Singtam: 27.2340, 88.4980 (~4.14 km)
        d_singtam = calculate_haversine_km(27.2010, 88.5180, 27.2340, 88.4980)
        self.assertTrue(3.8 <= d_singtam <= 4.5, f"Expected Singtam ~4.1 km, got {d_singtam}")

        # 2. Record fresh ping inside hazard zone
        rec = sar.record_ping(
            device_id="DEV-TEST-001",
            lat=27.2025,
            lng=88.5170,
            battery_level=85,
            name="Test Vehicle In-Zone"
        )
        self.assertEqual(rec["device_id"], "DEV-TEST-001")
        self.assertEqual(rec["status"], "ONLINE")
        self.assertFalse(rec["is_sar_target"])
        self.assertTrue(rec["inside_hazard_zone"])

        # 3. Simulate disconnect (> 120s timeout)
        sar.simulate_disconnect("DEV-TEST-001", silent_seconds=150.0)
        devices = sar.get_devices()
        dev_lookup = {d["device_id"]: d for d in devices}

        self.assertIn("DEV-TEST-001", dev_lookup)
        target_dev = dev_lookup["DEV-TEST-001"]
        self.assertEqual(target_dev["status"], "OFFLINE_DISCONNECTED")
        self.assertTrue(target_dev["is_sar_target"])
        self.assertGreater(target_dev["seconds_since_ping"], 120)

        # 4. Device outside hazard zone (> 15 km) should NOT be flagged as SAR target even if offline
        rec_far = sar.record_ping(
            device_id="DEV-FAR-002",
            lat=26.7271,
            lng=88.3953,  # Siliguri (~54 km away)
            battery_level=50,
            name="Distant Siliguri Truck"
        )
        self.assertFalse(rec_far["inside_hazard_zone"])
        sar.simulate_disconnect("DEV-FAR-002", silent_seconds=200.0)
        dev_lookup_far = {d["device_id"]: d for d in sar.get_devices()}
        self.assertFalse(dev_lookup_far["DEV-FAR-002"]["is_sar_target"])

        print("[PASS] 3. Offline Last-Known GPS tracking cache and SAR timeout rules verified.")

    def test_04_sar_telemetry_rest_endpoints(self):
        """Test /api/telemetry/ping, /api/telemetry/devices, and /api/telemetry/simulate-disconnect."""
        # 1. Post telemetry heartbeat ping
        ping_payload = {
            "device_id": "DEV-TEST-HTTP-PING",
            "lat": 27.2030,
            "lng": 88.5165,
            "battery_level": 78,
            "name": "HTTP Traveler Test",
            "driver_or_contact": "Rinchen Dorjee (+91 98001-12345)",
            "passengers": 3
        }
        req_ping = urllib.request.Request(
            f"{BASE_URL}/api/telemetry/ping",
            data=json.dumps(ping_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_ping, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "RECORDED")
            self.assertEqual(data["device"]["device_id"], "DEV-TEST-HTTP-PING")
            self.assertEqual(data["device"]["status"], "ONLINE")

        # 2. Get list of telemetry devices
        req_list = urllib.request.Request(f"{BASE_URL}/api/telemetry/devices")
        with urllib.request.urlopen(req_list, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "SUCCESS")
            self.assertIn("devices", data)
            self.assertGreaterEqual(len(data["devices"]), 2)
            self.assertGreaterEqual(data["sar_targets_count"], 1)

        # 3. Simulate disconnect endpoint
        req_disc = urllib.request.Request(
            f"{BASE_URL}/api/telemetry/simulate-disconnect",
            data=json.dumps({"device_id": "DEV-TEST-HTTP-PING", "silent_seconds": 180.0}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_disc, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "SIMULATED_DISCONNECT")
            self.assertEqual(data["device"]["status"], "OFFLINE_DISCONNECTED")
            self.assertTrue(data["device"]["is_sar_target"])

        print("[PASS] 4. SAR telemetry REST API endpoints fully verified.")

    # =========================================================================
    # TASK 3: Authority SAR Dashboard Integration
    # =========================================================================
    def test_05_authority_sar_dashboard_markup(self):
        """Verify presence of SAR Dashboard panel, pulsing markers, and layer controls."""
        # Panel markup
        self.assertIn('id="sar-tracking-panel"', self.index_html, "Missing #sar-tracking-panel")
        self.assertIn('Active SAR &amp; Disconnected Devices', self.index_html, "Missing SAR panel title")
        self.assertIn('id="sar-offline-count-badge"', self.index_html, "Missing #sar-offline-count-badge")
        self.assertIn('id="sar-devices-table-body"', self.index_html, "Missing #sar-devices-table-body")

        # Layer toggle
        self.assertIn('id="lc-toggle-sar"', self.index_html, "Missing #lc-toggle-sar layer toggle")
        self.assertIn('Disconnected Devices (SAR)', self.index_html, "Missing SAR toggle label")

        # JavaScript controllers
        self.assertIn('loadSARTargets', self.index_html, "loadSARTargets function missing")
        self.assertIn('focusSARTarget', self.index_html, "focusSARTarget function missing")
        self.assertIn('refreshSARDevices', self.index_html, "refreshSARDevices function missing")
        self.assertIn('[SAR TARGET: LAST KNOWN GPS]', self.index_html, "SAR TARGET badge label missing")
        self.assertIn('/api/telemetry/devices', self.index_html, "Telemetry devices URL missing in template")

        # SSE AI autonomous listener
        self.assertIn('ai_autonomous_broadcast', self.index_html, "ai_autonomous_broadcast listener missing")
        self.assertIn('AI_AUTONOMOUS_BROADCAST', self.index_html, "AI_AUTONOMOUS_BROADCAST type missing")

        print("[PASS] 5. Authority SAR Dashboard integration markup and Leaflet controls verified.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
