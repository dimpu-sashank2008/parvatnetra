"""
engine/pahad_lstm_private_runner.py
=====================================
PAHAD LSTM — Private Trained Model Inference Runner
-----------------------------------------------------
Drop-in replacement for LSTMTemporalPredictor that uses the locally-trained
GradientBoostingClassifier weights instead of the mathematical surrogate.

CRITICAL SAFETY INVARIANTS:
- This file is NOT imported by app.py until the user explicitly approves the flip
- The public surrogate in engine/pahad_lstm.py remains unchanged
- Output includes model_status: "TRAINED_LOCAL_PRIVATE" (different from public "NOT_TRAINED")
- Only use this runner via the local CLI or test scripts

Usage (local only — NOT for production yet):
  from engine.pahad_lstm_private_runner import PrivateLSTMRunner
  runner = PrivateLSTMRunner()
  result = runner.predict_horizon(
      sector_id="SK-SINGTAM-01",
      rainfall_series=[5.2, 8.1, 12.4, 18.3, 24.1, 29.0],
      antecedent_moisture=0.58,
      static_features={}   # Optional: override any static feature
  )

Model provenance:
  [PRIVATE] models/pahad_lstm_private_weights.pkl  (gitignored)
  Status  : TRAINED_LOCAL_PRIVATE
  Public  : NOT_TRAINED (unchanged until user approves flip)
"""

from __future__ import annotations

import logging
import math
import os
import pickle
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

_WEIGHTS_PATH = "models/pahad_lstm_private_weights.pkl"
_DB_PATH = "data/observations/pahad_observations.db"

# ─── Horizon decay factors (must match training constants) ────────────────────
_HORIZON_DECAY = {"6h": 1.00, "12h": 1.15, "24h": 1.32, "48h": 1.55}


