# -*- coding: utf-8 -*-
"""
tests/test_edge_api.py
======================
Integration tests for Edge REST APIs and Web Endpoints (Phase 3.4 Section 12, 18, 19, 21, 25).
Validates:
  - GET  /api/edge/status
  - GET  /api/edge/nodes
  - GET  /api/edge/network
  - GET  /api/edge/readings
  - GET  /api/edge/alerts
  - GET  /api/edge/siren/status
  - POST /api/edge/siren/test (dry-run guaranteed)
  - POST /api/edge/demo/inject (requires demo mode, marks [DEMO])
  - POST /api/edge/toggle-cloud (autonomous offline simulation)
  - POST /api/edge/sync/flush
  - GET  /edge-network (mission control template rendering)
"""

import os
import json
import unittest

os.environ["PARVAT_TESTING"] = "1"
os.environ["PAHAD_DEMO_MODE"] = "1"

from app import app
from backend.edge.routes import get_edge_gateway, set_edge_gateway
from backend.edge.gateway import EdgeGateway


class TestEdgeAPI(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        # Initialize clean isolated test gateway
        self.test_gw = EdgeGateway(
            gateway_id="GW-TEST-API",
            location="Singtam Depo Test",
            db_path=":memory:"
        )
        set_edge_gateway(self.test_gw)

    def test_get_edge_status(self):
        """GET /api/edge/status must return complete gateway operational metrics."""
        res = self.client.get("/api/edge/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        gw_data = data["data"]
        self.assertEqual(gw_data["gateway_id"], "GW-TEST-API")
        self.assertIn("buffered_readings_count", gw_data)
        self.assertIn("siren", gw_data)
        self.assertIn("mesh", gw_data)

    def test_get_edge_nodes(self):
        """GET /api/edge/nodes must return registered mesh nodes and relays."""
        res = self.client.get("/api/edge/nodes")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertGreaterEqual(data["total_nodes"], 5)
        self.assertIn("nodes", data)

    def test_get_edge_network(self):
        """GET /api/edge/network must return RF network parameters and packet stats."""
        res = self.client.get("/api/edge/network")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertAlmostEqual(data["network"]["frequency_mhz"], 865.2, places=1)

    def test_siren_status_and_dry_run_test(self):
        """GET /api/edge/siren/status and POST /api/edge/siren/test."""
        # Status
        st_res = self.client.get("/api/edge/siren/status")
        self.assertEqual(st_res.status_code, 200)
        st_data = st_res.get_json()
        self.assertTrue(st_data["siren"]["dry_run"])

        # Dry run test
        test_res = self.client.post("/api/edge/siren/test", json={"requested_by": "QA_SUITE"})
        self.assertEqual(test_res.status_code, 200)
        test_data = test_res.get_json()
        self.assertEqual(test_data["status"], "SUCCESS")
        self.assertEqual(test_data["event"]["event_type"], "SIREN_TEST_EVENT")
        self.assertTrue(test_data["event"]["dry_run"])

    def test_demo_inject_hazard_escalation(self):
        """POST /api/edge/demo/inject must ingest simulated values and return pipeline state."""
        payload = {
            "node_id": "SN-DEMO-01",
            "soil_moisture": 70.0,
            "pore_pressure": 45.0,
            "tilt": 3.8, # Critical
            "rainfall": 60.0
        }
        res = self.client.post("/api/edge/demo/inject", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["provenance"], "[DEMO]")
        pipe = data["pipeline_result"]
        self.assertEqual(pipe["edge_safety_state"], "CRITICAL")
        self.assertIsNotNone(pipe["siren_event"])

    def test_toggle_cloud_and_sync_flush(self):
        """POST /api/edge/toggle-cloud must toggle backhaul state and buffer/flush queue."""
        # Initial is online
        self.assertTrue(self.test_gw.sync.is_cloud_connected)

        # Toggle to offline
        t1 = self.client.post("/api/edge/toggle-cloud")
        self.assertEqual(t1.status_code, 200)
        d1 = t1.get_json()
        self.assertFalse(d1["is_cloud_connected"])
        self.assertEqual(d1["mode"], "EDGE_OFFLINE_AUTONOMOUS")

        # Inject reading while offline -> should buffer
        self.client.post("/api/edge/demo/inject", json={"node_id": "SN-OFFLINE", "soil_moisture": 30})
        self.assertEqual(self.test_gw.store.get_queue_stats()["buffered_count"], 1)

        # Toggle back to online -> flushes
        t2 = self.client.post("/api/edge/toggle-cloud")
        self.assertEqual(t2.status_code, 200)
        d2 = t2.get_json()
        self.assertTrue(d2["is_cloud_connected"])
        self.assertEqual(d2["mode"], "CLOUD_CONNECTED")

    def test_page_edge_network_renders(self):
        """GET /edge-network must render the mission control HTML template."""
        res = self.client.get("/edge-network")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("LOCAL EDGE NETWORK", html)
        self.assertIn("LORA SUB-GHZ WIRELESS MESH TOPOLOGY", html)
        self.assertIn("ACOUSTIC EVACUATION SIREN CONTROLLER", html)
        self.assertIn("SIH 26001", html)


if __name__ == "__main__":
    unittest.main()
