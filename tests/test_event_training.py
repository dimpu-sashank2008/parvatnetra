import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
import joblib
from scripts.train_event_model import train_and_evaluate


class TestEventTraining(unittest.TestCase):
    """Tests the event model training pipeline, reproducibility seed, and artifact generation."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.models_dir = os.path.join(cls.base_dir, "models")
        cls.features_dir = os.path.join(cls.base_dir, "data", "features")

    def test_train_and_evaluate_gradient_boosting(self):
        """Verify train_and_evaluate executes and returns structured metadata."""
        dataset = os.path.join(self.features_dir, "real_train.csv")
        out_model = os.path.join(self.models_dir, "test_pahad_event_model.pkl")

        metadata = train_and_evaluate(
            dataset_path=dataset,
            output_path=out_model,
            algorithm="gradient_boosting",
            seed=42,
            forecast_horizon_hours=24,
            model_version="test-v1.0"
        )

        self.assertEqual(metadata["model_name"], "PAHAD-Event-Classifier")
        self.assertEqual(metadata["status"], "TRAINED_LIMITED_DATA")
        self.assertIn("dataset_hash", metadata)
        self.assertGreater(len(metadata["dataset_hash"]), 20)

        # Cleanup test model file
        if os.path.exists(out_model):
            os.remove(out_model)

    def test_reproducible_seed_produces_identical_weights(self):
        """Verify identical seed produces identical metrics and dataset hash."""
        dataset = os.path.join(self.features_dir, "real_train.csv")
        m1 = train_and_evaluate(dataset_path=dataset, seed=42)
        m2 = train_and_evaluate(dataset_path=dataset, seed=42)

        self.assertEqual(m1["dataset_hash"], m2["dataset_hash"])
        self.assertEqual(m1["metrics"]["brier_score"], m2["metrics"]["brier_score"])


if __name__ == "__main__":
    unittest.main()
