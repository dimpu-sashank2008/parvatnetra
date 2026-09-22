# -*- coding: utf-8 -*-
"""
engine/kinematic_trigger_engine.py
==================================
PARVAT NETRA • Multi-Parameter Geotechnical Kinematic Trigger Engine
--------------------------------------------------------------------
Phase V4.6 Multi-sensor kinematic trigger evaluation engine.
Evaluates high-frequency in-situ telemetry against physics-informed
engineering thresholds:
1. Pore pressure spike (> 25.0 kPa)
2. Rate of pore pressure rise (> 10.0 kPa/h)
3. Tilt rate / acceleration (> 0.5 deg/h or > 0.2 deg/h^2)
4. Borehole shear displacement velocity (> 2.0 mm/h)
5. Rainfall rate intensity (> 30.0 mm/h)

All thresholds carry explicit validation status: ENGINEERING_DEFAULT.
Autonomous public dispatch is strictly disabled (public_dispatch: false).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("KINEMATIC_TRIGGER")

# Validation status constants
VAL_STATUS_ENGINEERING_DEFAULT = "ENGINEERING_DEFAULT"
VAL_STATUS_SITE_CALIBRATED = "SITE_CALIBRATED"
VAL_STATUS_NOT_VALIDATED = "NOT_VALIDATED"

# State constants
STATE_KINEMATIC_NORMAL = "KINEMATIC_NORMAL"
STATE_KINEMATIC_WATCH = "KINEMATIC_WATCH"
STATE_KINEMATIC_ELEVATED = "KINEMATIC_ELEVATED"
STATE_KINEMATIC_CRITICAL = "KINEMATIC_CRITICAL"
STATE_KINEMATIC_UNAVAILABLE = "KINEMATIC_UNAVAILABLE"


@dataclass
class TriggerThreshold:
    parameter: str
    threshold_value: float
    unit: str
    comparison: str  # "GT" or "LT"
    severity: str    # "WATCH", "ELEVATED", "CRITICAL"
    validation_status: str = VAL_STATUS_ENGINEERING_DEFAULT
    description: str = ""

    def evaluate(self, current_value: Optional[float]) -> bool:
        if current_value is None:
            return False
        if self.comparison == "GT":
            return current_value > self.threshold_value
        elif self.comparison == "LT":
            return current_value < self.threshold_value
        return False


# Canonical Phase V4.6 Threshold Catalog (Engineering Defaults)
CANONICAL_THRESHOLDS: List[TriggerThreshold] = [
    # Pore Pressure
    TriggerThreshold(
        parameter="pore_pressure_spike",
        threshold_value=25.0,
        unit="kPa",
        comparison="GT",
        severity="ELEVATED",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Piezometer pore water pressure exceeds 25 kPa threshold"
    ),
    TriggerThreshold(
        parameter="pore_pressure_critical",
        threshold_value=40.0,
        unit="kPa",
        comparison="GT",
        severity="CRITICAL",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Piezometer pore water pressure exceeds 40 kPa critical limit"
    ),
    TriggerThreshold(
        parameter="pore_pressure_velocity",
        threshold_value=10.0,
        unit="kPa/h",
        comparison="GT",
        severity="ELEVATED",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Pore water pressure rising faster than 10 kPa per hour"
    ),
    # Inclinometer Shear Displacement
    TriggerThreshold(
        parameter="shear_displacement_velocity",
        threshold_value=2.0,
        unit="mm/h",
        comparison="GT",
        severity="CRITICAL",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Borehole shear displacement velocity exceeds 2.0 mm/h"
    ),
    TriggerThreshold(
        parameter="shear_displacement_watch",
        threshold_value=0.8,
        unit="mm/h",
        comparison="GT",
        severity="WATCH",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Borehole shear displacement velocity exceeds 0.8 mm/h"
    ),
    # Surface Tilt
    TriggerThreshold(
        parameter="tilt_rate",
        threshold_value=0.5,
        unit="deg/h",
        comparison="GT",
        severity="ELEVATED",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Surface tilt rate exceeds 0.5 degrees per hour"
    ),
    TriggerThreshold(
        parameter="tilt_acceleration",
        threshold_value=0.2,
        unit="deg/h^2",
        comparison="GT",
        severity="CRITICAL",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Surface tilt acceleration exceeds 0.2 deg/h^2"
    ),
    # Local Rainfall
    TriggerThreshold(
        parameter="rainfall_intensity_spike",
        threshold_value=30.0,
        unit="mm/h",
        comparison="GT",
        severity="ELEVATED",
        validation_status=VAL_STATUS_ENGINEERING_DEFAULT,
        description="Local rain gauge intensity exceeds 30 mm/h"
    )
]


class KinematicTriggerEngine:
    """
    Evaluates in-situ kinematic telemetry features to produce explainable
    geotechnical advisory trigger states.
    """

    def __init__(self, thresholds: Optional[List[TriggerThreshold]] = None):
        self.thresholds = thresholds or list(CANONICAL_THRESHOLDS)

    def evaluate_features(self, kinematic_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes output from KinematicTelemetryService.compute_kinematic_features()
        and evaluates multi-parameter kinematic triggers.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        corridor_id = kinematic_features.get("corridor_id", "CORR-NH10-SIKKIM-KM48")
        corridor_status = kinematic_features.get("corridor_telemetry_status", "UNAVAILABLE")
        is_pending = kinematic_features.get("field_deployment_pending", True)

        # Check if telemetry is unavailable
        if corridor_status == "UNAVAILABLE" or is_pending:
            # Check if any sensor actually has data despite status
            sensors = kinematic_features.get("sensors", {})
            has_data = any(s.get("metrics") is not None for s in sensors.values())
            if not has_data:
                return {
                    "corridor_id": corridor_id,
                    "evaluated_at_utc": now_iso,
                    "kinematic_state": STATE_KINEMATIC_UNAVAILABLE,
                    "reason": "PHYSICAL_TELEMETRY_PENDING" if is_pending else "ALL_SENSORS_OFFLINE",
                    "triggers_fired": [],
                    "critical_triggers_count": 0,
                    "elevated_triggers_count": 0,
                    "watch_triggers_count": 0,
                    "advisory": "Physical telemetry pending slope installation. Rely on Stream A regional synoptic forecasts.",
                    "public_dispatch": False,
                    "human_authorization_required": True,
                    "thresholds_metadata": [asdict(t) for t in self.thresholds]
                }

        # Telemetry is available - evaluate metrics
        sensors = kinematic_features.get("sensors", {})
        fired_triggers: List[Dict[str, Any]] = []

        # Extract values for threshold checks
        # Piezometer metrics
        piezo_metrics = {}
        for s in sensors.values():
            if s.get("sensor_type") == "PIEZOMETER" and s.get("metrics"):
                piezo_metrics = s["metrics"]
                break

        # Inclinometer metrics
        incl_metrics = {}
        for s in sensors.values():
            if s.get("sensor_type") == "INCLINOMETER" and s.get("metrics"):
                incl_metrics = s["metrics"]
                break

        # Tiltmeter metrics
        tilt_metrics = {}
        for s in sensors.values():
            if s.get("sensor_type") == "TILTMETER" and s.get("metrics"):
                tilt_metrics = s["metrics"]
                break

        # Rain gauge metrics
        rain_metrics = {}
        for s in sensors.values():
            if s.get("sensor_type") == "RAIN_GAUGE" and s.get("metrics"):
                rain_metrics = s["metrics"]
                break

        # Check each threshold
        for t in self.thresholds:
            val = None
            if t.parameter == "pore_pressure_spike" or t.parameter == "pore_pressure_critical":
                val = piezo_metrics.get("pressure")
            elif t.parameter == "pore_pressure_velocity":
                val = piezo_metrics.get("pressure_velocity")
            elif t.parameter == "shear_displacement_velocity" or t.parameter == "shear_displacement_watch":
                val = incl_metrics.get("velocity")
            elif t.parameter == "tilt_rate":
                val = tilt_metrics.get("tilt_rate")
            elif t.parameter == "tilt_acceleration":
                val = tilt_metrics.get("tilt_acceleration")
            elif t.parameter == "rainfall_intensity_spike":
                val = rain_metrics.get("rainfall_intensity")

            if t.evaluate(val):
                fired_triggers.append({
                    "parameter": t.parameter,
                    "severity": t.severity,
                    "threshold_value": t.threshold_value,
                    "observed_value": val,
                    "unit": t.unit,
                    "validation_status": t.validation_status,
                    "description": t.description
                })

        crit_count = sum(1 for f in fired_triggers if f["severity"] == "CRITICAL")
        elev_count = sum(1 for f in fired_triggers if f["severity"] == "ELEVATED")
        watch_count = sum(1 for f in fired_triggers if f["severity"] == "WATCH")

        if crit_count >= 1 or elev_count >= 2:
            state = STATE_KINEMATIC_CRITICAL
            advisory = "CRITICAL KINEMATIC ANOMALY: Immediate BRO/SDRF site inspection recommended. Road corridor alert advisory."
        elif elev_count >= 1 or watch_count >= 2:
            state = STATE_KINEMATIC_ELEVATED
            advisory = "ELEVATED KINEMATIC SIGNAL: Accelerating pore pressure or displacement detected. Heightened watch active."
        elif watch_count >= 1:
            state = STATE_KINEMATIC_WATCH
            advisory = "KINEMATIC WATCH: Minor localized kinematic deviation observed. Continuous sampling active."
        else:
            state = STATE_KINEMATIC_NORMAL
            advisory = "KINEMATIC STABLE: All monitored geotechnical and hydrometric parameters within normal engineering baselines."

        return {
            "corridor_id": corridor_id,
            "evaluated_at_utc": now_iso,
            "kinematic_state": state,
            "reason": "ACTIVE_TELEMETRY_EVALUATION",
            "triggers_fired": fired_triggers,
            "critical_triggers_count": crit_count,
            "elevated_triggers_count": elev_count,
            "watch_triggers_count": watch_count,
            "advisory": advisory,
            "public_dispatch": False,
            "human_authorization_required": True,
            "thresholds_metadata": [asdict(t) for t in self.thresholds]
        }


# Global singleton engine
GLOBAL_KINEMATIC_TRIGGER_ENGINE = KinematicTriggerEngine()
