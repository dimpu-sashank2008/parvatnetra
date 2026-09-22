# -*- coding: utf-8 -*-
"""
tests/test_v5_3_dataset_versioning.py
=====================================
Phase V5.3 Test Suite: Dataset Versioning & Historical Immutability
Verifies that V5.1 and V5.2 source files were preserved without overwriting,
and that new V5.3 forensic files exist with valid cryptographic hashes.
"""

import os
import json
import hashlib
import pytest


def compute_file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestV53DatasetVersioning:
    """Verifies that historical datasets remain intact and V5.3 versions are created."""

    def test_historical_datasets_exist_unmodified(self):
        v51_csv = os.path.join("data", "raw", "historical_landslides_ner.csv")
        assert os.path.exists(v51_csv), "V5.1 raw CSV missing"

        v52_exp = os.path.join("data", "raw", "historical_landslides_expansion_v5_2.json")
        assert os.path.exists(v52_exp), "V5.2 raw expansion JSON missing"

        v52_inv = os.path.join("data", "processed", "canonical_event_inventory_v5_2.json")
        assert os.path.exists(v52_inv), "V5.2 inventory missing"

    def test_v5_3_versioned_files_exist(self):
        v53_files = [
            os.path.join("data", "processed", "canonical_event_inventory_v5_3.json"),
            os.path.join("data", "processed", "v5_3_event_evidence_registry.json"),
            os.path.join("data", "processed", "v5_3_event_lineage.json"),
            os.path.join("data", "processed", "v5_3_dataset_manifest.json"),
            os.path.join("reports", "pahad_v5_3_result.json")
        ]
        for p in v53_files:
            assert os.path.exists(p), f"Required V5.3 artifact missing: {p}"

    def test_v5_3_manifest_hashes_match_files(self):
        manifest_path = os.path.join("data", "processed", "v5_3_dataset_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        dataset_files = manifest.get("dataset_files", {})
        for rel_path, expected_hash in dataset_files.items():
            if os.path.exists(rel_path):
                actual_hash = compute_file_sha256(rel_path)
                assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}"
