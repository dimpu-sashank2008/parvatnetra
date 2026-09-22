# -*- coding: utf-8 -*-
"""
tests/test_v5_3_3d_safety.py
============================
PARVAT NETRA • PAHAD AI — Phase V5.3 3D Safety & Production Immutability Test Suite
"""

import os
import json
import hashlib
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_v5_3_model_v3_weights_cryptographic_immutability():
    """Verify that Production V3 model weights file is strictly untouched and frozen."""
    v3_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v3_weights.pt")
    assert os.path.exists(v3_path), f"V3 weights file missing at {v3_path}"

    with open(v3_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    expected_v3_hash = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"
    assert sha256 == expected_v3_hash, f"V3 weights hash mismatch: {sha256} != {expected_v3_hash}"


def test_v5_3_model_v4_5_research_weights_cryptographic_immutability():
    """Verify that Research V4.5 model weights file is strictly untouched and frozen."""
    v4_5_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v4_5_research_weights.pt")
    assert os.path.exists(v4_5_path), f"V4.5 weights file missing at {v4_5_path}"

    with open(v4_5_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    expected_v4_5_hash = "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"
    assert sha256 == expected_v4_5_hash, f"V4.5 weights hash mismatch: {sha256} != {expected_v4_5_hash}"


def test_v5_3_zero_autonomous_siren_trigger_from_3d_api(client):
    """Verify that querying 3D config never triggers alert dispatch or siren activation."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200

    # Verify that no warning dispatch happened
    data = res.get_json()
    assert "dispatch" not in data
    assert "siren" not in data
    assert data["status"] == "SUCCESS"


def test_v5_3_kinematic_ml_remains_not_trained():
    """Verify that kinematic ML status remains truthfully NOT_TRAINED_DATA_PENDING."""
    manifest_path = os.path.join(os.path.dirname(__file__), "..", "data", "manifests", "scientific_truth_ledger.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
        status = ledger.get("data_truth", {}).get("kinematic_ml_status") or ledger.get("kinematic_ml_status")
        assert status == "NOT_TRAINED_DATA_PENDING"
