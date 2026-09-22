# -*- coding: utf-8 -*-
"""
tests/test_v5_3_model_protection.py
===================================
Phase V5.3 Test Suite: Production Model Immutability & Model Training Prohibition
Verifies bit-for-bit preservation of Production V3 weights (SHA-256: 7cb8...),
offline isolation of Research V4.5 weights (SHA-256: 31e1...), and locked
kinematic ML training gate (NOT_TRAINED_DATA_PENDING).
"""

import os
import json
import hashlib
import pytest

EXPECTED_V3_SHA256 = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"
EXPECTED_V4_5_SHA256 = "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestV53ModelProtection:
    """Verifies that no models were trained or modified in Phase V5.3."""

    def test_v3_production_weights_immutable(self):
        v3_path = os.path.join("models", "pahad_lstm_v3_weights.pt")
        actual_hash = compute_sha256(v3_path)
        assert actual_hash == EXPECTED_V3_SHA256, (
            f"Production V3 corrupted! Expected {EXPECTED_V3_SHA256}, got {actual_hash}"
        )

    def test_v4_5_research_weights_immutable(self):
        v45_path = os.path.join("models", "pahad_lstm_v4_5_research_weights.pt")
        actual_hash = compute_sha256(v45_path)
        assert actual_hash == EXPECTED_V4_5_SHA256, (
            f"Research V4.5 corrupted! Expected {EXPECTED_V4_5_SHA256}, got {actual_hash}"
        )

    def test_kinematic_ml_remains_not_trained(self):
        manifest_path = os.path.join("data", "processed", "v5_3_dataset_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        status = data.get("model_gate_status", {}).get("kinematic_ml")
        assert status == "NOT_TRAINED_DATA_PENDING"
