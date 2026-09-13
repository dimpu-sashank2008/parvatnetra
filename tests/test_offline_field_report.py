# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Offline Field Report API & Synchronization Test Suite
Phase 3.2: Offline-First Web, Map Resilience & Data Synchronization
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import json
import time
import unittest
from app import app
from services.sync_service import SYNC_SERVICE


class TestOfflineFieldReport(unittest.TestCase):
    """Validates the offline field report submission endpoints and deduplication API contracts."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_sync_field_reports_single(self):
        """Verify POST /api/sync/field-reports synchronizes a single report payload."""
        local_id = f"PN-OFFLINE-API-{int(time.time() * 1000)}"
        payload = {
            "local_id": local_id,
            "reporter_name": "Field Officer Dorjee",
            "phone": "+91-9876543210",
            "latitude": 27.241,
            "longitude": 88.514,
            "severity": "CRITICAL",
            "hazard_type": "Tension Crack",
            "description": "5cm active tension crack on road verge."
        }

        res = self.client.post(
            "/api/sync/field-reports",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertGreaterEqual(data.get("synced_count", 0), 1)

        acks = data.get("acknowledgements", [])
        self.assertEqual(len(acks), 1)
        self.assertEqual(acks[0]["local_id"], local_id)
        self.assertIsNotNone(acks[0]["server_id"])
        self.assertTrue(acks[0]["tracking_ref"].startswith("PN-REPORT-2026-"))

    def test_02_sync_field_reports_batch(self):
        """Verify POST /api/sync/field-reports handles multi-report batch transmissions."""
        ts = int(time.time() * 1000)
        batch_payload = {
            "reports": [
                {
                    "local_id": f"PN-OFFLINE-B1-{ts}",
                    "reporter_name": "Villager Lobsang",
                    "phone": "+91-9100000001",
                    "latitude": 27.310,
                    "longitude": 88.620,
                    "severity": "SEVERE",
                    "hazard_type": "Mudflow",
                    "description": "Mud accumulation blocking drainage canal."
                },
                {
                    "local_id": f"PN-OFFLINE-B2-{ts}",
                    "reporter_name": "Tourist Alert",
                    "phone": "+91-9100000002",
                    "latitude": 27.195,
                    "longitude": 88.545,
                    "severity": "MODERATE",
                    "hazard_type": "Rockfall",
                    "description": "Fist-sized debris on highway lane."
                }
            ]
        }

        res = self.client.post(
            "/api/sync/field-reports",
            data=json.dumps(batch_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("synced_count"), 2)
        self.assertEqual(len(data.get("acknowledgements")), 2)

    def test_03_submit_report_with_local_id_deduplication(self):
        """Verify POST /api/reports/submit respects local_id and prevents duplicate DB rows."""
        local_id = f"PN-OFFLINE-SUBMIT-{int(time.time() * 1000)}"
        form_data = {
            "local_id": local_id,
            "reporter_name": "BRO Recon Unit",
            "phone": "+91-9400000000",
            "latitude": "27.250",
            "longitude": "88.520",
            "severity": "CRITICAL",
            "category": "Landslide / भूस्खलन",
            "description": "Massive rotational slide toe toe failure."
        }

        # First submit
        res1 = self.client.post("/api/reports/submit", data=form_data)
        self.assertIn(res1.status_code, [200, 201])
        data1 = res1.get_json()
        report_id1 = data1.get("report_id")
        self.assertIsNotNone(report_id1)

        # Second submit with exact same local_id (duplicate transmission retry)
        res2 = self.client.post("/api/reports/submit", data=form_data)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        report_id2 = data2.get("report_id")
        self.assertEqual(report_id1, report_id2, "Duplicate submission must return original server report_id")
        self.assertTrue(data2.get("deduplicated", True))

    def test_04_sync_endpoint_rejects_non_json(self):
        """Verify POST /api/sync/field-reports returns 400 when body is not valid JSON."""
        res = self.client.post(
            "/api/sync/field-reports",
            data="plain text body",
            content_type="text/plain"
        )
        self.assertEqual(res.status_code, 400)


if __name__ == '__main__':
    unittest.main(verbosity=2)
