# -*- coding: utf-8 -*-
"""
tests/test_sync_api.py
======================
PARVAT NETRA • Phase 5D Synchronization REST API Test Suite
-----------------------------------------------------------
Validates:
  1. POST /api/sync/push (batch reports, telemetry deltas, deduplication, error handling)
  2. GET /api/sync/pull (active alerts, critical sector snapshots, road blockages, shelters)
  3. GET /api/sync/status (operational health, queue metrics, bundle version)
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import time
import json
import unittest
from app import app


class TestSyncAPI(unittest.TestCase):
    """Verifies all Phase 5D synchronization HTTP endpoints."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_sync_push_single_report(self):
        """POST /api/sync/push successfully accepts and acknowledges an offline field report."""
        local_id = f"PN-OFFLINE-PUSH-{int(time.time() * 1000)}"
        payload = {
            "reports": [
                {
                    "local_id": local_id,
                    "reporter_name": "Field Responder Anita",
                    "latitude": 27.33,
                    "longitude": 88.61,
                    "severity": "CRITICAL",
                    "hazard_type": "Debris Flow",
                    "description": "Active road blockage on NH-10 Km 48"
                }
            ]
        }
        res = self.client.post("/api/sync/push", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("sync_id", data)
        self.assertIn("started_at", data)
        self.assertIn("completed_at", data)
        self.assertEqual(data.get("records_uploaded"), 1)
        self.assertEqual(data.get("records_failed"), 0)
        self.assertIn("acknowledgements", data)
        self.assertEqual(len(data["acknowledgements"]), 1)
        self.assertEqual(data["acknowledgements"][0]["local_id"], local_id)
        self.assertEqual(data["acknowledgements"][0]["sync_status"], "SYNCED")

    def test_02_sync_push_idempotent_deduplication(self):
        """POST /api/sync/push returns existing server_id when duplicate local_id is submitted."""
        local_id = f"PN-OFFLINE-IDEMP-{int(time.time() * 1000)}"
        report = {
            "local_id": local_id,
            "reporter_name": "SDRF Scout",
            "latitude": 27.24,
            "longitude": 88.50,
            "severity": "HIGH",
            "hazard_type": "Tension Crack"
        }
        payload = {"reports": [report]}

        # Push 1
        res1 = self.client.post("/api/sync/push", json=payload)
        self.assertEqual(res1.status_code, 200)
        ack1 = res1.get_json()["acknowledgements"][0]
        server_id_1 = ack1["server_id"]

        # Push 2 (retransmission)
        res2 = self.client.post("/api/sync/push", json=payload)
        self.assertEqual(res2.status_code, 200)
        ack2 = res2.get_json()["acknowledgements"][0]

        self.assertEqual(ack2["server_id"], server_id_1)
        self.assertTrue(ack2.get("duplicate") or ack2.get("deduplicated"))

    def test_03_sync_push_rejects_non_json(self):
        """POST /api/sync/push returns HTTP 400 when payload is not application/json."""
        res = self.client.post("/api/sync/push", data="raw string", content_type="text/plain")
        self.assertEqual(res.status_code, 400)

    def test_04_sync_pull_returns_server_state(self):
        """GET /api/sync/pull returns alerts, snapshots, road corridors, and shelters."""
        res = self.client.get("/api/sync/pull")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("sync_id", data)
        self.assertIn("pulled_at", data)
        self.assertIn("active_alerts", data)
        self.assertIn("critical_snapshots", data)
        self.assertIn("road_corridors", data)
        self.assertIn("shelters", data)
        self.assertGreaterEqual(len(data["shelters"]), 1)
        self.assertGreaterEqual(len(data["road_corridors"]), 1)

    def test_05_sync_status_endpoint(self):
        """GET /api/sync/status returns operational metrics and bundle version."""
        res = self.client.get("/api/sync/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertIn("total_synced_reports", data)
        self.assertIn("last_sync_timestamp", data)
        self.assertIn("connected_sources", data)
        self.assertIn("offline_bundle_version", data)
        self.assertIn("active_queues", data)


if __name__ == "__main__":
    unittest.main()
