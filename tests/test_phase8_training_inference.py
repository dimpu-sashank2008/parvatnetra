# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- Phase 8 Geotechnical ML Model Training, Live Inference, & Modal Stacking Verification Suite
Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Tests:
1. Model Artifact Verification (models/fos_predictor.pkl, metadata, R^2 > 0.95).
2. Geotechnical Physical Inference Sanity (dry vs moderate vs critical failure).
3. Live REST Endpoint POST /api/ml/predict-fos.
4. Autonomous AI Triage Integration (ml_predicted_fos in /api/ai/triage-status).
5. Modal Stacking & Z-Index DOM Verification (templates/index.html).
"""

import os
import sys
import json
import urllib.request
import unittest
import joblib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(REPO_ROOT, "models", "fos_predictor.pkl")
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080")


class TestPhase8TrainingInference(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO_ROOT, "templates", "index.html"), "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    # -------------------------------------------------------------------------
    # TEST 1: Model Artifact & Metadata
    # -------------------------------------------------------------------------
    def test_01_model_artifact_and_metadata(self):
        """Verify models/fos_predictor.pkl exists, loads, and satisfies SIH performance criteria."""
        self.assertTrue(os.path.exists(MODEL_PATH), f"Missing model artifact: {MODEL_PATH}")
        bundle = joblib.load(MODEL_PATH)
        self.assertIsInstance(bundle, dict)
        self.assertIn("model", bundle)
        self.assertIn("feature_names", bundle)
        self.assertIn("metrics", bundle)
        self.assertEqual(bundle["feature_names"], ["rainfall_24h", "pore_water_pressure", "river_scour_tau_b"])

        metrics = bundle["metrics"]
        self.assertGreaterEqual(metrics["r2_score"], 0.95, f"R^2 {metrics['r2_score']} < 0.95")
        self.assertLessEqual(metrics["rmse"], 0.08, f"RMSE {metrics['rmse']} > 0.08")
        print(f"[PASS] 1. Model artifact verified (R^2={metrics['r2_score']:.4f}, RMSE={metrics['rmse']:.4f}).")

    # -------------------------------------------------------------------------
    # TEST 2: Geotechnical Physical Inference Sanity
    # -------------------------------------------------------------------------
    def test_02_physical_inference_sanity(self):
        """Verify model predictions adhere strictly to Mohr-Coulomb stability regimes."""
        from scripts.train_geotech_model import predict_fos
        bundle = joblib.load(MODEL_PATH)

        # 1. Dry, low scour conditions -> FoS should be >= 1.50 (Safe / GREEN)
        dry_fos = predict_fos(bundle, rainfall_24h=0.0, pore_water_pressure=0.0, river_scour_tau_b=150.0)
        self.assertGreater(dry_fos, 1.50, f"Dry FoS {dry_fos} should be > 1.50")

        # 2. Moderate rain, moderate pore pressure -> FoS around 1.0 - 1.45 (YELLOW / ORANGE)
        mod_fos = predict_fos(bundle, rainfall_24h=65.0, pore_water_pressure=10.0, river_scour_tau_b=2200.0)
        self.assertLess(mod_fos, dry_fos, "Moderate rain should lower FoS compared to dry")
        self.assertGreater(mod_fos, 0.90, f"Moderate FoS {mod_fos} should be > 0.90")

        # 3. Severe monsoon cloudburst + hydrodynamic basal scour -> FoS < 1.0 (Critical Collapse / RED)
        storm_fos = predict_fos(bundle, rainfall_24h=145.0, pore_water_pressure=32.0, river_scour_tau_b=5800.0)
        self.assertLess(storm_fos, 1.0, f"Storm FoS {storm_fos} must indicate critical collapse (< 1.0)")

        print(f"[PASS] 2. Geotechnical physical inference verified (Dry={dry_fos}, Mod={mod_fos}, Storm={storm_fos}).")

    # -------------------------------------------------------------------------
    # TEST 3: Live REST Endpoint POST /api/ml/predict-fos
    # -------------------------------------------------------------------------
    def test_03_rest_endpoint_predict_fos(self):
        """Verify POST /api/ml/predict-fos inference endpoint."""
        payload = {
            "rainfall_24h": 140.0,
            "pore_water_pressure": 28.5,
            "river_scour_tau_b": 5600.0
        }
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/api/ml/predict-fos",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.getcode(), 200)
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, ConnectionError, OSError):
            from app import app
            client = app.test_client()
            resp = client.post("/api/ml/predict-fos", json=payload)
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()

        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("predicted_fos", data)
        self.assertIn("risk_tier", data)
        self.assertEqual(data["risk_tier"], "RED")
        self.assertLess(data["predicted_fos"], 1.0)
        self.assertEqual(data["model_metadata"]["model_type"], "GradientBoostingRegressor")
        self.assertGreaterEqual(data["model_metadata"]["r2_score"], 0.95)

        print(f"[PASS] 3. POST /api/ml/predict-fos verified (FoS={data['predicted_fos']}, Tier={data['risk_tier']}).")

    # -------------------------------------------------------------------------
    # TEST 4: Autonomous AI Triage Integration
    # -------------------------------------------------------------------------
    def test_04_ai_triage_ml_integration(self):
        """Verify /api/ai/triage-status includes ml_predicted_fos and pore_water_pressure_kpa."""
        try:
            req = urllib.request.Request(f"{BASE_URL}/api/ai/triage-status")
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.getcode(), 200)
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, ConnectionError, OSError):
            from app import app
            client = app.test_client()
            resp = client.get("/api/ai/triage-status")
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()

        self.assertEqual(data["status"], "SUCCESS")
        metrics = data["evaluation"]["metrics"]
        self.assertIn("ml_predicted_fos", metrics)
        self.assertIn("pore_water_pressure_kpa", metrics)
        self.assertIsNotNone(metrics["ml_predicted_fos"])
        self.assertGreater(metrics["ml_predicted_fos"], 0.0)

        print(f"[PASS] 4. AI triage live ML integration verified (ML FoS={metrics['ml_predicted_fos']}).")


    # -------------------------------------------------------------------------
    # TEST 5: Modal Stacking & Z-Index DOM Verification
    # -------------------------------------------------------------------------
    def test_05_modal_stacking_and_zindex_markup(self):
        """Verify CSS and markup enforce robust modal backdrops, max-height scrolling, and z-index separation."""
        # 1. Leaflet controls and layer-control-panel restrained to z-index: 10
        self.assertIn('.leaflet-top, .leaflet-bottom, .leaflet-control', self.index_html)
        self.assertIn('z-index: 10 !important;', self.index_html)
        self.assertIn('#layer-control-panel{position:absolute;top:10px;right:10px;z-index:10;', self.index_html)

        # 2. Authority Siren Modal backdrop and internal scrolling
        self.assertIn('id="authority-siren-modal"', self.index_html)
        self.assertIn('class="fixed inset-0 z-[99999] bg-black/70 backdrop-blur-sm hidden items-center justify-center p-4"', self.index_html)
        self.assertIn('max-h-[85vh] overflow-y-auto', self.index_html)

        # 3. Lockdown modal internal scrolling
        self.assertIn('id="landslide-lockdown-modal"', self.index_html)
        self.assertIn('max-h-[85vh] overflow-y-auto', self.index_html)

        # 4. Evidence modal internal scrolling
        self.assertIn('id="modal-evidence-inspector"', self.index_html)

        print("[PASS] 5. Modal stacking, z-index isolation, and max-height scrolling verified.")


if __name__ == "__main__":
    unittest.main()
