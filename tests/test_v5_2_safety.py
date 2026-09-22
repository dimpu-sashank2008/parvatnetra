# -*- coding: utf-8 -*-
"""
tests/test_v5_2_safety.py
=========================
Phase V5.2 Test Suite: Safety Boundaries & Model Immutability
Verifies cryptographic immutability of Production V3 weights, human authorization
locks on public dispatch, dry-run siren emulation, and the Kinematic ML training gate.
"""

import os
import hashlib
import pytest
from engine.physical_deployment_engine import (
    GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE,
    compute_sha256_file
)

EXPECTED_V3_SHA256 = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"
EXPECTED_V4_5_SHA256 = "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"


def test_production_v3_weights_cryptographic_immutability():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    v3_path = os.path.join(engine.base_dir, "models", "pahad_lstm_v3_weights.pt")
    actual_hash = compute_sha256_file(v3_path)
    assert actual_hash == EXPECTED_V3_SHA256, (
        f"Production V3 weight corrupted! Expected {EXPECTED_V3_SHA256}, got {actual_hash}"
    )


def test_research_v4_5_weights_cryptographic_immutability():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    v45_path = os.path.join(engine.base_dir, "models", "pahad_lstm_v4_5_research_weights.pt")
    actual_hash = compute_sha256_file(v45_path)
    assert actual_hash == EXPECTED_V4_5_SHA256, (
        f"Research V4.5 weight corrupted! Expected {EXPECTED_V4_5_SHA256}, got {actual_hash}"
    )


def test_public_dispatch_and_siren_safety_locks():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    res = engine.evaluate_v5_2_verdict()
    assert res["human_authorization_required"] is True
    assert res["public_dispatch_enabled"] is False
    assert res["siren_relay_hardware"] == "DRY_RUN_EMULATOR"


def test_kinematic_ml_training_gate_locked():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    res = engine.evaluate_v5_2_verdict()
    assert res["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"
    ml_gate = engine.verify_model_immutability()
    assert ml_gate["training_gate"] == "LOCKED_UNTIL_VERIFIED_PHYSICAL_DATA_AVAILABLE"
