import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import pandas as pd


class TestEventValidation(unittest.TestCase):
    """Tests temporal holdout split partitions, chronological validity, and class distributions."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.features_dir = os.path.join(cls.base_dir, "data", "features")
        cls.train_df = pd.read_csv(os.path.join(cls.features_dir, "real_train.csv"))
        cls.val_df = pd.read_csv(os.path.join(cls.features_dir, "real_val.csv"))
        cls.test_df = pd.read_csv(os.path.join(cls.features_dir, "real_test.csv"))

    def test_partition_sample_sizes_and_positives(self):
        """Verify reasonable class distribution across all three temporal holdout splits."""
        self.assertGreaterEqual(len(self.train_df), 10)
        self.assertGreaterEqual(len(self.val_df), 5)
        self.assertGreaterEqual(len(self.test_df), 5)

        # Both positive and negative classes in train, val, and test
        self.assertGreater(self.train_df["event_label"].sum(), 0)
        self.assertGreater(len(self.train_df) - self.train_df["event_label"].sum(), 0)

        self.assertGreater(self.val_df["event_label"].sum(), 0)
        self.assertGreater(len(self.val_df) - self.val_df["event_label"].sum(), 0)

        self.assertGreater(self.test_df["event_label"].sum(), 0)
        self.assertGreater(len(self.test_df) - self.test_df["event_label"].sum(), 0)

    def test_non_overlapping_temporal_windows(self):
        """Verify train, val, and test have strictly non-overlapping temporal periods."""
        train_max = pd.to_datetime(self.train_df["timestamp"], utc=True).max()
        val_min = pd.to_datetime(self.val_df["timestamp"], utc=True).min()
        val_max = pd.to_datetime(self.val_df["timestamp"], utc=True).max()
        test_min = pd.to_datetime(self.test_df["timestamp"], utc=True).min()

        self.assertTrue(train_max < val_min, f"Train max ({train_max}) not < Val min ({val_min})")
        self.assertTrue(val_max < test_min, f"Val max ({val_max}) not < Test min ({test_min})")


if __name__ == "__main__":
    unittest.main()
