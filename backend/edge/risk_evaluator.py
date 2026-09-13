# -*- coding: utf-8 -*-
"""
backend/edge/risk_evaluator.py
==============================
PARVAT NETRA • Local Edge Safety Risk Evaluator
-----------------------------------------------
Implements Section 8: Lightweight, zero-latency safety-critical heuristic
evaluation on edge gateways. Does NOT recreate the heavy cloud PAHAD AI model.
Computes deterministic multi-parameter anomaly scores and assigns an
authoritative EDGE SAFETY STATE (SAFE, WATCH, WARNING, CRITICAL).

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple


class EdgeRiskEvaluator:
    """
    Fast, deterministic safety threshold engine operating on the Edge Gateway.
    Protects mountain corridors during telecommunication blackouts.
    """

    # Conservative Geotechnical Thresholds (Eastern Himalaya Regolith Standards)
    THRESHOLDS = {
        "rainfall_mmh": {"watch": 10.0, "warning": 25.0, "critical": 45.0},
        "soil_moisture_pct": {"watch": 40.0, "warning": 48.0, "critical": 55.0},
        "pore_pressure_kpa": {"watch": 15.0, "warning": 28.0, "critical": 38.0},
        "tilt_degrees": {"watch": 0.5, "warning": 1.5, "critical": 3.0}
    }

    def __init__(self, custom_thresholds: Dict[str, Any] = None) -> None:
        self.thresholds = dict(self.THRESHOLDS)
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)

    def evaluate_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates an individual in-situ sensor reading against local safety limits.
        Returns:
          edge_safety_state: SAFE | WATCH | WARNING | CRITICAL
          anomaly_score: float [0.0 - 1.0]
          exceeded_indicators: list of specific indicator breaches
          action_recommendation: Siren / mobile dispatch action
        """
        sm = float(reading.get("soil_moisture", 0.0))
        pp = float(reading.get("pore_pressure", 0.0))
        tilt = float(reading.get("tilt", 0.0))
        rain = float(reading.get("rainfall", 0.0))

        exceeded: List[Dict[str, Any]] = []
        critical_count = 0
        warning_count = 0
        watch_count = 0

        # 1. Soil Moisture
        t_sm = self.thresholds["soil_moisture_pct"]
        if sm >= t_sm["critical"]:
            exceeded.append({"sensor": "soil_moisture", "level": "CRITICAL", "value": sm, "threshold": t_sm["critical"]})
            critical_count += 1
        elif sm >= t_sm["warning"]:
            exceeded.append({"sensor": "soil_moisture", "level": "WARNING", "value": sm, "threshold": t_sm["warning"]})
            warning_count += 1
        elif sm >= t_sm["watch"]:
            exceeded.append({"sensor": "soil_moisture", "level": "WATCH", "value": sm, "threshold": t_sm["watch"]})
            watch_count += 1

        # 2. Pore-water Pressure
        t_pp = self.thresholds["pore_pressure_kpa"]
        if pp >= t_pp["critical"]:
            exceeded.append({"sensor": "pore_pressure", "level": "CRITICAL", "value": pp, "threshold": t_pp["critical"]})
            critical_count += 1
        elif pp >= t_pp["warning"]:
            exceeded.append({"sensor": "pore_pressure", "level": "WARNING", "value": pp, "threshold": t_pp["warning"]})
            warning_count += 1
        elif pp >= t_pp["watch"]:
            exceeded.append({"sensor": "pore_pressure", "level": "WATCH", "value": pp, "threshold": t_pp["watch"]})
            watch_count += 1

        # 3. Borehole Tilt
        t_tilt = self.thresholds["tilt_degrees"]
        if tilt >= t_tilt["critical"]:
            exceeded.append({"sensor": "tilt", "level": "CRITICAL", "value": tilt, "threshold": t_tilt["critical"]})
            critical_count += 1
        elif tilt >= t_tilt["warning"]:
            exceeded.append({"sensor": "tilt", "level": "WARNING", "value": tilt, "threshold": t_tilt["warning"]})
            warning_count += 1
        elif tilt >= t_tilt["watch"]:
            exceeded.append({"sensor": "tilt", "level": "WATCH", "value": tilt, "threshold": t_tilt["watch"]})
            watch_count += 1

        # 4. Rainfall Intensity
        t_rain = self.thresholds["rainfall_mmh"]
        if rain >= t_rain["critical"]:
            exceeded.append({"sensor": "rainfall", "level": "CRITICAL", "value": rain, "threshold": t_rain["critical"]})
            critical_count += 1
        elif rain >= t_rain["warning"]:
            exceeded.append({"sensor": "rainfall", "level": "WARNING", "value": rain, "threshold": t_rain["warning"]})
            warning_count += 1
        elif rain >= t_rain["watch"]:
            exceeded.append({"sensor": "rainfall", "level": "WATCH", "value": rain, "threshold": t_rain["watch"]})
            watch_count += 1

        # Continuous Anomaly Index (Normalized 0.0 - 1.0)
        norm_sm = min(1.0, sm / 55.0)
        norm_pp = min(1.0, pp / 40.0)
        norm_tilt = min(1.0, tilt / 3.0)
        norm_rain = min(1.0, rain / 50.0)
        anomaly_score = round(0.35 * norm_sm + 0.30 * norm_pp + 0.20 * norm_tilt + 0.15 * norm_rain, 3)

        # Decision State Determination
        if critical_count >= 1 or anomaly_score >= 0.80:
            state = "CRITICAL"
            siren_action = "ACTIVATE_SIREN_EVACUATION"
            recommended_action = "IMMEDIATE_EVACUATION: Local highway closure and nearby shelter evacuation."
        elif warning_count >= 2 or (warning_count >= 1 and anomaly_score >= 0.40):
            state = "WARNING"
            siren_action = "ACOUSTIC_WARNING_CHIME"
            recommended_action = "ACOUSTIC_WARNING: Issue local warning via roadside BLE/chime. Halt heavy freight."
        elif warning_count >= 1 or watch_count >= 1 or anomaly_score >= 0.35:
            state = "WATCH"
            siren_action = "NONE"
            recommended_action = "LOCAL_WATCH: Accelerate edge sensor telemetry sampling to 10-second intervals."
        else:
            state = "SAFE"
            siren_action = "NONE"
            recommended_action = "MONITOR: Normal baseline monitoring."

        return {
            "edge_safety_state": state,
            "anomaly_score": anomaly_score,
            "critical_count": critical_count,
            "warning_count": warning_count,
            "watch_count": watch_count,
            "exceeded_indicators": exceeded,
            "recommended_siren_action": siren_action,
            "recommended_action": recommended_action,
            "action_recommendation": recommended_action,
            "timestamp": reading.get("timestamp"),
            "node_id": reading.get("node_id", "UNKNOWN"),
            "provenance": "[EDGE / LOCAL THRESHOLD DETERMINISTIC]",
            "evaluation_type": "EDGE SAFETY STATE",
            "disclaimer": "EDGE SAFETY STATE based strictly on in-situ sensor physical thresholds. Does not replace central PAHAD cloud multi-modal fusion prediction."
        }
