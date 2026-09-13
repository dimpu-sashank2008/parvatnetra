import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
import joblib
import hashlib


class TestModelRegistry(unittest.TestCase):
    """Tests the versioned model registry, SHA-256 dataset hash verification, and metadata schemas."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.models_dir = os.path.join(cls.base_dir, "models")
        cls.train_dataset_path = os.path.join(cls.base_dir, "data", "features", "real_train.csv")

    def test_versioned_registry_artifacts_exist(self):
        """Verify model bundle, versioned metadata, and metrics exist in models/."""
        m_pkl = os.path.join(self.models_dir, "pahad_event_model.pkl")
        m_meta = os.path.join(self.models_dir, "pahad_event_model.metadata.json")
        m_metrics = os.path.join(self.models_dir, "pahad_event_metrics.json")

        self.assertTrue(os.path.exists(m_pkl), "pahad_event_model.pkl missing!")
        self.assertTrue(os.path.exists(m_meta), "pahad_event_model.metadata.json missing!")
        self.assertTrue(os.path.exists(m_metrics), "pahad_event_metrics.json missing!")

    def test_dataset_sha256_hash_integrity(self):
        """Verify the SHA-256 hash in metadata accurately matches the training file on disk."""
        sha256 = hashlib.sha256()
        with open(self.train_dataset_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        expected_hash = sha256.hexdigest()

        m_meta = os.path.join(self.models_dir, "pahad_event_model.metadata.json")
        with open(m_meta, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.assertEqual(
            meta.get("dataset_hash"),
            expected_hash,
            "Stored dataset SHA-256 hash does not match actual real_train.csv hash!"
        )

    def test_model_bundle_contents(self):
        """Verify model bundle dictionary keys and prediction capability."""
        m_pkl = os.path.join(self.models_dir, "pahad_event_model.pkl")
        bundle = joblib.load(m_pkl)

        self.assertIsInstance(bundle, dict)
        self.assertIn("model", bundle)
        self.assertIn("feature_columns", bundle)
        self.assertIn("dataset_hash", bundle)
        self.assertIn("status", bundle)
        self.assertEqual(bundle.get("status"), "TRAINED_LIMITED_DATA")
        self.assertTrue(hasattr(bundle["model"], "predict_proba"))

    def test_geotechnical_models_strictly_preserved(self):
        """Ensure geotechnical FoS model was not overwritten or corrupted."""
        fos_path = os.path.join(self.models_dir, "pahad_fos_model.pkl")
        self.assertTrue(os.path.exists(fos_path))
        fos_bundle = joblib.load(fos_path)
        if isinstance(fos_bundle, dict):
            self.assertEqual(fos_bundle.get("target"), "factor_of_safety")
            self.assertTrue(hasattr(fos_bundle.get("model"), "predict"))


if __name__ == "__main__":
    unittest.main()
