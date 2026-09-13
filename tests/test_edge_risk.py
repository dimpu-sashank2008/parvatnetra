# -*- coding: utf-8 -*-
"""
tests/test_edge_risk.py
=======================
Unit tests for Edge Local Safety Risk Evaluator (Phase 3.4 Section 8).
Validates:
  - Deterministic evaluation of SAFE, WATCH, WARNING, CRITICAL states
  - Multi-sensor anomaly score computation (0.0 to 1.0 range)
  - Detection and reporting of specific exceeded geotechnical indicators
  - Action recommendations (MONITOR, LOCAL_WATCH, ACOUSTIC_WARNING, IMMEDIATE_EVACUATION)
"""

import unittest
from backend.edge.risk_evaluator import EdgeRiskEvaluator


class TestEdgeRiskEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = EdgeRiskEvaluator()

    def test_safe_state(self):
        """Baseline readings below all thresholds must return SAFE."""
        reading = {
            "soil_moisture": 32.0,
            "pore_pressure": 10.0,
            "tilt": 0.1,
            "rainfall": 2.0
        }
        res = self.evaluator.evaluate_reading(reading)
        self.assertEqual(res["edge_safety_state"], "SAFE")
        self.assertLess(res["anomaly_score"], 0.3)
        self.assertEqual(len(res["exceeded_indicators"]), 0)
        self.assertIn("MONITOR", res["action_recommendation"])

    def test_watch_state_on_single_threshold(self):
        """Elevated pore pressure alone entering watch band must yield WATCH."""
        reading = {
            "soil_moisture": 32.0,
            "pore_pressure": 18.0, # Watch >= 15.0
            "tilt": 0.2,
            "rainfall": 3.0
        }
        res = self.evaluator.evaluate_reading(reading)
        self.assertEqual(res["edge_safety_state"], "WATCH")
        self.assertGreaterEqual(len(res["exceeded_indicators"]), 1)
        self.assertEqual(res["exceeded_indicators"][0]["sensor"], "pore_pressure")

    def test_warning_state_on_multiple_elevations(self):
        """High rainfall and high soil moisture reaching warning levels must yield WARNING."""
        reading = {
            "soil_moisture": 50.0, # Warning >= 48.0
            "pore_pressure": 20.0, # Watch >= 15.0
            "tilt": 0.8,           # Watch >= 0.5
            "rainfall": 28.0       # Warning >= 25.0
        }
        res = self.evaluator.evaluate_reading(reading)
        self.assertEqual(res["edge_safety_state"], "WARNING")
        self.assertGreaterEqual(res["anomaly_score"], 0.5)
        self.assertIn("ACOUSTIC", res["action_recommendation"])

    def test_critical_state_on_tilt_failure(self):
        """Borehole inclinometer displacement exceeding critical threshold must trigger CRITICAL immediately."""
        reading = {
            "soil_moisture": 65.0,
            "pore_pressure": 40.0,
            "tilt": 3.5,           # Critical >= 3.0
            "rainfall": 50.0       # Critical >= 45.0
        }
        res = self.evaluator.evaluate_reading(reading)
        self.assertEqual(res["edge_safety_state"], "CRITICAL")
        self.assertGreaterEqual(res["anomaly_score"], 0.8)
        self.assertIn("EVACUATION", res["action_recommendation"])

    def test_custom_thresholds_override(self):
        """Evaluator must support custom localized thresholds for vulnerable micro-corridors."""
        custom = {
            "tilt_degrees": {"watch": 0.2, "warning": 0.6, "critical": 1.2}
        }
        stricter_evaluator = EdgeRiskEvaluator(custom_thresholds=custom)
        reading = {
            "soil_moisture": 35.0,
            "pore_pressure": 12.0,
            "tilt": 0.8, # Warning under custom threshold (warning: 0.6)
            "rainfall": 15.0
        }
        res = stricter_evaluator.evaluate_reading(reading)
        self.assertEqual(res["edge_safety_state"], "WARNING")


if __name__ == "__main__":
    unittest.main()
