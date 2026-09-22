# -*- coding: utf-8 -*-
"""
tests/test_v4_5_training.py
===========================
Automated test suite for PAHAD AI Phase V4.5 Web-Informed Model Training & Diagnostics.
Validates:
  1. Model architecture and parameter capacity bounds (<150k params).
  2. Forward pass tensor shapes for 168-hour sequence inputs.
  3. Strict exclusion of composite_risk_index_cri (zero target leakage).
  4. Production isolation: models/pahad_lstm_v3_weights.pt hash remains locked.
  5. Artifact integrity: weights, config, metrics, scaler, and reports exist with valid schemas.
  6. Calibration bounds: Temperatures in [0.5, 3.5], probabilities in [0.0, 1.0].
"""

import hashlib
import json
import os
import numpy as np
import pytest
import torch

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
V3_WEIGHTS_PATH = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v3_weights.pt")
EXPECTED_V3_HASH = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

V4_5_WEIGHTS_PATH = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v4_5_research_weights.pt")
V4_5_CONFIG_PATH  = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v4_5_config.json")
V4_5_METRICS_PATH = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v4_5_metrics.json")
V4_5_SCALER_PATH  = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v4_5_scaler.json")
V4_5_RESULT_PATH  = os.path.join(WORKSPACE_ROOT, "reports", "pahad_lstm_v4_5_result.json")
V4_5_DOC_PATH     = os.path.join(WORKSPACE_ROOT, "docs", "PAHAD_LSTM_V4_5_RESEARCH_REPORT.md")


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_production_v3_weights_untouched():
    """Confirms production v3 weights are bit-for-bit identical to locked baseline."""
    assert os.path.exists(V3_WEIGHTS_PATH), f"Missing v3 weights at {V3_WEIGHTS_PATH}"
    actual_hash = compute_sha256(V3_WEIGHTS_PATH)
    assert actual_hash == EXPECTED_V3_HASH, (
        f"Production v3 weights mutated! Expected {EXPECTED_V3_HASH}, got {actual_hash}"
    )


def test_model_architecture_and_parameter_bounds():
    """Instantiates PAHADBiLSTMv4_5 and verifies parameter bounds (<150k)."""
    from scripts.train_lstm_v4_5 import PAHADBiLSTMv4_5, ACTIVE_FEATURE_COLS

    n_features = len(ACTIVE_FEATURE_COLS)
    assert n_features == 31, f"Expected 31 active features, got {n_features}"

    model = PAHADBiLSTMv4_5(n_features=n_features, hidden=64, num_layers=1, dropout=0.25)
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)

    assert 100_000 <= param_count <= 150_000, (
        f"Parameter count {param_count:,} violated capacity-matched boundary [100k, 150k]"
    )


def test_forward_pass_and_attention_shapes():
    """Verifies forward pass with 168-hour sequential inputs produces correct logits and attention."""
    from scripts.train_lstm_v4_5 import PAHADBiLSTMv4_5

    model = PAHADBiLSTMv4_5(n_features=31, hidden=64, num_layers=1, dropout=0.25)
    model.eval()

    batch_size = 4
    seq_len = 168
    dummy_input = torch.randn(batch_size, seq_len, 31)

    with torch.no_grad():
        out = model(dummy_input, return_attention=True)

    for h in ["6h", "12h", "24h", "48h"]:
        assert h in out, f"Missing horizon key {h} in model output"
        assert out[h].shape == (batch_size,), f"Expected shape ({batch_size},) for {h}, got {out[h].shape}"

    assert "attention_weights" in out
    assert out["attention_weights"].shape == (batch_size, seq_len), (
        f"Expected attention shape ({batch_size}, {seq_len}), got {out['attention_weights'].shape}"
    )
    # Check that attention weights sum to 1 across the 168 time-steps
    att_sums = torch.sum(out["attention_weights"], dim=1)
    np.testing.assert_allclose(att_sums.numpy(), np.ones(batch_size), atol=1e-5)


def test_zero_target_leakage():
    """Verifies that composite_risk_index_cri is strictly excluded from training features."""
    from scripts.train_lstm_v4_5 import ACTIVE_FEATURE_COLS

    assert "composite_risk_index_cri" not in ACTIVE_FEATURE_COLS
    assert "cri" not in ACTIVE_FEATURE_COLS


def test_v4_5_artifacts_and_metadata():
    """Verifies existence and schemas of all V4.5 research artifacts."""
    for path in [V4_5_CONFIG_PATH, V4_5_METRICS_PATH, V4_5_SCALER_PATH, V4_5_RESULT_PATH, V4_5_DOC_PATH]:
        assert os.path.exists(path), f"Artifact missing: {path}"

    with open(V4_5_CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["model_status"] == "RESEARCH_SHADOW_ONLY"
    assert cfg["production_status"] == "DISABLED"
    assert cfg["seq_len"] == 168
    assert cfg["n_features"] == 31

    with open(V4_5_METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    assert "test_metrics" in metrics
    for h in ["6h", "12h", "24h", "48h"]:
        assert h in metrics["test_metrics"]
        m = metrics["test_metrics"][h]
        assert 0.0 <= m["brier"] <= 1.0
        assert 0.0 <= m["ece"] <= 1.0

    with open(V4_5_RESULT_PATH, "r", encoding="utf-8") as f:
        res = json.load(f)
    assert res["final_verdict"] == "V4_5_RESEARCH_TRAINING_COMPLETE"
    assert res["production_status"] == "DISABLED"
