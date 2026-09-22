# -*- coding: utf-8 -*-
"""
tests/test_v5_2_ground_truth.py
===============================
Phase V5.2 Test Suite: Ground Truth Independence & Scientific Baseline Validation
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager, CONTROL_VERIFIED_STABLE
from app import app


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


@pytest.fixture
def client():
    return app.test_client()


class TestV52GroundTruth:
    """Verifies that ground truth exists independently of ML predictions and satisfies the scientific baseline."""

    def test_canonical_counts(self, manager):
        events = manager.list_canonical_events()
        assert len(events) == 42
        controls = manager.list_canonical_controls()
        assert len(controls) == 20
        for c in controls:
            assert c["stability_status"] == CONTROL_VERIFIED_STABLE
            assert c["provenance"] == "[HISTORICAL]"

    def test_no_synthetic_in_canonical_events(self, manager):
        events = manager.list_canonical_events()
        for ev in events:
            assert "DEMO" not in ev.get("source", "").upper()
            assert "SYNTHETIC" not in ev.get("source", "").upper()
            assert ev["provenance"] == "[HISTORICAL]"

    def test_ground_truth_api_endpoint(self, client):
        res = client.get("/api/data/ground-truth/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["canonical_events_v5_1"] == 17
        assert data["authoritative_expansion_v5_2"] == 25
        assert data["total_canonical_events"] == 42
        assert data["verified_controls"] == 20
        assert data["temporal_sequences"] == 105
        assert data["physical_sensors_installed"] == 0
        assert data["live_mountain_telemetry_observations"] == 0
        assert data["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"
        assert data["production_model_v3"]["status"] == "ACTIVE_PRODUCTION_FROZEN"
        assert data["production_model_v3"]["sha256"] == "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"
