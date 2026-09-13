# -*- coding: utf-8 -*-
"""
tests/test_phase5b_model_registry.py
====================================
Verifies centralized model registry functionality, metadata consistency,
multi-horizon artifact loading, and cryptographic hash verification.
"""

import os
import hashlib
import unittest
from engine.model_registry import GLOBAL_MODEL_REGISTRY

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data", "processed")


class TestPhase5BModelRegistry(unittest.TestCase):

    def test_registry_metadata_contains_required_fields(self):
        """Metadata must contain model_version, status, algorithm, hashes, and thresholds."""
        meta = GLOBAL_MODEL_REGISTRY.get_metadata()
        required_fields = [
            "model_version", "status", "algorithm",
            "training_dataset_hash_sha256", "horizons_trained",
            "optimal_thresholds", "features"
        ]
        for f in required_fields:
            self.assertIn(f, meta, f"Metadata missing: {f}")

    def test_multi_horizon_models_load_successfully(self):
        """All 4 horizons (6, 12, 24, 48) must load valid artifacts with calibrator and base_model."""
        for h in [6, 12, 24, 48]:
            artifact = GLOBAL_MODEL_REGISTRY.get_model(horizon_hours=h)
            self.assertIsNotNone(artifact, f"Failed to load model artifact for {h}h")
            self.assertIn("calibrator", artifact)
            self.assertIn("base_model", artifact)
            self.assertIn("features", artifact)

    def test_dataset_hash_matches_disk_hash(self):
        """Training dataset SHA-256 in metadata must strictly match the actual training CSV."""
        meta = GLOBAL_MODEL_REGISTRY.get_metadata()
        expected_hash = meta.get("training_dataset_hash_sha256")

        train_path = os.path.join(DATA_DIR, "phase5b_temporal_train.csv")
        self.assertTrue(os.path.exists(train_path), "Training CSV missing on disk")

        sha256 = hashlib.sha256()
        with open(train_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        actual_hash = sha256.hexdigest()

        self.assertEqual(actual_hash, expected_hash, "Cryptographic hash mismatch in Model Registry!")


if __name__ == "__main__":
    unittest.main()
