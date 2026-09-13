# -*- coding: utf-8 -*-
"""
tests/test_live_inference.py
============================
PARVAT NETRA • PAHAD AI — Phase 5 Live Inference Pipeline Tests
---------------------------------------------------------------
Tests the complete live inference pipeline:
  - Feature collection and provenance tracking
  - FoS calculation integration
  - Event probability prediction
  - PAHAD fusion (CRI)
  - Alert eligibility (2-of-3 corroboration rule)
  - Data quality scoring
  - Multi-horizon forecast
  - Flask API endpoints

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import sys
import json
import unittest
from typing import Dict, Any

# Force demo mode — tests must not require live API credentials
os.environ["PAHAD_DEMO_MODE"] = "1"
os.environ["PARVAT_TESTING"] = "1"
os.environ["DRY_RUN"] = "true"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

# Reference sector for tests — real corridor from historical_landslides_ner.csv
_SECTOR = "SK-NH10-KM48"
_LAT = 27.33
_LON = 88.61

# High-risk feature set (mirrors EV-01)
HIGH_RISK_FEATURES = {
    "rainfall_24h": 185.0,
    "soil_moisture": 0.54,
    "pore_pressure_kpa": 28.2,
    "tilt_deg": 4.1,
    "ground_displacement_mm": 48.0,
    "slope_deg": 42.0,
    "elevation_m": 890.0,
}

# Low-risk feature set (dry season stable control)
LOW_RISK_FEATURES = {
    "rainfall_24h": 20.0,
    "soil_moisture": 0.25,
    "pore_pressure_kpa": 5.0,
    "tilt_deg": 1.0,
    "ground_displacement_mm": 2.0,
    "slope_deg": 42.0,
    "elevation_m": 890.0,
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. LIVE INFERENCE ENGINE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestLiveInferenceEngine(unittest.TestCase):
    """Test the run_live_inference() function directly."""

    @classmethod
    def setUpClass(cls):
        try:
            import engine.pahad_live_inference as _m
            cls._inference_module = _m
            cls.available = True
        except ImportError as exc:
            cls.available = False
            cls.skip_reason = str(exc)

    def _skip(self):
        if not self.available:
            self.skipTest(f"Live inference not importable: {getattr(self, 'skip_reason', '')}")

    def _run(self, features: Dict[str, Any] = None) -> Dict[str, Any]:
        result = self._inference_module.run_live_inference(
            sector_id=_SECTOR,
            latitude=_LAT,
            longitude=_LON,
            forecast_horizon_hours=24,
            override_features=features
        )
        return result.to_dict()


    def test_inference_returns_dict(self):
        """run_live_inference must always return a LiveInferenceResult."""
        self._skip()
        result = self._run()
        self.assertIsInstance(result, dict)

    def test_event_probability_in_bounds(self):
        """Event probability must be in [0.0, 1.0]."""
        self._skip()
        result = self._run()
        prob = result.get("event_probability", -1)
        self.assertGreaterEqual(prob, 0.0, "Probability must be >= 0")
        self.assertLessEqual(prob, 1.0, "Probability must be <= 1")

    def test_fos_in_physical_bounds(self):
        """FoS must be physically meaningful (0 < FoS <= 99)."""
        self._skip()
        result = self._run(LOW_RISK_FEATURES)
        fos = result.get("fos_physical", -1)
        self.assertGreater(fos, 0.0, "FoS must be positive")
        self.assertLessEqual(fos, 99.0, "FoS must be <= 99")

    def test_fos_status_set(self):
        """fos_status must be one of the canonical values."""
        self._skip()
        result = self._run()
        valid_statuses = {"STABLE", "MARGINAL_SAFE", "MARGINAL", "CRITICAL", "FAILED"}
        self.assertIn(result.get("fos_status"), valid_statuses)

    def test_cri_in_bounds(self):
        """CRI must be in [0, 100]."""
        self._skip()
        result = self._run()
        cri = result.get("cri", -1)
        self.assertGreaterEqual(cri, 0.0, "CRI must be >= 0")
        self.assertLessEqual(cri, 100.0, "CRI must be <= 100")

    def test_risk_band_set(self):
        """risk_band must be a non-empty string."""
        self._skip()
        result = self._run()
        self.assertIsInstance(result.get("risk_band"), str)
        self.assertTrue(len(result.get("risk_band", "")) > 0)

    def test_sector_id_preserved(self):
        """Sector ID from input must be echoed in result."""
        self._skip()
        result = self._run()
        self.assertEqual(result.get("sector_id"), _SECTOR)

    def test_timestamp_utc_set(self):
        """Result must contain a non-empty UTC timestamp."""
        self._skip()
        result = self._run()
        ts = result.get("timestamp_utc", "")
        self.assertTrue(len(ts) > 10, f"Timestamp too short: {ts}")
        self.assertIn("T", ts)  # ISO 8601 format

    def test_demo_mode_flag(self):
        """In PAHAD_DEMO_MODE=1, demo_mode must be True."""
        self._skip()
        result = self._run()
        self.assertTrue(result.get("demo_mode"), "demo_mode must be True in demo mode")

    def test_feature_provenance_list(self):
        """feature_provenance must be a non-empty list."""
        self._skip()
        result = self._run()
        prov = result.get("feature_provenance", [])
        self.assertIsInstance(prov, list)
        self.assertGreater(len(prov), 0, "feature_provenance must not be empty")

    def test_data_quality_score_in_bounds(self):
        """Data quality score must be in [0.0, 1.0]."""
        self._skip()
        result = self._run()
        dq = result.get("data_quality_score", -1)
        self.assertGreaterEqual(dq, 0.0)
        self.assertLessEqual(dq, 1.0)

    def test_inference_latency_positive(self):
        """Inference latency must be a positive number."""
        self._skip()
        result = self._run()
        lat_ms = result.get("inference_latency_ms", -1)
        self.assertGreater(lat_ms, 0.0)

    def test_forecast_horizon_echoed(self):
        """The requested horizon (24) must appear in the result."""
        self._skip()
        result = self._run()
        self.assertEqual(result.get("forecast_horizon_hours"), 24)

    def test_probability_percentage_matches_probability(self):
        """probability_percentage must equal event_probability * 100."""
        self._skip()
        result = self._run()
        prob = result.get("event_probability", 0.0)
        pct = result.get("probability_percentage", -1)
        self.assertAlmostEqual(pct, prob * 100, places=1,
            msg="probability_percentage must be event_probability * 100")


# ─────────────────────────────────────────────────────────────────────────────
# 2. ALERT ELIGIBILITY (2-OF-3 RULE) TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestAlertEligibility(unittest.TestCase):
    """Test the 2-of-3 corroboration safety rule in live inference."""

    def setUp(self):
        try:
            from engine.pahad_live_inference import _check_alert_eligibility
            self._check = _check_alert_eligibility
            self.available = True
        except ImportError:
            self.available = False

    def _skip(self):
        if not self.available:
            self.skipTest("Live inference not importable")

    def test_no_signals_met_not_eligible(self):
        """No signals met → not eligible."""
        self._skip()
        eligible, reason = self._check(fos=1.5, rainfall_24h=50.0, event_probability=0.30)
        self.assertFalse(eligible)
        self.assertIsNone(reason)

    def test_one_signal_met_not_eligible(self):
        """Only 1 signal met → still not eligible (need 2)."""
        self._skip()
        # Only FoS critical
        eligible, _ = self._check(fos=0.90, rainfall_24h=50.0, event_probability=0.30)
        self.assertFalse(eligible)

    def test_two_signals_met_eligible(self):
        """2 signals met → eligible."""
        self._skip()
        # FoS < 1.10 and rainfall > 150mm
        eligible, reason = self._check(fos=0.95, rainfall_24h=185.0, event_probability=0.30)
        self.assertTrue(eligible)
        self.assertIsNotNone(reason)

    def test_all_three_signals_met_eligible(self):
        """All 3 signals → eligible with all 3 noted."""
        self._skip()
        eligible, reason = self._check(fos=0.62, rainfall_24h=185.0, event_probability=0.85)
        self.assertTrue(eligible)
        self.assertIn("3/3", reason)

    def test_probability_only_not_eligible(self):
        """High probability alone is not enough for alert."""
        self._skip()
        eligible, _ = self._check(fos=1.5, rainfall_24h=30.0, event_probability=0.99)
        self.assertFalse(eligible)


# ─────────────────────────────────────────────────────────────────────────────
# 3. FOS COMPUTATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestFosComputation(unittest.TestCase):
    """Test the infinite slope FoS computation."""

    def setUp(self):
        try:
            from scripts.build_temporal_dataset import compute_fos
            self._fos = compute_fos
            self.available = True
        except ImportError:
            self.available = False

    def _skip(self):
        if not self.available:
            self.skipTest("build_temporal_dataset not importable")

    def test_high_slope_high_pore_low_fos(self):
        """Steep slope + high pore pressure → FoS < 1."""
        self._skip()
        fos, prov = self._fos(slope_deg=45.0, pore_pressure_kpa=35.0)
        self.assertLess(fos, 1.0, f"Steep+saturated slope should be critical, got FoS={fos}")
        self.assertEqual(prov, "MODELLED")

    def test_low_slope_low_pore_high_fos(self):
        """Gentle slope + low pore pressure → FoS > 1.5 (stable)."""
        self._skip()
        fos, prov = self._fos(slope_deg=15.0, pore_pressure_kpa=2.0)
        self.assertGreater(fos, 1.5, f"Gentle slope should be stable, got FoS={fos}")

    def test_fos_always_positive(self):
        """FoS must always be a positive finite number."""
        self._skip()
        import math
        for slope in [10.0, 20.0, 30.0, 45.0, 60.0]:
            for pore in [0.0, 10.0, 25.0, 40.0]:
                fos, _ = self._fos(slope, pore)
                self.assertGreater(fos, 0.0, f"FoS must be positive for slope={slope}, pore={pore}")
                self.assertFalse(math.isnan(fos), f"FoS must not be NaN")
                self.assertFalse(math.isinf(fos), f"FoS must not be inf")


# ─────────────────────────────────────────────────────────────────────────────
# 4. MULTI-HORIZON FORECAST TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestMultiHorizonForecast(unittest.TestCase):
    """Test the run_forecast() multi-horizon wrapper."""

    @classmethod
    def setUpClass(cls):
        try:
            import engine.pahad_live_inference as _m
            cls._inference_module = _m
            cls.available = True
        except ImportError:
            cls.available = False

    def _skip(self):
        if not self.available:
            self.skipTest("Live inference not importable")

    def test_forecast_returns_all_horizons(self):
        """Forecast must contain an entry for each requested horizon."""
        self._skip()
        result = self._inference_module.run_forecast(
            sector_id=_SECTOR,
            latitude=_LAT,
            longitude=_LON,
            horizons=[6, 24],
            override_features=HIGH_RISK_FEATURES
        )
        horizons_dict = result.get("horizons", {})
        self.assertIn("6h", horizons_dict)
        self.assertIn("24h", horizons_dict)

    def test_forecast_contains_max_risk_horizon(self):
        """Forecast must identify the max_risk_horizon."""
        self._skip()
        result = self._inference_module.run_forecast(
            sector_id=_SECTOR,
            latitude=_LAT,
            longitude=_LON,
            horizons=[6, 12, 24],
            override_features=HIGH_RISK_FEATURES
        )
        self.assertIn("max_risk_horizon", result)
        self.assertIn("max_event_probability", result)

    def test_forecast_limitation_disclosed(self):
        """Forecast must include the honest limitation statement."""
        self._skip()
        result = self._inference_module.run_forecast(
            sector_id=_SECTOR,
            latitude=_LAT,
            longitude=_LON,
            horizons=[24],
            override_features=LOW_RISK_FEATURES
        )
        limitation = result.get("model_limitation", "")
        self.assertTrue(len(limitation) > 20,
            "Forecast must include a non-empty model limitation statement")

    def test_each_horizon_has_valid_probability(self):
        """Each horizon result must have event_probability in [0, 1]."""
        self._skip()
        result = self._inference_module.run_forecast(
            sector_id=_SECTOR,
            latitude=_LAT,
            longitude=_LON,
            horizons=[6, 24],
            override_features=HIGH_RISK_FEATURES
        )
        for h_key, h_result in result.get("horizons", {}).items():
            prob = h_result.get("event_probability", -1)
            self.assertGreaterEqual(prob, 0.0, f"Horizon {h_key} probability < 0")
            self.assertLessEqual(prob, 1.0, f"Horizon {h_key} probability > 1")



# ─────────────────────────────────────────────────────────────────────────────
# 5. FLASK API ENDPOINT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestLiveInferenceFlaskAPI(unittest.TestCase):
    """Test Phase 5 Flask API endpoints via test client."""

    @classmethod
    def setUpClass(cls):
        try:
            from app import app
            app.config["TESTING"] = True
            cls.client = app.test_client()
            cls.app_available = True
        except Exception as exc:
            cls.app_available = False
            cls.skip_reason = str(exc)

    def _skip(self):
        if not self.app_available:
            self.skipTest(f"Flask app not importable: {getattr(self, 'skip_reason', '')}")

    def _post(self, path: str, body: dict):
        resp = self.client.post(
            path,
            data=json.dumps(body),
            content_type="application/json"
        )
        try:
            data = json.loads(resp.data)
        except Exception:
            data = {}
        return resp.status_code, data

    def _get(self, path: str):
        resp = self.client.get(path)
        try:
            data = json.loads(resp.data)
        except Exception:
            data = {}
        return resp.status_code, data

    def test_live_inference_post_returns_200(self):
        """POST /api/pahad/live-inference must return 200."""
        self._skip()
        status, data = self._post("/api/pahad/live-inference", {
            "sector_id": _SECTOR,
            "latitude": _LAT,
            "longitude": _LON,
            "horizon_hours": 24,
            "features": HIGH_RISK_FEATURES
        })
        self.assertEqual(status, 200, f"Expected 200, got {status}: {data.get('message', '')}")
        self.assertEqual(data.get("status"), "SUCCESS")

    def test_live_inference_contains_inference_dict(self):
        """Response must contain 'inference' dict with key fields."""
        self._skip()
        status, data = self._post("/api/pahad/live-inference", {
            "sector_id": _SECTOR,
            "latitude": _LAT,
            "longitude": _LON,
        })
        if status == 200:
            inf = data.get("inference", {})
            self.assertIn("event_probability", inf)
            self.assertIn("fos_physical", inf)
            self.assertIn("cri", inf)
            self.assertIn("risk_band", inf)
            self.assertIn("alert_eligible", inf)

    def test_live_inference_get_returns_200(self):
        """GET /api/pahad/live-inference must also work."""
        self._skip()
        status, data = self._get(
            f"/api/pahad/live-inference?sector_id={_SECTOR}&latitude={_LAT}&longitude={_LON}"
        )
        self.assertEqual(status, 200)

    def test_forecast_post_returns_200(self):
        """POST /api/pahad/forecast must return 200 with horizon results."""
        self._skip()
        status, data = self._post("/api/pahad/forecast", {
            "sector_id": _SECTOR,
            "latitude": _LAT,
            "longitude": _LON,
            "horizons": "6,24",
            "features": HIGH_RISK_FEATURES
        })
        self.assertEqual(status, 200, f"Expected 200, got {status}")
        forecast = data.get("forecast", {})
        self.assertIn("horizons", forecast)
        self.assertIn("max_risk_horizon", forecast)

    def test_data_status_returns_200(self):
        """GET /api/pahad/data-status must return 200 with stream info."""
        self._skip()
        status, data = self._get("/api/pahad/data-status")
        self.assertEqual(status, 200)
        self.assertIn("data_streams", data)
        self.assertIn("weather", data.get("data_streams", {}))
        self.assertIn("seismic", data.get("data_streams", {}))

    def test_data_status_demo_mode_flag(self):
        """GET /api/pahad/data-status must report demo_mode=True."""
        self._skip()
        status, data = self._get("/api/pahad/data-status")
        if status == 200:
            self.assertTrue(data.get("demo_mode"),
                "demo_mode must be True in PAHAD_DEMO_MODE=1 environment")

    def test_invalid_coordinates_return_422(self):
        """Non-numeric lat/lon must return 422, not 500."""
        self._skip()
        status, data = self._post("/api/pahad/live-inference", {
            "sector_id": _SECTOR,
            "latitude": "NOT_A_NUMBER",
            "longitude": _LON,
        })
        self.assertEqual(status, 422,
            f"Non-numeric coordinate should be 422, got {status}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. TEMPORAL DATASET BUILDER TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTemporalDatasetBuilder(unittest.TestCase):
    """Test the build_temporal_dataset.py script."""

    def setUp(self):
        try:
            from scripts.build_temporal_dataset import (
                process_event_record, generate_control_windows,
                compute_dataset_hash, normalize_confidence, compute_fos
            )
            self._process = process_event_record
            self._gen_controls = generate_control_windows
            self._hash = compute_dataset_hash
            self._normalize = normalize_confidence
            self._fos = compute_fos
            self.available = True
        except ImportError as exc:
            self.available = False
            self.skip_reason = str(exc)

    def _skip(self):
        if not self.available:
            self.skipTest(f"Dataset builder not importable: {getattr(self, 'skip_reason', '')}")

    def test_process_event_returns_dict(self):
        """process_event_record must return a dict with required keys."""
        self._skip()
        raw = {
            "event_id": "EV-01",
            "timestamp": "2024-10-04T06:00:00Z",
            "latitude": "27.33",
            "longitude": "88.61",
            "state": "Sikkim",
            "district": "Pakyong",
            "sector_id": "SK-NH10-KM48",
            "geographic_group": "sikkim_teesta_corridor",
            "event_label": "1",
            "rainfall_trigger_mm": "185.0",
            "soil_moisture": "0.54",
            "pore_pressure_kpa": "28.2",
            "tilt_deg": "4.1",
            "ground_displacement_mm": "48.0",
            "slope_deg": "42.0",
            "elevation_m": "890.0",
            "source": "GSI Pakyong Field Inspection",
            "source_confidence": "HIGH",
            "provenance": "[HISTORICAL]",
        }
        rec = self._process(raw)
        self.assertIn("event_id", rec)
        self.assertIn("fos", rec)
        self.assertIn("event_label", rec)
        self.assertEqual(rec["event_label"], 1)
        self.assertIsNotNone(rec["fos"])
        self.assertGreater(float(rec["fos"]), 0.0)

    def test_fos_provenance_is_modelled(self):
        """FoS must have _prov_fos = MODELLED."""
        self._skip()
        raw = {
            "event_id": "EV-01", "slope_deg": "42.0",
            "pore_pressure_kpa": "28.2", "event_label": "1",
            "source": "GSI Test", "source_confidence": "HIGH",
        }
        rec = self._process(raw)
        self.assertEqual(rec.get("_prov_fos"), "MODELLED")

    def test_seismic_and_ndvi_missing(self):
        """Seismic and NDVI must be marked MISSING for historical events."""
        self._skip()
        raw = {
            "event_id": "EV-01", "slope_deg": "42.0",
            "pore_pressure_kpa": "28.2", "event_label": "1",
            "source": "GSI Test", "source_confidence": "HIGH",
        }
        rec = self._process(raw)
        self.assertIsNone(rec.get("seismic_magnitude"))
        self.assertIsNone(rec.get("ndvi_anomaly"))
        self.assertEqual(rec.get("_prov_seismic"), "MISSING")
        self.assertEqual(rec.get("_prov_ndvi"), "MISSING")

    def test_normalize_confidence_string(self):
        """String confidence values must map to correct floats."""
        self._skip()
        self.assertEqual(self._normalize("VERY_HIGH"), 0.95)
        self.assertEqual(self._normalize("HIGH"), 0.80)
        self.assertEqual(self._normalize("MEDIUM"), 0.65)
        self.assertEqual(self._normalize("LOW"), 0.40)

    def test_normalize_confidence_numeric(self):
        """Numeric confidence values must pass through unchanged."""
        self._skip()
        self.assertAlmostEqual(self._normalize(0.80), 0.80)
        self.assertAlmostEqual(self._normalize("0.70"), 0.70)

    def test_dataset_hash_reproducible(self):
        """Same records produce same hash."""
        self._skip()
        records = [{"event_id": "EV-01", "event_label": 1, "timestamp": "2024-01-01"}]
        h1 = self._hash(records)
        h2 = self._hash(records)
        self.assertEqual(h1, h2)

    def test_controls_have_label_zero(self):
        """Generated controls must all have event_label=0."""
        self._skip()
        # Build a minimal event list
        events = [{
            "event_id": "EV-01",
            "timestamp": "2024-10-04T06:00:00Z",
            "latitude": 27.33, "longitude": 88.61,
            "state": "Sikkim", "district": "Pakyong",
            "sector_id": "SK-NH10-KM48",
            "geographic_group": "sikkim_teesta_corridor",
            "slope_deg": 42.0, "elevation_m": 890.0,
        }]
        controls = self._gen_controls(events, controls_per_event=1)
        for ctrl in controls:
            self.assertEqual(ctrl.get("event_label"), 0,
                f"Control {ctrl.get('event_id')} must have label=0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
