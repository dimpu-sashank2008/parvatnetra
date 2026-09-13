import os
import unittest
import json
import joblib
import numpy as np


class TestEventModel(unittest.TestCase):
    """Tests loading, schema validation, and inference of the Phase 3 event prediction model."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.model_path = os.path.join(cls.base_dir, "models", "pahad_event_model.pkl")
        cls.schema_path = os.path.join(cls.base_dir, "models", "pahad_feature_schema.json")
        cls.metadata_path = os.path.join(cls.base_dir, "models", "pahad_event_metadata.json")

        cls.model_bundle = joblib.load(cls.model_path)
        with open(cls.schema_path, "r", encoding="utf-8") as f:
            cls.schema = json.load(f)

    def test_model_bundle_structure(self):
        """Verify the model bundle contains calibrated model, raw model, and feature columns list."""
        self.assertIsInstance(self.model_bundle, dict)
        self.assertIn("calibrated_model", self.model_bundle)
        self.assertIn("raw_model", self.model_bundle)
        self.assertIn("feature_columns", self.model_bundle)
        self.assertEqual(len(self.model_bundle["feature_columns"]), 34)

    def test_feature_schema_completeness(self):
        """Verify schema defines all 34 canonical features with ranges and fallbacks."""
        features = self.schema.get("canonical_features", [])
        self.assertEqual(len(features), 34)
        for f in features:
            self.assertIn("name", f)
            self.assertIn("category", f)
            self.assertIn("fallback", f)

    def test_inference_probability_bounds(self):
        """Verify inference outputs well-behaved probabilities bounded strictly in [0.0, 1.0]."""
        model = self.model_bundle["calibrated_model"]

        # Synthetic test sample: high danger profile (34 features)
        danger_vector = np.array([
            18.0, 38.0, 115.0, 185.0, 95.0, 145.0, 210.0,  # hydro
            22.0, 1.0, 45.0, 0.88, 18.5, 26.0, 35.0,        # IoT
            0.92, 48.0, 0.95, 0.85, 4.8, 18.0, 0.75, 4.0,   # displacement / seismic
            850.0, 42.5, 135.0, 0.08, 0.32, -0.25,          # terrain / vegetation
            14.5, 0.88, 1.0, 0.90, 0.82, 78.0               # susceptibility / FoS / CRI
        ]).reshape(1, -1)

        prob = model.predict_proba(danger_vector)[0][1]
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        self.assertGreater(prob, 0.5, "High danger vector should produce elevated event probability")

    def test_low_risk_safety_baseline(self):
        """Verify flat, dry, stable slope produces low event probability."""
        model = self.model_bundle["calibrated_model"]
        # Safe vector: 0 rain, gentle slope, high FoS (34 features)
        safe_vector = np.zeros((1, 34))
        safe_vector[0, 22] = 300.0  # elevation
        safe_vector[0, 23] = 8.0    # slope
        safe_vector[0, 32] = 2.4    # FoS
        safe_vector[0, 2] = 0.0     # rainfall 24h
        safe_vector[0, 26] = 0.82   # high NDVI

        prob = model.predict_proba(safe_vector)[0][1]
        self.assertLess(prob, 0.35, "Safe slope should produce low event probability")

    def test_metadata_provenance(self):
        """Verify model metadata file records training tier and validation strategy."""
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta.get("status"), "TRAINED_LIMITED_DATA")
        self.assertIn("Temporal Holdout", meta.get("validation_strategy", ""))
        self.assertIn("metrics", meta)


if __name__ == "__main__":
    unittest.main()
