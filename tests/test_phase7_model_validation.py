# -*- coding: utf-8 -*-
"""
tests/test_phase7_model_validation.py
=====================================
PARVAT NETRA • PAHAD AI — Phase 7 Model Scientific Validation Tests
-------------------------------------------------------------------
Tests baseline comparisons, threshold sensitivity, ablation findings, and honest small-sample disclosures.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from scripts.validate_phase7_models import run_scientific_model_audit

def test_model_scientific_audit_runs():
    """Verify scientific audit executes and returns expected schema."""
    res = run_scientific_model_audit()
    assert res["model_status"] == "TRAINED_LIMITED_DATA"
    assert res["dataset_summary"]["canonical_events"] == 17
    assert res["dataset_summary"]["baseline_observations"] == 36
    assert res["dataset_summary"]["temporal_windows"] == 105
    assert "small N=17" in res["sample_size_limitation"]

def test_five_baseline_strategies_evaluated():
    """Verify all 5 comparative decision strategies are present and valid."""
    res = run_scientific_model_audit()
    comparisons = res["baseline_comparisons"]
    assert len(comparisons) == 5

    names = [c["strategy_name"] for c in comparisons]
    assert any("Rainfall-Only" in n for n in names)
    assert any("Geotechnical FoS" in n for n in names)
    assert any("Compound Heuristic" in n for n in names)
    assert any("Calibrated ML" in n for n in names)
    assert any("2-of-3 Corroboration" in n for n in names)

    for c in comparisons:
        assert 0.0 <= c["pod_recall"] <= 1.0
        assert 0.0 <= c["far"] <= 1.0
        assert 0.0 <= c["csi_threat_score"] <= 1.0
        assert c["brier_score"] >= 0.0

def test_threshold_sensitivity_table():
    """Verify threshold sweep covers 0.50 to 0.90."""
    res = run_scientific_model_audit()
    sens = res["threshold_sensitivity"]
    assert len(sens) == 5
    ths = [s["threshold"] for s in sens]
    assert ths == [0.50, 0.60, 0.70, 0.80, 0.90]

def test_feature_ablation_shows_rain_and_fos_critical():
    """Verify ablation proves rainfall and FoS are top drivers."""
    res = run_scientific_model_audit()
    abl = res["ablation_analysis"]
    assert len(abl) >= 5
    rain_drop = [a["delta_auc"] for a in abl if "Rainfall" in a["removed_signal"]][0]
    fos_drop = [a["delta_auc"] for a in abl if "Factor of Safety" in a["removed_signal"]][0]
    assert rain_drop < -0.20
    assert fos_drop < -0.20

def test_calibrated_ml_and_gate_metrics():
    """Verify calibrated ML model achieves expected metrics on held-out test split."""
    res = run_scientific_model_audit()
    comparisons = {c["strategy_name"]: c for c in res["baseline_comparisons"]}
    
    ml_comp = next(v for k, v in comparisons.items() if "Calibrated ML" in k)
    assert ml_comp["pod_recall"] == 1.0
    assert ml_comp["far"] == 0.0
    assert ml_comp["csi_threat_score"] == 1.0
    assert ml_comp["brier_score"] == pytest.approx(0.0824, rel=1e-2)

    gate_comp = next(v for k, v in comparisons.items() if "2-of-3 Corroboration" in k)
    assert gate_comp["pod_recall"] == 1.0
    assert gate_comp["far"] == 0.0
    assert gate_comp["csi_threat_score"] == 1.0
    assert gate_comp["brier_score"] == 0.0

