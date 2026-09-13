# -*- coding: utf-8 -*-
"""
tests/test_phase5b_ood.py
=========================
Verifies Out-Of-Distribution (OOD) diagnostic logic, detection of extreme anomalies,
and proper confidence penalty application.
"""

import os
import unittest
from engine.model_registry import GLOBAL_MODEL_REGISTRY

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(REPO_ROOT, "models")


class TestPhase5BOOD(unittest.TestCase):

    def test_ood_bounds_file_exists(self):
        """pahad_ood_bounds.json must exist."""
        path = os.path.join(MODELS_DIR, "pahad_ood_bounds.json")
        self.assertTrue(os.path.exists(path), "Missing pahad_ood_bounds.json")

    def test_in_distribution_sample_passes(self):
        """Realistic normal hill features should be evaluated as in-distribution."""
        normal_features = {
            "rain_24h": 45.0,
            "slope": 35.0,
            "elevation": 850.0,
            "pore_pressure": 12.0,
            "soil_moisture": 0.38,
            "tilt": 0.8
        }
        is_ood, ood_score, reasons = GLOBAL_MODEL_REGISTRY.check_ood(normal_features)
        self.assertFalse(is_ood, f"Normal sample falsely flagged as OOD: {reasons}")
        self.assertLess(ood_score, 0.5)

    def test_extreme_anomalous_features_trigger_ood(self):
        """Extreme physical values (e.g. 1500mm rain, 85 deg slope) must trigger OOD."""
        extreme_features = {
            "rain_24h": 1500.0,  # 1500mm in 24h is extreme outside training range
            "slope": 85.0,       # 85 degree slope is vertical cliff
            "pore_pressure": 250.0 # 250 kPa
        }
        is_ood, ood_score, reasons = GLOBAL_MODEL_REGISTRY.check_ood(extreme_features)
        self.assertTrue(is_ood, "Extreme anomalous sample failed to trigger OOD flag!")
        self.assertGreater(ood_score, 0.0)
        self.assertGreater(len(reasons), 0)

    def test_ood_downgrades_confidence_tier(self):
        """When an observation is OOD, compute_confidence must return LOW_CONFIDENCE."""
        dummy_features = {"rain_24h": 2000.0}
        tier, score, why = GLOBAL_MODEL_REGISTRY.compute_confidence(
            features=dummy_features,
            data_completeness=1.0,
            provenance_quality_score=1.0,
            is_ood=True,
            calibrated_probability=0.85
        )
        self.assertEqual(tier, "LOW_CONFIDENCE")
        self.assertLess(score, 0.70)


if __name__ == "__main__":
    unittest.main()
