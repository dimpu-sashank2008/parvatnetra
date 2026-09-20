"""
tests/test_lstm_real_training.py
=================================
Regression test suite for the PAHAD PyTorch BiLSTM Temporal Sequence Model.
Verifies model weights integrity, multi-horizon calibrated inference,
sensitivity to precipitation and shear strength, and fallback hierarchy.
"""

import os
import json
import pytest
import numpy as np


class TestPAHADBiLSTMTemporalModel:

    def test_01_weights_and_config_integrity(self):
        weights_path = "models/pahad_lstm_real_weights.pt"
        config_path = "models/pahad_lstm_real_config.json"
        metrics_path = "models/pahad_lstm_real_metrics.json"

        assert os.path.exists(weights_path), f"PyTorch weights missing at {weights_path}"
        assert os.path.getsize(weights_path) > 500_000, "Weights file smaller than expected"

        assert os.path.exists(config_path), f"Model config missing at {config_path}"
        with open(config_path, "r") as f:
            cfg = json.load(f)
        assert cfg["architecture"] == "2-layer Bidirectional LSTM"
        assert cfg["hidden_size"] == 64
        assert cfg["seq_len"] == 72
        assert cfg["n_features"] == 3
        assert "temperature" in cfg
        assert 0.2 <= cfg["temperature"] <= 3.0

        assert os.path.exists(metrics_path), f"Metrics JSON missing at {metrics_path}"
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        assert metrics["model_status"] == "TRAINED_LIMITED_DATA"
        assert "val_metrics" in metrics
        assert "test_metrics" in metrics
        for h in ["6h", "12h", "24h", "48h"]:
            assert h in metrics["val_metrics"]
            assert h in metrics["test_metrics"]
            assert metrics["val_metrics"][h]["roc_auc"] >= 0.80

    def test_02_inference_probability_bounds_and_format(self):
        from engine.pahad_lstm import LSTMTemporalPredictor

        predictor = LSTMTemporalPredictor()
        result = predictor.predict_horizon(
            rainfall_series=[2.0, 5.0, 8.0, 12.0, 18.0],
            antecedent_moisture=0.45,
            sector_id="SK-NH10-KM48",
            static_features={"FoS": 1.4},
        )

        assert result["status"] == "SUCCESS"
        assert result["model_status"] == "TRAINED_LIMITED_DATA"
        # surrogate_type reflects active engine (v1 or v2 — both start with PYTORCH_BILSTM)
        assert result["surrogate_type"].startswith("PYTORCH_BILSTM"), f"Unexpected surrogate_type: {result['surrogate_type']}"
        assert "data" in result

        data = result["data"]
        for h in ["6h", "12h", "24h", "48h"]:
            p_val = data[f"p_exceedance_{h}"]
            assert 0.0 <= p_val <= 1.0, f"Exceedance probability {h} out of bounds: {p_val}"

        assert data["peak_window"] in ["6h", "12h", "24h", "48h"]
        assert data["trend"] in ["STABLE", "RISING", "FALLING"]

    def test_03_physical_consistency_and_sensitivity(self):
        from engine.pahad_lstm import LSTMTemporalPredictor

        predictor = LSTMTemporalPredictor()

        # Baseline: Dry, stable slope
        dry_res = predictor.predict_horizon(
            rainfall_series=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            antecedent_moisture=0.15,
            sector_id="SK-SINGTAM-01",
            static_features={"FoS": 2.5},
        )

        # Destabilized: Extreme torrential rain with critical FoS < 1.0
        critical_res = predictor.predict_horizon(
            rainfall_series=[15.0, 25.0, 35.0, 48.0, 55.0, 60.0],
            antecedent_moisture=0.85,
            sector_id="SK-SINGTAM-01",
            static_features={"FoS": 0.78},
        )

        dry_24h = dry_res["data"]["p_exceedance_24h"]
        critical_24h = critical_res["data"]["p_exceedance_24h"]

        # Critical failure probability must exceed dry probability by a wide margin
        assert critical_24h > dry_24h, f"Physics violation: critical ({critical_24h}) <= dry ({dry_24h})"
        assert critical_24h > 0.80, f"Critical condition did not trigger high probability: {critical_24h}"
        assert dry_24h < 0.20, f"Dry condition produced elevated probability: {dry_24h}"
        assert critical_res["data"]["trend"] == "RISING"

    def test_04_temperature_calibration_applied(self):
        from engine.pahad_lstm import _load_engine

        engine = _load_engine()
        assert engine is not None
        # Accept v1 or v2 — both start with PYTORCH_BILSTM
        assert engine["type"].startswith("PYTORCH_BILSTM"), f"Unexpected engine type: {engine['type']}"
        assert "temperature" in engine
        # Temperature must be positive and reasonable
        assert 0.3 < engine["temperature"] < 2.5
