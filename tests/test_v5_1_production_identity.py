# -*- coding: utf-8 -*-
"""
tests/test_v5_1_production_identity.py
=======================================
Verifies bit-for-bit cryptographic immutability and distinct identities
of Production V3 and Research V4.5 neural network models.
"""

import os
import pytest
from engine.scientific_truth_engine import (
    GLOBAL_SCIENTIFIC_TRUTH_ENGINE,
    EXPECTED_V3_SHA256,
    EXPECTED_V4_5_SHA256,
    compute_sha256_file
)


def test_v3_production_weights_sha256():
    base_dir = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.base_dir
    v3_path = os.path.join(base_dir, "models", "pahad_lstm_v3_weights.pt")
    assert os.path.exists(v3_path), f"Production V3 weights not found at {v3_path}"
    actual_sha = compute_sha256_file(v3_path)
    assert actual_sha == EXPECTED_V3_SHA256, (
        f"Production V3 weights mutated! Expected {EXPECTED_V3_SHA256}, got {actual_sha}"
    )


def test_v4_5_research_weights_sha256():
    base_dir = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.base_dir
    v45_path = os.path.join(base_dir, "models", "pahad_lstm_v4_5_research_weights.pt")
    assert os.path.exists(v45_path), f"Research V4.5 weights not found at {v45_path}"
    actual_sha = compute_sha256_file(v45_path)
    assert actual_sha == EXPECTED_V4_5_SHA256, (
        f"Research V4.5 weights mutated! Expected {EXPECTED_V4_5_SHA256}, got {actual_sha}"
    )


def test_model_immutability_engine_method():
    immutability = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.verify_model_immutability()
    assert immutability["v3_immutable"] is True
    assert immutability["v4_5_immutable"] is True
    assert immutability["all_models_invariant"] is True


def test_distinct_model_identities():
    ledger = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_ledger()
    v3 = ledger.get("production_model", {})
    research_models = ledger.get("research_models", [])
    v45 = next((m for m in research_models if m.get("model_id") == "Model_D_1Layer_BiLSTM_Att_V4_5"), {})

    # Models must have distinct architectures and hashes
    assert v3.get("sha256") != v45.get("sha256")
    assert v3.get("sha256") == EXPECTED_V3_SHA256
    assert v45.get("sha256") == EXPECTED_V4_5_SHA256
    assert v3.get("input_sequence_length_hours") == 72
    assert v45.get("input_sequence_length_hours") == 168
    assert v3.get("feature_count") == 33
    assert v45.get("feature_count") == 31
