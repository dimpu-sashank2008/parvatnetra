# -*- coding: utf-8 -*-
"""
tests/test_dataset_status.py
============================
Tests the Phase 4 status and metrics endpoints:
  - GET /api/pahad/dataset-status
  - GET /api/pahad/model-status
  - GET /api/pahad/model-metrics
"""

import os
os.environ["PARVAT_TESTING"] = "1"
os.environ["PAHAD_DEMO_MODE"] = "1"
import json
import unittest
from app import app


class TestDatasetStatus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_dataset_status_endpoint(self):
        """Verify GET /api/pahad/dataset-status returns accurate historical and control counts."""
        res = self.client.get("/api/pahad/dataset-status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("total_records"), 36)
        self.assertEqual(data.get("real_events_count"), 17)
        self.assertEqual(data.get("negative_controls_count"), 19)

        splits = data.get("splits", {})
        self.assertEqual(splits.get("train"), 16)
        self.assertEqual(splits.get("val"), 12)
        self.assertEqual(splits.get("test"), 8)

        self.assertEqual(data.get("leakage_audit_status"), "PASSED")
        self.assertIn("hashes", data)

    def test_model_status_endpoint(self):
        """Verify GET /api/pahad/model-status returns versioning and research status."""
        res = self.client.get("/api/pahad/model-status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("model_status"), "TRAINED_LIMITED_DATA")
        self.assertIn("DATA-GROUNDED RESEARCH PROTOTYPE", data.get("research_stage", ""))
        self.assertEqual(data.get("training_rows"), 16)
        self.assertEqual(data.get("validation_rows"), 12)
        self.assertEqual(data.get("test_rows"), 8)
        self.assertIn("dataset_hash", data)
        self.assertGreater(len(data.get("dataset_hash")), 10)

    def test_model_metrics_endpoint(self):
        """Verify GET /api/pahad/model-metrics returns statistical and operational metrics."""
        res = self.client.get("/api/pahad/model-metrics")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        stat = data.get("statistical_metrics", {})
        self.assertIn("roc_auc", stat)
        self.assertIn("brier_score", stat)
        self.assertIn("calibration_error", stat)

        ops = data.get("operational_metrics", {})
        self.assertIn("pod", ops)
        self.assertIn("far", ops)
        self.assertIn("csi", ops)

        self.assertIn("sample_size_caveat", data)


if __name__ == "__main__":
    unittest.main()
