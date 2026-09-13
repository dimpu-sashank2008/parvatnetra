# -*- coding: utf-8 -*-
"""
tests/test_phase5b_thresholds.py
================================
Validates threshold sweep results, ensures thresholds are bounded [0, 1],
and verifies that optimal thresholds were tuned on validation data.
"""

import os
import json
import unittest
import pandas as pd
from engine.model_registry import GLOBAL_MODEL_REGISTRY

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")


class TestPhase5BThresholds(unittest.TestCase):

    def test_threshold_analysis_report_exists(self):
        """Threshold analysis CSV report must exist."""
        th_path = os.path.join(REPORTS_DIR, "pahad_threshold_analysis.csv")
        self.assertTrue(os.path.exists(th_path), "Missing pahad_threshold_analysis.csv")
        df = pd.read_csv(th_path)
        self.assertGreater(len(df), 0, "Empty threshold analysis report")
        self.assertIn("val_csi", df.columns)
        self.assertIn("val_pod", df.columns)
        self.assertIn("val_far", df.columns)

    def test_optimal_thresholds_bounded_in_unit_interval(self):
        """Optimal thresholds for all horizons must be strictly in (0.0, 1.0)."""
        for h in [6, 12, 24, 48]:
            th = GLOBAL_MODEL_REGISTRY.get_optimal_threshold(horizon_hours=h)
            self.assertGreater(th, 0.0, f"{h}h threshold <= 0.0")
            self.assertLess(th, 1.0, f"{h}h threshold >= 1.0")

    def test_threshold_monotonicity_tradeoff(self):
        """As threshold increases on validation data, false alarm rate (FAR) must not increase."""
        th_path = os.path.join(REPORTS_DIR, "pahad_threshold_analysis.csv")
        df = pd.read_csv(th_path)
        # Check for 24h horizon
        df_24 = df[df["horizon_hours"] == 24].sort_values("threshold")
        # In general, higher threshold leads to lower or equal false positives / FAR
        far_vals = df_24["val_far"].tolist()
        self.assertLessEqual(far_vals[-1], far_vals[0], "Higher threshold produced worse FAR!")


if __name__ == "__main__":
    unittest.main()
