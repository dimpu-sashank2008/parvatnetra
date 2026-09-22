# -*- coding: utf-8 -*-
"""
tests/test_v5_1_metric_reproducibility.py
=========================================
Phase V5.1 Test Suite: Metric Lineage & Reproducibility
Verifies reproducible model metrics and formal demotion of untraced metric claims.
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestV51MetricReproducibility:
    """Verifies that model performance metrics are grounded in reproducible artifacts."""

    def test_gbdt_event_classifier_metrics(self, truth_engine):
        metrics = truth_engine.audit_metric_lineage()
        reproducible = metrics.get("authoritative_reproducible_metrics", [])
        gbdt = next((m for m in reproducible if "Event-Classifier" in m.get("model", "")), None)
        assert gbdt is not None
        assert gbdt.get("roc_auc") == 1.0
        assert gbdt.get("pr_auc") == 1.0
        assert gbdt.get("csi") == 1.0
        assert gbdt.get("pod") == 1.0
        assert gbdt.get("far") == 0.0
        assert gbdt.get("brier_score") == 0.0824
        assert gbdt.get("status") == "REPRODUCIBLE"
        assert "TRAINED_LIMITED_DATA" in gbdt.get("qualification", "")

    def test_v4_5_bilstm_metrics_reproducible(self, truth_engine):
        metrics = truth_engine.audit_metric_lineage()
        reproducible = metrics.get("authoritative_reproducible_metrics", [])
        v45 = next((m for m in reproducible if "V4_5" in m.get("model", "")), None)
        assert v45 is not None
        horizons = v45.get("horizons", {})
        assert "48h" in horizons
        assert horizons["48h"]["csi"] == pytest.approx(0.9524, rel=1e-3)
        assert horizons["48h"]["pod"] == 1.0
        assert horizons["48h"]["far"] == pytest.approx(0.0476, rel=1e-3)
        assert v45.get("status") == "REPRODUCIBLE"

    def test_untraced_metrics_demoted_to_unsupported(self, truth_engine):
        metrics = truth_engine.audit_metric_lineage()
        unsupported = metrics.get("unsupported_metric_claims", [])
        assert len(unsupported) > 0
        untraced = unsupported[0]
        assert "ROC-AUC: 0.81" in untraced.get("claim_text", "")
        assert "PR-AUC: 0.74" in untraced.get("claim_text", "")
        assert "POD: 0.78" in untraced.get("claim_text", "")
        assert "FAR: 0.22" in untraced.get("claim_text", "")
        assert "CSI: 0.64" in untraced.get("claim_text", "")
        assert untraced.get("forensic_status") == "UNSUPPORTED"
