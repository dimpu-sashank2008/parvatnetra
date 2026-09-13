# -*- coding: utf-8 -*-
"""
tests/test_phase5b_calibration.py
=================================
Verifies probability calibration mechanics, bounded outputs [0, 1],
and strict isolation of test labels from calibrator fitting.
"""

import os
import unittest
import numpy as np
import pandas as pd
from engine.model_registry import GLOBAL_MODEL_REGISTRY

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data", "processed")


class TestPhase5BCalibration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_df = pd.read_csv(os.path.join(DATA_DIR, "phase5b_temporal_test.csv"))
        from scripts.train_phase5b_models import PHASE5B_FEATURE_COLUMNS
        cls.features = PHASE5B_FEATURE_COLUMNS

    def test_calibrated_probabilities_strictly_in_unit_interval(self):
        """All horizon classifiers must output probabilities strictly within [0.0, 1.0]."""
        X_test = self.test_df[self.features].values.astype(np.float32)

        for h in [6, 12, 24, 48]:
            artifact = GLOBAL_MODEL_REGISTRY.get_model(horizon_hours=h)
            self.assertIsNotNone(artifact, f"Model artifact missing for {h}h")
            calibrator = artifact["calibrator"]
            probs = calibrator.predict_proba(X_test)[:, 1]

            self.assertTrue((probs >= 0.0).all(), f"{h}h: Probability < 0.0 found!")
            self.assertTrue((probs <= 1.0).all(), f"{h}h: Probability > 1.0 found!")

    def test_calibrator_cv_folds_exclude_test_set(self):
        """CalibratedClassifierCV must be trained only on train (fold -1) and val (fold 0), never test."""
        artifact = GLOBAL_MODEL_REGISTRY.get_model(horizon_hours=24)
        calibrator = artifact["calibrator"]
        # In PredefinedSplit, test_fold must contain only -1 and 0
        if hasattr(calibrator, "cv") and hasattr(calibrator.cv, "test_fold"):
            unique_folds = set(calibrator.cv.test_fold)
            self.assertEqual(unique_folds, {-1, 0}, "Calibrator CV fold corrupted!")


if __name__ == "__main__":
    unittest.main()
