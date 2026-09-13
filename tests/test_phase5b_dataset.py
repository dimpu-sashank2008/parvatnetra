# -*- coding: utf-8 -*-
"""
tests/test_phase5b_dataset.py
=============================
Validates Phase 5B True Temporal Multi-Horizon Dataset integrity, schemas,
target distributions, and cryptographic reproducibility.
"""

import os
import json
import hashlib
import unittest
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data", "processed")
MANIFESTS_DIR = os.path.join(REPO_ROOT, "data", "manifests")


class TestPhase5BDataset(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.full_path = os.path.join(DATA_DIR, "phase5b_temporal_full.csv")
        cls.train_path = os.path.join(DATA_DIR, "phase5b_temporal_train.csv")
        cls.val_path = os.path.join(DATA_DIR, "phase5b_temporal_val.csv")
        cls.test_path = os.path.join(DATA_DIR, "phase5b_temporal_test.csv")
        cls.manifest_train = os.path.join(MANIFESTS_DIR, "phase5b_train.json")

    def test_dataset_files_exist(self):
        """All Phase 5B partitioned dataset files must exist on disk."""
        for path in [self.full_path, self.train_path, self.val_path, self.test_path, self.manifest_train]:
            self.assertTrue(os.path.exists(path), f"Missing dataset file: {path}")

    def test_multi_horizon_targets_present(self):
        """All 4 multi-horizon forecast targets must exist and be binary."""
        df = pd.read_csv(self.full_path)
        for h in [6, 12, 24, 48]:
            col = f"target_{h}h"
            self.assertIn(col, df.columns, f"Missing target: {col}")
            unique_vals = set(df[col].unique())
            self.assertTrue(unique_vals.issubset({0, 1}), f"Non-binary values in {col}: {unique_vals}")

    def test_no_cri_in_feature_columns(self):
        """CRI (Composite Risk Index) must NOT be present as an input feature (circular leakage)."""
        df = pd.read_csv(self.train_path)
        feature_candidates = [c for c in df.columns if not c.startswith("target_") and c not in ["sample_id", "event_id", "sector_id", "timestamp"]]
        self.assertNotIn("cri", [c.lower() for c in feature_candidates], "CRI found in training features!")

    def test_physical_features_present(self):
        """Physical, hydrometeorological, and geotechnical features must exist."""
        df = pd.read_csv(self.train_path)
        expected_features = [
            "rain_1h", "rain_3h", "rain_6h", "rain_12h", "rain_24h", "rain_48h", "rain_72h",
            "antecedent_rain_3d", "antecedent_rain_7d", "rain_intensity",
            "fos", "slope", "aspect", "elevation", "curvature",
            "soil_moisture", "pore_pressure", "tilt", "ground_displacement"
        ]
        for f in expected_features:
            self.assertIn(f, df.columns, f"Feature missing: {f}")

    def test_train_sha256_matches_manifest(self):
        """SHA-256 hash of training CSV must strictly match manifest."""
        sha256 = hashlib.sha256()
        with open(self.train_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        actual_hash = sha256.hexdigest()

        with open(self.manifest_train, "r", encoding="utf-8") as f:
            m = json.load(f)
        manifest_hash = m.get("sha256")
        self.assertEqual(actual_hash, manifest_hash, "Training dataset SHA-256 does not match manifest!")

    def test_positive_event_antecedent_monotonicity(self):
        """For antecedent samples of the same event, remaining lead time must decrease toward failure."""
        df = pd.read_csv(self.full_path)
        ev_df = df[df["event_id"] == "EV-01"].sort_values("timestamp")
        lead_times = ev_df["lead_time_to_event_hours"].tolist()
        # Lead time should decrease: [48, 36, 24, 12, 6]
        self.assertEqual(lead_times, sorted(lead_times, reverse=True))


if __name__ == "__main__":
    unittest.main()
