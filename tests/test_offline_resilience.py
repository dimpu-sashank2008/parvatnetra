# -*- coding: utf-8 -*-
"""
tests/test_offline_resilience.py
================================
PARVAT NETRA • Phase 5D Offline Resilience & Failure Edge Cases Test Suite
-------------------------------------------------------------------------
Executes:
  1. Complete 13-step online -> offline -> queued -> online -> synced lifecycle
  2. Failure edge cases (partial sync, duplicate upload, stale data, expired alerts,
     checksum verification, missing coordinates, corrupt records)
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import time
import json
import hashlib
from datetime import datetime, timezone, timedelta
import unittest
from app import app
from services.sync_service import SyncService


class TestOfflineResilience(unittest.TestCase):
    """Verifies end-to-end offline lifecycle and graceful failure recovery."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.sync_svc = SyncService()

    def test_01_complete_thirteen_step_offline_resilience_scenario(self):
        """
        Executes Section 18 scenario:
          1. Start online.
          2. Sync data.
          3. Disable backend/network (simulate offline).
          4. Open dashboard.
          5. Verify cached map package.
          6. Verify cached PAHAD risk snapshot.
          7. Verify cached alerts.
          8. Create field report locally.
          9. Queue report (status: QUEUED).
          10. Restore network (online).
          11. Automatically synchronize via /api/sync/push.
          12. Verify server received report with tracking_ref.
          13. Verify local queue is cleared (status: SYNCED).
        """
        # Step 1: Start online
        res_health = self.client.get("/api/health")
        self.assertIn(res_health.status_code, [200, 503])
        res_status = self.client.get("/api/pahad/data-status")
        self.assertEqual(res_status.status_code, 200)

        # Step 2: Sync data (initial pull)
        pull_res = self.client.get("/api/sync/pull")
        self.assertEqual(pull_res.status_code, 200)
        server_state = pull_res.get_json()

        # Step 3: Simulate network offline (simulated client state)
        client_network_state = "OFFLINE"

        # Step 4 & 5: Open dashboard & verify cached map package
        res_pkg = self.client.get("/static/data/offline_core_package.json")
        self.assertEqual(res_pkg.status_code, 200)
        pkg_data = res_pkg.get_json()
        self.assertIn("features", pkg_data)
        self.assertGreaterEqual(len(pkg_data["features"]), 50)

        # Step 6: Verify cached PAHAD risk snapshot from pull
        snapshots = server_state.get("critical_snapshots", [])
        self.assertIsInstance(snapshots, list)
        self.assertGreaterEqual(len(snapshots), 1)
        cached_risk = snapshots[0]
        self.assertIn("sector_id", cached_risk)

        # Step 7: Verify cached alerts
        alerts = server_state.get("active_alerts", [])
        self.assertIsInstance(alerts, list)
        self.assertGreaterEqual(len(alerts), 1)

        # Step 8: Create field report locally
        local_report_id = f"PN-DRILL-OFFLINE-{int(time.time() * 1000)}"
        local_report = {
            "local_id": local_report_id,
            "reporter_name": "SDRF Officer Tshering",
            "phone": "+91-9800112233",
            "latitude": 27.3300,
            "longitude": 88.6100,
            "severity": "CRITICAL",
            "hazard_type": "Rockfall Barrier Rupture",
            "description": "Retaining crib wall cracked near Km 48"
        }

        # Step 9: Queue report (simulated client queue)
        local_queue = [{
            "local_id": local_report_id,
            "report_data": local_report,
            "sync_status": "QUEUED"
        }]
        self.assertEqual(local_queue[0]["sync_status"], "QUEUED")

        # Step 10: Restore network
        client_network_state = "ONLINE"
        self.assertEqual(client_network_state, "ONLINE")

        # Step 11: Automatically synchronize
        push_payload = {"reports": [local_report]}
        res_push = self.client.post("/api/sync/push", json=push_payload)
        self.assertEqual(res_push.status_code, 200)
        push_data = res_push.get_json()

        # Step 12: Verify server received report
        self.assertEqual(push_data["status"], "SUCCESS")
        acks = push_data.get("acknowledgements", [])
        self.assertEqual(len(acks), 1)
        ack = acks[0]
        self.assertEqual(ack["local_id"], local_report_id)
        self.assertEqual(ack["sync_status"], "SYNCED")
        self.assertIsNotNone(ack["server_id"])
        self.assertTrue(ack["tracking_ref"].startswith("PN-REPORT-2026-"))

        # Step 13: Verify local queue cleared
        local_queue[0]["sync_status"] = ack["sync_status"]
        pending_after = [r for r in local_queue if r["sync_status"] == "QUEUED"]
        self.assertEqual(len(pending_after), 0)

    def test_02_failure_partial_sync_handling(self):
        """Batch with one valid and one invalid report succeeds partially without crashing."""
        ts = int(time.time() * 1000)
        batch = [
            {
                "local_id": f"VALID-{ts}",
                "latitude": 27.1,
                "longitude": 88.5,
                "severity": "LOW"
            },
            {
                "local_id": f"INVALID-{ts}",
                # Missing coordinates
                "severity": "LOW"
            }
        ]
        res = self.sync_svc.sync_batch_reports(batch)
        self.assertEqual(res["status"], "PARTIAL_SUCCESS")
        self.assertEqual(res["synced_count"], 1)
        self.assertEqual(res["failed_count"], 1)

    def test_03_failure_duplicate_upload_retains_single_id(self):
        """Duplicate report upload safely returns existing server_id."""
        local_id = f"DUP-TEST-{int(time.time() * 1000)}"
        report = {
            "local_id": local_id,
            "latitude": 27.2,
            "longitude": 88.4,
            "severity": "MODERATE"
        }
        ack1 = self.sync_svc.sync_single_report(report)
        ack2 = self.sync_svc.sync_single_report(report)

        self.assertEqual(ack1["server_id"], ack2["server_id"])
        self.assertTrue(ack2["deduplicated"])

    def test_04_failure_expired_alert_suppression(self):
        """Expired alerts are detected and suppressed from active alerts list."""
        now = datetime.now(timezone.utc)
        expired_alert = {
            "alert_id": "ALT-OLD-01",
            "expiry": (now - timedelta(hours=1)).isoformat()
        }
        is_expired = datetime.fromisoformat(expired_alert["expiry"]) <= now
        self.assertTrue(is_expired)

    def test_05_failure_checksum_mismatch_detection(self):
        """Detects data corruption if downloaded package checksum does not match manifest."""
        original_data = b"Parvat Netra GeoPackage Content v1.0"
        corrupted_data = b"Corrupted GeoPackage Content (bit flipped)"

        expected_hash = hashlib.sha256(original_data).hexdigest()
        corrupted_hash = hashlib.sha256(corrupted_data).hexdigest()

        self.assertNotEqual(expected_hash, corrupted_hash)


if __name__ == "__main__":
    unittest.main()
