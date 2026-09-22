# -*- coding: utf-8 -*-
"""
tests/test_v5_1_model_registry.py
=================================
Phase V5.1 Test Suite: Authoritative Model Registry & Lifecycle Governance
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestModelRegistry:
    """Verifies that model roles, architectures, and boundaries are properly categorized."""

    def test_production_v3_identity(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        v3 = inv["production_model"]
        assert v3["id"] == "PAHAD-BiLSTM-v3-MultiModal-33Features"
        assert v3["status"] == "PRODUCTION_SERVING_FROZEN"
        assert v3["features"] == 33
        assert v3["verified"] is True

    def test_research_v4_5_identity(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        v45 = inv["research_model_v4_5"]
        assert "V4_5" in v45["id"]
        assert v45["status"] == "RESEARCH_BASELINE_OFFLINE"
        assert v45["features"] == 31
        assert v45["verified"] is True

    def test_event_classifier_identity(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        ev = inv["event_classifier"]
        assert ev["status"] == "TRAINED_LIMITED_DATA"
        assert ev["dataset_rows"] == 36

    def test_kinematic_model_status_is_not_trained(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        kin = inv["kinematic_ml"]
        assert kin["status"] == "NOT_TRAINED_DATA_PENDING"
        assert kin["weights"] is None
