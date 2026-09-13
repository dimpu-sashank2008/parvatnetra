"""
engine/pahad_lstm.py
====================
PAHAD Phase 2 — Dynamic Rolling Forecast Engine
------------------------------------------------
Physics-informed LSTM surrogate for multi-horizon failure
probability estimation on the NH-10 Sikkim corridor.

Data   : [SIMULATED] NE Himalaya calibration constants
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List

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
            "provenance": "[SIMULATED] NE Himalaya LSTM surrogate v2",
            "metadata": self.metadata,
        }


class LSTMTemporalPredictor:
    """Rolling-window multi-horizon failure probability estimator."""

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
    ) -> dict:
        """Compute exceedance probabilities for 6h/12h/24h/48h windows."""
        series = [max(0.0, float(v)) for v in rainfall_series]
        if len(series) < 2:
            series = [0.0] * (2 - len(series)) + series
        am = max(0.0, min(1.0, float(antecedent_moisture)))

        am_half = self._t_half / 24.0
        saturation_fraction = am + (1.0 - am) * (
            1.0 - math.exp(-am / max(am_half, 1e-9))
        )
        saturation_fraction = min(saturation_fraction, 1.0)

        n_vel = min(6, len(series))
        recent = series[-n_vel:]
        if len(recent) > 1:
            deltas = [recent[i + 1] - recent[i] for i in range(len(recent) - 1)]
            velocity = sum(deltas) / len(deltas)
        else:
            velocity = 0.0

        mean_intensity = sum(series) / len(series) if series else 0.0
        base_p = self._sigmoid(
            mean_intensity * self._v_scale + saturation_fraction * 0.35
        )

        horizons: dict = {}
        for label, decay in _HORIZON_DECAY.items():
            if 0.0 < base_p < 1.0:
                raw = self._sigmoid(
                    math.log(base_p / (1.0 - base_p) + 1e-9) * decay
                )
            else:
                raw = base_p
            horizons[label] = round(max(0.0, min(1.0, raw)), 4)

        peak_window = max(horizons, key=horizons.__getitem__)

        if velocity >= _TREND_RISE_THRESHOLD:
            trend = "RISING"
        elif velocity <= _TREND_FALL_THRESHOLD:
            trend = "FALLING"
        else:
            trend = "STABLE"

        result = ForecastResult(
            p_exceedance_6h=horizons["6h"],
            p_exceedance_12h=horizons["12h"],
            p_exceedance_24h=horizons["24h"],
            p_exceedance_48h=horizons["48h"],
            peak_window=peak_window,
            trend=trend,
            antecedent_saturation=round(saturation_fraction, 4),
            rainfall_velocity=round(velocity, 4),
            metadata={
                "series_length": len(series),
                "mean_intensity_mmh": round(mean_intensity, 3),
                "base_exceedance_p": round(base_p, 4),
            },
        )
        return result.to_dict()

    @staticmethod
    def _sigmoid(x: float) -> float:
        if x >= 0:
            return 1.0 / (1.0 + math.exp(-x))
        exp_x = math.exp(x)
        return exp_x / (1.0 + exp_x)
