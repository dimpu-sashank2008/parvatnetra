# -*- coding: utf-8 -*-
"""
tests/test_offline_lora_mesh.py
================================
Automated unit & integration test suite for:
1. First Responder Offline Field Triage sync (/api/edge/field-reports/sync)
2. Field reports retrieval (/api/edge/field-reports)
3. Sub-GHz LoRa RF packet frame stream (/api/edge/mesh/packets)
4. Emergency LoRa packet burst simulation (/api/edge/mesh/simulate-burst)
5. EdgeStore persistent field reports schema & querying
6. LoRaMesh RF packet buffer & synthetic hex frames
7. Service Worker precache & PWA manifest shortcuts
"""

import os
import json
import unittest

os.environ["PARVAT_TESTING"] = "1"
os.environ["PAHAD_DEMO_MODE"] = "1"

from app import app
from backend.edge.routes import get_edge_gateway, set_edge_gateway
from backend.edge.gateway import EdgeGateway
from backend.edge.edge_store import EdgeStore
from backend.edge.mesh import LoRaMesh


class TestOfflineLoRaMesh(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        # Initialize an isolated in-memory gateway
        self.test_gw = EdgeGateway(
            gateway_id="GW-TEST-LORA",
            location="Likhu Veer Deep Gorge Test",
            db_path=":memory:"
        )
        set_edge_gateway(self.test_gw)

    def test_field_reports_sync_and_query(self):
        """Test POST /api/edge/field-reports/sync and GET /api/edge/field-reports."""
        reports_payload = {
            "reports": [
                {
                    "report_id": "RPT-TEST-001",
                    "incident_type": "SLOPE_CRACK",
                    "severity": "CRITICAL",
                    "latitude": 27.0984,
                    "longitude": 88.4892,
                    "crack_aperture_mm": 48.5,
                    "casualties": 0,
                    "notes": "Tension crack widening along NH-10 Likhu Veer corridor",
                    "reporter_name": "SDRF Unit 4 Patrol",
                    "reporter_role": "FIRST_RESPONDER",
                    "created_at": "2026-09-18T09:00:00Z"
                },
                {
                    "report_id": "RPT-TEST-002",
                    "incident_type": "ROCKFALL_BLOCKAGE",
                    "severity": "HIGH",
                    "latitude": 27.1050,
                    "longitude": 88.4920,
                    "crack_aperture_mm": 0.0,
                    "casualties": 2,
                    "notes": "Boulder debris blocking NH-10 KM 48. Two light vehicles stopped.",
                    "reporter_name": "BRO Quick Reaction Team",
                    "reporter_role": "HIGHWAY_PATROL",
                    "created_at": "2026-09-18T09:05:00Z"
                }
            ]
        }

        # 1. Sync batch of reports
        sync_res = self.client.post("/api/edge/field-reports/sync", json=reports_payload)
        self.assertEqual(sync_res.status_code, 200)
        sync_data = sync_res.get_json()
        self.assertEqual(sync_data["status"], "SUCCESS")
        self.assertEqual(sync_data["synced_count"], 2)
        self.assertEqual(sync_data["provenance"], "[EDGE_LORA_SYNC]")

        # 2. Re-syncing same reports should deduplicate without error
        sync_res_dup = self.client.post("/api/edge/field-reports/sync", json=reports_payload)
        self.assertEqual(sync_res_dup.status_code, 200)
        dup_data = sync_res_dup.get_json()
        self.assertEqual(dup_data["status"], "SUCCESS")
        self.assertEqual(dup_data["synced_count"], 2)

        # 3. Query stored field reports
        get_res = self.client.get("/api/edge/field-reports")
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.get_json()
        self.assertEqual(get_data["status"], "SUCCESS")
        self.assertEqual(get_data["provenance"], "[EDGE_LOCAL_STORE]")
        self.assertGreaterEqual(get_data["count"], 2)

        # Verify fields in queried reports
        report_ids = [r["report_id"] for r in get_data["reports"]]
        self.assertIn("RPT-TEST-001", report_ids)
        self.assertIn("RPT-TEST-002", report_ids)

        r1 = next(r for r in get_data["reports"] if r["report_id"] == "RPT-TEST-001")
        self.assertEqual(r1["severity"], "CRITICAL")
        self.assertEqual(r1["incident_type"], "SLOPE_CRACK")
        self.assertAlmostEqual(r1["crack_aperture_mm"], 48.5, places=1)
        self.assertEqual(r1["sync_status"], "SYNCED_EDGE")

    def test_field_reports_empty_sync(self):
        """Test syncing empty list gracefully returns 0 synced."""
        res = self.client.post("/api/edge/field-reports/sync", json={"reports": []})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["synced_count"], 0)

    def test_lora_packet_stream_and_burst(self):
        """Test GET /api/edge/mesh/packets and POST /api/edge/mesh/simulate-burst."""
        # 1. Initial packets
        init_res = self.client.get("/api/edge/mesh/packets?limit=10")
        self.assertEqual(init_res.status_code, 200)
        init_data = init_res.get_json()
        self.assertEqual(init_data["status"], "SUCCESS")
        self.assertIn("packets", init_data)
        self.assertIn("frequency_mhz", init_data)
        self.assertAlmostEqual(init_data["frequency_mhz"], 865.2, places=1)

        # 2. Simulate emergency LoRa RF packet burst
        burst_res = self.client.post("/api/edge/mesh/simulate-burst?count=3")
        self.assertEqual(burst_res.status_code, 200)
        burst_data = burst_res.get_json()
        self.assertEqual(burst_data["status"], "SUCCESS")
        self.assertEqual(len(burst_data["packets"]), 3)

        # 3. Packets should now contain newly generated bursts
        after_res = self.client.get("/api/edge/mesh/packets?limit=10")
        self.assertEqual(after_res.status_code, 200)
        after_data = after_res.get_json()
        self.assertGreaterEqual(len(after_data["packets"]), 3)

        # Verify frame structure
        packet = after_data["packets"][0]
        self.assertIn("node_id", packet)
        self.assertIn("payload_hex", packet)
        self.assertTrue(packet["payload_hex"].startswith("0x"))
        self.assertIn("rssi_dbm", packet)
        self.assertIn("snr_db", packet)
        self.assertIn("battery_pct", packet)
        self.assertIn("hops", packet)
        self.assertEqual(packet["provenance"], "[SIMULATED / MESH]")

    def test_backhaul_toggle_offline_mode(self):
        """Test POST /api/edge/toggle-cloud switches backhaul state."""
        # Toggle to severed
        res1 = self.client.post("/api/edge/toggle-cloud")
        self.assertEqual(res1.status_code, 200)
        d1 = res1.get_json()
        self.assertFalse(d1["is_cloud_connected"])
        self.assertEqual(d1["mode"], "EDGE_OFFLINE_AUTONOMOUS")

        # Toggle back to connected
        res2 = self.client.post("/api/edge/toggle-cloud")
        self.assertEqual(res2.status_code, 200)
        d2 = res2.get_json()
        self.assertTrue(d2["is_cloud_connected"])
        self.assertEqual(d2["mode"], "CLOUD_CONNECTED")

    def test_edge_store_direct_unit(self):
        """Unit test for EdgeStore field report methods."""
        store = EdgeStore(db_path=":memory:")
        report = {
            "report_id": "RPT-DIRECT-UNIT-1",
            "incident_type": "DEBRIS_SLOPE",
            "severity": "MODERATE",
            "latitude": 27.2000,
            "longitude": 88.5000,
            "crack_aperture_mm": 12.0,
            "casualties": 0,
            "notes": "Minor scree slide near bridge abutment",
            "reporter_name": "Civil Defense Volunteer"
        }
        res = store.insert_field_report(report, buffer_for_cloud=True)
        self.assertTrue(res)

        items = store.query_field_reports(limit=10)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["report_id"], "RPT-DIRECT-UNIT-1")
        self.assertEqual(items[0]["sync_status"], "SYNCED_EDGE")

    def test_lora_mesh_direct_unit(self):
        """Unit test for LoRaMesh packet buffer and burst generation."""
        mesh = LoRaMesh(frequency_mhz=865.2)
        # Verify initial buffer
        pkts = mesh.get_recent_packets(limit=5)
        self.assertIsInstance(pkts, list)

        # Simulate burst of 3 packets
        burst = mesh.simulate_burst(count=3)
        self.assertEqual(len(burst), 3)
        for b in burst:
            self.assertTrue(b["payload_hex"].startswith("0x"))
            self.assertIn("provenance", b)
            self.assertEqual(b["provenance"], "[SIMULATED / MESH]")

        # Verify recent buffer includes burst
        recent = mesh.get_recent_packets(limit=10)
        self.assertGreaterEqual(len(recent), 3)

    def test_pwa_and_service_worker_assets(self):
        """Verify service worker precaches /edge-network and triage script, and manifest has shortcuts."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Check sw.js
        sw_path = os.path.join(base_dir, "static", "sw.js")
        self.assertTrue(os.path.exists(sw_path), "static/sw.js missing")
        with open(sw_path, "r", encoding="utf-8") as f:
            sw_content = f.read()
        self.assertIn("'/edge-network'", sw_content)
        self.assertIn("'/static/js/offline_field_triage.js'", sw_content)

        # Check manifest.json
        manifest_path = os.path.join(base_dir, "static", "manifest.json")
        self.assertTrue(os.path.exists(manifest_path), "static/manifest.json missing")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        shortcut_urls = [s.get("url") for s in manifest.get("shortcuts", [])]
        self.assertIn("/edge-network", shortcut_urls)


if __name__ == "__main__":
    unittest.main()
