# -*- coding: utf-8 -*-
"""
tests/test_v5_1_immutability.py
===============================
Phase V5.1 Test Suite: Cryptographic Model Immutability
Verifies bit-for-bit invariance of production V3 and research V4.5 weights.
"""

import os
import hashlib
import pytest
from engine.scientific_truth_engine import (
    ScientificTruthEngine,
    EXPECTED_V3_SHA256,
    EXPECTED_V4_5_SHA256,
    compute_sha256_file
)


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestV51Immutability:
    """Cryptographically verifies that no model weights were modified in Phase V5.1."""

    def test_production_v3_sha256_exact(self, truth_engine):
        v3_path = os.path.join(truth_engine.base_dir, "models", "pahad_lstm_v3_weights.pt")
        actual_hash = compute_sha256_file(v3_path)
        assert actual_hash == EXPECTED_V3_SHA256, (
            f"Production V3 weight corruption! Expected {EXPECTED_V3_SHA256}, got {actual_hash}"
        )

    def test_research_v4_5_sha256_exact(self, truth_engine):
        v45_path = os.path.join(truth_engine.base_dir, "models", "pahad_lstm_v4_5_research_weights.pt")
        actual_hash = compute_sha256_file(v45_path)
        assert actual_hash == EXPECTED_V4_5_SHA256, (
            f"Research V4.5 weight corruption! Expected {EXPECTED_V4_5_SHA256}, got {actual_hash}"
        )

    def test_engine_verify_model_immutability(self, truth_engine):
        res = truth_engine.verify_model_immutability()
        assert res["v3_immutable"] is True
        assert res["v4_5_immutable"] is True
        assert res["all_models_invariant"] is True
