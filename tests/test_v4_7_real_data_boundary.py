# -*- coding: utf-8 -*-
"""
tests/test_v4_7_real_data_boundary.py
=====================================
Phase V4.7 Test Suite: Real vs Simulated Provenance Boundary & Model Immutability
"""

import os
import hashlib
from datetime import datetime, timezone
import pytest

from services.kinematic_telemetry_service import KinematicTelemetryService
from engine.dual_stream_fusion import DualStreamFusionEngine


class TestProvenanceBoundary:
    """Tests strict separation between LIVE, BENCH, HIL, and SIMULATED data."""

    @pytest.fixture
    def service(self, tmp_path):
        reg_file = str(tmp_path / "test_reg.json")
        with open(reg_file, "w", encoding="utf-8") as f:
            f.write('{"corridor_id":"CORR-TEST","field_deployment_pending":true,"sensors":[]}')
        return KinematicTelemetryService(registry_path=reg_file)

    def test_bench_cannot_claim_live(self, service):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": "test-obs-1",
            "sensor_id": "PIEZO-TEST",
            "corridor_id": "CORR-TEST",
            "site_id": "SITE-1",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 15.0,
            "unit": "kPa",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "LIVE",  # FRAUDULENT
            "status": "LIVE",
            "sequence_number": 1
        }
        res = service.ingest_canonical_observation(obs)
        assert res.is_valid is False
        assert res.status == "REJECTED_PROVENANCE_COUNTERFEIT"

    def test_synthetic_cannot_claim_live(self, service):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": "test-obs-2",
            "sensor_id": "INCL-TEST",
            "corridor_id": "CORR-TEST",
            "site_id": "SITE-1",
            "sensor_type": "INCLINOMETER",
            "timestamp_utc": now_iso,
            "value": 2.5,
            "unit": "mm",
            "quality": "GOOD",
            "source": "SYNTHETIC",
            "provenance": "LIVE",  # FRAUDULENT
            "status": "LIVE",
            "sequence_number": 1
        }
        res = service.ingest_canonical_observation(obs)
        assert res.is_valid is False
        assert res.status == "REJECTED_PROVENANCE_COUNTERFEIT"

    def test_kinematic_ml_state_is_not_trained_data_pending(self):
        fusion = DualStreamFusionEngine()
        res = fusion.evaluate_corridor("CORR-NH10-SIKKIM-KM48")
        stream_b = res["stream_b_kinematic"]
        assert stream_b["ml_model_status"] == "NOT_TRAINED_DATA_PENDING"


class TestCryptographicIntegrity:
    """Ensures production V3 and research V4.5 weights are 100% bit-for-bit unchanged."""

    def test_v3_production_hash_locked(self):
        v3_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v3_weights.pt")
        with open(v3_path, "rb") as f:
            v3_hash = hashlib.sha256(f.read()).hexdigest()
        assert v3_hash == "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

    def test_v4_5_research_hash_locked(self):
        v4_5_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v4_5_research_weights.pt")
        with open(v4_5_path, "rb") as f:
            v4_5_hash = hashlib.sha256(f.read()).hexdigest()
        assert v4_5_hash == "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"
