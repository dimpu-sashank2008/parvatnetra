# -*- coding: utf-8 -*-
"""
engine/pahad_temporal_model.py
==============================
PARVAT NETRA • PAHAD AI Temporal Sequence Architecture & Feature Engineering
----------------------------------------------------------------------------
Implements:
  1. Multi-horizon temporal feature window calculator (1h, 3h, 6h, 12h, 24h, 48h, 72h).
  2. Rolling derivative kernels (accumulation, intensity, acceleration, tilt rates, pore pressure trends).
  3. PyTorch LSTM/GRU sequence architecture definition.
  4. Explicit Model Readiness State:
     - When event sample size is limited, the deep temporal LSTM is marked strictly as `NOT_TRAINED`,
       and temporal features are fed transparently into the calibrated Gradient Boosting classifier.
     - Never pretends an untrained deep model is producing live predictions ("No fake AI").

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import math
import logging
from typing import Dict, Any, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("PAHAD_TEMPORAL_MODEL")

# Check optional PyTorch availability
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TemporalFeatureWindowEngine:
    """
    Computes temporal derivatives, accelerations, and rolling windows
    across 1h, 3h, 6h, 12h, 24h, 48h, and 72h horizons.
    """

    @staticmethod
    def calculate_temporal_trends(
        rainfall_series: List[float],
        soil_moisture_series: List[float],
        pore_pressure_series: List[float],
        tilt_series: List[float],
        displacement_series: List[float],
        time_step_hours: float = 1.0
    ) -> Dict[str, float]:
        """
        Computes dynamic derivative and trend metrics from hourly telemetry series.
        """
        # 1. Rainfall Dynamics
        r_arr = np.array(rainfall_series, dtype=np.float32) if rainfall_series else np.zeros(24, dtype=np.float32)
        n_steps = len(r_arr)

        r_1h = float(r_arr[-1]) if n_steps >= 1 else 0.0
        r_3h = float(np.sum(r_arr[-3:])) if n_steps >= 3 else r_1h * 3.0
        r_6h = float(np.sum(r_arr[-6:])) if n_steps >= 6 else r_3h * 2.0
        r_12h = float(np.sum(r_arr[-12:])) if n_steps >= 12 else r_6h * 2.0
        r_24h = float(np.sum(r_arr[-24:])) if n_steps >= 24 else r_12h * 2.0
        r_48h = float(np.sum(r_arr[-48:])) if n_steps >= 48 else r_24h * 1.5
        r_72h = float(np.sum(r_arr[-72:])) if n_steps >= 72 else r_24h * 1.8

        intensity_3h = r_3h / 3.0
        intensity_6h = r_6h / 6.0

        # Rainfall acceleration: d(intensity)/dt
        if n_steps >= 6:
            prev_intensity_3h = float(np.sum(r_arr[-6:-3])) / 3.0
            accel = (intensity_3h - prev_intensity_3h) / 3.0
        else:
            accel = 0.0

        # 2. Soil Moisture Trend
        sm_arr = np.array(soil_moisture_series, dtype=np.float32) if soil_moisture_series else np.array([0.35], dtype=np.float32)
        sm_curr = float(sm_arr[-1])
        sm_trend_24h = float(sm_curr - sm_arr[0]) if len(sm_arr) >= 2 else 0.0

        # 3. Pore-Water Pressure Dynamics
        pp_arr = np.array(pore_pressure_series, dtype=np.float32) if pore_pressure_series else np.array([8.5], dtype=np.float32)
        pp_curr = float(pp_arr[-1])
        pp_trend_24h = float(pp_curr - pp_arr[0]) if len(pp_arr) >= 2 else 0.0

        # 4. Inclinometer Tilt & Ground Displacement
        tilt_arr = np.array(tilt_series, dtype=np.float32) if tilt_series else np.array([0.45], dtype=np.float32)
        tilt_curr = float(tilt_arr[-1])
        tilt_rate_24h = float(tilt_curr - tilt_arr[0]) if len(tilt_arr) >= 2 else 0.0

        disp_arr = np.array(displacement_series, dtype=np.float32) if displacement_series else np.array([1.2], dtype=np.float32)
        disp_curr = float(disp_arr[-1])
        disp_velocity_24h = float(disp_curr - disp_arr[0]) if len(disp_arr) >= 2 else 0.0

        return {
            "rainfall_1h": round(r_1h, 2),
            "rainfall_3h": round(r_3h, 2),
            "rainfall_6h": round(r_6h, 2),
            "rainfall_12h": round(r_12h, 2),
            "rainfall_24h": round(r_24h, 2),
            "rainfall_48h": round(r_48h, 2),
            "rainfall_72h": round(r_72h, 2),
            "rainfall_accumulation_3h": round(r_3h, 2),
            "rainfall_intensity_3h": round(intensity_3h, 2),
            "rainfall_intensity_6h": round(intensity_6h, 2),
            "rainfall_acceleration": round(accel, 3),
            "soil_moisture": round(sm_curr, 3),
            "soil_moisture_trend_24h": round(sm_trend_24h, 3),
            "pore_pressure": round(pp_curr, 2),
            "pore_pressure_trend_24h": round(pp_trend_24h, 2),
            "tilt": round(tilt_curr, 3),
            "tilt_rate_24h": round(tilt_rate_24h, 3),
            "ground_displacement": round(disp_curr, 2),
            "displacement_velocity_24h": round(disp_velocity_24h, 2)
        }


if TORCH_AVAILABLE:
    class PahadLSTMSequenceClassifier(nn.Module):
        """
        Bidirectional LSTM / GRU sequence classifier for multi-step temporal predictions.
        Reserved for operational phase when N_events > 500.
        """
        def __init__(self, input_dim: int = 12, hidden_dim: int = 32, num_layers: int = 2, dropout: float = 0.2):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=input_dim,
                hidden_size=hidden_dim,
                num_layers=num_layers,
                batch_first=True,
                bidirectional=True,
                dropout=dropout if num_layers > 1 else 0.0
            )
            self.fc = nn.Sequential(
                nn.Linear(hidden_dim * 2, 16),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(16, 1),
                nn.Sigmoid()
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out, _ = self.lstm(x)
            last_step = out[:, -1, :]
            prob = self.fc(last_step)
            return prob
else:
    class PahadLSTMSequenceClassifier:
        """Stub when PyTorch is not loaded."""
        pass


class TemporalModelRegistry:
    """
    Tracks operational temporal model state in accordance with Section 6 of the constitution:
      - Marks deep learning sequence architecture as NOT_TRAINED when sample size is limited.
      - Dispatches temporal features to calibrated GBDT baseline.
    """
    def __init__(self):
        self.status = "NOT_TRAINED"
        self.reason = "Historical event sample size (N < 500) insufficient for deep PyTorch LSTM training without overfitting."
        self.active_inference_backend = "CALIBRATED_GRADIENT_BOOSTING"

    def get_status(self) -> Dict[str, Any]:
        return {
            "model_type": "PyTorch BiLSTM Sequence Classifier",
            "status": self.status,
            "torch_available": TORCH_AVAILABLE,
            "reason": self.reason,
            "active_inference_backend": self.active_inference_backend,
            "temporal_feature_windows": ["1h", "3h", "6h", "12h", "24h", "48h", "72h"],
            "provenance": "[HISTORICAL+SIMULATED]"
        }


TEMPORAL_MODEL_REGISTRY = TemporalModelRegistry()
