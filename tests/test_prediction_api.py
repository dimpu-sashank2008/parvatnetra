import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app


class TestPredictionAPI(unittest.TestCase):
    """Tests the POST /api/pahad/predict-event endpoint and response contract."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_predict_event_default_payload(self):
        """Test POST /api/pahad/predict-event with basic sector payload."""
        payload = {
            "sector_id": "S14",
            "timestamp": "2026-09-09T18:00:00Z",
            "features": {
                "rainfall_24h_mm": 115.0,
                "fos_physical": 0.89,
                "slope_deg": 38.5,
                "insar_velocity_mm_year": -14.2,
            },
        }
        res = self.client.post(
            "/api/pahad/predict-event",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # Contract checks
        self.assertEqual(data.get("sector_id"), "S14")
        self.assertIn("prediction", data)
        pred = data["prediction"]
        for h in ["6h", "12h", "24h", "48h"]:
            self.assertIn(h, pred)
            self.assertIsInstance(pred[h], (float, int))
            self.assertGreaterEqual(pred[h], 0.0)
            self.assertLessEqual(pred[h], 1.0)

        self.assertTrue(data.get("calibrated"))
        self.assertIn("confidence", data)
        self.assertIn("physical_fos", data)
        self.assertIn("rainfall_trigger", data)
        self.assertIn("model_agreement", data)
        self.assertIn("risk_band", data)
        self.assertIn("top_drivers", data)
        self.assertIn("data_provenance", data)
        self.assertIn("model_version", data)

    def test_predict_event_empty_features(self):
        """Test API fallback behavior when features are empty or omitted."""
        payload = {"sector_id": "S01"}
        res = self.client.post(
            "/api/pahad/predict-event",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("sector_id"), "S01")
        self.assertIn("24h", data.get("prediction", {}))

    def test_predict_event_safe_sector(self):
        """Test prediction for low-hazard sector produces low risk band."""
        payload = {
            "sector_id": "S_SAFE",
            "features": {
                "rainfall_24h_mm": 0.0,
                "fos_physical": 2.2,
                "slope_deg": 12.0,
                "insar_velocity_mm_year": 0.0,
            },
        }
        res = self.client.post(
            "/api/pahad/predict-event",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn(data.get("risk_band"), ["LOW", "MODERATE"])


if __name__ == "__main__":
    unittest.main()
