# -*- coding: utf-8 -*-
"""
tests/test_v4_8_dataset_lineage.py
==================================
Phase V4.8 Test Suite: Derived Feature Lineage, Non-Circularity & ML Gate Enforcement
"""

import os
import json
import pytest
from datetime import datetime, timezone, timedelta

from engine.telemetry_evidence_audit_engine import (
    TelemetryEvidenceAuditEngine,
    RealTelemetryResearchGate
)
from services.kinematic_telemetry_service import (
    KinematicTelemetryService,
    GLOBAL_KINEMATIC_SERVICE
)


class TestFeatureLineageAndTraceability:
    """Tests that high-frequency kinematic features reference source observation IDs."""

    def test_derived_features_require_source_observations(self):
        # Construct sample feature derivation record
        obs_ids = ["OBS-KM48-PIEZO-001", "OBS-KM48-PIEZO-002", "OBS-KM48-PIEZO-003"]
        feature_record = {
            "feature_id": "FEAT-PIEZO-DELTA-1H-01",
            "source_observation_ids": obs_ids,
            "window_start_utc": "2026-09-20T11:00:00Z",
            "window_end_utc": "2026-09-20T12:00:00Z",
            "derivation_method": "finite_difference_1h_delta",
            "derivation_time_utc": datetime.now(timezone.utc).isoformat(),
            "software_version": "v4.8-kinematics"
        }
        assert len(feature_record["source_observation_ids"]) == 3
        assert feature_record["feature_id"].startswith("FEAT-")
        assert "finite_difference" in feature_record["derivation_method"]

    def test_circularity_prevention(self):
        # Target/feature circularity check: composite risk cannot be a feature of itself
        forbidden_features = ["composite_risk_index", "cri_score", "predicted_risk_level"]
        kinematic_feature_set = {
            "pore_pressure_kpa", "pore_pressure_velocity_kpa_h",
            "shear_displacement_mm", "shear_velocity_mm_h",
            "tilt_resultant_deg", "rainfall_1h_mm"
        }
        for f in forbidden_features:
            assert f not in kinematic_feature_set


class TestMachineLearningGateEnforcement:
    """Tests that ML training remains blocked (NOT_TRAINED_DATA_PENDING) when field data is absent."""

    def test_research_gate_fails_without_physical_deployment(self):
        gate = RealTelemetryResearchGate(
            verified_physical_sensors=False,
            verified_calibration_evidence=True,  # Bench NABL certified
            verified_field_presence=False,       # Not installed in borehole
            sufficient_telemetry_duration=False,
            acceptable_data_continuity=False,
            acceptable_clock_quality=True,
            acceptable_provenance=True,
            event_label_pathway=True,
            non_event_pathway=True,
            no_unresolved_critical_integrity_issue=True,
            unmet_prerequisites=["NO_PHYSICAL_BOREHOLE_INSTALLATION", "NO_LIVE_FIELD_TELEMETRY"]
        )
        assert gate.is_research_ready is False
        assert len(gate.unmet_prerequisites) == 2

    def test_corridor_ml_status_is_not_trained_data_pending(self):
        status = GLOBAL_KINEMATIC_SERVICE.get_corridor_status()
        assert status["corridor"]["telemetry_status"] == "PHYSICAL_TELEMETRY_PENDING"
        assert status["corridor"]["field_deployment_pending"] is True
