# -*- coding: utf-8 -*-
"""
tests/test_v5_1_metric_lineage.py
=================================
Phase V5.1 Test Suite: Metric Lineage Tracing & Demotion of Untraced Claims
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestMetricLineage:
    """Verifies that every reported metric is traceable to reproducible model artifacts."""

    def test_reproducible_event_classifier_metrics(self, truth_engine):
        metrics = truth_engine.audit_metric_lineage()
        rep = metrics.get("authoritative_reproducible_metrics", [])
        gbdt = next((m for m in rep if "Event-Classifier" in m["model"]), None)
        assert gbdt is not None
        assert gbdt["roc_auc"] == 1.000
        assert gbdt["brier_score"] == 0.0824
        assert gbdt["median_warning_lead_hours"] == 24.0
        assert gbdt["status"] == "REPRODUCIBLE"

    def test_reproducible_v4_5_bilstm_metrics(self, truth_engine):
        metrics = truth_engine.audit_metric_lineage()
        rep = metrics.get("authoritative_reproducible_metrics", [])
        v45 = next((m for m in rep if "V4_5" in m["model"]), None)
        assert v45 is not None
        horizons = v45["horizons"]
        assert horizons["48h"]["csi"] == pytest.approx(0.9524, rel=1e-3)
        assert horizons["48h"]["pod"] == 1.000
        assert horizons["48h"]["far"] == pytest.approx(0.0476, rel=1e-3)
        assert horizons["24h"]["csi"] == pytest.approx(0.5000, rel=1e-3)

    def test_untraced_metric_claims_demoted_to_unsupported(self, truth_engine):
        metrics = truth_engine.audit_metric_lineage()
        unsupported = metrics.get("unsupported_metric_claims", [])
        assert len(unsupported) > 0
        untraced = unsupported[0]
        assert "0.81" in untraced["claim_text"]
        assert "0.74" in untraced["claim_text"]
        assert "0.78" in untraced["claim_text"]
        assert "0.22" in untraced["claim_text"]
        assert "0.64" in untraced["claim_text"]
        assert untraced["forensic_status"] == "UNSUPPORTED"
