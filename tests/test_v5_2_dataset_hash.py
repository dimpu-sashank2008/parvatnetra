# -*- coding: utf-8 -*-
"""
tests/test_v5_2_dataset_hash.py
===============================
Phase V5.2 Test Suite: Dataset & Model Weight Cryptographic Hash Verification
"""

import os
import json
import hashlib
import pytest

EXPECTED_V3_SHA256 = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"
EXPECTED_V4_5_SHA256 = "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestV52DatasetHash:
    """Verifies that model weights and raw datasets match canonical cryptographic hashes."""

    def test_production_v3_weight_hash_unmodified(self):
        v3_path = os.path.join("models", "pahad_lstm_v3_weights.pt")
        assert os.path.exists(v3_path), "Production V3 weights file missing"
        actual_hash = sha256_file(v3_path)
        assert actual_hash == EXPECTED_V3_SHA256, (
            f"PRODUCTION V3 CORRUPTED! Expected {EXPECTED_V3_SHA256}, got {actual_hash}"
        )

    def test_research_v4_5_weight_hash_unmodified(self):
        v4_path = os.path.join("models", "pahad_lstm_v4_5_research_weights.pt")
        assert os.path.exists(v4_path), "Research V4.5 weights file missing"
        actual_hash = sha256_file(v4_path)
        assert actual_hash == EXPECTED_V4_5_SHA256, (
            f"RESEARCH V4.5 CORRUPTED! Expected {EXPECTED_V4_5_SHA256}, got {actual_hash}"
        )

    def test_expansion_json_matches_manifest(self):
        exp_path = os.path.join("data", "raw", "historical_landslides_expansion_v5_2.json")
        assert os.path.exists(exp_path), "Expansion JSON missing"
        actual_hash = sha256_file(exp_path)

        manifest_path = os.path.join("data", "manifests", "v5_2_external_data_manifest.json")
        assert os.path.exists(manifest_path), "V5.2 manifest missing"
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = json.load(f)

        assert m["dataset_hashes"]["historical_landslides_expansion_v5_2_json"] == actual_hash
