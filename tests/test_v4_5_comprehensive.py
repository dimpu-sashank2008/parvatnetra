# -*- coding: utf-8 -*-
"""
tests/test_v4_5_comprehensive.py
================================
Comprehensive pytest test suite for PAHAD AI Phase V4.5 Long-Range Multi-Horizon Temporal Modeling.
Verifies:
  1. Production V3 weights hash is strictly locked and untouched.
  2. Capacity-matched architecture parameter counts (<150k params).
  3. Multi-horizon forward pass shapes across 24h, 48h, 72h, 120h, and 168h input windows.
  4. Zero target leakage (composite_risk_index_cri excluded).
  5. Existence and valid schemas for all 9 required documentation reports in docs/ and root docs/.
  6. Existence and valid JSON schemas for manifests and results.
  7. Calibration bounds (Brier in [0, 1], ECE in [0, 1]).
"""

import hashlib
import json
import os
import pytest
import torch

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DOCS      = os.path.abspath(os.path.join(WORKSPACE_ROOT, "..", "docs"))
V3_WEIGHTS_PATH = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v3_weights.pt")
EXPECTED_V3_HASH = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

REQUIRED_DOCS = [
    "PAHAD_LSTM_V4_5_BASELINE.md",
    "PAHAD_LSTM_V4_5_TRAINING_REPORT.md",
    "PAHAD_LSTM_V4_5_HORIZON_REPORT.md",
    "PAHAD_LSTM_V4_5_ABLATION_REPORT.md",
    "PAHAD_LSTM_V4_5_LOEO_REPORT.md",
    "PAHAD_LSTM_V4_5_CALIBRATION_REPORT.md",
    "PAHAD_LSTM_V4_5_ROBUSTNESS_REPORT.md",
    "PAHAD_LSTM_V4_5_CLAIM_AUDIT.md",
    "PAHAD_LSTM_V4_5_FINAL_RESEARCH_REPORT.md",
]


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_01_production_v3_weights_untouched():
    """Confirms production v3 weights are bit-for-bit identical to locked baseline."""
    assert os.path.exists(V3_WEIGHTS_PATH), f"Missing v3 weights at {V3_WEIGHTS_PATH}"
    actual_hash = compute_sha256(V3_WEIGHTS_PATH)
    assert actual_hash == EXPECTED_V3_HASH, (
        f"Production v3 weights mutated! Expected {EXPECTED_V3_HASH}, got {actual_hash}"
    )


def test_02_model_d_architecture_and_parameter_bounds():
    """Instantiates BiLSTMv4_5 and verifies parameter capacity (<150k params)."""
    from scripts.train_lstm_v4_5 import BiLSTMv4_5, N_FEATURES

    model = BiLSTMv4_5(n_features=N_FEATURES, hidden=64, num_layers=1, dropout=0.25, use_attention=True)
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)

    assert 100_000 <= param_count <= 150_000, (
        f"Parameter count {param_count:,} violated capacity-matched boundary [100k, 150k]"
    )


def test_03_forward_pass_across_input_windows():
    """Verifies forward pass with varying input windows (24h, 48h, 72h, 120h, 168h)."""
    from scripts.train_lstm_v4_5 import BiLSTMv4_5, ALL_HORIZONS

    model = BiLSTMv4_5(n_features=31, hidden=64, num_layers=1, dropout=0.25, use_attention=True)
    model.eval()

    batch_size = 3
    for win in [24, 48, 72, 120, 168]:
        dummy_input = torch.randn(batch_size, win, 31)
        with torch.no_grad():
            out = model(dummy_input, return_attention=True)

        for h in ALL_HORIZONS:
            assert h in out, f"Missing horizon {h} in output"
            assert out[h].shape == (batch_size,), f"Expected shape ({batch_size},) for {h}"

        assert "attention_weights" in out
        assert out["attention_weights"].shape == (batch_size, win)


def test_04_zero_target_leakage_and_cri_exclusion():
    """Verifies that composite_risk_index_cri is strictly excluded from features."""
    from scripts.train_lstm_v4_5 import ACTIVE_FEATURE_COLS

    assert "composite_risk_index_cri" not in ACTIVE_FEATURE_COLS
    assert "cri" not in ACTIVE_FEATURE_COLS
    assert len(ACTIVE_FEATURE_COLS) == 31


def test_05_all_9_documentation_reports_exist():
    """Verifies that all 9 required markdown reports exist in docs/ and root docs/."""
    for doc in REQUIRED_DOCS:
        local_p = os.path.join(WORKSPACE_ROOT, "docs", doc)
        assert os.path.exists(local_p), f"Missing report: {local_p}"
        assert os.path.getsize(local_p) > 200, f"Report {local_p} is empty or incomplete"

        if os.path.exists(ROOT_DOCS):
            root_p = os.path.join(ROOT_DOCS, doc)
            assert os.path.exists(root_p), f"Missing mirrored report: {root_p}"


def test_06_manifest_and_result_json_schemas():
    """Verifies valid JSON structure and non-deployment research labels."""
    manifest_p = os.path.join(WORKSPACE_ROOT, "data", "processed", "lstm_v4_5_manifest.json")
    result_p   = os.path.join(WORKSPACE_ROOT, "reports", "pahad_lstm_v4_5_result.json")

    assert os.path.exists(manifest_p), f"Missing manifest at {manifest_p}"
    assert os.path.exists(result_p), f"Missing result at {result_p}"

    with open(manifest_p, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["dataset_version"] == "v4.5"
    assert manifest["production_status"] == "DISABLED"
    assert manifest["event_count"] == 17
    assert manifest["control_count"] == 20

    with open(result_p, "r", encoding="utf-8") as f:
        res = json.load(f)
    assert res["phase"] == "V4.5"
    assert res["deployment_status"] == "DISABLED"
    assert res["production_modified"] is False
    assert res["overall_verdict"] in ["V4_5_RESEARCH_IMPROVED", "V4_5_NO_CLEAR_IMPROVEMENT", "V4_5_DATA_LIMITED"]


def test_07_calibration_and_operational_bounds():
    """Verifies that calibration metrics and operational bounds are mathematically sound."""
    result_p = os.path.join(WORKSPACE_ROOT, "reports", "pahad_lstm_v4_5_result.json")
    with open(result_p, "r", encoding="utf-8") as f:
        res = json.load(f)

    for h in ["24h", "48h", "72h", "168h"]:
        m = res[f"metrics_{h}"]
        assert 0.0 <= m["brier"] <= 1.0, f"Invalid Brier score {m['brier']} for {h}"
        assert 0.0 <= m["ece"] <= 1.0, f"Invalid ECE {m['ece']} for {h}"
        assert 0.0 <= m["pod"] <= 1.0
        assert 0.0 <= m["far"] <= 1.0
        assert 0.0 <= m["csi"] <= 1.0
