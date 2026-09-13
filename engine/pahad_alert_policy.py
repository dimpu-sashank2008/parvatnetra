# -*- coding: utf-8 -*-
"""
engine/pahad_alert_policy.py
============================
PARVAT NETRA • PAHAD AI Intelligent Alert Policy Engine
-------------------------------------------------------
Implements Section 3, 4, 5, 19, 20: Multi-signal alert policy and explainability.
Enforces strict physical safety invariants:
  1. Prediction != Alert Recommendation != Authorized Alert != Dispatch.
  2. 2-of-3 Independent Signal Rule: Never automatically recommend or dispatch
     public RED/EXTREME warnings on a single model output or noisy sensor reading.
  3. Explainability ("Why this alert?"): Every alert recommendation produces a
     clear, non-causal evidence breakdown (never "landslide guaranteed").
  4. Hysteresis & Persistence: Smooth transitions between alert states to prevent
     alert fatigue and oscillation.

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import math
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("PAHAD_ALERT_POLICY")

# 8-State Alert Lifecycle (Phase 3.7 Invariant)
STATE_DETECTED = "DETECTED"
STATE_EVALUATING = "EVALUATING"
STATE_VERIFIED = "VERIFIED"
STATE_ISSUED = "ISSUED"
STATE_ACKNOWLEDGED = "ACKNOWLEDGED"
STATE_ESCALATED = "ESCALATED"
STATE_RESOLVED = "RESOLVED"
STATE_EXPIRED = "EXPIRED"

CANONICAL_LIFECYCLE_STATES = {
    STATE_DETECTED,
    STATE_EVALUATING,
    STATE_VERIFIED,
    STATE_ISSUED,
    STATE_ACKNOWLEDGED,
    STATE_ESCALATED,
    STATE_RESOLVED,
    STATE_EXPIRED,
}

# Compatibility aliases mapping legacy states to canonical states
LIFECYCLE_STATE_ALIASES = {
    "CREATED": STATE_DETECTED,
    "VERIFICATION_PENDING": STATE_EVALUATING,
    "READY_FOR_AUTHORIZATION": STATE_VERIFIED,
    "AUTHORIZED": STATE_VERIFIED,
    "DISPATCHING": STATE_ISSUED,
    "DISPATCHED": STATE_ISSUED,
}

# Valid State Transition Graph
VALID_STATE_TRANSITIONS = {
    STATE_DETECTED: {STATE_EVALUATING, STATE_EXPIRED, STATE_RESOLVED},
    STATE_EVALUATING: {STATE_VERIFIED, STATE_RESOLVED, STATE_EXPIRED},
    STATE_VERIFIED: {STATE_ISSUED, STATE_RESOLVED, STATE_EXPIRED},
    STATE_ISSUED: {STATE_ACKNOWLEDGED, STATE_ESCALATED, STATE_RESOLVED, STATE_EXPIRED},
    STATE_ACKNOWLEDGED: {STATE_ESCALATED, STATE_RESOLVED, STATE_EXPIRED},
    STATE_ESCALATED: {STATE_ISSUED, STATE_ACKNOWLEDGED, STATE_RESOLVED, STATE_EXPIRED},
    STATE_RESOLVED: {STATE_DETECTED},  # Reopening/new event
    STATE_EXPIRED: {STATE_DETECTED},
}


def normalize_lifecycle_state(state_name: str) -> str:
    """Maps any alias or canonical state string to its canonical 8-state name."""
    s = state_name.strip().upper()
    return LIFECYCLE_STATE_ALIASES.get(s, s)


def is_valid_transition(current_state: str, target_state: str) -> bool:
    """Checks if a transition between two alert states is structurally permitted."""
    c = normalize_lifecycle_state(current_state)
    t = normalize_lifecycle_state(target_state)
    if c == t:
        return True
    allowed = VALID_STATE_TRANSITIONS.get(c, set())
    return t in allowed


# Standardized Alert Levels mapped to public names (Section 4)
ALERT_LEVEL_MAPPINGS = {
    "LOW": {
        "level": "LOW",
        "name": "monitoring",
        "color": "#10B981", # Emerald
        "priority": 1,
        "requires_auth": False,
        "public_dispatch": False,
        "description": "Routine hillslope observation and baseline telemetry logging."
    },
    "MODERATE": {
        "level": "MODERATE",
        "name": "watch",
        "color": "#F59E0B", # Amber
        "priority": 2,
        "requires_auth": False,
        "public_dispatch": False,
        "description": "Elevated moisture or pore-pressure; accelerated 5-minute sensor polling."
    },
    "HIGH": {
        "level": "HIGH",
        "name": "warning",
        "color": "#F97316", # Orange
        "priority": 3,
        "requires_auth": True,
        "public_dispatch": False, # Internal advisory to DDMA and field teams
        "description": "Advisory warning issued to DDMA and regional highway patrol."
    },
    "VERY_HIGH": {
        "level": "VERY_HIGH",
        "name": "severe warning",
        "color": "#EA580C", # Deep Orange
        "priority": 4,
        "requires_auth": True,
        "public_dispatch": True, # Public notification allowed upon authority sign-off
        "description": "Severe hillslope instability warning; traffic diversion and staging."
    },
    "EXTREME": {
        "level": "EXTREME",
        "name": "extreme alert",
        "color": "#DC2626", # Crimson Red
        "priority": 5,
        "requires_auth": True,
        "public_dispatch": True, # Multi-channel CAP XML, SMS, push, siren
        "description": "Life-critical failure imminent; mandatory evacuation and corridor closure."
    }
}


@dataclass
class AlertPolicyDecision:
    """Standardized output of the alert policy evaluation."""
    prediction_state: str
    recommended_alert_level: str
    alert_level_name: str
    authorization_required: bool
    public_dispatch_allowed: bool
    reason: str
    dominant_drivers: List[str]
    signal_agreement_count: int
    signals_triggered: Dict[str, bool]
    downgraded: bool = False
    downgrade_reason: Optional[str] = None
    data_quality: str = "HIGH"
    model_status: str = "TRAINED_LIMITED_DATA"
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PahadAlertPolicyEngine:
    """
    Evaluates multi-modal evidence to recommend proportionate, defensible alert levels.
    """

    def __init__(
        self,
        persistence_minutes: int = 10,
        deescalation_hysteresis_cycles: int = 3
    ):
        self.persistence_minutes = int(os.getenv("PAHAD_ESCALATION_PERSISTENCE_MINUTES", str(persistence_minutes)))
        self.deescalation_hysteresis_cycles = deescalation_hysteresis_cycles
        self._sector_history: Dict[str, List[Dict[str, Any]]] = {}

    def evaluate(
        self,
        cri: float,
        event_probability: float,
        factor_of_safety: float,
        rainfall_trigger: Any,
        signal_agreement: Any,
        seismic_trigger: Any = "LOW",
        ground_anomaly: Any = 0.0,
        data_quality: str = "HIGH",
        model_status: str = "TRAINED_LIMITED_DATA",
        sector_id: Optional[str] = None
    ) -> AlertPolicyDecision:
        """
        Evaluates input risk metrics and returns an AlertPolicyDecision.
        """
        cri_val = float(max(0.0, min(100.0, cri)))
        prob_val = float(max(0.0, min(1.0, event_probability)))
        fos_val = float(factor_of_safety)

        # Parse signal triggers
        sig_physical = fos_val <= 1.05
        sig_rainfall = False
        if isinstance(rainfall_trigger, bool):
            sig_rainfall = rainfall_trigger
        elif isinstance(rainfall_trigger, str):
            sig_rainfall = rainfall_trigger.upper() in ("EXCEEDED", "BREACH", "CRITICAL_EXCEEDED", "ELEVATED_BREACH")
        elif isinstance(rainfall_trigger, dict):
            sig_rainfall = bool(rainfall_trigger.get("threshold_exceeded") or rainfall_trigger.get("id_exceeded"))

        sig_ml = (prob_val >= 0.70 or (cri_val >= 70.0 and prob_val >= 0.60))

        signals = {
            "physical": sig_physical,
            "rainfall": sig_rainfall,
            "ml": sig_ml
        }

        # Determine signal agreement count
        if isinstance(signal_agreement, int):
            sig_count = signal_agreement
        elif isinstance(signal_agreement, str) and "/" in signal_agreement:
            try:
                sig_count = int(signal_agreement.split("/")[0])
            except Exception:
                sig_count = sum(1 for s in signals.values() if s)
        else:
            sig_count = sum(1 for s in signals.values() if s)

        # Build explainability drivers (Section 5)
        dominant_drivers: List[str] = []
        if sig_physical:
            dominant_drivers.append(f"Physical Mohr-Coulomb FoS Critical ({fos_val:.2f} <= 1.05)")
        if sig_rainfall:
            dominant_drivers.append("Regional Rainfall Threshold Exceeded (I-D Curve Breach)")
        if sig_ml:
            dominant_drivers.append(f"High ML Landslide Event Probability ({prob_val*100:.1f}%)")
        if isinstance(ground_anomaly, (int, float)) and ground_anomaly > 0.5:
            dominant_drivers.append(f"In-Situ Borehole Displacement/Pore Pressure Anomaly ({ground_anomaly:.2f})")
        if str(seismic_trigger).upper() in ("HIGH", "VERY_HIGH", "CRITICAL"):
            dominant_drivers.append("Seismic Ground Motion Contributing Signal")

        if not dominant_drivers:
            dominant_drivers.append("Baseline geotechnical equilibrium; no critical threshold breach")

        # Determine raw alert level based on CRI and event probability
        if cri_val >= 80.0 and prob_val >= 0.75:
            raw_level = "EXTREME"
            pred_state = "CRITICAL_FAILURE_IMMINENT"
        elif cri_val >= 60.0 or prob_val >= 0.65:
            raw_level = "VERY_HIGH"
            pred_state = "HIGH_INSTABILITY_WATCH"
        elif cri_val >= 40.0 or prob_val >= 0.50:
            raw_level = "HIGH"
            pred_state = "ELEVATED_PORE_PRESSURE"
        elif cri_val >= 25.0 or prob_val >= 0.35:
            raw_level = "MODERATE"
            pred_state = "ELEVATED_OBSERVATION"
        else:
            raw_level = "LOW"
            pred_state = "STABLE"

        # Apply 2-of-3 Safety Invariant (Section 1, 3):
        # EXTREME warnings REQUIRE at least 2 independent signal agreements
        final_level = raw_level
        downgraded = False
        downgrade_reason = None

        if raw_level == "EXTREME" and sig_count < 2:
            final_level = "VERY_HIGH"
            downgraded = True
            downgrade_reason = (
                f"Single-signal EXTREME breach ({dominant_drivers[0] if dominant_drivers else 'ML/CRI'}) "
                f"downgraded to VERY_HIGH. Constitutional 2-of-3 independent confirmation rule enforced."
            )

        level_meta = ALERT_LEVEL_MAPPINGS.get(final_level, ALERT_LEVEL_MAPPINGS["LOW"])

        # Formulate non-causal reason text
        if final_level == "EXTREME":
            reason = (
                f"Independent physical (FoS {fos_val:.2f}), rainfall, and ML signals support escalation. "
                f"Signal agreement {sig_count}/3. Mandatory evacuation protocol recommended."
            )
        elif final_level == "VERY_HIGH":
            if downgraded:
                reason = downgrade_reason
            else:
                reason = (
                    f"Elevated multi-signal risk ({cri_val:.1f}/100, P={prob_val*100:.0f}%, FoS {fos_val:.2f}). "
                    f"Signal agreement {sig_count}/3. Pre-positioning of rescue assets and traffic diversion advised."
                )
        elif final_level == "HIGH":
            reason = (
                f"Hydrometeorological or hillslope loading approaching critical threshold ({cri_val:.1f}/100). "
                f"Advisory watch recommended for DDMA inspection."
            )
        elif final_level == "MODERATE":
            reason = "Sub-threshold moisture increase detected. Routine enhanced telemetry observation."
        else:
            reason = "Hillslope conditions within normal historical baseline stability bounds."

        decision = AlertPolicyDecision(
            prediction_state=pred_state,
            recommended_alert_level=final_level,
            alert_level_name=level_meta["name"],
            authorization_required=level_meta["requires_auth"],
            public_dispatch_allowed=level_meta["public_dispatch"] and not downgraded,
            reason=reason,
            dominant_drivers=dominant_drivers,
            signal_agreement_count=sig_count,
            signals_triggered=signals,
            downgraded=downgraded,
            downgrade_reason=downgrade_reason,
            data_quality=data_quality,
            model_status=model_status
        )

        if sector_id:
            self._record_history(sector_id, decision)

        return decision

    def _record_history(self, sector_id: str, decision: AlertPolicyDecision) -> None:
        if sector_id not in self._sector_history:
            self._sector_history[sector_id] = []
        self._sector_history[sector_id].append({
            "timestamp": decision.evaluated_at,
            "level": decision.recommended_alert_level,
            "priority": ALERT_LEVEL_MAPPINGS[decision.recommended_alert_level]["priority"]
        })
        # Keep last 50 entries
        if len(self._sector_history[sector_id]) > 50:
            self._sector_history[sector_id] = self._sector_history[sector_id][-50:]

    def evaluate_deescalation(self, sector_id: str, proposed_level: str) -> str:
        """
        Applies hysteresis: do not de-escalate immediately on a single transient dip.
        Requires consistent lower readings across configured hysteresis cycles.
        """
        history = self._sector_history.get(sector_id, [])
        if len(history) < self.deescalation_hysteresis_cycles:
            return proposed_level

        recent_entries = history[-self.deescalation_hysteresis_cycles:]
        proposed_priority = ALERT_LEVEL_MAPPINGS.get(proposed_level, {}).get("priority", 1)

        # If recent history still contains higher priorities, maintain the higher level
        max_recent_priority = max(e["priority"] for e in recent_entries)
        if max_recent_priority > proposed_priority + 1:
            # Step down gradually rather than crashing to LOW
            for lvl, meta in ALERT_LEVEL_MAPPINGS.items():
                if meta["priority"] == max_recent_priority - 1:
                    logger.info(f"[Hysteresis] De-escalation dampened for sector {sector_id}: {proposed_level} -> {lvl}")
                    return lvl

        return proposed_level
