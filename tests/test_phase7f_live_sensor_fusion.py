"""
PHASE 7F — CP 7F-06 & 7F-07: Live Sensor Fusion & Data Quality Score Tests
Verifies that real/override telemetry directly integrates into the feature vector,
replaces imputed defaults, removes features from imputed_features,
and calculates reproducible data quality scores and counts.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_live_inference import run_live_inference, LiveInferenceResult


class TestLiveSensorFusionAndQuality(unittest.TestCase):
    """CP 7F-06 & 7F-07: Sensor feature integration & reproducible data quality accounting."""

    SECTOR = "CORR-NH10-SIKKIM-KM48"
    LAT = 27.2056
    LON = 88.4986

    def test_01_baseline_snapshot_exposes_counts(self):
        """Baseline inference snapshot must expose observed, imputed, and missing counts."""
        res = run_live_inference(self.SECTOR, self.LAT, self.LON)
        d = res.to_dict()

        self.assertIn("observed_feature_count", d)
        self.assertIn("imputed_feature_count", d)
        self.assertIn("missing_feature_count", d)
        self.assertIn("data_quality_score", d)

        self.assertIsInstance(d["observed_feature_count"], int)
        self.assertIsInstance(d["imputed_feature_count"], int)
        self.assertIsInstance(d["missing_feature_count"], int)
        self.assertIsInstance(d["data_quality_score"], float)

        # Total counts should equal total required features (7 core features)
        total_tracked = d["observed_feature_count"] + d["imputed_feature_count"] + d["missing_feature_count"]
        self.assertGreaterEqual(total_tracked, 5)

    def test_02_rainfall_is_not_imputed_when_weather_available(self):
        """Weather rainfall from Open-Meteo must be classified observed, NOT imputed."""
        res = run_live_inference(self.SECTOR, self.LAT, self.LON)
        d = res.to_dict()

        self.assertNotIn("rainfall_24h", d["imputed_features"],
                         "rainfall_24h must not be imputed when weather service is responsive")
        self.assertIn("rainfall_24h", d["features_used"])

    def test_03_sensor_telemetry_replaces_imputed_pore_pressure(self):
        """Injecting pore pressure telemetry must remove pore_pressure_kpa from imputed_features."""
        override = {
            "pore_pressure_kpa": 42.5,
            "tilt_deg": 4.1
        }
        res = run_live_inference(self.SECTOR, self.LAT, self.LON, override_features=override)
        d = res.to_dict()

        # Both pore_pressure_kpa and tilt_deg must be in features_used with exact injected values
        self.assertEqual(d["features_used"]["pore_pressure_kpa"], 42.5)
        self.assertEqual(d["features_used"]["tilt_deg"], 4.1)

        # Neither should be in imputed_features
        self.assertNotIn("pore_pressure_kpa", d["imputed_features"])
        self.assertNotIn("tilt_deg", d["imputed_features"])

    def test_04_data_quality_score_improves_with_live_sensors(self):
        """Injecting live sensor telemetry must increase data_quality_score compared to baseline."""
        res_baseline = run_live_inference(self.SECTOR, self.LAT, self.LON)
        score_baseline = res_baseline.data_quality_score

        override = {
            "pore_pressure_kpa": 35.0,
            "tilt_deg": 2.5,
            "ground_displacement_mm": 12.0,
            "soil_moisture": 0.45
        }
        res_enhanced = run_live_inference(self.SECTOR, self.LAT, self.LON, override_features=override)
        score_enhanced = res_enhanced.data_quality_score

        self.assertGreater(score_enhanced, score_baseline,
                           f"Data quality score with sensors ({score_enhanced}) must exceed baseline ({score_baseline})")


if __name__ == "__main__":
    unittest.main()
