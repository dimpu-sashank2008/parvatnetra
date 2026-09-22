# -*- coding: utf-8 -*-
"""
tests/test_v5_1_api_model_identity.py
======================================
Tests the Phase V5.1 REST API endpoints for model identity,
dataset registries, and audit summary verification.
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app
from engine.scientific_truth_engine import EXPECTED_V3_SHA256, EXPECTED_V4_5_SHA256


class TestV51ApiModelIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_get_scientific_truth_ledger_endpoint(self):
        res = self.client.get("/api/scientific-truth/ledger")
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertEqual(payload.get("status"), "SUCCESS")
        ledger = payload.get("data", {})

        # Verify audit metadata
        self.assertEqual(ledger.get("phase"), "V5.1")
        self.assertEqual(ledger.get("overall_verdict"), "V5_1_TRUTH_LEDGER_VERIFIED")

        # Verify production model identity & hash
        prod = ledger.get("production_model", {})
        self.assertEqual(prod.get("sha256"), EXPECTED_V3_SHA256)
        self.assertEqual(prod.get("input_sequence_length_hours"), 72)
        self.assertEqual(prod.get("feature_count"), 33)

        # Verify research models
        research_models = ledger.get("research_models", [])
        v45 = next((m for m in research_models if m.get("model_id") == "Model_D_1Layer_BiLSTM_Att_V4_5"), None)
        self.assertIsNotNone(v45)
        self.assertEqual(v45.get("sha256"), EXPECTED_V4_5_SHA256)
        self.assertEqual(v45.get("input_sequence_length_hours"), 168)
        self.assertEqual(v45.get("feature_count"), 31)

        # Verify kinematic ML model status
        kinematic = next((m for m in research_models if m.get("model_id") == "PAHAD-Kinematic-IoT-ML-Model"), None)
        self.assertIsNotNone(kinematic)
        self.assertEqual(kinematic.get("status"), "NOT_TRAINED_DATA_PENDING")

        # Verify dataset counts from data_truth
        data_truth = ledger.get("data_truth", {})
        self.assertEqual(data_truth.get("canonical_documented_events"), 17)
        self.assertEqual(data_truth.get("canonical_documented_controls"), 20)
        self.assertEqual(data_truth.get("canonical_temporal_sequences"), 105)

        # Verify dataset registry list entries
        datasets = ledger.get("dataset_registry", [])
        raw_events = next((d for d in datasets if d.get("dataset_id") == "DS-RAW-NER-17"), None)
        self.assertIsNotNone(raw_events)
        self.assertEqual(raw_events.get("rows"), 17)

    def test_get_scientific_truth_audit_summary_endpoint(self):
        res = self.client.get("/api/scientific-truth/audit-summary")
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertEqual(payload.get("status"), "SUCCESS")
        summary = payload.get("data", {})

        # Verify verdict and model immutability
        verdict = summary.get("verdict", {})
        self.assertEqual(verdict.get("overall_verdict"), "V5_1_TRUTH_LEDGER_VERIFIED")
        self.assertTrue(verdict.get("models_immutable"))

        immutability = summary.get("model_immutability", {})
        self.assertTrue(immutability.get("all_models_invariant"))

        # Verify canonical counts
        counts = summary.get("canonical_data_counts", {})
        self.assertEqual(counts.get("canonical_events"), 17)
        self.assertEqual(counts.get("canonical_controls"), 20)
        self.assertEqual(counts.get("canonical_sequences"), 105)

        # Verify conflict resolution status
        conflicts = summary.get("conflict_resolutions", [])
        self.assertGreaterEqual(len(conflicts), 9)
        for conflict in conflicts:
            self.assertEqual(conflict.get("status"), "RESOLVED")
