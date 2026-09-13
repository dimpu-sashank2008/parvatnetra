import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app


class TestEventAPI(unittest.TestCase):
    """Tests the new Phase 3.1 REST APIs: /event-model/status and /event-model/data-quality."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_get_event_model_status_contract(self):
        """Verify GET /api/pahad/event-model/status response contract."""
        res = self.client.get("/api/pahad/event-model/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("model_status", data)
        self.assertEqual(data.get("model_status"), "TRAINED_LIMITED_DATA")
        self.assertIn("model_version", data)
        self.assertIn("training_rows", data)
        self.assertIn("dataset_hash", data)
        self.assertGreater(len(data.get("dataset_hash", "")), 10)

        # Check metrics summary
        self.assertIn("metrics_summary", data)
        m = data["metrics_summary"]
        self.assertIn("brier_score", m)
        self.assertIn("roc_auc", m)
        self.assertIn("pod", m)
        self.assertIn("far", m)
        self.assertIn("csi", m)
        self.assertIn("median_lead_time_hours", m)

    def test_get_event_model_data_quality_contract(self):
        """Verify GET /api/pahad/event-model/data-quality response contract."""
        res = self.client.get("/api/pahad/event-model/data-quality")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("event_count", data)
        self.assertIn("control_count", data)
        self.assertIn("states", data)
        self.assertEqual(len(data.get("states", [])), 8)
        self.assertIn("feature_completeness", data)
        self.assertEqual(data.get("feature_completeness"), 100.0)
        self.assertIn("provenance_summary", data)

    def test_predict_event_integration(self):
        """Verify POST /api/pahad/predict-event works in harmony with the trained event model."""
        payload = {
            "sector_id": "SK-NH10-KM48",
            "features": {
                "rainfall_24h_mm": 185.0,
                "fos_physical": 0.62,
                "slope_deg": 42.0
            }
        }
        res = self.client.post("/api/pahad/predict-event", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("sector_id"), "SK-NH10-KM48")
        self.assertIn("prediction", data)
        self.assertIn("24h", data["prediction"])


if __name__ == "__main__":
    unittest.main()