class PrivateLSTMRunner:
    """
    Locally-trained temporal sequence inference runner.
    Provides the same interface as LSTMTemporalPredictor but uses real weights.
    """

    def __init__(self, weights_path: str = _WEIGHTS_PATH) -> None:
        self._weights_path = weights_path
        self._artifact: Optional[Dict[str, Any]] = None
        self._loaded = False
        self._load_error: Optional[str] = None

    def _load(self) -> bool:
        """Lazy-load the private trained weights."""
        if self._loaded:
            return True
        if not os.path.exists(self._weights_path):
            self._load_error = f"Private weights not found: {self._weights_path}"
            log.warning(self._load_error)
            return False
        try:
            with open(self._weights_path, "rb") as fh:
                self._artifact = pickle.load(fh)
            self._loaded = True
            log.info(
                "[PRIVATE LSTM] Loaded weights — horizons=%s  hash=%s",
                self._artifact.get("forecast_horizons"),
                str(self._artifact.get("dataset_hash", ""))[:16],
            )
            return True
        except Exception as exc:
            self._load_error = str(exc)
            log.error("[PRIVATE LSTM] Failed to load weights: %s", exc)
            return False

    def _build_feature_vector(
        self,
        sector_id: str,
        rainfall_series: List[float],
        antecedent_moisture: float,
        static_features: Optional[Dict[str, float]] = None,
    ) -> List[float]:
        """Build a feature vector matching the training schema."""
        if not self._artifact:
            return []

        feature_cols = self._artifact.get("feature_cols", [])

        # Start with zero vector matching the training feature schema
        feat_dict: Dict[str, float] = {c: 0.0 for c in feature_cols}

        # Fill static features from STATIC defaults / provided overrides
        defaults = {
            "rainfall_1h": rainfall_series[-1] if rainfall_series else 0.0,
            "rainfall_6h": sum(rainfall_series[-6:]) if len(rainfall_series) >= 6 else sum(rainfall_series),
            "rainfall_24h": sum(rainfall_series[-24:]) if len(rainfall_series) >= 24 else sum(rainfall_series),
            "rainfall_72h": sum(rainfall_series) if rainfall_series else 0.0,
            "API_3d": sum(rainfall_series[-72:]) * 1.2 if rainfall_series else 0.0,
            "API_7d": sum(rainfall_series) * 1.5 if rainfall_series else 0.0,
            "API_30d": sum(rainfall_series) * 2.0 if rainfall_series else 0.0,
            "rainfall_accumulation_3h": sum(rainfall_series[-3:]) if len(rainfall_series) >= 3 else sum(rainfall_series),
            "rainfall_intensity_3h": (sum(rainfall_series[-3:]) / 3.0) if len(rainfall_series) >= 3 else 0.0,
            "rainfall_acceleration": (rainfall_series[-1] - rainfall_series[-2]) if len(rainfall_series) >= 2 else 0.0,
            "soil_moisture": antecedent_moisture,
            "soil_moisture_trend_24h": 0.0,
            "pore_pressure": antecedent_moisture * 40.0,
            "pore_pressure_trend_24h": 0.0,
            "FoS": 1.5 - antecedent_moisture * 0.8,
            "CRI": antecedent_moisture * 100.0,
        }

        for k, v in defaults.items():
            if k in feat_dict:
                feat_dict[k] = float(v)

        if static_features:
            for k, v in static_features.items():
                if k in feat_dict:
                    feat_dict[k] = float(v)

        # Temporal lag features from rainfall series
        rain_series = list(rainfall_series) if rainfall_series else [0.0]
        lags = [1, 3, 6, 12, 24, 48, 72]
        for lag in lags:
            key = f"precipitation_lag{lag}h"
            if key in feat_dict:
                idx = max(0, len(rain_series) - lag)
                feat_dict[key] = float(rain_series[idx]) if rain_series else 0.0

        # Rolling window features
        rolls = [3, 6, 12, 24]
        for win in rolls:
            window = rain_series[-win:] if len(rain_series) >= win else rain_series
            for stat_key, val in [
                (f"precipitation_roll_mean_{win}h", sum(window) / len(window) if window else 0.0),
                (f"precipitation_roll_max_{win}h", max(window) if window else 0.0),
                (f"precipitation_roll_std_{win}h", _std(window)),
            ]:
                if stat_key in feat_dict:
                    feat_dict[stat_key] = float(val)

        return [feat_dict.get(c, 0.0) for c in feature_cols]

    def predict_horizon(
        self,
        sector_id: str = "",
        rainfall_series: Optional[List[float]] = None,
        antecedent_moisture: float = 0.0,
        static_features: Optional[Dict[str, float]] = None,
    ) -> dict:
        """
        Predict multi-horizon failure exceedance probabilities.

        Falls back gracefully to the surrogate math if weights are unavailable.
        """
        rainfall_series = rainfall_series or [0.0]

        if not self._load():
            # Graceful fallback to surrogate calculation
            return self._surrogate_fallback(rainfall_series, antecedent_moisture)

        try:
            feat_vec = self._build_feature_vector(
                sector_id=sector_id,
                rainfall_series=rainfall_series,
                antecedent_moisture=antecedent_moisture,
                static_features=static_features,
            )
            import numpy as np
            X = np.array([feat_vec], dtype=np.float32)

            horizons = {}
            models = self._artifact.get("models", {})
            for horizon in ["6h", "12h", "24h", "48h"]:
                if horizon not in models:
                    horizons[horizon] = 0.0
                    continue
                p = models[horizon].predict_proba(X)[0, 1]
                horizons[horizon] = round(float(max(0.0, min(1.0, p))), 4)

            peak_window = max(horizons, key=horizons.__getitem__)

            # Trend from recent rainfall velocity
            recent = rainfall_series[-6:] if len(rainfall_series) >= 6 else rainfall_series
            deltas = [recent[i + 1] - recent[i] for i in range(len(recent) - 1)] if len(recent) > 1 else [0.0]
            velocity = sum(deltas) / len(deltas) if deltas else 0.0
            trend = "RISING" if velocity >= 0.30 else ("FALLING" if velocity <= -0.15 else "STABLE")

            return {
                "status": "SUCCESS",
                "data": {
                    "p_exceedance_6h": horizons["6h"],
                    "p_exceedance_12h": horizons["12h"],
                    "p_exceedance_24h": horizons["24h"],
                    "p_exceedance_48h": horizons["48h"],
                    "peak_window": peak_window,
                    "trend": trend,
                    "antecedent_saturation": round(float(antecedent_moisture), 4),
                    "rainfall_velocity": round(float(velocity), 4),
                },
                "provenance": "[HISTORICAL+LIVE] PAHAD Private LSTM — NOT yet promoted to production",
                # ─── CRITICAL: public_status must remain NOT_TRAINED ─────────────
                "model_status": "TRAINED_LOCAL_PRIVATE",
                "surrogate_type": "WINDOWED_GBDT_SEQUENCE",
                "metadata": {
                    "sector_id": sector_id,
                    "series_length": len(rainfall_series),
                    "dataset_hash": str(self._artifact.get("dataset_hash", ""))[:16],
                    "private_weights_path": self._weights_path,
                },
            }

        except Exception as exc:
            log.error("[PRIVATE LSTM] Inference error: %s — falling back to surrogate", exc)
            return self._surrogate_fallback(rainfall_series, antecedent_moisture)

    def _surrogate_fallback(self, rainfall_series: List[float], antecedent_moisture: float) -> dict:
        """Mathematical surrogate fallback (same as engine/pahad_lstm.py)."""
        series = [max(0.0, float(v)) for v in rainfall_series]
        if len(series) < 2:
            series = [0.0] * (2 - len(series)) + series
        am = max(0.0, min(1.0, float(antecedent_moisture)))
        am_half = 18.0 / 24.0
        sat = am + (1.0 - am) * (1.0 - math.exp(-am / max(am_half, 1e-9)))
        sat = min(sat, 1.0)
        mean_i = sum(series) / len(series)
        base_p = 1.0 / (1.0 + math.exp(-(mean_i * 0.048 + sat * 0.35)))
        horizons = {}
        for label, decay in _HORIZON_DECAY.items():
            if 0.0 < base_p < 1.0:
                raw = 1.0 / (1.0 + math.exp(-(math.log(base_p / (1.0 - base_p) + 1e-9)) * decay))
            else:
                raw = base_p
            horizons[label] = round(max(0.0, min(1.0, raw)), 4)
        return {
            "status": "SUCCESS",
            "data": {
                "p_exceedance_6h": horizons["6h"],
                "p_exceedance_12h": horizons["12h"],
                "p_exceedance_24h": horizons["24h"],
                "p_exceedance_48h": horizons["48h"],
                "peak_window": max(horizons, key=horizons.__getitem__),
                "trend": "STABLE",
                "antecedent_saturation": round(sat, 4),
                "rainfall_velocity": 0.0,
            },
            "provenance": "[SIMULATED] NE Himalaya LSTM surrogate v2 (fallback)",
            "model_status": "NOT_TRAINED",
            "surrogate_type": "MATHEMATICAL_SURROGATE",
            "metadata": {"fallback_reason": self._load_error or "weights_loading_failed"},
        }

    @property
    def is_trained(self) -> bool:
        """True only if private weights successfully loaded."""
        return self._load()

    @property
    def dataset_hash(self) -> Optional[str]:
        if self._artifact:
            return self._artifact.get("dataset_hash")
        return None


def _std(vals: List[float]) -> float:
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    return math.sqrt(sum((v - mean) ** 2 for v in vals) / (len(vals) - 1))
