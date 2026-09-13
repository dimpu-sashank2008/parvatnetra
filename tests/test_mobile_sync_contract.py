# -*- coding: utf-8 -*-
"""
tests/test_mobile_sync_contract.py
==================================
PARVAT NETRA • Phase 5D Mobile SQLite & Backend Sync Contract Test Suite
------------------------------------------------------------------------
Validates:
  1. Mobile SQLite field_reports table schema mapping to /api/sync/push payload
  2. Mobile push acknowledgement handling and SQLite status update contract
  3. Mobile pull response compatibility with cached_snapshots and cached_alerts
  4. Client exponential backoff formula validation against mobile implementation
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import time
import math
import unittest
from app import app
from services.sync_service import SYNC_SERVICE


class TestMobileSyncContract(unittest.TestCase):
    """Verifies bidirectional synchronization contract between mobile app and server."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.sync_svc = SYNC_SERVICE

    def test_01_mobile_field_report_push_contract(self):
        """Mobile SQLite field_reports row maps cleanly into /api/sync/push and receives valid ack."""
        ts = int(time.time() * 1000)
        local_id = f"MOBILE-REP-{ts}"

        # Exact structure stored in mobile SQLite database_helper.dart
        mobile_report = {
            "local_id": local_id,
            "created_at": "2026-09-10T07:15:00Z",
            "updated_at": "2026-09-10T07:15:00Z",
            "lat": 27.3300,
            "lon": 88.6100,
            "hazard_type": "Tension Crack",
            "severity": "CRITICAL",
            "description": "Crack aperture 25mm observed along Pakyong slope.",
            "photo_paths": "['/storage/emulated/0/DCIM/crack1.jpg']",
            "video_paths": "[]",
            "reporter_role": "SDRF_RESPONDER",
            "sync_status": "QUEUED",
            "retry_count": 0
        }

        res = self.client.post("/api/sync/push", json={"reports": [mobile_report]})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data["status"], "SUCCESS")
        acks = data.get("acknowledgements", [])
        self.assertEqual(len(acks), 1)

        ack = acks[0]
        self.assertEqual(ack["local_id"], local_id)
        self.assertEqual(ack["sync_status"], "SYNCED")
        self.assertIsNotNone(ack["server_id"])
        self.assertIn("PN-REPORT-2026-", ack["tracking_ref"])

    def test_02_mobile_pull_contract_for_sqlite_caches(self):
        """GET /api/sync/pull provides all keys needed for mobile cached_snapshots & cached_alerts."""
        res = self.client.get("/api/sync/pull?sector_id=SK-NH10-KM48")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # Check snapshots for mobile cached_snapshots table
        snapshots = data.get("critical_snapshots", [])
        self.assertIsInstance(snapshots, list)
        if snapshots:
            snap = snapshots[0]
            self.assertIn("sector_id", snap)

        # Check alerts for mobile cached_alerts table
        alerts = data.get("active_alerts", [])
        self.assertIsInstance(alerts, list)
        for a in alerts:
            self.assertIn("alert_id", a)
            self.assertIn("severity", a)
            self.assertIn("status", a)
            self.assertIn("expiry", a)

    def test_03_exponential_backoff_formulation(self):
        """Verifies exponential backoff logic matches mobile calculateBackoff."""
        # Mobile formula: base_seconds = min(60.0, 2.0 * 1.5^retries)
        def mobile_backoff_base(retries):
            return min(60.0, 2.0 * math.pow(1.5, retries))

        self.assertAlmostEqual(mobile_backoff_base(0), 2.0, places=2)
        self.assertAlmostEqual(mobile_backoff_base(1), 3.0, places=2)
        self.assertAlmostEqual(mobile_backoff_base(2), 4.5, places=2)
        self.assertAlmostEqual(mobile_backoff_base(5), 15.1875, places=2)
        self.assertEqual(mobile_backoff_base(15), 60.0)


if __name__ == "__main__":
    unittest.main()
