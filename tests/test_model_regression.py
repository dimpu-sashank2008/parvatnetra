import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
import joblib
from app import app


class TestModelRegression(unittest.TestCase):
    """Regression tests verifying preservation of existing geotechnical models and core APIs."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.models_dir = os.path.join(cls.base_dir, "models")

    def test_geotechnical_fos_models_preserved(self):
        """Verify that existing geotechnical FoS models exist, are distinct from event model, and predict FoS."""
        pahad_fos_path = os.path.join(self.models_dir, "pahad_fos_model.pkl")
        fos_predictor_path = os.path.join(self.models_dir, "fos_predictor.pkl")
        event_model_path = os.path.join(self.models_dir, "pahad_event_model.pkl")

        self.assertTrue(os.path.exists(pahad_fos_path), "pahad_fos_model.pkl was deleted or moved!")
        self.assertTrue(os.path.exists(fos_predictor_path), "fos_predictor.pkl was deleted or moved!")
        self.assertTrue(os.path.exists(event_model_path), "pahad_event_model.pkl does not exist!")

        # Verify models are distinct files
        self.assertNotEqual(
            os.path.getsize(pahad_fos_path),
            os.path.getsize(event_model_path),
            "pahad_fos_model.pkl was erroneously overwritten with event model!",
        )

        # Load geotechnical model and verify it predicts continuous FoS
        fos_bundle = joblib.load(pahad_fos_path)
        predictor = fos_bundle.get("model") if isinstance(fos_bundle, dict) else fos_bundle
        self.assertTrue(hasattr(predictor, "predict"))
        if isinstance(fos_bundle, dict):
            self.assertEqual(fos_bundle.get("target"), "factor_of_safety")

    def test_existing_api_ml_latest_risk(self):
        """Verify GET /api/ml/latest-risk continues to function and includes enhanced event fields."""
        res = self.client.get("/api/ml/latest-risk")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertIn("evaluations", data)
        self.assertGreater(len(data["evaluations"]), 0)
        top = data["evaluations"][0]

        # Backward compatibility checks
        self.assertIn("risk_index", top)
        self.assertIn("severity", top)
        self.assertIn("physical_fos", top)

        # Phase 3 enhancement checks
        self.assertIn("event_probability", top)
        self.assertIn("model_agreement", top)

    def test_existing_api_pahad_evaluate_sector(self):
        """Verify POST /api/pahad/evaluate-sector backward compatibility."""
        payload = {
            "sector_id": "NH10-KM48",
            "rainfall_mm": 65.0,
            "soil_cohesion_kpa": 12.0,
            "friction_angle_deg": 28.0,
            "slope_angle_deg": 35.0,
        }
        res = self.client.post("/api/pahad/evaluate-sector", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # Original fields
        self.assertIn("sector_id", data)
        self.assertIn("composite_risk", data)
        self.assertIn("physical_model", data)

        # Phase 3 enhancements
        self.assertIn("event_prediction", data)
        self.assertIn("model_agreement", data)

    def test_existing_api_pahad_critical_sectors(self):
        """Verify GET /api/pahad/critical-sectors continues to return ranked corridors."""
        res = self.client.get("/api/pahad/critical-sectors")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertIn("sectors", data)
        self.assertGreater(len(data["sectors"]), 0)
        s0 = data["sectors"][0]
        self.assertIn("sector_id", s0)
        self.assertIn("event_probability_24h", s0)


if __name__ == "__main__":
    unittest.main()
