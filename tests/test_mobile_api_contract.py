# -*- coding: utf-8 -*-
"""
tests/test_mobile_api_contract.py
=================================
PARVAT NETRA • Mobile API Contract Test Suite
Validates backend response schemas against Flutter mobile client models
(PahadRiskSnapshot, FieldReport, AlertModel, ShelterModel).
Problem Statement ID: 26001 (Smart India Hackathon)
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app


class TestMobileApiContract(unittest.TestCase):
    """Validates contract compliance for mobile endpoints."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_pahad_risk_snapshot_contract(self):
        """Verify /api/pahad/evaluate-sector returns fields required by PahadRiskSnapshot."""
        payload = {"sector_id": "S14"}
        res = self.client.post(
            "/api/pahad/evaluate-sector",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # Contract fields required by mobile PahadRiskSnapshot.fromJson
        self.assertIn("sector_id", data)
        self.assertIn("composite_risk_score", data)
        self.assertIn("alert_band", data)
        self.assertIn("factor_of_safety", data)
        self.assertIn("confidence", data)
        self.assertIn("provenance", data)

        self.assertIsInstance(data["composite_risk_score"], (int, float))
        self.assertIsInstance(data["factor_of_safety"], (int, float))

    def test_02_dynamic_forecast_contract(self):
        """Verify /api/pahad/dynamic-forecast returns multi-horizon probability forecast."""
        payload = {
            "sector_id": "S14",
            "rainfall_series": [12.0, 18.5, 24.0, 42.0, 68.0, 85.0],
            "antecedent_moisture": 0.82
        }
        res = self.client.post(
            "/api/pahad/dynamic-forecast",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("probabilities", data)

    def test_03_active_alerts_contract(self):
        """Verify /api/alerts/active returns alert list conforming to AlertModel."""
        res = self.client.get("/api/alerts/active")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(isinstance(data, list) or "alerts" in data)

    def test_04_weather_current_contract(self):
        """Verify /api/weather/current returns meteorological observations."""
        res = self.client.get("/api/weather/current?region=Sikkim")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("rainfall_24h", data)
        self.assertIn("provenance", data)

    def test_05_seismic_recent_contract(self):
        """Verify /api/seismic/recent returns seismic events."""
        res = self.client.get("/api/seismic/recent")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("status") in ("SUCCESS", "OPERATIONAL", "CACHED", "SIMULATED", "LIVE"))

    def test_06_shelters_contract(self):
        """Verify /api/shelters returns evacuation facilities matching ShelterModel."""
        res = self.client.get("/api/shelters")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertIn("shelters", data)
        self.assertIsInstance(data["shelters"], list)
        self.assertGreaterEqual(len(data["shelters"]), 1)

        first_shelter = data["shelters"][0]
        self.assertIn("name", first_shelter)
        self.assertIn("capacity_people", first_shelter)
        self.assertIn("lat", first_shelter)
        self.assertIn("lon", first_shelter)

    def test_07_safe_route_contract(self):
        """Verify /api/routing/safe-route returns primary vs recommended bypass route."""
        res = self.client.get("/api/routing/safe-route?gvw_class=LIGHT_UTILITY")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertIn("primary_corridor", data)
        self.assertIn("recommended_route", data)

        rec = data["recommended_route"]
        self.assertIn("name", rec)
        self.assertIn("status", rec)
        self.assertIn("estimated_distance_km", rec)
        self.assertIn("estimated_time_hours", rec)
        self.assertIn("hazard_exposure", rec)

    def test_08_field_report_submission_and_sync(self):
        """Verify mobile field report ingestion via single and batch endpoints."""
        report_payload = {
            "local_id": "PN-MOBILE-TEST-99881",
            "hazard_type": "rockfall",
            "severity": "HIGH",
            "latitude": 27.2458,
            "longitude": 88.5124,
            "description": "Talus rockfall accumulation along NH-10 Km 48.",
            "reporter_role": "Field Officer",
            "created_at": "2026-09-09T14:32:00Z"
        }

        # Test single submit
        res1 = self.client.post(
            "/api/reports/submit",
            data=json.dumps(report_payload),
            content_type="application/json"
        )
        self.assertIn(res1.status_code, (200, 201))
        data1 = res1.get_json()
        self.assertIn(data1.get("status"), ("SUCCESS", "SYNCED"))

        # Test batch sync
        batch_payload = {
            "device_id": "MOBILE-FLUTTER-EMULATOR",
            "client_timestamp": "2026-09-09T14:35:00Z",
            "reports": [report_payload]
        }
        res2 = self.client.post(
            "/api/sync/field-reports",
            data=json.dumps(batch_payload),
            content_type="application/json"
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertIn(data2.get("status"), ("SUCCESS", "SYNCED"))
        self.assertGreaterEqual(data2.get("synced_count", 0), 1)

    def test_09_offline_manifest_contract(self):
        """Verify mobile offline manifest retrieval."""
        res = self.client.get("/api/geospatial/offline-manifest")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertIn("datasets", data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
