# -*- coding: utf-8 -*-
"""
tests/test_phase5b_temporal_leakage.py
======================================
Strict verification of zero lookahead, zero temporal inversion, and zero
feature leakage in the Phase 5B multi-horizon prediction dataset.
"""

import os
import unittest
import pandas as pd
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data", "processed")


class TestPhase5BTemporalLeakage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.full_df = pd.read_csv(os.path.join(DATA_DIR, "phase5b_temporal_full.csv"))

    def test_rainfall_window_hierarchy_no_lookahead(self):
        """Rainfall accumulations must follow strict hierarchy: 1h <= 3h <= 6h <= 12h <= 24h <= 48h <= 72h."""
        df = self.full_df
        # Tolerating tiny numerical roundoff
        eps = 1e-4
        self.assertTrue((df["rain_1h"] <= df["rain_3h"] + eps).all(), "Leakage: rain_1h > rain_3h")
        self.assertTrue((df["rain_3h"] <= df["rain_6h"] + eps).all(), "Leakage: rain_3h > rain_6h")
        self.assertTrue((df["rain_6h"] <= df["rain_12h"] + eps).all(), "Leakage: rain_6h > rain_12h")
        self.assertTrue((df["rain_12h"] <= df["rain_24h"] + eps).all(), "Leakage: rain_12h > rain_24h")
        self.assertTrue((df["rain_24h"] <= df["rain_48h"] + eps).all(), "Leakage: rain_24h > rain_48h")
        self.assertTrue((df["rain_48h"] <= df["rain_72h"] + eps).all(), "Leakage: rain_48h > rain_72h")

    def test_observation_timestamp_strictly_precedes_event_timestamp(self):
        """For all positive event samples, observation timestamp must be strictly BEFORE event_date."""
        event_samples = self.full_df[self.full_df["is_event_sample"] == 1]
        for _, row in event_samples.iterrows():
            obs_dt = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            ev_dt  = datetime.fromisoformat(row["event_date"].replace("Z", "+00:00"))
            self.assertLess(obs_dt, ev_dt, f"Lookahead Leakage! Obs {obs_dt} is not strictly before event {ev_dt}")

    def test_target_implication_monotonicity(self):
        """If failure occurs within 6h, it MUST also occur within 12h, 24h, and 48h."""
        df = self.full_df
        # target_6h=1 => target_12h=1, target_24h=1, target_48h=1
        t6_pos = df[df["target_6h"] == 1]
        self.assertTrue((t6_pos["target_12h"] == 1).all(), "Target inconsistency: 6h=1 but 12h=0")
        self.assertTrue((t6_pos["target_24h"] == 1).all(), "Target inconsistency: 6h=1 but 24h=0")
        self.assertTrue((t6_pos["target_48h"] == 1).all(), "Target inconsistency: 6h=1 but 48h=0")

    def test_controls_have_zero_positive_targets(self):
        """Controls must never have positive failure targets in any horizon."""
        ctrls = self.full_df[self.full_df["is_event_sample"] == 0]
        for h in [6, 12, 24, 48]:
            col = f"target_{h}h"
            self.assertEqual(ctrls[col].sum(), 0, f"Control sample has positive target in {col}!")


if __name__ == "__main__":
    unittest.main()
