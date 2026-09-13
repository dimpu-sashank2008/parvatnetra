import os
import unittest
import json
import joblib
import numpy as np


class TestEventCalibration(unittest.TestCase):
    """Tests model probability calibration using Platt scaling / isotonic regression."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.calibrator_path = os.path.join(cls.base_dir, "models", "pahad_event_calibrator.pkl")
        cls.metrics_path = os.path.join(cls.base_dir, "models", "pahad_training_metrics.json")
        cls.calibrator = joblib.load(cls.calibrator_path)

    def test_calibrator_loads_and_has_method(self):
        """Verify calibrator is loaded and has predict_proba method."""
        self.assertIsNotNone(self.calibrator)
        self.assertTrue(hasattr(self.calibrator, "predict_proba"))

    def test_calibration_bounds(self):
        """Verify calibrated probabilities never escape [0.0, 1.0]."""
        # Test across 20 synthetic input points
        test_inputs = np.random.uniform(0.0, 50.0, size=(20, 34))
        probs = self.calibrator.predict_proba(test_inputs)[:, 1]
        self.assertTrue(np.all(probs >= 0.0), "Found calibrated prob < 0.0")
        self.assertTrue(np.all(probs <= 1.0), "Found calibrated prob > 1.0")

    def test_calibration_metrics_recorded(self):
        """Verify Brier score and calibration error are recorded in metrics."""
        self.assertTrue(os.path.exists(self.metrics_path), f"Missing {self.metrics_path}")
        with open(self.metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        brier = metrics.get("brier_score", metrics.get("spatial_group_cv", {}).get("brier_score"))
        ece = metrics.get("calibration_error", metrics.get("spatial_group_cv", {}).get("calibration_error"))
        self.assertIsNotNone(brier)
        self.assertIsNotNone(ece)

        self.assertGreaterEqual(brier, 0.0)
        self.assertLess(brier, 0.25, f"Brier score {brier} is too high for a calibrated model")
        self.assertGreaterEqual(ece, 0.0)
        self.assertLess(ece, 0.40, f"ECE {ece} indicates severe miscalibration")

    def test_monotonic_response_to_increasing_rainfall(self):
        """Verify probability scales monotonically with increasing rainfall stress."""
        base_sample = np.zeros((1, 34))
        base_sample[0, 22] = 600.0  # elevation
        base_sample[0, 23] = 32.0   # slope
        base_sample[0, 32] = 1.05   # FoS
        base_sample[0, 26] = 0.45   # NDVI

        rain_levels = [5.0, 30.0, 80.0, 160.0]
        probs = []
        for r in rain_levels:
            sample = base_sample.copy()
            sample[0, 2] = r  # rainfall_24h
            p = self.calibrator.predict_proba(sample)[0][1]
            probs.append(p)

        # Higher rainfall should yield >= probability
        self.assertLessEqual(probs[0], probs[1])
        self.assertLessEqual(probs[1], probs[2])
        self.assertLessEqual(probs[2], probs[3])


if __name__ == "__main__":
    unittest.main()
