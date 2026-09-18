# -*- coding: utf-8 -*-
"""
tests/test_pahad_data_fusion.py
===============================
Unit & Integration Tests for PAHAD Multi-Modal Data Fusion, Alert Safety Rules,
and Flask REST API Endpoints.
"""

import os
os.environ["PARVAT_TESTING"] = "1"

import unittest
import json

from engine.pahad_models import evaluate_pahad_fused_risk
from app import app


class TestPahadDataFusion(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_evaluate_pahad_fused_risk_output_contract(self):
        res = evaluate_pahad_fused_risk("SK-NH10-KM48")
        self.assertEqual(res["sector_id"], "SK-NH10-KM48")
        self.assertIn("cri", res)
        self.assertIn("risk_band", res)
        self.assertIn("failure_probability", res)
        self.assertIn("factor_of_safety", res)
        self.assertIn("rainfall_trigger", res)
        self.assertIn("seismic_trigger", res)
        self.assertIn("ground_anomaly", res)
        self.assertIn("data_quality", res)
        self.assertIn("signal_agreement", res)
        self.assertIn("dominant_drivers", res)
        self.assertIn("recommended_action", res)
        self.assertIn("operational_states", res)
        self.assertIn("provenance", res)
        self.assertIn("model_version", res)

        # Operational states verification
        ops = res["operational_states"]
        self.assertIn("prediction", ops)
        self.assertIn("alert_recommendation", ops)
        self.assertIn("public_alert_dispatch", ops)

    def test_alert_safety_rule_2_of_3_false_alarm_suppression(self):
        # Scenario: High raw hazard, but ONLY ML is high, while physical FoS is stable and no rain
        # (Single signal false alarm)
        overrides_single_signal = {
            "pore_water_pressure_kpa": 0.0,
            "rainfall_current_mmh": 0.0,
            "rainfall_24h_mm": 5.0,
            "slope_deg": 28.0,
            "cohesion_kpa": 30.0,
            "friction_deg": 35.0,
            "seismic_shaking_proxy_g": 0.0
        }
        res = evaluate_pahad_fused_risk("SK-NH10-KM48", overrides=overrides_single_signal)
        # Factor of safety should be stable (> 1.5)
        self.assertGreater(res["physical_fs"], 1.4)
        # Should not be EXTREME
        self.assertNotEqual(res["risk_band"], "EXTREME")
        self.assertNotEqual(res["operational_states"]["public_alert_dispatch"], "AUTHORIZED_FOR_CAP_BROADCAST")

    def test_alert_safety_rule_2_of_3_confirmed_extreme_alert(self):
        # Scenario: Severe cloudburst (180 mm rain, 25 mm/hr intensity, 35 kPa pore pressure)
        # Both Physical FoS <= 1.0 AND Rainfall I-D exceeded
        overrides_critical = {
            "pore_water_pressure_kpa": 38.0,
            "rainfall_current_mmh": 22.0,
            "rainfall_24h_mm": 175.0,
            "slope_deg": 42.0,
            "cohesion_kpa": 12.0,
            "friction_deg": 26.0,
            "seismic_shaking_proxy_g": 0.15,
            "road_criticality": 0.95
        }
        res = evaluate_pahad_fused_risk("SK-NH10-KM48", overrides=overrides_critical)
        self.assertLessEqual(res["physical_fs"], 1.0)
        self.assertTrue(res["signal_agreement"]["physical"])
        self.assertTrue(res["signal_agreement"]["rainfall"])
        self.assertGreaterEqual(res["signal_agreement"]["count"], 2)
        self.assertEqual(res["risk_band"], "EXTREME")
        self.assertEqual(res["operational_states"]["public_alert_dispatch"], "AUTHORIZED_FOR_CAP_BROADCAST")
        self.assertFalse(res["downgraded"])

    # ---------------- FLASK REST API TESTS ----------------

    def test_api_weather_endpoints(self):
        # 1. /api/weather/live
        r_live = self.client.get("/api/weather/live?sector_id=SK-NH10-KM48")
        self.assertEqual(r_live.status_code, 200)
        d_live = json.loads(r_live.data)
        self.assertIn("rainfall", d_live)
        self.assertIn("provenance", d_live)

        # 2. /api/weather/status
        r_status = self.client.get("/api/weather/status")
        self.assertEqual(r_status.status_code, 200)
        d_status = json.loads(r_status.data)
        self.assertIn("providers", d_status)

        # 3. /api/weather/climate-map
        r_cmap = self.client.get("/api/weather/climate-map")
        self.assertEqual(r_cmap.status_code, 200)
        d_cmap = json.loads(r_cmap.data)
        self.assertIn("sectors", d_cmap)

        # 4. /api/weather/forecast
        r_fc = self.client.get("/api/weather/forecast?sector_id=SK-NH10-KM48")
        self.assertEqual(r_fc.status_code, 200)
        d_fc = json.loads(r_fc.data)
        self.assertIn("forecast", d_fc)

    def test_api_seismic_endpoints(self):
        # 1. /api/seismic/latest
        r_lat = self.client.get("/api/seismic/latest")
        self.assertEqual(r_lat.status_code, 200)
        d_lat = json.loads(r_lat.data)
        self.assertIn("status", d_lat)

        # 2. /api/seismic/recent
        r_rec = self.client.get("/api/seismic/recent?limit=3")
        self.assertEqual(r_rec.status_code, 200)
        d_rec = json.loads(r_rec.data)
        self.assertIn("events", d_rec)

        # 3. /api/seismic/status
        r_stat = self.client.get("/api/seismic/status")
        self.assertEqual(r_stat.status_code, 200)
        d_stat = json.loads(r_stat.data)
        self.assertIn("geographic_bbox", d_stat)

        # 4. /api/seismic/impact
        r_imp = self.client.get("/api/seismic/impact?sector_id=SK-NH10-KM48")
        self.assertEqual(r_imp.status_code, 200)
        d_imp = json.loads(r_imp.data)
        self.assertIn("impact", d_imp)

    def test_api_pahad_fused_risk_endpoint(self):
        # POST /api/pahad/fused-risk
        payload = {
            "sector_id": "SK-NH10-KM48",
            "overrides": {
                "rainfall_24h_mm": 45.0
            }
        }
        r = self.client.post("/api/pahad/fused-risk", json=payload)
        self.assertEqual(r.status_code, 200)
        d = json.loads(r.data)
        self.assertEqual(d["sector_id"], "SK-NH10-KM48")
        self.assertIn("cri", d)
        self.assertIn("factor_of_safety", d)
        self.assertIn("operational_states", d)

    def test_api_pahad_inputs_endpoint(self):
        # GET /api/pahad/inputs/SK-NH10-KM48
        r = self.client.get("/api/pahad/inputs/SK-NH10-KM48")
        self.assertEqual(r.status_code, 200)
        d = json.loads(r.data)
        self.assertEqual(d["status"], "SUCCESS")
        self.assertIn("vector", d)


if __name__ == "__main__":
    unittest.main()
