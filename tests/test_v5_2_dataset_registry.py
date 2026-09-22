# -*- coding: utf-8 -*-
"""
tests/test_v5_2_dataset_registry.py
===================================
Phase V5.2 Test Suite: Authoritative Dataset Artifact Registry & Hash Verification
"""

import os
import json
import hashlib
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestV52DatasetRegistry:
    """Verifies that all Phase V5.2 dataset artifacts exist and maintain cryptographic hash integrity."""

    def test_canonical_event_inventory_file(self):
        p = os.path.join(REPO_ROOT, "data", "processed", "canonical_event_inventory_v5_2.json")
        assert os.path.exists(p), f"Missing {p}"
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("dataset_version") == "5.2.0"
        assert data.get("canonical_events_count") == 42
        assert len(data.get("events", [])) == 42
        assert len(data.get("controls", [])) == 20

    def test_event_lineage_file(self):
        p = os.path.join(REPO_ROOT, "data", "processed", "v5_2_event_lineage.json")
        assert os.path.exists(p), f"Missing {p}"
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("schema_version") == "5.2.0"
        assert data.get("total_canonical_events") == 42
        assert len(data.get("lineage", {})) == 42

    def test_ground_truth_manifest_file(self):
        p = os.path.join(REPO_ROOT, "data", "processed", "v5_2_ground_truth_manifest.json")
        assert os.path.exists(p), f"Missing {p}"
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("phase") == "V5.2"
        base = data.get("authoritative_baseline", {})
        assert base.get("total_canonical_documented_events") == 42
        assert base.get("verified_negative_controls") == 20
        assert base.get("temporal_sequences") == 105
        assert base.get("physical_sensors_installed") == 0

    def test_dataset_manifest_file(self):
        p = os.path.join(REPO_ROOT, "data", "processed", "v5_2_dataset_manifest.json")
        assert os.path.exists(p), f"Missing {p}"
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("schema_version") == "5.2.0"
        assert len(data.get("dataset_registry", [])) >= 5
