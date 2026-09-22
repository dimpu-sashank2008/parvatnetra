# -*- coding: utf-8 -*-
"""
tests/test_v5_1_warning_lead.py
===============================
Phase V5.1 Test Suite: Authoritative Warning Lead Times & Horizon Mappings
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestWarningLeadRegistry:
    """Verifies authoritative warning lead times per model family."""

    def test_synoptic_v3_lead_time(self, truth_engine):
        leads = truth_engine.get_warning_lead_registry()
        v3 = next((l for l in leads if "Production BiLSTM V3" in l["model_family"]), None)
        assert v3 is not None
        assert "24.0 to 48.0 hours" in v3["operational_lead_time"]

    def test_event_classifier_gbdt_lead_time(self, truth_engine):
        leads = truth_engine.get_warning_lead_registry()
        gbdt = next((l for l in leads if "Event Classifier" in l["model_family"]), None)
        assert gbdt is not None
        assert "24.0 hours" in gbdt["operational_lead_time"]

    def test_historical_ensemble_defense_sheet_median(self, truth_engine):
        leads = truth_engine.get_warning_lead_registry()
        ens = next((l for l in leads if "Defense Sheet" in l["model_family"]), None)
        assert ens is not None
        assert "14.5 hours" in ens["operational_lead_time"]
        assert "4.2 hours" in ens["operational_lead_time"]  # Minimum lead time

    def test_kinematic_ml_lead_time_is_zero(self, truth_engine):
        leads = truth_engine.get_warning_lead_registry()
        kin = next((l for l in leads if "Kinematic" in l["model_family"]), None)
        assert kin is not None
        assert "0.0 hours" in kin["operational_lead_time"]
        assert "NOT_TRAINED" in kin["operational_lead_time"]
