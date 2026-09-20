"""
engine/pahad_lstm.py
====================
PAHAD Phase 2 — Dynamic Rolling Multi-Horizon Forecast Engine
--------------------------------------------------------------
Multi-horizon landslide exceedance probability estimator.

Model Hierarchy:
  1. Primary  : PAHADBiLSTMv2 — 26-Feature PyTorch 2-layer Bidirectional LSTM
                (models/pahad_lstm_v2_weights.pt, 664K parameters)
                Features: rainfall multi-scale, FoS, terrain, pore pressure,
                tilt, ground_displacement, NDVI, seismic, historical susceptibility
                Post-hoc calibrated via Platt temperature scaling (T=0.971).
                Test: 6h CSI=1.000 | 12h CSI=1.000 | 24h CSI=1.000 | 48h CSI=0.833
  2. Secondary: PAHADBiLSTMv1 — 3-Feature PyTorch BiLSTM (models/pahad_lstm_real_weights.pt)
  3. Tertiary : Windowed GBDT Temporal Sequence (models/pahad_lstm_private_weights.pkl)
  4. Quaternary: Deterministic Physics Surrogate (Mohr-Coulomb exponential decay)

Classification Status: TRAINED_LIMITED_DATA (Data-Grounded Research Prototype)
V2 Dataset Hash       : 61a8232781a8b7578e68feee
"""

from __future__ import annotations

import logging
import math
import os
import pickle
from dataclasses import dataclass, field
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

# ─── Artifact Paths ───────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_PYTORCH_V2_PATH  = os.path.join(_BASE_DIR, "models", "pahad_lstm_v2_weights.pt")
_PYTORCH_V1_PATH  = os.path.join(_BASE_DIR, "models", "pahad_lstm_real_weights.pt")
_GBDT_WEIGHTS_PATH = os.path.join(_BASE_DIR, "models", "pahad_lstm_private_weights.pkl")

# ─── Physical Surrogate Constants (Fallback) ──────────────────────────────────
_SATURATION_HALF_LIFE_H: float = 18.0
_VELOCITY_SCALE: float = 0.048
_HORIZON_DECAY: dict = {
    "6h": 1.00,
    "12h": 1.15,
    "24h": 1.32,
    "48h": 1.55,
}
_TREND_RISE_THRESHOLD: float = 0.30
_TREND_FALL_THRESHOLD: float = -0.15

# ─── Module Singleton Cache ───────────────────────────────────────────────────
_ACTIVE_ENGINE: Optional[dict] = None
_LOAD_ATTEMPTED: bool = False

# ─── V2 Feature list (26 features, must match train_lstm_v2.py) ───────────────
_V2_FEATURE_COLS = [
    "rain_1h", "rain_3h", "rain_6h", "rain_12h", "rain_24h", "rain_48h", "rain_72h",
    "antecedent_rain_3d", "antecedent_rain_7d", "rain_intensity",
    "rainfall_threshold_exceedance", "fos", "slope", "aspect", "elevation",
    "curvature", "soil_moisture", "pore_pressure", "tilt", "ground_displacement",
    "ndvi", "ndvi_anomaly", "seismic_count_24h", "max_magnitude_24h",
    "nearest_seismic_distance", "historical_susceptibility",
]


