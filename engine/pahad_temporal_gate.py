# -*- coding: utf-8 -*-
"""
engine/pahad_temporal_gate.py
==============================
PARVAT NETRA • PAHAD AI — Training Eligibility Gate for Temporal Deep Learning
-------------------------------------------------------------------------------
Enforces Phase 12B strict criteria and gates recurrent neural network (LSTM/GRU/TCN)
training against rigorous, scientifically defensible PROJECT TARGETS.

Gate Status Taxonomy:
  - KEEP_SURROGATE: Maintain analytical physics surrogate (default state when data < target)
  - DATA_COLLECTION_REQUIRED: Formal gate verdict when real sequences < minimum requirements
  - TRAINING_ELIGIBLE: All sample volume, cadence, and completeness targets met for research training
  - VALIDATION_REQUIRED: Trained model awaiting independent multi-basin temporal validation
  - PRODUCTION_ELIGIBLE: Audited model certified for live operational early-warning inference

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Standard: SIH 26001 / Project Constitution Section 12 & 32
"""

from __future__ import annotations

import os
import json
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("PAHAD_TEMPORAL_GATE")


class GateStatus(str, Enum):
    """Formal training eligibility gate verdicts."""
    KEEP_SURROGATE = "KEEP_SURROGATE"
    DATA_COLLECTION_REQUIRED = "DATA_COLLECTION_REQUIRED"
    TRAINING_ELIGIBLE = "TRAINING_ELIGIBLE"
    VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
    PRODUCTION_ELIGIBLE = "PRODUCTION_ELIGIBLE"


class TemporalReadinessError(RuntimeError):
    """Raised when deep sequence model training is requested without meeting eligibility criteria."""
    pass


# ==============================================================================
# EXPLICIT PROJECT TARGET SPECIFICATION (Himalayan Corridor Standard)
# ==============================================================================
# These are project-specific engineering thresholds justified by geotechnical
# and statistical learning mechanics, not arbitrary universal constants.
PROJECT_TARGETS: Dict[str, Any] = {
    "event_sequence_volume": {
        "target": 500,
        "unit": "independent failure sequences",
        "rationale": (
            "A standard 2-layer Bidirectional LSTM network with 26 physical features contains "
            "~25,000 trainable parameters. Optimizing this parameter space without severe "
            "over-parameterization requires at least 500 distinct failure events across the 8 NER states."
        )
    },
    "control_sequence_volume": {
        "target": 2000,
        "unit": "independent non-event control sequences",
        "rationale": (
            "Mountain slopes in Northeast India are stable during 99%+ of rain hours. Training on "
            "balanced data produces false-alarm rates > 80%. A 1:4 event-to-control ratio is the "
            "minimum required for defensible early-warning discrimination."
        )
    },
    "minimum_sequence_duration_hours": {
        "target": 48.0,
        "unit": "contiguous hours per sequence",
        "rationale": (
            "Himalayan regolith saturation and basal pore-water pressure respond to antecedent rainfall "
            "on a 24h to 72h lag. Sequences shorter than 48h truncate the hydrological accumulation phase."
        )
    },
    "cadence_in_situ_minutes": {
        "target": 15.0,
        "unit": "minutes between consecutive readings",
        "rationale": (
            "Tertiary creep shear acceleration and sudden pore-pressure dissipation leading to slope failure "
            "occur rapidly within 15-30 minutes. Coarser 24h snapshots fail to capture precursor velocity spikes."
        )
    },
    "cadence_rainfall_hours": {
        "target": 1.0,
        "unit": "hour per rainfall accumulation step",
        "rationale": (
            "Cloudburst and high-intensity convective rainfall pulses trigger shallow mudflows within 1 to 3 hours. "
            "Hourly accumulation is required to resolve intensity thresholds."
        )
    },
    "seasonal_coverage_monsoons": {
        "target": 2,
        "unit": "complete monsoon cycles (min 24 contiguous months)",
        "rationale": (
            "Captures inter-annual Southwest monsoon variability (El Nino / La Nina modulation) "
            "and prevents catastrophic distribution shift when deployed across varying dry and wet seasons."
        )
    },
    "data_completeness_pct": {
        "target": 95.0,
        "unit": "percentage observed without imputation",
        "rationale": (
            "Synthetic or spline imputation of missing sensor packets in temporal sequences distorts "
            "higher-order derivatives (acceleration, tilt rates) that serve as critical failure predictors."
        )
    },
    "timestamp_confidence_seconds": {
        "target": 15.0,
        "unit": "maximum allowable timestamp uncertainty",
        "rationale": (
            "Required to accurately synchronize high-frequency seismic P-wave / S-wave rumble with "
            "piezometric and displacement spikes during co-seismic or rain-induced mass wasting."
        )
    }
}


