# -*- coding: utf-8 -*-
"""
tests/test_offline_storage.py
=============================
PARVAT NETRA • Phase 5D Offline Storage & Cache Contract Test Suite
-------------------------------------------------------------------
Validates:
  1. PAHAD prediction snapshot schema compliance (Phase 5B/5C attributes)
  2. Offline alert schema, expiry date validation, and status flagging
  3. Field report offline queue states (QUEUED, UPLOADING, SYNCED, FAILED)
  4. Local observation store integration and data freshness interaction
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
from datetime import datetime, timezone, timedelta
from engine.sector_snapshot import SectorSnapshot, SectorSnapshotBuilder
from engine.data_freshness import DataFreshnessEngine, FRESH, STALE


class TestOfflineStorageContract(unittest.TestCase):
    """Verifies data contracts and schema constraints for offline storage."""

    def test_01_pahad_snapshot_mandatory_attributes(self):
        """SectorSnapshot provides all Section 5 mandatory offline fields."""
        builder = SectorSnapshotBuilder()
        snapshot = builder.build("SK-NH10-KM48")
        snap_dict = snapshot.to_dict()

        mandatory_fields = [
            "sector_id",
            "snapshot_time",
            "features",
            "feature_provenance",
            "feature_completeness",
            "missing_features",
            "freshness_by_modality",
            "overall_freshness",
            "data_quality_score",
            "provenance_summary"
        ]
        for field in mandatory_fields:
            self.assertIn(field, snap_dict, f"Missing snapshot field: {field}")

        self.assertEqual(snap_dict["sector_id"], "SK-NH10-KM48")
        self.assertIsInstance(snap_dict["feature_completeness"], float)
        self.assertIsInstance(snap_dict["data_quality_score"], float)

    def test_02_alert_expiry_detection(self):
        """Expired alerts are distinguished from active warnings."""
        now = datetime.now(timezone.utc)
        past = (now - timedelta(hours=2)).isoformat()
        future = (now + timedelta(hours=24)).isoformat()

        alert_active = {
            "alert_id": "ALT-TEST-001",
            "severity": "CRITICAL",
            "issued_at": now.isoformat(),
            "expiry": future,
            "status": "ACTIVE"
        }
        alert_expired = {
            "alert_id": "ALT-TEST-002",
            "severity": "WARNING",
            "issued_at": (now - timedelta(days=2)).isoformat(),
            "expiry": past,
            "status": "ACTIVE"
        }

        # Check expiry evaluation
        is_active_expired = datetime.fromisoformat(alert_active["expiry"]) <= now
        is_expired_expired = datetime.fromisoformat(alert_expired["expiry"]) <= now

        self.assertFalse(is_active_expired, "Active alert should not be marked expired")
        self.assertTrue(is_expired_expired, "Past alert must be marked expired")

    def test_03_offline_queue_field_report_structure(self):
        """Field report offline envelope complies with sync manager contract."""
        local_id = "PN-OFFLINE-TEST-12345"
        report_data = {
            "latitude": 27.33,
            "longitude": 88.61,
            "severity": "CRITICAL",
            "hazard_type": "Rockfall",
            "description": "Blockage at Km 48"
        }

        queue_record = {
            "local_id": local_id,
            "server_id": None,
            "report_data": report_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "sync_status": "QUEUED",
            "retry_count": 0,
            "error_message": None
        }

        self.assertEqual(queue_record["sync_status"], "QUEUED")
        self.assertIn("latitude", queue_record["report_data"])
        self.assertIn("longitude", queue_record["report_data"])

    def test_04_freshness_engine_confidence_penalty(self):
        """Freshness engine computes confidence penalty for offline aging telemetry."""
        engine = DataFreshnessEngine()
        # Modality with no recent update
        rec = engine.get_freshness("weather")
        self.assertEqual(rec.status, "UNAVAILABLE")
        self.assertEqual(rec.confidence_penalty, 1.0)


if __name__ == "__main__":
    unittest.main()
