# -*- coding: utf-8 -*-
"""
tests/test_prediction_explanation.py
====================================
Tests the POST /api/pahad/prediction-explanation endpoint:
  - Validates calibrated vs raw event probability
  - Verifies presence of top contributing drivers with directional indicators
  - Asserts model driver terminology without causal claims
  - Checks provenance flags and data completeness score
"""

import os
os.environ["PARVAT_TESTING"] = "1"
os.environ["PAHAD_DEMO_MODE"] = "1"
import json
import unittest
from app import app


class TestPredictionExplanation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_prediction_explanation_structure(self):
        """Verify response contains all required fields and valid probability bounds."""
        payload = {
            "sector_id": "SK-NH10-KM48",
            "horizon_hours": 24,
            "features": {
                "rainfall_24h": 140.0,
                "soil_moisture": 0.45,
                "pore_pressure": 18.0,
                "slope": 38.0,
                "FoS": 1.05
            }
        }
        res = self.client.post("/api/pahad/prediction-explanation", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("sector_id"), "SK-NH10-KM48")
        self.assertEqual(data.get("forecast_horizon_hours"), 24)

        # Probabilities
        prob_cal = data.get("event_probability_calibrated")
        prob_raw = data.get("event_probability_raw")
        self.assertIsInstance(prob_cal, float)
        self.assertIsInstance(prob_raw, float)
        self.assertGreaterEqual(prob_cal, 0.0)
        self.assertLessEqual(prob_cal, 1.0)

        # Drivers
        drivers = data.get("top_contributing_drivers", [])
        self.assertGreaterEqual(len(drivers), 1)
        for d in drivers:
            self.assertIn("feature", d)
            self.assertIn("importance", d)
            self.assertIn("direction", d)
            self.assertEqual(d.get("driver_role"), "Model driver")

        # Scientific disclaimer
        disclaimer = data.get("disclaimer", "")
        self.assertIn("do not constitute physical causal proof", disclaimer)

        # Data quality & provenance
        dq = data.get("data_quality", {})
        self.assertIn("completeness_score", dq)
        self.assertIn("provenance_flags", data)
        self.assertIsInstance(data.get("provenance_flags"), dict)


if __name__ == "__main__":
    unittest.main()
