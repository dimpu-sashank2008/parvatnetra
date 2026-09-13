import os
import unittest
import pandas as pd


class TestEventDataset(unittest.TestCase):
    """Tests Phase 3 historical landslide event dataset and temporal splits."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.data_dir = os.path.join(cls.base_dir, "data")
        cls.features_all = os.path.join(cls.data_dir, "features", "features_all.csv")
        cls.train_set = os.path.join(cls.data_dir, "features", "train_set.csv")
        cls.val_set = os.path.join(cls.data_dir, "features", "val_set.csv")
        cls.test_set = os.path.join(cls.data_dir, "features", "test_set.csv")

    def test_feature_files_exist(self):
        """Verify that all partitioned dataset CSVs exist on disk."""
        self.assertTrue(os.path.exists(self.features_all), f"Missing {self.features_all}")
        self.assertTrue(os.path.exists(self.train_set), f"Missing {self.train_set}")
        self.assertTrue(os.path.exists(self.val_set), f"Missing {self.val_set}")
        self.assertTrue(os.path.exists(self.test_set), f"Missing {self.test_set}")

    def test_sample_counts_and_partition_sum(self):
        """Ensure partitions sum up exactly to the total feature rows."""
        df_all = pd.read_csv(self.features_all)
        df_train = pd.read_csv(self.train_set)
        df_val = pd.read_csv(self.val_set)
        df_test = pd.read_csv(self.test_set)

        self.assertGreaterEqual(len(df_all), 30, "Expected at least 30 samples in total dataset")
        self.assertEqual(len(df_all), len(df_train) + len(df_val) + len(df_test))

    def test_temporal_holdout_integrity(self):
        """Ensure strictly chronological split with zero future leakage."""
        df_train = pd.read_csv(self.train_set)
        df_val = pd.read_csv(self.val_set)
        df_test = pd.read_csv(self.test_set)

        # Dates: train <= 2023-12-31, val in 2024 H1, test >= 2024-07-01
        train_max = pd.to_datetime(df_train["timestamp"], utc=True).max()
        val_min = pd.to_datetime(df_val["timestamp"], utc=True).min()
        val_max = pd.to_datetime(df_val["timestamp"], utc=True).max()
        test_min = pd.to_datetime(df_test["timestamp"], utc=True).min()

        self.assertLessEqual(train_max, pd.Timestamp("2023-12-31 23:59:59", tz="UTC"))
        self.assertGreaterEqual(val_min, pd.Timestamp("2024-01-01 00:00:00", tz="UTC"))
        self.assertLessEqual(val_max, pd.Timestamp("2024-06-30 23:59:59", tz="UTC"))
        self.assertGreaterEqual(test_min, pd.Timestamp("2024-07-01 00:00:00", tz="UTC"))

    def test_eight_ner_states_represented(self):
        """Verify that all 8 North-Eastern Region states are covered in geographic groups."""
        df_all = pd.read_csv(self.features_all)
        geo_groups = " ".join(df_all["geographic_group"].dropna().unique().tolist()).lower()
        required_states = [
            "sikkim",
            "mizoram",
            "manipur",
            "assam",
            "meghalaya",
            "nagaland",
            "arunachal",
            "tripura",
        ]
        for st in required_states:
            self.assertIn(st, geo_groups, f"Required NER state '{st}' is missing from geographic groups")

    def test_class_balance_and_target_variable(self):
        """Verify binary target event_label has both classes and no unexpected values."""
        df_all = pd.read_csv(self.features_all)
        self.assertIn("event_label", df_all.columns)
        unique_targets = set(df_all["event_label"].unique())
        self.assertEqual(unique_targets, {0, 1})

        pos_count = (df_all["event_label"] == 1).sum()
        neg_count = (df_all["event_label"] == 0).sum()
        self.assertGreater(pos_count, 5, "Too few positive landslide events")
        self.assertGreater(neg_count, 5, "Too few negative control windows")

    def test_feature_completeness_no_unplanned_nulls(self):
        """Verify key geotechnical and hydrometeorological features are non-null."""
        df_all = pd.read_csv(self.features_all)
        critical_cols = [
            "slope",
            "elevation",
            "rainfall_24h",
            "rainfall_72h",
            "FoS",
            "NDVI",
            "ground_displacement",
        ]
        for col in critical_cols:
            self.assertIn(col, df_all.columns, f"Column {col} missing from features")
            null_count = df_all[col].isnull().sum()
            self.assertEqual(null_count, 0, f"Column {col} contains unexpected nulls")


if __name__ == "__main__":
    unittest.main()
