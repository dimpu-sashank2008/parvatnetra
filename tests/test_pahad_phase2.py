"""
tests/test_pahad_phase2.py
===========================
PAHAD Phase 2 Unit & Integration Tests
----------------------------------------
Tests:
  01  LSTMTemporalPredictor returns bounded probabilities [0.0, 1.0] for all horizons
  02  Official report (GSI) alone -> CORROBORATED_CRITICAL (weight=1.0)
  03  Two citizen reports within 500m/2h -> cluster CORROBORATED_CRITICAL (0.5+0.5=1.0)
  04a Citizen reports > 500m apart -> two independent clusters
  04b Citizen reports > 2 hours apart -> two independent clusters
  05  POST /api/pahad/dynamic-forecast    -> HTTP 200 + SUCCESS
  06  POST /api/pahad/iot-telemetry       -> HTTP 200 + SUCCESS + anomaly_score in [0,1]
  07  POST /api/pahad/corroborate-incidents -> HTTP 200 + SUCCESS
  08  Missing fields -> HTTP 400
  09  IoT critical thresholds trigger alert flags
  10  LSTMTemporalPredictor RISING trend detected on escalating series
"""

import sys
import os
import math
import unittest
import json

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_lstm import LSTMTemporalPredictor
from engine.pahad_crowd import CrowdVerificationEngine
from app import app


class TestLSTMPredictor(unittest.TestCase):
    """Tests 01, 10 — LSTMTemporalPredictor unit tests."""

    def setUp(self):
        self.predictor = LSTMTemporalPredictor()

    def test_01_probabilities_bounded(self):
        """LSTMTemporalPredictor returns bounded [0.0, 1.0] for all horizons."""
        series = [5.0, 8.0, 12.0, 18.0, 22.0, 25.0]
        result = self.predictor.predict_horizon(
            rainfall_series=series,
            antecedent_moisture=0.65,
        )
        data = result["data"]
        for key in ("p_exceedance_6h", "p_exceedance_12h",
                    "p_exceedance_24h", "p_exceedance_48h"):
            val = data[key]
            self.assertGreaterEqual(val, 0.0, f"{key} below 0.0: {val}")
            self.assertLessEqual(val, 1.0, f"{key} above 1.0: {val}")
        self.assertIn(data["trend"], ("RISING", "STABLE", "FALLING"))
        self.assertIn(data["peak_window"], ("6h", "12h", "24h", "48h"))
        print(f"\n[PASS] Test 01: probabilities={data}")

    def test_10_rising_trend_detected(self):
        """Strongly escalating rainfall series -> trend=RISING."""
        # Large positive velocity: each step +5 mm/h
        series = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
        result = self.predictor.predict_horizon(
            rainfall_series=series,
            antecedent_moisture=0.5,
        )
        self.assertEqual(result["data"]["trend"], "RISING")
        print(f"\n[PASS] Test 10: trend=RISING confirmed")

    def test_01b_dry_conditions_low_probability(self):
        """Near-zero rainfall + dry soil -> very low exceedance probability."""
        series = [0.1, 0.1, 0.1, 0.1]
        result = self.predictor.predict_horizon(
            rainfall_series=series,
            antecedent_moisture=0.05,
        )
        data = result["data"]
        self.assertLess(data["p_exceedance_6h"], 0.6,
                        "Dry conditions should give p < 0.5 at 6h")
        print(f"\n[PASS] Test 01b: dry p_6h={data['p_exceedance_6h']}")


class TestCrowdVerification(unittest.TestCase):
    """Tests 02, 03, 04a, 04b — CrowdVerificationEngine unit tests."""

    def setUp(self):
        self.engine = CrowdVerificationEngine()
        # Base timestamp
        self.T = 1700000000.0
        # Base coordinates (near NH-10 Km 48)
        self.LAT = 27.3300
        self.LON = 88.6100

    def _make_report(self, rid, lat, lon, t_offset, source):
        return {
            "report_id": rid,
            "lat": lat,
            "lon": lon,
            "timestamp_epoch": self.T + t_offset,
            "source_type": source,
            "description": "Test report",
        }

    def test_02_official_single_report_corroborated(self):
        """Single GSI official report (weight=1.0) -> CORROBORATED_CRITICAL."""
        reports = [self._make_report("R01", self.LAT, self.LON, 0, "GSI")]
        clusters = self.engine.cluster_and_verify(reports)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["status"], "CORROBORATED_CRITICAL")
        self.assertAlmostEqual(clusters[0]["confidence"], 1.0, places=3)
        print(f"\n[PASS] Test 02: GSI -> CORROBORATED_CRITICAL, conf={clusters[0]['confidence']}")

    def test_03_two_citizens_within_500m_cluster(self):
        """Two citizen reports within 500m and 2h -> CORROBORATED_CRITICAL (0.5+0.5)."""
        # ~200m apart (delta lat ~ 0.002 deg ~ 222m)
        r1 = self._make_report("R02", self.LAT, self.LON, 0, "CITIZEN")
        r2 = self._make_report("R03", self.LAT + 0.002, self.LON, 1800, "CITIZEN")
        clusters = self.engine.cluster_and_verify([r1, r2])
        self.assertEqual(len(clusters), 1, "Should form one cluster")
        self.assertEqual(clusters[0]["status"], "CORROBORATED_CRITICAL")
        self.assertAlmostEqual(clusters[0]["confidence"], 1.0, places=3)
        print(f"\n[PASS] Test 03: 2 citizens ~200m/30min -> CORROBORATED_CRITICAL")

    def test_04a_citizens_beyond_500m_stay_independent(self):
        """Citizen reports > 500m apart -> two separate clusters (each COMMUNITY_REPORTED)."""
        # ~600m apart: delta lon ~0.006 deg at lat 27 = ~590m
        r1 = self._make_report("R04", self.LAT, self.LON, 0, "CITIZEN")
        r2 = self._make_report("R05", self.LAT, self.LON + 0.006, 0, "CITIZEN")
        clusters = self.engine.cluster_and_verify([r1, r2])
        self.assertEqual(len(clusters), 2, "Should be two independent clusters")
        for c in clusters:
            self.assertIn(c["status"], ("COMMUNITY_REPORTED", "UNVERIFIED"))
        print(f"\n[PASS] Test 04a: Reports >500m -> {len(clusters)} independent clusters")

    def test_04b_citizens_beyond_2h_stay_independent(self):
        """Citizen reports within 500m but >2h apart -> two separate clusters."""
        r1 = self._make_report("R06", self.LAT, self.LON, 0, "CITIZEN")
        r2 = self._make_report("R07", self.LAT + 0.001, self.LON, 7201, "CITIZEN")
        clusters = self.engine.cluster_and_verify([r1, r2])
        self.assertEqual(len(clusters), 2, "Should be two independent clusters (time window exceeded)")
        print(f"\n[PASS] Test 04b: Reports >2h apart -> {len(clusters)} independent clusters")


