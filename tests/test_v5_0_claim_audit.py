# -*- coding: utf-8 -*-
"""
tests/test_v5_0_claim_audit.py
==============================
Phase V5.0 Test Suite: Claims Audit, Model Invariants & Authoritative Verdict
"""

import os
import hashlib
import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    VERDICT_EVIDENCE_PENDING
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestPhaseV5ClaimAuditAndVerdict:
    """Verifies claims governance, cryptographic model locking, and Phase V5.0 verdict."""

    def test_prototype_status_and_claims_demotion(self, deployment_engine):
        res = deployment_engine.audit_authority_and_claims()
        assert res["total_claims_audited"] >= 6
        assert "Smart India Hackathon" in res["system_designation"]
        assert "research and decision-support prototype" in res["system_designation"]
        assert res["unsupported_count"] >= 3

    def test_production_v3_model_hash_immutable(self, deployment_engine):
        v = deployment_engine.verify_model_immutability()
        assert v["production_v3_verified"] is True
        assert v["production_v3_hash"] == "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

    def test_research_v4_5_model_hash_immutable(self, deployment_engine):
        v = deployment_engine.verify_model_immutability()
        assert v["research_v4_5_verified"] is True
        assert v["research_v4_5_hash"] == "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"

    def test_kinematic_ml_training_gate_locked(self, deployment_engine):
        v = deployment_engine.verify_model_immutability()
        assert v["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"
        assert v["training_gate"] == "LOCKED_UNTIL_VERIFIED_PHYSICAL_DATA_AVAILABLE"

    def test_overall_v5_0_verdict_is_evidence_pending(self, deployment_engine):
        v = deployment_engine.evaluate_v5_0_overall_verdict()
        assert v["overall_verdict"] == VERDICT_EVIDENCE_PENDING
        assert v["physical_sensors_verified"] == 0
        assert v["field_installation_verified"] == 0
        assert v["field_commissioning_verified"] == 0
        assert v["live_mountain_observations"] == 0
        assert v["continuous_live_telemetry_hours"] == 0.0
        assert v["borehole_status"] == "NOT_INSTALLED"
        assert v["calibration_status"] == "CALIBRATION_EVIDENCE_MISSING"
        assert v["authority_status"] == "AUTHORIZATION_EVIDENCE_MISSING"
        assert v["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"

    def test_v5_0_deployment_status_endpoint(self):
        import app
        client = app.app.test_client()
        res = client.get("/api/telemetry/v5-0-deployment-status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert "verdict" in data["data"]
        assert data["data"]["verdict"]["overall_verdict"] == VERDICT_EVIDENCE_PENDING
        assert data["data"]["verdict"]["live_mountain_observations"] == 0