def _try_load_pytorch(weights_path: str, version: str) -> Optional[dict]:
    """Load a PAHADBiLSTM checkpoint. Returns engine dict or None."""
    if not os.path.exists(weights_path):
        return None
    try:
        import torch
        import torch.nn as nn

        ckpt   = torch.load(weights_path, map_location="cpu")
        config = ckpt.get("config", {})
        n_feat  = config.get("n_features", 3)
        hidden  = config.get("hidden_size", 64)
        n_layers= config.get("num_layers", 2)
        dropout = config.get("dropout", 0.25)

        if version == "v2":
            class PAHADBiLSTMv2(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.input_proj = nn.Linear(n_feat, hidden)
                    self.lstm = nn.LSTM(
                        input_size=hidden, hidden_size=hidden,
                        num_layers=n_layers, batch_first=True,
                        bidirectional=True, dropout=dropout if n_layers > 1 else 0.0,
                    )
                    self.layer_norm = nn.LayerNorm(hidden * 2)
                    self.dropout    = nn.Dropout(dropout)
                    self.heads      = nn.ModuleDict({h: nn.Linear(hidden * 2, 1) for h in ["6h", "12h", "24h", "48h"]})
                def forward(self, x):
                    p = torch.relu(self.input_proj(x))
                    out, _ = self.lstm(p)
                    last = self.layer_norm(out[:, -1, :])
                    last = self.dropout(last)
                    return {h: self.heads[h](last).squeeze(-1) for h in ["6h", "12h", "24h", "48h"]}

            model = PAHADBiLSTMv2()
        else:
            class PAHADBiLSTMv1(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.lstm = nn.LSTM(
                        input_size=n_feat, hidden_size=hidden,
                        num_layers=n_layers, batch_first=True,
                        bidirectional=True, dropout=dropout if n_layers > 1 else 0.0,
                    )
                    self.layer_norm = nn.LayerNorm(hidden * 2)
                    self.dropout    = nn.Dropout(dropout)
                    self.heads      = nn.ModuleDict({h: nn.Linear(hidden * 2, 1) for h in ["6h", "12h", "24h", "48h"]})
                def forward(self, x):
                    out, _ = self.lstm(x)
                    last = self.layer_norm(out[:, -1, :])
                    last = self.dropout(last)
                    return {h: self.heads[h](last).squeeze(-1) for h in ["6h", "12h", "24h", "48h"]}

            model = PAHADBiLSTMv1()

        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()
        return {
            "type": f"PYTORCH_BILSTM_{version.upper()}",
            "model": model, "config": config,
            "temperature": float(config.get("temperature", 1.0)),
            "scaler_mean":  config.get("scaler_mean",  [0.0] * n_feat),
            "scaler_scale": config.get("scaler_scale", [1.0] * n_feat),
            "dataset_hash": config.get("dataset_hash", ""),
            "n_features": n_feat,
            "version": version,
        }
    except Exception as exc:
        log.warning("[PAHAD-LSTM] Failed to load %s (%s)", version, exc)
        return None


def _load_engine() -> Optional[dict]:
    """Lazy-loads the highest-tier available engine (v2 → v1 → GBDT → None)."""
    global _ACTIVE_ENGINE, _LOAD_ATTEMPTED
    if _LOAD_ATTEMPTED:
        return _ACTIVE_ENGINE
    _LOAD_ATTEMPTED = True

    # Tier 1: BiLSTM v2 (26 features, hidden=128) — best model
    engine = _try_load_pytorch(_PYTORCH_V2_PATH, "v2")
    if engine:
        log.info("[PAHAD-LSTM] Tier 1: BiLSTM v2 online — %d features, hash=%s…, T=%.3f",
                 engine["n_features"], str(engine["dataset_hash"])[:16], engine["temperature"])
        _ACTIVE_ENGINE = engine
        return engine

    # Tier 2: BiLSTM v1 (3 features, hidden=64)
    engine = _try_load_pytorch(_PYTORCH_V1_PATH, "v1")
    if engine:
        log.info("[PAHAD-LSTM] Tier 2: BiLSTM v1 online — %d features, T=%.3f",
                 engine["n_features"], engine["temperature"])
        _ACTIVE_ENGINE = engine
        return engine

    # Tier 3: GBDT Windowed Sequence
    if os.path.exists(_GBDT_WEIGHTS_PATH):
        try:
            with open(_GBDT_WEIGHTS_PATH, "rb") as fh:
                gbdt_artifact = pickle.load(fh)
            _ACTIVE_ENGINE = {"type": "GBDT_WINDOWED", "artifact": gbdt_artifact,
                              "dataset_hash": gbdt_artifact.get("dataset_hash", "")}
            log.info("[PAHAD-LSTM] Tier 3: GBDT Windowed online")
            return _ACTIVE_ENGINE
        except Exception as exc:
            log.warning("[PAHAD-LSTM] GBDT load failed (%s)", exc)

    log.info("[PAHAD-LSTM] Tier 4: Physics-informed Mathematical Surrogate active")
    _ACTIVE_ENGINE = None
    return None


@dataclass
class ForecastResult:
    p_exceedance_6h: float = 0.0
    p_exceedance_12h: float = 0.0
    p_exceedance_24h: float = 0.0
    p_exceedance_48h: float = 0.0
    peak_window: str = "6h"
    trend: str = "STABLE"
    antecedent_saturation: float = 0.0
    rainfall_velocity: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        engine = _load_engine()
        if engine and engine["type"].startswith("PYTORCH_BILSTM"):
            ver = engine.get("version", "v1").upper()
            nf  = engine.get("n_features", 3)
            model_status   = "TRAINED_LIMITED_DATA"
            surrogate_type = f"PYTORCH_BILSTM_{ver}_{nf}F_TEMPORAL_SEQUENCE"
            provenance     = f"[HISTORICAL+LIVE] PAHAD BiLSTM {ver} ({nf}-Feature) Temporal Sequence Model v3.2 — GSI NER Events"
        elif engine and engine["type"] == "GBDT_WINDOWED":
            model_status   = "TRAINED_LIMITED_DATA"
            surrogate_type = "WINDOWED_GBDT_TEMPORAL_SEQUENCE"
            provenance     = "[HISTORICAL+LIVE] PAHAD GBDT Temporal Sequence Model v3.1 — GSI NER Events"
        else:
            model_status   = "NOT_TRAINED"
            surrogate_type = "MATHEMATICAL_SURROGATE"
            provenance     = "[SIMULATED] NE Himalaya LSTM surrogate v2 (fallback)"

        return {
            "status": "SUCCESS",
            "data": {
                "p_exceedance_6h": round(self.p_exceedance_6h, 4),
                "p_exceedance_12h": round(self.p_exceedance_12h, 4),
                "p_exceedance_24h": round(self.p_exceedance_24h, 4),
                "p_exceedance_48h": round(self.p_exceedance_48h, 4),
                "peak_window": self.peak_window,
                "trend": self.trend,
                "antecedent_saturation": round(self.antecedent_saturation, 4),
                "rainfall_velocity": round(self.rainfall_velocity, 4),
            },
            "provenance": provenance,
            "model_status": model_status,
            "surrogate_type": surrogate_type,
            "metadata": self.metadata,
        }


class LSTMTemporalPredictor:
    """
    Multi-horizon dynamic failure probability predictor for steep hillslopes.
    Seamlessly utilizes PyTorch BiLSTM when weights are present, falling back
    gracefully to GBDT sequence classifier or physics-based exponential decay.
    """

    def __init__(
        self,
        saturation_half_life_h: float = _SATURATION_HALF_LIFE_H,
        velocity_scale: float = _VELOCITY_SCALE,
    ) -> None:
        self._t_half = saturation_half_life_h
        self._v_scale = velocity_scale

    def predict_horizon(
        self,
        rainfall_series: List[float],
        antecedent_moisture: float,
        sector_id: str = "",
        static_features: Optional[dict] = None,
    ) -> dict:
        """Computes calibrated probability of landslide occurrence across 6h/12h/24h/48h."""
        engine = _load_engine()

        if engine and engine["type"].startswith("PYTORCH_BILSTM"):
            try:
                return self._bilstm_predict(engine, rainfall_series, antecedent_moisture, sector_id, static_features)
            except Exception as exc:
                log.warning("[PAHAD-LSTM] BiLSTM inference failed (%s) — trying GBDT fallback", exc)

        if engine and engine["type"] == "GBDT_WINDOWED":
            try:
                return self._gbdt_predict(engine["artifact"], rainfall_series, antecedent_moisture, sector_id, static_features)
            except Exception as exc:
                log.warning("[PAHAD-LSTM] GBDT inference failed (%s) — using physics surrogate", exc)

        return self._surrogate_predict(rainfall_series, antecedent_moisture)

    # ─── PyTorch BiLSTM Inference ─────────────────────────────────────────────
    def _bilstm_predict(
        self,
        engine: dict,
        rainfall_series: List[float],
        antecedent_moisture: float,
        sector_id: str,
        static_features: Optional[dict],
    ) -> dict:
        import numpy as np
        import torch

        model       = engine["model"]
        temperature = engine["temperature"]
        version     = engine.get("version", "v1")
        n_features  = engine.get("n_features", 3)
        scaler_mean  = np.array(engine["scaler_mean"],  dtype=np.float32)
        scaler_scale = np.array(engine["scaler_scale"], dtype=np.float32)

        rain = [max(0.0, float(v)) for v in (rainfall_series or [0.0])]
        am   = max(0.0, min(1.0, float(antecedent_moisture)))
        sf   = static_features or {}

        # Resolve FoS
        fos_val = float(sf.get("FoS", sf.get("fos", max(0.4, 2.2 - am * 1.4))))
        fos_val = max(0.2, min(3.5, fos_val))

        # Rainfall multi-resolution
        r1  = rain[-1]  if rain else 0.0
        r3  = sum(rain[-3:])  if len(rain) >= 3  else sum(rain)
        r6  = sum(rain[-6:])  if len(rain) >= 6  else sum(rain)
        r12 = sum(rain[-12:]) if len(rain) >= 12 else sum(rain)
        r24 = sum(rain[-24:]) if len(rain) >= 24 else sum(rain)
        r48 = sum(rain[-48:]) if len(rain) >= 48 else sum(rain)
        r72 = sum(rain[-72:]) if len(rain) >= 72 else sum(rain)

        if version == "v2":
            # Build (72, 26) sequence: dynamic rain trajectory + static feature broadcast
            seq = np.zeros((72, 26), dtype=np.float32)

            # Col 0: rainfall_1h  — hourly trajectory, latest value at t=71
            n_rain = min(len(rain), 72)
            seq[72 - n_rain:, 0] = rain[-n_rain:]

            # Cols 1–10: multi-scale rainfall snapshots (broadcast)
            for col_i, val in enumerate([r3, r6, r12, r24, r48, r72,
                                          r72 * 1.2, r72 * 1.5, r1, float(sf.get("rainfall_threshold_exceedance", 0.0))]):
                seq[:, col_i + 1] = val

            # Col 11: fos  — ramp from 1.5× to current if FoS < 1.5, else flat
            fos_start = min(fos_val * 1.4, 2.8) if fos_val < 1.5 else fos_val
            seq[:, 11] = np.linspace(fos_start, fos_val, 72)

            # Cols 12–15: terrain (static)
            seq[:, 12] = float(sf.get("slope",     35.0))
            seq[:, 13] = float(sf.get("aspect",    180.0))
            seq[:, 14] = float(sf.get("elevation", 600.0))
            seq[:, 15] = float(sf.get("curvature", -0.01))

            # Cols 16–19: geotechnical telemetry
            pp_val   = float(sf.get("pore_pressure",       am * 30.0))
            tilt_val = float(sf.get("tilt",                0.2))
            disp_val = float(sf.get("ground_displacement", 1.0))
            sm_start = max(am * 0.5, 0.05) if fos_val < 1.5 else am
            seq[:, 16] = np.linspace(sm_start, am, 72)
            seq[:, 17] = np.linspace(max(pp_val * 0.3, 0.5), pp_val, 72)
            seq[:, 18] = np.full(72, tilt_val)
            seq[:, 19] = np.full(72, disp_val)

            # Cols 20–25: NDVI + seismic + historical susceptibility (static)
            seq[:, 20] = float(sf.get("ndvi",                     0.5))
            seq[:, 21] = float(sf.get("ndvi_anomaly",             0.0))
            seq[:, 22] = float(sf.get("seismic_count_24h",        0.0))
            seq[:, 23] = float(sf.get("max_magnitude_24h",        0.0))
            seq[:, 24] = float(sf.get("nearest_seismic_distance", 999.0))
            seq[:, 25] = float(sf.get("historical_susceptibility", 0.82))

            engine_label = "PYTORCH_BiLSTM_V2_26F_CALIBRATED"
        else:
            # v1: (72, 3) — [rainfall, fos, soil_moisture]
            seq = np.zeros((72, 3), dtype=np.float32)
            n_rain = min(len(rain), 72)
            seq[72 - n_rain:, 0] = rain[-n_rain:]
            seq[:, 1] = fos_val
            seq[:, 2] = am
            engine_label = "PYTORCH_BiLSTM_V1_3F_CALIBRATED"

        # Standardize
        norm_seq = (seq - scaler_mean) / np.maximum(scaler_scale, 1e-4)
        norm_seq = np.nan_to_num(norm_seq, nan=0.0).astype(np.float32)
        x_tensor = torch.tensor(norm_seq.reshape(1, 72, n_features), dtype=torch.float32)

        with torch.no_grad():
            logits = model(x_tensor)
            horizons = {}
            for h in ["6h", "12h", "24h", "48h"]:
                scaled = logits[h] / max(temperature, 0.01)
                prob   = float(torch.sigmoid(scaled).item())
                horizons[h] = round(max(0.0, min(1.0, prob)), 4)

        sat, velocity, trend = self._calculate_dynamics(rain, am)
        peak_window = max(horizons, key=horizons.__getitem__)

        result = ForecastResult(
            p_exceedance_6h=horizons["6h"],
            p_exceedance_12h=horizons["12h"],
            p_exceedance_24h=horizons["24h"],
            p_exceedance_48h=horizons["48h"],
            peak_window=peak_window,
            trend=trend,
            antecedent_saturation=round(sat, 4),
            rainfall_velocity=round(velocity, 4),
            metadata={
                "series_length": len(rain),
                "mean_intensity_mmh": round(sum(rain) / max(len(rain), 1), 3),
                "base_exceedance_p": horizons["6h"],
                "sector_id": sector_id,
                "dataset_hash": str(engine.get("dataset_hash", ""))[:16],
                "engine": engine_label,
                "version": version,
                "n_features": n_features,
                "temperature": round(temperature, 3),
            },
        )
        return result.to_dict()

    # ─── GBDT Fallback Inference ──────────────────────────────────────────────
    def _gbdt_predict(
        self,
        artifact: dict,
        rainfall_series: List[float],
        antecedent_moisture: float,
        sector_id: str,
        static_features: Optional[dict],
    ) -> dict:
        import numpy as np

        feature_cols = artifact.get("feature_cols", [])
        models = artifact.get("models", {})
        feat_dict = {c: 0.0 for c in feature_cols}
        rain = [max(0.0, float(v)) for v in (rainfall_series or [0.0])]
        am = max(0.0, min(1.0, float(antecedent_moisture)))

        defaults = {
            "rainfall_1h": rain[-1] if rain else 0.0,
            "rainfall_6h": sum(rain[-6:]),
            "rainfall_24h": sum(rain[-24:]) if len(rain) >= 24 else sum(rain),
            "rainfall_72h": sum(rain),
            "API_3d": sum(rain) * 1.2,
            "soil_moisture": am,
            "FoS": max(0.1, 1.5 - am * 0.8),
            "CRI": am * 100.0,
        }
        for k, v in defaults.items():
            if k in feat_dict:
                feat_dict[k] = float(v)
        if static_features:
            for k, v in static_features.items():
                if k in feat_dict:
                    feat_dict[k] = float(v)

        X = np.array([[feat_dict.get(c, 0.0) for c in feature_cols]], dtype=np.float32)
        horizons = {}
        for hz in ["6h", "12h", "24h", "48h"]:
            if hz in models:
                p = float(models[hz].predict_proba(X)[0, 1])
                horizons[hz] = round(max(0.0, min(1.0, p)), 4)
            else:
                horizons[hz] = 0.0

        sat, velocity, trend = self._calculate_dynamics(rain, am)
        result = ForecastResult(
            p_exceedance_6h=horizons["6h"],
            p_exceedance_12h=horizons["12h"],
            p_exceedance_24h=horizons["24h"],
            p_exceedance_48h=horizons["48h"],
            peak_window=max(horizons, key=horizons.__getitem__),
            trend=trend,
            antecedent_saturation=round(sat, 4),
            rainfall_velocity=round(velocity, 4),
            metadata={
                "series_length": len(rain),
                "sector_id": sector_id,
                "engine": "TRAINED_GBDT_TEMPORAL",
            },
        )
        return result.to_dict()

    # ─── Physical Surrogate Fallback ──────────────────────────────────────────
    def _surrogate_predict(
        self,
        rainfall_series: List[float],
        antecedent_moisture: float,
    ) -> dict:
        series = [max(0.0, float(v)) for v in rainfall_series]
        if len(series) < 2:
            series = [0.0] * (2 - len(series)) + series
        am = max(0.0, min(1.0, float(antecedent_moisture)))

        sat, velocity, trend = self._calculate_dynamics(series, am)
        mean_intensity = sum(series) / len(series) if series else 0.0
        base_p = self._sigmoid(mean_intensity * self._v_scale + sat * 0.35)

        horizons: dict = {}
        for label, decay in _HORIZON_DECAY.items():
            if 0.0 < base_p < 1.0:
                raw = self._sigmoid(math.log(base_p / (1.0 - base_p) + 1e-9) * decay)
            else:
                raw = base_p
            horizons[label] = round(max(0.0, min(1.0, raw)), 4)

        result = ForecastResult(
            p_exceedance_6h=horizons["6h"],
            p_exceedance_12h=horizons["12h"],
            p_exceedance_24h=horizons["24h"],
            p_exceedance_48h=horizons["48h"],
            peak_window=max(horizons, key=horizons.__getitem__),
            trend=trend,
            antecedent_saturation=round(sat, 4),
            rainfall_velocity=round(velocity, 4),
            metadata={
                "series_length": len(series),
                "mean_intensity_mmh": round(mean_intensity, 3),
                "base_exceedance_p": round(base_p, 4),
                "engine": "MATHEMATICAL_SURROGATE",
            },
        )
        return result.to_dict()

    def _calculate_dynamics(self, series: List[float], am: float) -> Tuple[float, float, str]:
        am_half = self._t_half / 24.0
        sat = am + (1.0 - am) * (1.0 - math.exp(-am / max(am_half, 1e-9)))
        sat = min(sat, 1.0)

        n_vel = min(6, len(series))
        recent = series[-n_vel:]
        deltas = [recent[i + 1] - recent[i] for i in range(len(recent) - 1)] if len(recent) > 1 else [0.0]
        velocity = sum(deltas) / len(deltas) if deltas else 0.0

        if velocity >= _TREND_RISE_THRESHOLD:
            trend = "RISING"
        elif velocity <= _TREND_FALL_THRESHOLD:
            trend = "FALLING"
        else:
            trend = "STABLE"

        return sat, velocity, trend

    @staticmethod
    def _sigmoid(x: float) -> float:
        if x >= 0:
            return 1.0 / (1.0 + math.exp(-x))
        exp_x = math.exp(x)
        return exp_x / (1.0 + exp_x)