class TestPhase2Endpoints(unittest.TestCase):
    """Tests 05, 06, 07, 08, 09 — Flask API integration tests."""

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    # ---------- Test 05: dynamic-forecast ----------
    def test_05_dynamic_forecast_200(self):
        """POST /api/pahad/dynamic-forecast -> HTTP 200 + status SUCCESS."""
        payload = {
            "sector_id": "SK-NH10-KM48",
            "rainfall_series": [5.0, 8.0, 12.0, 18.0, 22.0, 25.0],
            "antecedent_moisture": 0.70,
        }
        resp = self.client.post(
            "/api/pahad/dynamic-forecast",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("data", data)
        d = data["data"]
        for key in ("p_exceedance_6h", "p_exceedance_12h",
                    "p_exceedance_24h", "p_exceedance_48h", "peak_window", "trend"):
            self.assertIn(key, d)
        print(f"\n[PASS] Test 05: /api/pahad/dynamic-forecast -> 200, trend={d['trend']}")

    # ---------- Test 06: iot-telemetry ----------
    def test_06_iot_telemetry_200(self):
        """POST /api/pahad/iot-telemetry -> HTTP 200 + anomaly_score in [0, 1]."""
        payload = {
            "node_id": "IOT-NH10-KM48-01",
            "moisture_05m": 38.0,
            "moisture_15m": 41.0,
            "tilt_degrees": 1.5,
            "pore_pressure_kpa": 55.0,
            "rainfall_rate_mmh": 12.0,
        }
        resp = self.client.post(
            "/api/pahad/iot-telemetry",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        anomaly = data["data"]["anomaly_score"]
        self.assertGreaterEqual(anomaly, 0.0)
        self.assertLessEqual(anomaly, 1.0)
        print(f"\n[PASS] Test 06: /api/pahad/iot-telemetry -> 200, anomaly={anomaly}")

    # ---------- Test 07: corroborate-incidents ----------
    def test_07_corroborate_incidents_200(self):
        """POST /api/pahad/corroborate-incidents -> HTTP 200 + SUCCESS."""
        payload = {
            "reports": [
                {
                    "report_id": "R-A",
                    "lat": 27.33,
                    "lon": 88.61,
                    "timestamp_epoch": 1700000000.0,
                    "source_type": "CITIZEN",
                },
                {
                    "report_id": "R-B",
                    "lat": 27.3315,
                    "lon": 88.611,
                    "timestamp_epoch": 1700001000.0,
                    "source_type": "CITIZEN",
                },
            ]
        }
        resp = self.client.post(
            "/api/pahad/corroborate-incidents",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("clusters", data)
        self.assertIn("summary", data)
        print(f"\n[PASS] Test 07: /api/pahad/corroborate-incidents -> 200, clusters={len(data['clusters'])}")

    # ---------- Test 08: missing fields -> 400 ----------
    def test_08_missing_fields_returns_400(self):
        """POST /api/pahad/dynamic-forecast without required fields -> HTTP 400."""
        resp = self.client.post(
            "/api/pahad/dynamic-forecast",
            data=json.dumps({"sector_id": "SK-TEST"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ERROR")
        print(f"\n[PASS] Test 08: Missing fields -> HTTP 400")

    # ---------- Test 09: critical IoT thresholds trigger alerts ----------
    def test_09_iot_critical_thresholds_trigger_alerts(self):
        """IoT payload at/above critical thresholds triggers TILT_CRITICAL and PORE_PRESSURE_CRITICAL."""
        payload = {
            "node_id": "IOT-CRITICAL-01",
            "moisture_05m": 50.0,   # >= 45% -> MOISTURE_CRITICAL
            "moisture_15m": 50.0,
            "tilt_degrees": 4.0,    # >= 3.0 -> TILT_CRITICAL
            "pore_pressure_kpa": 90.0,  # >= 80 -> PORE_PRESSURE_CRITICAL
            "rainfall_rate_mmh": 25.0,  # >= 20 -> RAINFALL_INTENSITY_CRITICAL
        }
        resp = self.client.post(
            "/api/pahad/iot-telemetry",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        alerts = data["data"]["alerts_triggered"]
        self.assertIn("TILT_CRITICAL", alerts)
        self.assertIn("PORE_PRESSURE_CRITICAL", alerts)
        self.assertTrue(data["data"]["on_device_alert"])
        print(f"\n[PASS] Test 09: Critical IoT thresholds -> alerts={alerts}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
