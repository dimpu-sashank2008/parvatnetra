# -*- coding: utf-8 -*-
"""
tests/test_v5_0_evidence_chain.py
=================================
Phase V5.0 Test Suite: Cryptographic Evidence Chain, Dual Stream, Authority & Model Immutability
"""

import os
import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    AUTH_MISSING
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestEvidenceChain:
    """Verifies evidence custody, dual stream state, authority tokens, and ML freeze."""

    def test_production_v3_model_immutability(self, deployment_engine):
        ml = deployment_engine.verify_model_immutability()
        assert ml["production_v3_verified"] is True
        assert ml["production_v3_hash"] == "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

    def test_research_v4_5_model_immutability(self, deployment_engine):
        ml = deployment_engine.verify_model_immutability()
        assert ml["research_v4_5_verified"] is True
        assert ml["research_v4_5_hash"] == "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"

    def test_kinematic_ml_training_gate_locked(self, deployment_engine):
        ml = deployment_engine.verify_model_immutability()
        assert ml["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"
        assert ml["training_gate"] == "LOCKED_UNTIL_VERIFIED_PHYSICAL_DATA_AVAILABLE"

    def test_authority_status_missing(self, deployment_engine):
        claims = deployment_engine.audit_authority_and_claims()
        assert claims["authorization_status"] == AUTH_MISSING
        assert claims["unsupported_count"] >= 3

    def test_raw_custody_hashing_and_tamper_detection(self, deployment_engine):
        batch = deployment_engine.record_raw_telemetry_batch(
            corridor_id="CORR-NH10-SIKKIM-KM48",
            site_id="KM48",
            sensor_id="TEST-NODE-99",
            raw_payload=b"\x01\x02\x03\x04TESTPAYLOAD\xAA\xBB",
            metadata={"test": True}
        )
        assert os.path.exists(batch["payload_path"])
        assert os.path.exists(batch["manifest_path"])

        ok, msg = deployment_engine.verify_custody_integrity(batch["manifest_path"])
        assert ok is True
        assert "bit-for-bit identical" in msg

        # Tamper payload file and verify detection
        with open(batch["payload_path"], "ab") as f:
            f.write(b"TAMPER_BYTES")
        ok2, msg2 = deployment_engine.verify_custody_integrity(batch["manifest_path"])
        assert ok2 is False
        assert "TAMPER_DETECTED" in msg2

    def test_overall_verdict_authoritatively_hardware_evidence_pending(self, deployment_engine):
        v = deployment_engine.evaluate_v5_0_overall_verdict()
        assert v["overall_verdict"] == "V5_0_HARDWARE_EVIDENCE_PENDING"
        assert v["final_verdict"] == "V5_0_HARDWARE_EVIDENCE_PENDING"
