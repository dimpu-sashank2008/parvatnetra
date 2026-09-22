# -*- coding: utf-8 -*-
"""
tests/test_v5_1_model_status.py
===============================
Phase V5.1 Test Suite: Model Status & Operational Roles
Verifies distinct operational roles for Production V3, Research V4.5,
Event Classifier GBDT, FoS Predictor, and Kinematic ML.
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestV51ModelStatus:
    """Verifies operational roles and statuses across all model families."""

    def test_production_v3_status(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        v3 = inv["production_model"]
        assert v3["status"] == "PRODUCTION_SERVING_FROZEN"
        assert v3["verified"] is True
        assert v3["features"] == 33
        assert "48h" in v3["horizons"]

    def test_research_v4_5_status(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        v45 = inv["research_model_v4_5"]
        assert v45["status"] == "RESEARCH_BASELINE_OFFLINE"
        assert v45["verified"] is True
        assert v45["features"] == 31
        assert "168h" in v45["horizons"]

    def test_event_classifier_gbdt_status(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        gbdt = inv["event_classifier"]
        assert gbdt["status"] == "TRAINED_LIMITED_DATA"
        assert gbdt["dataset_rows"] == 36

    def test_fos_predictor_status(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        fos = inv["fos_predictor"]
        assert fos["status"] == "PHYSICS_SURROGATE_ACTIVE"

    def test_kinematic_ml_status_not_trained(self, truth_engine):
        inv = truth_engine.get_model_inventory()
        kin = inv["kinematic_ml"]
        assert kin["status"] == "NOT_TRAINED_DATA_PENDING"
        assert kin["weights"] is None
