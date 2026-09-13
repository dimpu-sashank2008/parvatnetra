# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- Phase 4 Tactical Resilience and Hydro-Telemetry Unit Tests
Tests:
1. CWCTeestaHydroService hydraulics and monotonic FoS degradation with river level rise.
2. GET /api/hydro/teesta-status and GET /api/hydrology/teesta-status.
3. GET /api/fleet/bro-machinery with live heavy machinery units and telemetry.
4. POST /api/alerts/ivr-broadcast with multilingual telephony dispatch.
5. GET and POST /api/mesh/toggle-relay with offline BLE mesh node state transitions.
"""

import unittest
import json
import time
from app import app
from services.cwc_sync import CWCTeestaHydroService, CWC_TEESTA_SERVICE


class TestPhase4TacticalResilience(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # -------------------------------------------------------------------------
    # PART 1: CWC Hydro-Telemetry Hydraulics and Physics Mechanics
    # -------------------------------------------------------------------------
    def test_cwc_hydraulics_computation(self):
        service = CWCTeestaHydroService()
        h = service.compute_hydraulics(water_level_m=218.4, discharge_cumecs=2480.0)
        
        self.assertEqual(h["water_level_m"], 218.4)
        self.assertEqual(h["discharge_cumecs"], 2480.0)
        self.assertAlmostEqual(h["hydraulic_radius_r_m"], 218.4 * 0.35, places=2)
        self.assertGreater(h["basal_shear_stress_pa"], 5000.0)
        self.assertGreater(h["excess_shear_ratio"], 50.0)
        self.assertGreaterEqual(h["toe_resistance_loss_pct"], 90.0)
        self.assertEqual(h["scour_risk_level"], "CRITICAL")

    def test_coupled_fos_monotonic_degradation(self):
        """
        Critical Invariant: Rising river water levels MUST increase basal shear stress (tau_b)
        and strictly decrease the slope Factor of Safety (FoS) monotonically.
        """
        service = CWCTeestaHydroService()
        stages = [200.0, 205.0, 210.0, 215.0, 218.4, 220.0, 222.0]
        
        prev_fos = float("inf")
        prev_tau = -float("inf")

        for wl in stages:
            coupled = service.compute_coupled_fos(water_level_m=wl)
            fos = coupled["factor_of_safety"]
            tau = coupled["basal_shear_pa"]

            # Strictly increasing basal shear stress
            self.assertGreater(tau, prev_tau, f"Basal shear did not increase at WL={wl}m: {tau} <= {prev_tau}")
            # Strictly decreasing Factor of Safety
            self.assertLess(fos, prev_fos, f"FoS did not decrease at WL={wl}m: {fos} >= {prev_fos}")

            prev_fos = fos
            prev_tau = tau

        # Benchmark calibration check at wl = 218.4m
        benchmark = service.compute_coupled_fos(water_level_m=218.4)
        self.assertEqual(benchmark["factor_of_safety"], 0.928)
        self.assertEqual(benchmark["risk_tier"], "RED")

    def test_cwc_background_worker_lifecycle(self):
        service = CWCTeestaHydroService()
        service.start_cwc_sync_worker(interval_seconds=1)
        self.assertIsNotNone(service._worker_thread)
        self.assertTrue(service._worker_thread.is_alive())
        time.sleep(0.1)
        service.stop_cwc_sync_worker()
        self.assertFalse(service._worker_thread.is_alive())

    # -------------------------------------------------------------------------
    # PART 2: REST API Endpoints: Hydro-Telemetry
    # -------------------------------------------------------------------------
    def test_get_teesta_hydro_status(self):
        for endpoint in ["/api/hydro/teesta-status", "/api/hydrology/teesta-status"]:
            resp = self.app.get(endpoint)
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["status"], "SUCCESS")
            self.assertIn("water_level_m", data)
            self.assertIn("discharge_cumecs", data)
            self.assertIn("basal_shear_stress_pa", data)
            self.assertIn("coupled_fos", data)
            self.assertIn("scour_risk_level", data)
            self.assertIn("reaches", data)
            self.assertGreaterEqual(len(data["reaches"]), 1)
            for reach in data["reaches"]:
                self.assertEqual(reach["geometry"]["type"], "LineString")
                self.assertGreaterEqual(len(reach["geometry"]["coordinates"]), 2)

    # -------------------------------------------------------------------------
    # PART 3: REST API Endpoints: BRO Heavy Machinery Fleet
    # -------------------------------------------------------------------------
    def test_get_bro_fleet_machinery(self):
        resp = self.app.get("/api/fleet/bro-machinery")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("command", data)
        self.assertGreaterEqual(data["count"], 4)
        
        fleet_ids = [m["id"] for m in data["fleet"]]
        self.assertIn("BRO-EXC-758A", fleet_ids)
        self.assertIn("BRO-DZR-412B", fleet_ids)
        self.assertIn("BRO-WLD-104C", fleet_ids)
        self.assertIn("BRO-BLY-991D", fleet_ids)

        for m in data["fleet"]:
            self.assertIn("name", m)
            self.assertIn("corridor", m)
            self.assertTrue(25.0 <= m["lat"] <= 29.0)
            self.assertTrue(87.0 <= m["lng"] <= 90.0)
            self.assertIn("status", m)
            self.assertIn("fuel_level_pct", m)
            self.assertIn("operator_callsign", m)
            self.assertIn("operator_contact", m)

    # -------------------------------------------------------------------------
    # PART 4: Multilingual IVR Voice Broadcast Simulation
    # -------------------------------------------------------------------------
    def test_dispatch_ivr_broadcast(self):
        payload = {
            "sector": "Sector A-17 (NH-10 Km 48 / 29th Mile)",
            "languages": ["Nepali", "Hindi", "English"]
        }
        resp = self.app.post(
            "/api/alerts/ivr-broadcast",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("broadcast_id", data)
        self.assertGreater(data["subscribers_reached"], 1000)
        self.assertIn("Nepali", data["scripts"])
        self.assertIn("Hindi", data["scripts"])
        self.assertIn("telecom_operators", data)
        self.assertGreater(data["delivery_rate_pct"], 90.0)

    # -------------------------------------------------------------------------
    # PART 5: Local BLE Mesh Node Relay Toggle
    # -------------------------------------------------------------------------
    def test_toggle_mesh_relay(self):
        resp_get = self.app.get("/api/mesh/toggle-relay")
        self.assertEqual(resp_get.status_code, 200)
        data_get = resp_get.get_json()
        initial_enabled = data_get["mesh_relay_enabled"]

        resp_toggle = self.app.post("/api/mesh/toggle-relay", json={})
        self.assertEqual(resp_toggle.status_code, 200)
        data_toggle = resp_toggle.get_json()
        self.assertEqual(data_toggle["mesh_relay_enabled"], not initial_enabled)

        resp_on = self.app.post("/api/mesh/toggle-relay", json={"enabled": True})
        self.assertEqual(resp_on.status_code, 200)
        data_on = resp_on.get_json()
        self.assertTrue(data_on["mesh_relay_enabled"])
        self.assertEqual(data_on["active_mesh_nodes"], 14)
        self.assertEqual(data_on["hops_supported"], 7)

        resp_off = self.app.post("/api/mesh/toggle-relay", json={"enabled": False})
        self.assertEqual(resp_off.status_code, 200)
        data_off = resp_off.get_json()
        self.assertFalse(data_off["mesh_relay_enabled"])
        self.assertEqual(data_off["active_mesh_nodes"], 0)


if __name__ == "__main__":
    unittest.main()
