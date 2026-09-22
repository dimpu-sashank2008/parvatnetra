# -*- coding: utf-8 -*-
"""
tests/test_v4_8_ml_training_gate.py
===================================
Automated test suite for Phase V4.8 ML Training Gate & Critical Safety Interlocks.
Tests:
  1. Default Kinematic ML status is NOT_TRAINED_DATA_PENDING.
  2. Machine-readable gate: REAL_TELEMETRY_RESEARCH_READY evaluates to False.
  3. Strict production V3 weights immutability (7cb823888646ca2b...).
  4. Strict research V4.5 weights immutability (31e16ce003cdd2c5...).
  5. Public emergency dispatch remains strictly disabled.
  6. Autonomous siren dispatch remains strictly false.
"""

import os
import hashlib
import json
import pytest
from engine.telemetry_evidence_audit_engine import (
    GLOBAL_EVIDENCE_AUDIT_ENGINE,
    TelemetryEvidenceAuditEngine
)
from engine.dual_stream_fusion import GLOBAL_DUAL_STREAM_ENGINE

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
V3_PATH = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v3_weights.pt")
EXPECTED_V3_HASH = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

V4_5_PATH = os.path.join(WORKSPACE_ROOT, "models", "pahad_lstm_v4_5_research_weights.pt")
EXPECTED_V4_5_HASH = "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_production_v3_immutability():
    """Verifies that production V3 weights are bit-for-bit identical to locked baseline."""
    assert os.path.exists(V3_PATH), f"Missing v3 weights at {V3_PATH}"
    actual_hash = compute_sha256(V3_PATH)
    assert actual_hash == EXPECTED_V3_HASH, f"V3 weights mutated! Got {actual_hash}"


def test_research_v4_5_immutability():
    """Verifies that research V4.5 weights are bit-for-bit identical to locked baseline."""
    assert os.path.exists(V4_5_PATH), f"Missing v4.5 weights at {V4_5_PATH}"
    actual_hash = compute_sha256(V4_5_PATH)
    assert actual_hash == EXPECTED_V4_5_HASH, f"V4.5 weights mutated! Got {actual_hash}"


def test_kinematic_ml_status_not_trained():
    """Confirms Stream B Kinematic model is NOT_TRAINED_DATA_PENDING."""
    dual = GLOBAL_DUAL_STREAM_ENGINE.evaluate_corridor("CORR-NH10-SIKKIM-KM48")
    assert dual["stream_b_kinematic"]["status"] == "UNAVAILABLE"
    assert dual["stream_b_kinematic"]["ml_model_status"] == "NOT_TRAINED_DATA_PENDING"


def test_research_readiness_gate_evaluates_false():
    """Confirms machine-readable REAL_TELEMETRY_RESEARCH_READY gate is strictly False."""
    audit = GLOBAL_EVIDENCE_AUDIT_ENGINE.perform_full_corridor_audit()
    gate = audit["research_readiness_gate"]
    assert gate["is_research_ready"] is False
    assert len(gate["unmet_prerequisites"]) > 0


def test_public_dispatch_safety_interlock():
    """Confirms public dispatch is hardcoded disabled and autonomous sirens are false."""
    dual = GLOBAL_DUAL_STREAM_ENGINE.evaluate_corridor("CORR-NH10-SIKKIM-KM48")
    safeguards = dual.get("safety_safeguards", {})
    assert safeguards.get("public_dispatch_enabled") is False
    assert safeguards.get("autonomous_siren_dispatch") is False
    assert safeguards.get("human_authorization_required") is True
