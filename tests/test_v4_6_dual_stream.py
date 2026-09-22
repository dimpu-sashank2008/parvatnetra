# -*- coding: utf-8 -*-
"""
tests/test_v4_6_dual_stream.py
==============================
Phase V4.6 Test Suite: Dual-Stream Decoupled Inference, Kinematic Triggers & Production Immutability
"""

import os
import hashlib
from datetime import datetime, timezone, timedelta
import pytest

from engine.kinematic_trigger_engine import (
    KinematicTriggerEngine,
    CANONICAL_THRESHOLDS,
    VAL_STATUS_ENGINEERING_DEFAULT,
    STATE_KINEMATIC_NORMAL,
    STATE_KINEMATIC_WATCH,
    STATE_KINEMATIC_ELEVATED,
    STATE_KINEMATIC_CRITICAL,
    STATE_KINEMATIC_UNAVAILABLE
)
from engine.dual_stream_fusion import (
    DualStreamFusionEngine,
    GLOBAL_DUAL_STREAM_ENGINE
)
from services.kinematic_telemetry_service import KinematicTelemetryService, CORRIDOR_ID_NH10


class TestKinematicTriggerEngine:
    """Tests multi-parameter geotechnical triggers and engineering default validation."""

    def test_thresholds_have_engineering_default_validation(self):
        engine = KinematicTriggerEngine()
        for t in engine.thresholds:
            assert t.validation_status == VAL_STATUS_ENGINEERING_DEFAULT
            assert t.threshold_value > 0

    def test_trigger_eval_when_telemetry_unavailable(self):
        engine = KinematicTriggerEngine()
        empty_features = {
            "corridor_id": CORRIDOR_ID_NH10,
            "corridor_telemetry_status": "UNAVAILABLE",
            "field_deployment_pending": True,
            "sensors": {}
        }
        res = engine.evaluate_features(empty_features)
        assert res["kinematic_state"] == STATE_KINEMATIC_UNAVAILABLE
        assert res["reason"] == "PHYSICAL_TELEMETRY_PENDING"
        assert res["public_dispatch"] is False
        assert res["human_authorization_required"] is True

    def test_trigger_elevated_on_pore_pressure_spike(self):
        engine = KinematicTriggerEngine()
        active_features = {
            "corridor_id": CORRIDOR_ID_NH10,
            "corridor_telemetry_status": "LIVE",
            "field_deployment_pending": False,
            "sensors": {
                "PIEZO-01": {
                    "sensor_type": "PIEZOMETER",
                    "status": "LIVE",
                    "metrics": {
                        "pressure": 32.0,  # Exceeds 25.0 kPa threshold
                        "pressure_velocity": 4.0
                    }
                }
            }
        }
        res = engine.evaluate_features(active_features)
        assert res["kinematic_state"] == STATE_KINEMATIC_ELEVATED
        assert len(res["triggers_fired"]) >= 1
        assert res["triggers_fired"][0]["parameter"] == "pore_pressure_spike"
        assert res["public_dispatch"] is False

    def test_trigger_critical_on_shear_velocity(self):
        engine = KinematicTriggerEngine()
        active_features = {
            "corridor_id": CORRIDOR_ID_NH10,
            "corridor_telemetry_status": "LIVE",
            "field_deployment_pending": False,
            "sensors": {
                "INCL-01": {
                    "sensor_type": "INCLINOMETER",
                    "status": "LIVE",
                    "metrics": {
                        "displacement": 8.5,
                        "velocity": 3.2  # Exceeds 2.0 mm/h CRITICAL limit
                    }
                }
            }
        }
        res = engine.evaluate_features(active_features)
        assert res["kinematic_state"] == STATE_KINEMATIC_CRITICAL
        assert res["critical_triggers_count"] >= 1
        assert res["public_dispatch"] is False


class TestDualStreamDecoupling:
    """Tests architectural decoupling and fail-closed degradation."""

    def test_streams_are_decoupled(self):
        fusion = DualStreamFusionEngine()
        res = fusion.evaluate_corridor(CORRIDOR_ID_NH10)

        assert "stream_a_regional" in res
        assert "stream_b_kinematic" in res
        assert "assessment" in res

        # Verify Stream A has synoptic horizons
        stream_a = res["stream_a_regional"]
        assert "24h" in stream_a["horizons"]
        assert "48h" in stream_a["horizons"]
        assert "72h" in stream_a["horizons"]
        assert "168h" in stream_a["horizons"]
        assert stream_a["status"] == "AVAILABLE"

        # Verify Stream B has imminent horizons
        stream_b = res["stream_b_kinematic"]
        assert "0h" in stream_b["horizons"]
        assert "1h" in stream_b["horizons"]
        assert "3h" in stream_b["horizons"]
        assert "6h" in stream_b["horizons"]

    def test_fail_closed_assessment_when_kinematic_pending(self):
        """When in-situ telemetry is pending, system degrades confidence and does NOT claim stability."""
        fusion = DualStreamFusionEngine()
        res = fusion.evaluate_corridor(CORRIDOR_ID_NH10)

        assessment = res["assessment"]
        assert assessment["mode"] == "REGIONAL_ONLY_MONITORING"
        assert assessment["system_confidence"] == "MEDIUM_DEGRADED"
        assert assessment["kinematic_coverage"] == "PENDING_FIELD_INSTALLATION"
        assert res["safety_safeguards"]["public_dispatch_enabled"] is False

    def test_dual_stream_api_endpoint(self):
        import app
        client = app.app.test_client()
        resp = client.get("/api/pahad/dual-stream-status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "SUCCESS"
        assert "data" in data
        assert data["data"]["architecture"] == "DUAL_STREAM_DECOUPLED_V4_6"

    def test_kinematic_risk_api_endpoint(self):
        import app
        client = app.app.test_client()
        resp = client.get("/api/pahad/kinematic-risk")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "SUCCESS"
        assert "features" in data
        assert "trigger_evaluation" in data


class TestProductionModelImmutability:
    """Cryptographic verification of production V3 and V4.5 research weights."""

    def test_v3_production_model_hash_unchanged(self):
        v3_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v3_weights.pt")
        assert os.path.exists(v3_path), f"V3 weights file not found at {v3_path}"
        with open(v3_path, "rb") as f:
            v3_hash = hashlib.sha256(f.read()).hexdigest()
        assert v3_hash == "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

    def test_v4_5_research_model_hash_unchanged(self):
        v4_5_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v4_5_research_weights.pt")
        assert os.path.exists(v4_5_path), f"V4.5 weights file not found at {v4_5_path}"
        with open(v4_5_path, "rb") as f:
            v4_5_hash = hashlib.sha256(f.read()).hexdigest()
        assert v4_5_hash == "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"
