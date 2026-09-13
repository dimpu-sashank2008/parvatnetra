# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Sync Engine & Conflict Resolution Test Suite
Phase 3.2: Offline-First Web, Map Resilience & Data Synchronization
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import time
from services.sync_service import SyncService


class TestSyncManager(unittest.TestCase):
    """Validates the backend SyncService synchronization protocol, deduplication, and retry logic."""

    def setUp(self):
        self.sync_svc = SyncService()

    def test_01_idempotent_report_deduplication(self):
        """Verify that submitting the same local_id twice returns the cached server_id without duplication."""
        local_id = f"PN-OFFLINE-TEST-{int(time.time() * 1000)}"
        report_payload = {
            "local_id": local_id,
            "reporter_name": "Field Volunteer Tashi",
            "phone": "+91-9876543210",
            "latitude": 27.245,
            "longitude": 88.512,
            "severity": "CRITICAL",
            "hazard_type": "Tension Crack",
            "description": "Widening fissure on NH-10 Km 48 uphill slope."
        }

        # First synchronization attempt
        ack1 = self.sync_svc.sync_single_report(report_payload)
        self.assertEqual(ack1.get("status"), "SUCCESS")
        self.assertIn("server_id", ack1)
        self.assertIn("tracking_ref", ack1)
        self.assertEqual(ack1.get("local_id"), local_id)
        server_id_first = ack1["server_id"]
        tracking_ref_first = ack1["tracking_ref"]

        # Second attempt with same local_id (simulating network retry/duplicate transmission)
        ack2 = self.sync_svc.sync_single_report(report_payload)
        self.assertEqual(ack2.get("status"), "SUCCESS")
        self.assertEqual(ack2.get("server_id"), server_id_first)
        self.assertEqual(ack2.get("tracking_ref"), tracking_ref_first)
        self.assertTrue(ack2.get("deduplicated"))

    def test_02_batch_synchronization(self):
        """Verify batch synchronization processes multiple pending offline reports."""
        ts = int(time.time() * 1000)
        batch = [
            {
                "local_id": f"PN-OFFLINE-BATCH-1-{ts}",
                "reporter_name": "SDRF Scout 1",
                "phone": "+91-9800000001",
                "latitude": 27.301,
                "longitude": 88.611,
                "severity": "SEVERE",
                "hazard_type": "Rockfall",
                "description": "Active debris roll near Singtam."
            },
            {
                "local_id": f"PN-OFFLINE-BATCH-2-{ts}",
                "reporter_name": "BRO Highway Patrol",
                "phone": "+91-9800000002",
                "latitude": 27.180,
                "longitude": 88.530,
                "severity": "MODERATE",
                "hazard_type": "Subsidence",
                "description": "Pavement shoulder depression 15cm."
            }
        ]

        result = self.sync_svc.sync_batch(batch)
        self.assertEqual(result.get("status"), "SUCCESS")
        self.assertEqual(result.get("total"), 2)
        self.assertEqual(result.get("synced"), 2)
        self.assertEqual(result.get("errors_count"), 0)
        self.assertEqual(len(result.get("acknowledgements", [])), 2)

    def test_03_server_tracking_ref_formatting(self):
        """Verify tracking references adhere to standard institutional format PN-REPORT-2026-XXXX."""
        local_id = f"PN-OFFLINE-FMT-{int(time.time() * 1000)}"
        report = {
            "local_id": local_id,
            "reporter_name": "Test Reporter",
            "phone": "+91-0000000000",
            "latitude": 27.1,
            "longitude": 88.5,
            "severity": "LOW",
            "description": "Minor seepage on culvert"
        }
        ack = self.sync_svc.sync_single_report(report)
        tracking_ref = ack.get("tracking_ref")
        self.assertIsNotNone(tracking_ref)
        self.assertTrue(tracking_ref.startswith("PN-REPORT-2026-"))

    def test_04_missing_coordinates_handling(self):
        """Verify that invalid/missing coordinates return an error without crashing the engine."""
        invalid_report = {
            "local_id": f"PN-OFFLINE-INV-{int(time.time() * 1000)}",
            "reporter_name": "Missing GPS Reporter",
            "description": "Forgot to turn on GPS"
        }
        ack = self.sync_svc.sync_single_report(invalid_report)
        self.assertEqual(ack.get("status"), "ERROR")
        self.assertIn("error", ack)


if __name__ == '__main__':
    unittest.main(verbosity=2)
