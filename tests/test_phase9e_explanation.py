# -*- coding: utf-8 -*-
"""
tests/test_phase9e_explanation.py
=================================
PARVAT NETRA - PAHAD AI Phase 9E Plain-Language Explainability Audit
--------------------------------------------------------------------
Validates:
  1. Plain-language explanation generated from actual prediction inputs.
  2. Clear identification of primary driver, secondary driver, and supporting evidence.
  3. Non-causal phrasing (rejects "proves", "caused by"; requires "associated with", "signal").
  4. Data freshness and source provenance presence.
  5. API endpoint POST /api/pahad/prediction-explanation returns structured explanation.
"""

import os
import sys
import json
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.pahad_live_inference import run_live_inference
from app import app as flask_app


class TestPhase9EExplainability(unittest.TestCase):
    """Audit plain-language explainability, driver ranking, and non-causal language."""

    def test_structured_explanation_payload(self):
        """Inference explanation must contain summary, drivers, evidence, and non-causal phrasing."""
        res = run_live_inference(sector_id="SK-NH10-KM48", latitude=27.33, longitude=88.61)
        d = res.to_dict()

        self.assertIn("explanation", d)
        exp = d["explanation"]
        self.assertIn("summary", exp)
        self.assertIn("primary_driver", exp)
        self.assertIn("secondary_driver", exp)
        self.assertIn("supporting_evidence", exp)
        self.assertIn("data_freshness", exp)
        self.assertIn("provenance_summary", exp)

        # Verify non-causal phrasing
        summary_lower = exp["summary"].lower()
        self.assertNotIn("caused by", summary_lower, "Explanation must not assert unverified causality")
        self.assertNotIn("proves that", summary_lower, "Explanation must not assert proof")
        self.assertTrue(
            "associated with" in summary_lower or "indicates" in summary_lower or "corroborates" in summary_lower,
            "Explanation must use scientific association or indication phrasing"
        )

        # Supporting evidence should have multiple items
        self.assertIsInstance(exp["supporting_evidence"], list)
        self.assertGreaterEqual(len(exp["supporting_evidence"]), 2)

    def test_prediction_explanation_api_endpoint(self):
        """POST /api/pahad/prediction-explanation must return structured drivers and disclaimer."""
        client = flask_app.test_client()
        resp = client.post(
            "/api/pahad/prediction-explanation",
            data=json.dumps({"sector_id": "SK-NH10-KM48", "horizon_hours": 24}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("event_probability_calibrated", data)
        self.assertIn("top_contributing_drivers", data)
        self.assertIn("disclaimer", data)
        self.assertIn("statistical contributing signals", data["disclaimer"])
        self.assertIn("data_quality", data)
        self.assertIn("completeness_score", data["data_quality"])


if __name__ == "__main__":
    unittest.main()
