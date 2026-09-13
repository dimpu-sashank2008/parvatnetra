import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import pandas as pd
import json


class TestEventDataQuality(unittest.TestCase):
    """Tests data provenance, separation of real vs demo datasets, and feature completeness."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.data_dir = os.path.join(cls.base_dir, "data")
        cls.features_dir = os.path.join(cls.data_dir, "features")
        cls.reports_dir = os.path.join(cls.base_dir, "reports")

    def test_real_dataset_files_exist_without_synthetic_contamination(self):
        """Verify real_train, real_val, real_test exist and do not contain [DEMO] records."""
        for split in ["real_train.csv", "real_val.csv", "real_test.csv"]:
            p = os.path.join(self.features_dir, split)
            self.assertTrue(os.path.exists(p), f"Missing {split}")
            df = pd.read_csv(p)
            self.assertGreater(len(df), 0)
            if "provenance" in df.columns:
                self.assertFalse((df["provenance"] == "[DEMO]").any(), f"Found [DEMO] sample in {split}!")

    def test_demo_dataset_is_isolated(self):
        """Verify demo_train.csv exists and is tagged with [DEMO] provenance."""
        demo_p = os.path.join(self.features_dir, "demo_train.csv")
        self.assertTrue(os.path.exists(demo_p), f"Missing {demo_p}")
        df = pd.read_csv(demo_p)
        self.assertGreater(len(df), 0)
        self.assertTrue((df["provenance"] == "[DEMO]").all(), "Demo dataset contains non-DEMO tags!")

    def test_raw_historical_events_catalog(self):
        """Verify historical_landslides_ner.csv covers 8 NER states with valid coordinates."""
        raw_p = os.path.join(self.data_dir, "raw", "historical_landslides_ner.csv")
        self.assertTrue(os.path.exists(raw_p), f"Missing {raw_p}")
        df = pd.read_csv(raw_p)
        self.assertGreaterEqual(len(df), 15)

        # Check required columns
        req_cols = ["event_id", "timestamp", "latitude", "longitude", "state", "district", "sector_id", "source"]
        for c in req_cols:
            self.assertIn(c, df.columns)

        # Coordinates valid for NE India (Lat 21..30 N, Lon 88..98 E)
        self.assertTrue((df["latitude"] >= 20.0).all() and (df["latitude"] <= 30.0).all())
        self.assertTrue((df["longitude"] >= 88.0).all() and (df["longitude"] <= 98.0).all())

        # All 8 NER states represented
        states = set(df["state"].unique())
        self.assertEqual(len(states), 8, f"Expected 8 states, found: {states}")

    def test_data_quality_report_exists_and_valid(self):
        """Verify reports/pahad_data_quality_report.json matches data statistics."""
        json_p = os.path.join(self.reports_dir, "pahad_data_quality_report.json")
        self.assertTrue(os.path.exists(json_p), f"Missing {json_p}")
        with open(json_p, "r", encoding="utf-8") as f:
            dq = json.load(f)

        self.assertEqual(dq.get("status"), "OPERATIONAL")
        self.assertEqual(dq.get("data_tier"), "TRAINED_LIMITED_DATA")
        self.assertEqual(dq.get("positive_events"), 17)
        self.assertEqual(dq.get("negative_samples"), 19)
        self.assertEqual(dq.get("feature_completeness_pct"), 100.0)


if __name__ == "__main__":
    unittest.main()
