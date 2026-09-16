# -*- coding: utf-8 -*-
"""
tests/test_phase12b_readiness_gate.py
======================================
PARVAT NETRA • PAHAD AI — Phase 12B Training Readiness Gate Automated Tests
"""

import os
import pytest
from engine.pahad_temporal_gate import (
    PahadTemporalGate,
    TemporalReadinessError,
    GateStatus,
    PROJECT_TARGETS,
)


@pytest.fixture
def client():
    """Create test client for Flask app."""
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_project_targets_specification():
    """Verify that project targets are well-formed and meet Himalayan corridor criteria."""
    required_keys = [
        "event_sequence_volume",
        "control_sequence_volume",
        "minimum_sequence_duration_hours",
        "cadence_in_situ_minutes",
        "cadence_rainfall_hours",
        "seasonal_coverage_monsoons",
        "data_completeness_pct",
        "timestamp_confidence_seconds",
    ]
    for key in required_keys:
        assert key in PROJECT_TARGETS, f"Missing project target: {key}"
        assert "target" in PROJECT_TARGETS[key]
        assert "unit" in PROJECT_TARGETS[key]
        assert "rationale" in PROJECT_TARGETS[key]

    assert PROJECT_TARGETS["event_sequence_volume"]["target"] == 500
    assert PROJECT_TARGETS["control_sequence_volume"]["target"] == 2000
    assert PROJECT_TARGETS["minimum_sequence_duration_hours"]["target"] == 48.0
    assert PROJECT_TARGETS["cadence_in_situ_minutes"]["target"] == 15.0
    assert PROJECT_TARGETS["seasonal_coverage_monsoons"]["target"] == 2
    assert PROJECT_TARGETS["data_completeness_pct"]["target"] == 95.0


def test_evaluate_readiness_unmet_targets():
    """Verify that evaluate_readiness rejects training when targets are not met."""
    res = PahadTemporalGate.evaluate_readiness(
        total_continuous_event_seqs=10,
        total_continuous_ctrl_seqs=50,
        min_sequence_duration_hours=24.0,
        mean_cadence_minutes=60.0,
        seasonal_monsoons_covered=1,
        data_completeness_pct=80.0,
        has_real_sensor_telemetry=False,
    )
    assert res["gate_status"] == GateStatus.DATA_COLLECTION_REQUIRED.value
    assert res["training_authorized"] is False
    assert res["recommended_action"] == "KEEP_SURROGATE_CONTINUE_TELEMETRY_DEPLOYMENT"
    assert res["checks"]["event_volume_satisfied"] is False
    assert res["checks"]["control_volume_satisfied"] is False
    assert res["checks"]["real_telemetry_present"] is False


def test_evaluate_readiness_met_targets():
    """Verify that evaluate_readiness authorizes training when all targets are met."""
    res = PahadTemporalGate.evaluate_readiness(
        total_continuous_event_seqs=550,
        total_continuous_ctrl_seqs=2200,
        min_sequence_duration_hours=72.0,
        mean_cadence_minutes=15.0,
        seasonal_monsoons_covered=2,
        data_completeness_pct=98.0,
        has_real_sensor_telemetry=True,
    )
    assert res["gate_status"] == GateStatus.TRAINING_ELIGIBLE.value
    assert res["training_authorized"] is True
    assert res["recommended_action"] == "AUTHORIZE_RESEARCH_LSTM_TRAINING"
    assert all(res["checks"].values())


def test_evaluate_current_repository():
    """Verify that the current repository strictly evaluates to DATA_COLLECTION_REQUIRED."""
    res = PahadTemporalGate.evaluate_current_repository()
    assert res["gate_status"] == GateStatus.DATA_COLLECTION_REQUIRED.value
    assert res["training_authorized"] is False
    assert res["model_status"] == "NOT_TRAINED"
    assert "Surrogate" in res["active_temporal_model"]
    assert res["actual_vs_target"]["event_sequences"]["actual"] == 0
    assert res["actual_vs_target"]["control_sequences"]["actual"] == 0
    assert res["actual_vs_target"]["real_telemetry"]["status"] == "FAIL"


def test_enforce_training_guard_raises_error():
    """Verify that enforce_training_guard raises TemporalReadinessError on current repo."""
    old_demo = os.environ.get("PAHAD_DEMO_MODE")
    if "PAHAD_DEMO_MODE" in os.environ:
        del os.environ["PAHAD_DEMO_MODE"]

    try:
        with pytest.raises(TemporalReadinessError) as exc_info:
            PahadTemporalGate.enforce_training_guard()
        assert "TRAINING REFUSED" in str(exc_info.value)
        assert "DATA_COLLECTION_REQUIRED" in str(exc_info.value)
    finally:
        if old_demo is not None:
            os.environ["PAHAD_DEMO_MODE"] = old_demo


def test_enforce_training_guard_demo_override():
    """Verify that demo override allows execution only when PAHAD_DEMO_MODE=1."""
    old_demo = os.environ.get("PAHAD_DEMO_MODE")
    os.environ["PAHAD_DEMO_MODE"] = "1"
    try:
        PahadTemporalGate.enforce_training_guard(allow_demo_override=True)
    finally:
        if old_demo is not None:
            os.environ["PAHAD_DEMO_MODE"] = old_demo
        else:
            del os.environ["PAHAD_DEMO_MODE"]


def test_temporal_readiness_api_endpoint(client):
    """Test Flask API endpoint GET /api/pahad/temporal/readiness."""
    resp = client.get("/api/pahad/temporal/readiness")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["gate_status"] == "DATA_COLLECTION_REQUIRED"
    assert data["training_authorized"] is False
    assert data["model_status"] == "NOT_TRAINED"
    assert "actual_vs_target" in data
    assert data["actual_vs_target"]["event_sequences"]["target"] == 500


def test_temporal_readiness_alias_endpoint(client):
    """Test Flask API alias GET /api/pahad/training-readiness."""
    resp = client.get("/api/pahad/training-readiness")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["gate_status"] == "DATA_COLLECTION_REQUIRED"