class PahadTemporalGate:
    """
    Automated gate that inspects available temporal datasets and determines
    whether deep neural network sequence training is scientifically authorized.
    """

    @classmethod
    def evaluate_readiness(
        cls,
        total_continuous_event_seqs: int = 0,
        total_continuous_ctrl_seqs: int = 0,
        min_sequence_duration_hours: float = 0.0,
        mean_cadence_minutes: float = 1440.0,  # 24h for discrete snapshots
        seasonal_monsoons_covered: int = 0,
        data_completeness_pct: float = 0.0,
        has_real_sensor_telemetry: bool = False
    ) -> Dict[str, Any]:
        """Evaluates candidate data statistics against PROJECT TARGETS."""

        checks = {
            "event_volume_satisfied": bool(total_continuous_event_seqs >= PROJECT_TARGETS["event_sequence_volume"]["target"]),
            "control_volume_satisfied": bool(total_continuous_ctrl_seqs >= PROJECT_TARGETS["control_sequence_volume"]["target"]),
            "duration_satisfied": bool(min_sequence_duration_hours >= PROJECT_TARGETS["minimum_sequence_duration_hours"]["target"]),
            "cadence_satisfied": bool(mean_cadence_minutes <= PROJECT_TARGETS["cadence_in_situ_minutes"]["target"]),
            "seasonal_coverage_satisfied": bool(seasonal_monsoons_covered >= PROJECT_TARGETS["seasonal_coverage_monsoons"]["target"]),
            "completeness_satisfied": bool(data_completeness_pct >= PROJECT_TARGETS["data_completeness_pct"]["target"]),
            "real_telemetry_present": bool(has_real_sensor_telemetry)
        }

        all_passed = all(checks.values())

        if all_passed:
            gate_status = GateStatus.TRAINING_ELIGIBLE
            recommended_action = "AUTHORIZE_RESEARCH_LSTM_TRAINING"
        else:
            gate_status = GateStatus.DATA_COLLECTION_REQUIRED
            recommended_action = "KEEP_SURROGATE_CONTINUE_TELEMETRY_DEPLOYMENT"

        return {
            "gate_status": gate_status.value,
            "training_authorized": all_passed,
            "recommended_action": recommended_action,
            "active_temporal_model": "PAHAD LSTM (Physics-Informed Surrogate v2)",
            "model_status": "NOT_TRAINED",
            "checks": checks,
            "actual_vs_target": {
                "event_sequences": {
                    "actual": total_continuous_event_seqs,
                    "target": PROJECT_TARGETS["event_sequence_volume"]["target"],
                    "status": "PASS" if checks["event_volume_satisfied"] else "FAIL"
                },
                "control_sequences": {
                    "actual": total_continuous_ctrl_seqs,
                    "target": PROJECT_TARGETS["control_sequence_volume"]["target"],
                    "status": "PASS" if checks["control_volume_satisfied"] else "FAIL"
                },
                "min_duration_hours": {
                    "actual": min_sequence_duration_hours,
                    "target": PROJECT_TARGETS["minimum_sequence_duration_hours"]["target"],
                    "status": "PASS" if checks["duration_satisfied"] else "FAIL"
                },
                "cadence_minutes": {
                    "actual": mean_cadence_minutes,
                    "target": PROJECT_TARGETS["cadence_in_situ_minutes"]["target"],
                    "status": "PASS" if checks["cadence_satisfied"] else "FAIL"
                },
                "seasonal_monsoons": {
                    "actual": seasonal_monsoons_covered,
                    "target": PROJECT_TARGETS["seasonal_coverage_monsoons"]["target"],
                    "status": "PASS" if checks["seasonal_coverage_satisfied"] else "FAIL"
                },
                "completeness_pct": {
                    "actual": data_completeness_pct,
                    "target": PROJECT_TARGETS["data_completeness_pct"]["target"],
                    "status": "PASS" if checks["completeness_satisfied"] else "FAIL"
                },
                "real_telemetry": {
                    "actual": "PRESENT" if has_real_sensor_telemetry else "ABSENT (Modelled Historical)",
                    "target": "PRESENT",
                    "status": "PASS" if checks["real_telemetry_present"] else "FAIL"
                }
            },
            "project_targets_specification": PROJECT_TARGETS
        }

    @classmethod
    def evaluate_current_repository(cls) -> Dict[str, Any]:
        """Evaluates the actual state of the PARVAT NETRA repository as verified in Phase 12A."""
        # Ground truth verified metrics:
        # - Continuous real event sequences = 0 (only 17 discrete 5-point snapshots)
        # - Continuous real control sequences = 0 (only 20 static control snapshots)
        # - Duration of continuous sequences = 0.0h
        # - Real sensor telemetry = False (historical sensor readings are physically reconstructed)
        return cls.evaluate_readiness(
            total_continuous_event_seqs=0,
            total_continuous_ctrl_seqs=0,
            min_sequence_duration_hours=0.0,
            mean_cadence_minutes=720.0,  # Snapshot step 12h-24h
            seasonal_monsoons_covered=0,
            data_completeness_pct=0.0,
            has_real_sensor_telemetry=False
        )

    @classmethod
    def enforce_training_guard(cls, allow_demo_override: bool = False) -> None:
        """
        Hard execution guard: throws TemporalReadinessError if called when repository
        is in DATA_COLLECTION_REQUIRED state, completely refusing execution.
        """
        res = cls.evaluate_current_repository()
        if not res["training_authorized"]:
            if allow_demo_override and os.environ.get("PAHAD_DEMO_MODE") == "1":
                logger.warning(
                    "[PAHAD GATE] Training executed in strictly isolated DEMO mode "
                    "(PAHAD_DEMO_MODE=1). Model artifacts will NOT be used for operational dispatch."
                )
                return

            failed_checks = [k for k, v in res["checks"].items() if not v]
            msg = (
                f"\n{'='*70}\n"
                f"PAHAD AI TEMPORAL GATE: TRAINING REFUSED (Status: {res['gate_status']})\n"
                f"{'='*70}\n"
                f"Scientific learning theory prohibits training deep sequence models on insufficient sample volume.\n"
                f"Failed prerequisites: {failed_checks}\n\n"
                f"Continuous Real Sequences Available : 0\n"
                f"Continuous Sequences Required (Target) : {PROJECT_TARGETS['event_sequence_volume']['target']}\n\n"
                f"Operational Status Retained: {res['active_temporal_model']}\n"
                f"Recommended Action          : {res['recommended_action']}\n"
                f"{'='*70}\n"
            )
            raise TemporalReadinessError(msg)
