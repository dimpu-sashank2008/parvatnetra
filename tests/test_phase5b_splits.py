# -*- coding: utf-8 -*-
"""
tests/test_phase5b_splits.py
============================
Verifies partition isolation, event-grouping integrity, and zero cross-partition
leakage across Train, Validation, and Test datasets.
"""

import os
import unittest
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data", "processed")


class TestPhase5BSplits(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.train_df = pd.read_csv(os.path.join(DATA_DIR, "phase5b_temporal_train.csv"))
        cls.val_df   = pd.read_csv(os.path.join(DATA_DIR, "phase5b_temporal_val.csv"))
        cls.test_df  = pd.read_csv(os.path.join(DATA_DIR, "phase5b_temporal_test.csv"))

    def test_zero_event_overlap_across_partitions(self):
        """No disaster event_id may exist in more than one partition (strict event grouping)."""
        train_events = set(self.train_df[self.train_df["is_event_sample"] == 1]["event_id"].unique())
        val_events   = set(self.val_df[self.val_df["is_event_sample"] == 1]["event_id"].unique())
        test_events  = set(self.test_df[self.test_df["is_event_sample"] == 1]["event_id"].unique())

        self.assertEqual(len(train_events.intersection(val_events)), 0, "Event overlap between TRAIN and VAL!")
        self.assertEqual(len(train_events.intersection(test_events)), 0, "Event overlap between TRAIN and TEST!")
        self.assertEqual(len(val_events.intersection(test_events)), 0, "Event overlap between VAL and TEST!")

    def test_zero_sample_id_overlap(self):
        """No individual sample_id may cross partitions."""
        train_ids = set(self.train_df["sample_id"].unique())
        val_ids   = set(self.val_df["sample_id"].unique())
        test_ids  = set(self.test_df["sample_id"].unique())

        self.assertEqual(len(train_ids.intersection(val_ids)), 0, "Sample overlap between TRAIN and VAL!")
        self.assertEqual(len(train_ids.intersection(test_ids)), 0, "Sample overlap between TRAIN and TEST!")
        self.assertEqual(len(val_ids.intersection(test_ids)), 0, "Sample overlap between VAL and TEST!")

    def test_all_partitions_have_positive_and_negative_samples(self):
        """Each partition must have both positive and negative samples for valid evaluation."""
        for name, df in [("TRAIN", self.train_df), ("VAL", self.val_df), ("TEST", self.test_df)]:
            pos_count = (df["is_event_sample"] == 1).sum()
            neg_count = (df["is_event_sample"] == 0).sum()
            self.assertGreater(pos_count, 0, f"{name} partition has 0 positive events!")
            self.assertGreater(neg_count, 0, f"{name} partition has 0 negative controls!")


if __name__ == "__main__":
    unittest.main()
