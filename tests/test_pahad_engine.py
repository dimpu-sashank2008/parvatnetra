#!/usr/bin/env python3
"""
Unit and Integration Test Suite for PAHAD (Predictive AI for Hillslope Analysis & Disaster-response)
Verifies:
  1. Physical Infinite-Slope Stability FS calculations against manual ground truth
  2. North-East Himalaya empirical thresholds (ID, ED, Monga-Ganguli antecedent)
  3. Composite Risk Index (CRI) and 2-of-3 signal false-alarm suppression logic
  4. Flask REST API endpoints: POST /api/pahad/evaluate-sector & GET /api/pahad/threshold-curve
"""

import unittest
import math
from app import app
from engine.pahad_models import (
    calculate_infinite_slope_fs,
    calculate_id_threshold,
    calculate_ed_threshold,
    calculate_antecedent_threshold,
    is_empirical_threshold_exceeded,
    calculate_composite_risk_index,
    evaluate_sector_hazard,
    generate_threshold_curve_points,
    ALERT_PROTOCOLS
)


class TestPahadEngine(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        self.app.config["TESTING"] = True

    # =========================================================================
    # 1. PHYSICAL INFINITE-SLOPE STABILITY MODEL (MOHR-COULOMB)
    # =========================================================================

    def test_01_infinite_slope_known_ground_truth_stable(self):
        """
        Ground Truth Case 1: Gentle unsaturated slope
          c' = 10.0 kPa, gamma_sat = 20.0 kN/m3, gamma_w = 9.81 kN/m3
          z = 2.0 m, m = 0.0, beta = 30 deg, phi = 30 deg
          Expected FS = [10 + (20 - 0)*2*(cos 30)^2 * tan 30] / [20*2*sin 30*cos 30]
                      = [10 + 40*0.75*(1/sqrt(3))] / [40*0.5*(sqrt(3)/2)]
                      = [10 + 17.3205] / [17.3205] = 27.3205 / 17.3205 = 1.57735
        """
        res = calculate_infinite_slope_fs(
            cohesion_kpa=10.0,
            friction_deg=30.0,
            slope_deg=30.0,
            soil_depth_m=2.0,
            water_table_ratio=0.0,
            soil_sat_weight=20.0,
            water_unit_weight=9.81
        )
        self.assertAlmostEqual(res.factor_of_safety, 1.5774, places=3)
        self.assertEqual(res.classification, "STABLE")
        self.assertFalse(res.is_unstable)
        print(f"[PASS] Physical Ground Truth 1 (Stable): FS = {res.factor_of_safety} [STABLE]")

    def test_02_infinite_slope_known_ground_truth_critical(self):
        """
        Ground Truth Case 2: Saturated steep slope (Critical Unstable)
          c' = 5.0 kPa, gamma_sat = 19.5 kN/m3, gamma_w = 9.81 kN/m3
          z = 4.0 m, m = 1.0, beta = 40 deg, phi = 25 deg
          Expected FS ~= 0.4063 <= 1.0
        """
        res = calculate_infinite_slope_fs(
            cohesion_kpa=5.0,
            friction_deg=25.0,
            slope_deg=40.0,
            soil_depth_m=4.0,
            water_table_ratio=1.0,
            soil_sat_weight=19.5,
            water_unit_weight=9.81
        )
        self.assertAlmostEqual(res.factor_of_safety, 0.4063, places=3)
        self.assertEqual(res.classification, "CRITICAL_UNSTABLE")
        self.assertTrue(res.is_unstable)
        print(f"[PASS] Physical Ground Truth 2 (Critical): FS = {res.factor_of_safety} [CRITICAL_UNSTABLE]")

    def test_03_infinite_slope_known_ground_truth_watch(self):
        """
        Ground Truth Case 3: Marginal slope under partial saturation (Watch band)
          c' = 12.0 kPa, gamma_sat = 19.5 kN/m3, gamma_w = 9.81 kN/m3
          z = 3.0 m, m = 0.4, beta = 32 deg, phi = 30 deg
          Expected FS ~= 1.1945 (1.0 < FS <= 1.5)
        """
        res = calculate_infinite_slope_fs(
            cohesion_kpa=12.0,
            friction_deg=30.0,
            slope_deg=32.0,
            soil_depth_m=3.0,
            water_table_ratio=0.4,
            soil_sat_weight=19.5,
            water_unit_weight=9.81
        )
        self.assertAlmostEqual(res.factor_of_safety, 1.1945, places=3)
        self.assertEqual(res.classification, "WATCH")
        self.assertFalse(res.is_unstable)
        print(f"[PASS] Physical Ground Truth 3 (Watch): FS = {res.factor_of_safety} [WATCH]")

    # =========================================================================
    # 2. NORTH-EAST HIMALAYA EMPIRICAL RAINFALL THRESHOLDS
    # =========================================================================

    def test_04_ne_himalaya_empirical_threshold_calculations(self):
        """
        Verifies North-East Himalaya regional empirical formulas:
          1. ID: I_thresh = 5.8294 * (D ** -0.4141)
          2. ED: E_thresh = 1.3728 * (D_days ** 1.1083)
          3. Antecedent: E_ante = -11.10 + 0.62 * D_hours
        """
        # 1-hour duration
        id_1h = calculate_id_threshold(1.0)
        self.assertAlmostEqual(id_1h, 5.8294, places=3)

        # 24-hour duration
        id_24h = calculate_id_threshold(24.0)
        expected_id_24h = 5.8294 * (24.0 ** -0.4141)
        self.assertAlmostEqual(id_24h, expected_id_24h, places=3)

        # 24-hour ED (D_days = 1.0)
        ed_24h = calculate_ed_threshold(24.0)
        self.assertAlmostEqual(ed_24h, 1.3728, places=3)

        # 72-hour ED (D_days = 3.0)
        ed_72h = calculate_ed_threshold(72.0)
        expected_ed_72h = 1.3728 * (3.0 ** 1.1083)
        self.assertAlmostEqual(ed_72h, expected_ed_72h, places=3)

        # Antecedent Moisture (Monga & Ganguli)
        ante_24h = calculate_antecedent_threshold(24.0)
        self.assertAlmostEqual(ante_24h, 3.7800, places=3)

        ante_72h = calculate_antecedent_threshold(72.0)
        self.assertAlmostEqual(ante_72h, 33.5400, places=3)

        print("[PASS] NE Himalaya empirical ID, ED, and Antecedent calculations verified.")

    def test_05_empirical_threshold_exceedance_evaluator(self):
        """
        Tests is_empirical_threshold_exceeded() under heavy storm vs gentle drizzle.
        """
        # Heavy monsoon downpour (18.5 mm/h over 6h vs threshold ~2.77 mm/h)
        storm_res = is_empirical_threshold_exceeded(rainfall_intensity_mmh=18.5, duration_hours=6.0)
        self.assertTrue(storm_res.threshold_exceeded)
        self.assertTrue(storm_res.id_exceeded)
        self.assertGreater(storm_res.exceedance_ratio, 1.0)

        # Light drizzle (0.04 mm/h over 24h = 0.96 mm vs threshold ~1.56 mm/h & 1.37 mm)
        light_res = is_empirical_threshold_exceeded(rainfall_intensity_mmh=0.04, duration_hours=24.0)
        self.assertFalse(light_res.threshold_exceeded)
        self.assertFalse(light_res.id_exceeded)
        self.assertFalse(light_res.ed_exceeded)
        self.assertLess(light_res.exceedance_ratio, 1.0)
        print("[PASS] Empirical threshold exceedance detection verified.")

    # =========================================================================
    # 3. COMPOSITE RISK INDEX (CRI) & 2-OF-3 SIGNAL FALSE ALARM SUPPRESSION
    # =========================================================================

    def test_06_cri_bands_classification(self):
        """
        Verifies standard CRI bands (LOW, MODERATE, HIGH, VERY_HIGH).
        """
        # LOW (CRI < 20)
        low_res = calculate_composite_risk_index(
            static_susceptibility=0.1,
            dynamic_rainfall_prob=0.1,
            ground_anomaly_score=0.0,
            vulnerability_score=0.2,
            physical_fs=1.8,
            empirical_threshold_exceeded=False,
            ml_probability=0.1
        )
        self.assertEqual(low_res.alert_band, "LOW")
        self.assertLess(low_res.raw_cri, 20.0)

        # MODERATE (20 <= CRI < 40)
        mod_res = calculate_composite_risk_index(
            static_susceptibility=0.4,
            dynamic_rainfall_prob=0.4,
            ground_anomaly_score=0.2,
            vulnerability_score=0.6,
            physical_fs=1.4,
            empirical_threshold_exceeded=False,
            ml_probability=0.4
        )
        self.assertEqual(mod_res.alert_band, "MODERATE")
        self.assertTrue(20.0 <= mod_res.raw_cri < 40.0)

        # HIGH (40 <= CRI < 60)
        high_res = calculate_composite_risk_index(
            static_susceptibility=0.6,
            dynamic_rainfall_prob=0.6,
            ground_anomaly_score=0.5,
            vulnerability_score=0.8,
            physical_fs=1.2,
            empirical_threshold_exceeded=False,
            ml_probability=0.6
        )
        self.assertEqual(high_res.alert_band, "HIGH")
        self.assertTrue(40.0 <= high_res.raw_cri < 60.0)

        # VERY_HIGH (60 <= CRI < 80)
        vh_res = calculate_composite_risk_index(
            static_susceptibility=0.8,
            dynamic_rainfall_prob=0.8,
            ground_anomaly_score=0.6,
            vulnerability_score=0.9,
            physical_fs=1.1,
            empirical_threshold_exceeded=False,
            ml_probability=0.75
        )
        self.assertEqual(vh_res.alert_band, "VERY_HIGH")
        self.assertTrue(60.0 <= vh_res.raw_cri < 80.0)
        print("[PASS] Standard CRI bands (LOW, MODERATE, HIGH, VERY_HIGH) verified.")

    def test_07_false_alarm_suppression_single_outlier_downgrades(self):
        """
        Crucial Safety Invariant:
        If raw CRI >= 80, but fewer than 2 of the 3 independent signals agree:
          1) FS <= 1.0
          2) Empirical threshold exceeded
          3) ML probability > 0.8
        Then auto-downgrade alert to VERY_HIGH (Orange/Watch) to prevent costly false sirens.
        """
        # Case A: Only ML probability > 0.8 is high, but FS = 1.6 (stable) and rain did not breach threshold
        # H = 0.40*0.95 + 0.35*0.95 + 0.25*0.90 = 0.9375; V = 0.95 -> raw CRI = 89.06 >= 80
        outlier_res = calculate_composite_risk_index(
            static_susceptibility=0.95,
            dynamic_rainfall_prob=0.95,
            ground_anomaly_score=0.90,
            vulnerability_score=0.95,
            physical_fs=1.6,                       # NOT triggered (> 1.0)
            empirical_threshold_exceeded=False,    # NOT triggered
            ml_probability=0.85                    # TRIGGERED (> 0.8) [Only 1 signal]
        )

        self.assertGreaterEqual(outlier_res.raw_cri, 80.0)
        self.assertEqual(outlier_res.signals_triggered, 1)
        self.assertTrue(outlier_res.downgraded)
        self.assertEqual(outlier_res.alert_band, "VERY_HIGH")
        self.assertLessEqual(outlier_res.final_cri, 79.9)
        self.assertIn("Auto-downgraded from EXTREME to VERY_HIGH", outlier_res.downgrade_reason)
        print(f"[PASS] False Alarm Suppression verified: 1 signal outlier auto-downgraded to {outlier_res.alert_band}.")

    def test_08_two_of_three_agreement_retains_extreme_alert(self):
        """
        When 2 or more independent signals confirm instability, EXTREME (Red) alert is retained:
          Signal 1 (FS <= 1.0): True
          Signal 2 (Empirical exceeded): True
          Signal 3 (ML > 0.8): False
        """
        confirmed_res = calculate_composite_risk_index(
            static_susceptibility=0.95,
            dynamic_rainfall_prob=0.95,
            ground_anomaly_score=0.90,
            vulnerability_score=0.95,
            physical_fs=0.85,                      # TRIGGERED (FS <= 1.0)
            empirical_threshold_exceeded=True,     # TRIGGERED
            ml_probability=0.75                    # NOT triggered (<= 0.8) [2 signals total]
        )

        self.assertGreaterEqual(confirmed_res.raw_cri, 80.0)
        self.assertEqual(confirmed_res.signals_triggered, 2)
        self.assertFalse(confirmed_res.downgraded)
        self.assertEqual(confirmed_res.alert_band, "EXTREME")
        self.assertTrue(confirmed_res.is_extreme)
        self.assertTrue(confirmed_res.protocol["evacuation_required"])
        print("[PASS] 2-of-3 Signal Confirmation retains EXTREME alert and evacuation protocol.")

    # =========================================================================
    # 4. REST API ENDPOINT INTEGRATION TESTS
    # =========================================================================

    def test_09_api_evaluate_sector_post(self):
        """
        Tests POST /api/pahad/evaluate-sector with sample corridor payload.
        """
        payload = {
            "sector_id": "SK-NH10-KM48",
            "slope_deg": 41.5,
            "cohesion_kpa": 12.0,
            "friction_deg": 28.0,
            "soil_depth_m": 4.5,
            "water_table_ratio": 0.85,
            "soil_sat_weight": 19.5,
            "rainfall_intensity_mmh": 18.2,
            "duration_hours": 6.0,
            "static_susceptibility": 0.85,
            "ml_probability": 0.88,
            "vulnerability_score": 0.95
        }

        resp = self.client.post(
            "/api/pahad/evaluate-sector",
            json=payload,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["sector_id"], "SK-NH10-KM48")
        self.assertIn("physical_model", data)
        self.assertIn("empirical_thresholds", data)
        self.assertIn("composite_risk", data)
        self.assertIn("protocol", data)

        # Inspect physical results
        pm = data["physical_model"]
        self.assertIn(pm["classification"], ["STABLE", "WATCH", "CRITICAL_UNSTABLE"])
        self.assertIsInstance(pm["factor_of_safety"], float)

        # Inspect empirical results
        em = data["empirical_thresholds"]
        self.assertTrue(em["threshold_exceeded"])
        self.assertGreater(em["exceedance_ratio"], 1.0)

        # Inspect CRI and protocols
        cri = data["composite_risk"]
        self.assertIn("alert_band", cri)
        self.assertIn("signals_triggered", cri)
        self.assertIn("actions", data["protocol"])
        print(f"[PASS] POST /api/pahad/evaluate-sector returned HTTP 200 with alert band: {cri['alert_band']}.")

    def test_10_api_evaluate_sector_bad_request(self):
        """
        Verifies POST /api/pahad/evaluate-sector returns HTTP 400 when body is missing.
        """
        resp = self.client.post(
            "/api/pahad/evaluate-sector",
            data="",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data["status"], "ERROR")
        print("[PASS] Empty payload correctly rejected with HTTP 400.")

    def test_11_api_threshold_curve_get(self):
        """
        Tests GET /api/pahad/threshold-curve returning 1h to 72h reference points.
        """
        resp = self.client.get("/api/pahad/threshold-curve?min_hours=1&max_hours=72&step_hours=1")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("id_curve", data)
        self.assertIn("ed_curve", data)
        self.assertIn("antecedent_curve", data)
        self.assertIn("points", data)
        self.assertEqual(len(data["points"]), 72)
        self.assertEqual(data["points"][0]["duration_hours"], 1.0)
        self.assertEqual(data["points"][-1]["duration_hours"], 72.0)
        print(f"[PASS] GET /api/pahad/threshold-curve returned HTTP 200 with {len(data['points'])} curve points.")


if __name__ == "__main__":
    unittest.main()
