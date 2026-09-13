import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import pandas as pd


class TestEventLabeling(unittest.TestCase):
    """Tests traceability of event labels and validity of negative controls."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.labels_path = os.path.join(cls.base_dir, "data", "labels", "event_labels.csv")
        cls.obs_path = os.path.join(cls.base_dir, "data", "processed", "pahad_event_observations.csv")

    def test_labels_file_structure(self):
        """Verify event_labels.csv schema and binary target values {0, 1}."""
        self.assertTrue(os.path.exists(self.labels_path))
        df = pd.read_csv(self.labels_path)
        self.assertIn("event_label", df.columns)
        self.assertIn("sector_id", df.columns)
        self.assertIn("timestamp", df.columns)
        self.assertIn("source", df.columns)

        unique_labels = set(df["event_label"].unique())
        self.assertTrue(unique_labels.issubset({0, 1}))

    def test_positive_events_have_traceable_disaster_source(self):
        """Positive labels (1) must carry authenticated institutional disaster sources."""
        df = pd.read_csv(self.labels_path)
        positives = df[df["event_label"] == 1]
        self.assertGreaterEqual(len(positives), 15)

        for _, row in positives.iterrows():
            source = str(row["source"]).strip()
            self.assertGreater(len(source), 5)
            self.assertTrue(
                any(k in source for k in ["GSI", "SDMA", "PWD", "BRO", "ISRO", "NLSM", "Disaster"]),
                f"Source '{source}' is unauthenticated!"
            )

    def test_negative_controls_have_defensible_mechanics(self):
        """Negative controls (0) must correspond to stable FoS (> 1.10) in observation records."""
        obs = pd.read_csv(self.obs_path)
        negatives = obs[obs["event_label"] == 0]
        self.assertGreaterEqual(len(negatives), 15)

        # FoS for negative controls should be physically stable (FoS > 1.0)
        self.assertTrue((negatives["FoS"] >= 1.10).all(), "Found negative control with unstable FoS < 1.10!")


if __name__ == "__main__":
    unittest.main()
