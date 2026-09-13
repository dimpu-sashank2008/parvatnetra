"""
tests/test_pahad_phase4.py
===========================
PAHAD Phase 4 Unit & Integration Tests
----------------------------------------
Tests:
  01  InSARDeformationProcessor identifies tertiary creep when displacement accelerates
  02  InSARDeformationProcessor produces bounded anomaly factors in [0.0, 1.0] and computes 1/v
  03  Radar low coherence (< 0.45) correctly flags low reliability (coherence_reliable=False)
  04  InSAR steady secondary creep state (v > 15 mm/yr) vs base stable (v <= 15 mm/yr)
  05  PAHADMLOpsPipeline correctly computes meteorological metrics (POD, FAR, CSI, AUC-ROC)
  06  PAHADMLOpsPipeline registers new feedback reports and updates sample counts
  07  CriticalSectorRegistry supports state filtering across NER states
  08  CriticalSectorRegistry supports Haversine proximity search (query_nearby)
  09  POST /api/pahad/insar-deformation -> HTTP 200 + valid JSON schema
  10  POST /api/pahad/mlops/feedback-retrain -> HTTP 200 + valid verification metrics
  11  GET /api/pahad/critical-sectors (all, state-filter, proximity) -> HTTP 200
  12  Missing fields return HTTP 400
"""

import sys
import os
import unittest
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_insar import InSARDeformationProcessor, COHERENCE_THRESHOLD
from engine.pahad_mlops import PAHADMLOpsPipeline
from engine.pahad_sectors import CriticalSectorRegistry, GSI_CRITICAL_SECTORS
from app import app


class TestInSARProcessor(unittest.TestCase):
    """Tests 01, 02, 03, 04: Radar InSAR deformation and creep analysis."""

    def setUp(self):
        self.processor = InSARDeformationProcessor()

    def test_01_tertiary_creep_acceleration_identified(self):
        """Accelerating displacement series -> TERTIARY_CREEP_ACCELERATION."""
        # Accelerating series: 0 -> 2 -> 6 -> 18 -> 45 mm over 12-day intervals
        d_series = [0.0, 2.0, 6.0, 18.0, 45.0]
        t_series = [0.0, 12.0, 24.0, 36.0, 48.0]
        coherence = 0.65

        res = self.processor.analyze_slope_deformation(d_series, t_series, coherence)
        self.assertEqual(res["status"], "SUCCESS")
        data = res["data"]
        self.assertEqual(data["creep_status"], "TERTIARY_CREEP_ACCELERATION")
        self.assertGreater(data["velocity_mm_year"], 50.0)
        self.assertGreater(data["acceleration_mm_day2"], 0.0)
        self.assertGreaterEqual(data["insar_anomaly_factor"], 0.80)
        self.assertLessEqual(data["insar_anomaly_factor"], 1.0)
        print(f"\n[PASS] Test 01: Tertiary creep acceleration detected: v={data['velocity_mm_year']} mm/yr, a={data['acceleration_mm_day2']}")

    def test_02_bounded_anomaly_and_inverse_velocity(self):
        """InSAR anomaly factor is bounded [0, 1] and inverse velocity (1/v) computed."""
        d_series = [0.0, 1.0, 2.5, 4.2]
        t_series = [0.0, 10.0, 20.0, 30.0]
        res = self.processor.analyze_slope_deformation(d_series, t_series, coherence=0.55)
        data = res["data"]
        self.assertGreaterEqual(data["insar_anomaly_factor"], 0.0)
        self.assertLessEqual(data["insar_anomaly_factor"], 1.0)
        self.assertIsNotNone(data["inverse_velocity"])
        self.assertGreater(data["inverse_velocity"], 0.0)
        print(f"\n[PASS] Test 02: Inverse velocity 1/v={data['inverse_velocity']} day/mm, anomaly={data['insar_anomaly_factor']}")

    def test_03_low_coherence_flags_unreliability(self):
        """Radar coherence < 0.45 correctly flags low reliability."""
        d_series = [0.0, 5.0, 12.0, 22.0]
        t_series = [0.0, 12.0, 24.0, 36.0]
        low_coh = 0.32  # Below 0.45 threshold

        res = self.processor.analyze_slope_deformation(d_series, t_series, coherence=low_coh)
        data = res["data"]
        self.assertFalse(data["coherence_reliable"])
        self.assertEqual(data["reliability"], "LOW")

        # High coherence test
        high_res = self.processor.analyze_slope_deformation(d_series, t_series, coherence=0.72)
        self.assertTrue(high_res["data"]["coherence_reliable"])
        self.assertEqual(high_res["data"]["reliability"], "HIGH")
        print("\n[PASS] Test 03: Radar low coherence threshold (<0.45) correctly flags reliability.")

    def test_04_secondary_creep_vs_stable(self):
        """Steady secondary creep (v > 15 mm/yr) vs stable settling (v <= 15 mm/yr)."""
        # ~25 mm/yr: 2 mm in 30 days = 0.0667 mm/day * 365.25 = ~24.3 mm/yr
        d_sec = [0.0, 2.0]
        t_sec = [0.0, 30.0]
        res_sec = self.processor.analyze_slope_deformation(d_sec, t_sec, coherence=0.6)
        self.assertEqual(res_sec["data"]["creep_status"], "STEADY_SECONDARY_CREEP")

        # ~6 mm/yr: 0.5 mm in 30 days = 0.0167 mm/day * 365.25 = ~6.1 mm/yr
        d_stab = [0.0, 0.5]
        t_stab = [0.0, 30.0]
        res_stab = self.processor.analyze_slope_deformation(d_stab, t_stab, coherence=0.6)
        self.assertEqual(res_stab["data"]["creep_status"], "BASE_STABLE_OR_SETTLING")
        print("\n[PASS] Test 04: Steady secondary creep vs base stable properly classified.")


class TestMLOpsPipeline(unittest.TestCase):
    """Tests 05, 06: Continuous MLOps Retraining & Verification."""

    def setUp(self):
        self.pipeline = PAHADMLOpsPipeline(version_prefix="test.v2026")

    def test_05_meteorological_verification_metrics(self):
        """PAHADMLOpsPipeline correctly computes POD, FAR, CSI, and AUC-ROC."""
        eval_res = self.pipeline.trigger_retraining_evaluation()
        self.assertEqual(eval_res["status"], "SUCCESS")
        m = eval_res["metrics"]
        self.assertIn("pod", m)
        self.assertIn("far", m)
        self.assertIn("csi", m)
        self.assertIn("auc_roc", m)

        # Mathematical constraints: POD, FAR, CSI must be in [0, 1]
        self.assertGreaterEqual(m["pod"], 0.0)
        self.assertLessEqual(m["pod"], 1.0)
        self.assertGreaterEqual(m["far"], 0.0)
        self.assertLessEqual(m["far"], 1.0)
        self.assertGreaterEqual(m["csi"], 0.0)
        self.assertLessEqual(m["csi"], 1.0)

        # Baseline expected range for calibrated operational model
        self.assertGreater(m["pod"], 0.80, "POD should be >= 0.80 for baseline")
        self.assertLess(m["far"], 0.25, "FAR should be <= 0.25 for baseline")
        self.assertGreaterEqual(m["auc_roc"], 0.85)
        self.assertLessEqual(m["auc_roc"], 0.95)
        print(f"\n[PASS] Test 05: Verification metrics: POD={m['pod']}, FAR={m['far']}, CSI={m['csi']}, AUC={m['auc_roc']}")

    def test_06_register_feedback_and_retrain(self):
        """Registering field feedback updates corpus and advances version iteration."""
        init_eval = self.pipeline.trigger_retraining_evaluation()
        init_total = init_eval["metrics"]["total_samples"]

        # Register 3 new verified events
        reg_res = self.pipeline.register_field_verification(
            report_id="TEST-VERIF-001",
            sector_id="SK-NH10-KM48",
            verified_failure=True,
            source_tier="GSI_FIELD_TEAM",
            features={"predicted_alert": True, "cri_score": 88.0},
        )
        self.assertEqual(reg_res["status"], "SUCCESS")

        post_eval = self.pipeline.trigger_retraining_evaluation()
        self.assertEqual(post_eval["metrics"]["total_samples"], init_total + 1)
        self.assertNotEqual(init_eval["version_tag"], post_eval["version_tag"])
        print(f"\n[PASS] Test 06: MLOps buffer updated to {post_eval['metrics']['total_samples']} samples, tag: {post_eval['version_tag']}")


class TestCriticalSectorRegistry(unittest.TestCase):
    """Tests 07, 08: GSI Critical Sector Registry & Spatial Querying."""

    def setUp(self):
        self.registry = CriticalSectorRegistry()

    def test_07_state_filtering_across_ner(self):
        """CriticalSectorRegistry accurately filters sectors by state."""
        all_sec = self.registry.list_sectors()
        self.assertGreaterEqual(len(all_sec), 15)

        sikkim_sec = self.registry.list_sectors("Sikkim")
        self.assertGreaterEqual(len(sikkim_sec), 3)
        self.assertTrue(all(s["state"] == "Sikkim" for s in sikkim_sec))

        mizoram_sec = self.registry.list_sectors("Mizoram")
        self.assertGreaterEqual(len(mizoram_sec), 2)
        self.assertTrue(all(s["state"] == "Mizoram" for s in mizoram_sec))

        nagaland_sec = self.registry.list_sectors("Nagaland")
        self.assertGreaterEqual(len(nagaland_sec), 2)
        self.assertTrue(all(s["state"] == "Nagaland" for s in nagaland_sec))
        print(f"\n[PASS] Test 07: State filtering verified: Sikkim={len(sikkim_sec)}, Mizoram={len(mizoram_sec)}, Nagaland={len(nagaland_sec)}")

    def test_08_haversine_proximity_search(self):
        """Haversine proximity query returns nearby sectors within radius sorted by distance."""
        # Query near NH-10 Km 48 (27.33, 88.61) with 30 km radius
        nearby = self.registry.query_nearby(lat=27.3300, lon=88.6100, radius_km=30.0)
        self.assertGreaterEqual(len(nearby), 1)

        # Nearest sector must be SK-NH10-KM48 with distance ~0.0 km
        nearest = nearby[0]
        self.assertEqual(nearest["sector_id"], "SK-NH10-KM48")
        self.assertLess(nearest["distance_km"], 1.0)

        # Verify sorted order
        for i in range(len(nearby) - 1):
            self.assertLessEqual(nearby[i]["distance_km"], nearby[i + 1]["distance_km"])
        print(f"\n[PASS] Test 08: Proximity search found {len(nearby)} sectors; nearest is {nearest['sector_id']} ({nearest['distance_km']} km)")


class TestPhase4Endpoints(unittest.TestCase):
    """Tests 09, 10, 11, 12: Flask REST API endpoint verification."""

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_09_post_insar_deformation_success(self):
        """POST /api/pahad/insar-deformation -> HTTP 200 + valid schema."""
        payload = {
            "sector_id": "SK-NH10-KM48",
            "displacement_series_mm": [0.0, 3.5, 9.0, 22.0],
            "days_intervals": [0.0, 12.0, 24.0, 36.0],
            "coherence": 0.68,
        }
        resp = self.client.post(
            "/api/pahad/insar-deformation",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        d = data["data"]
        self.assertIn("velocity_mm_year", d)
        self.assertIn("acceleration_mm_day2", d)
        self.assertIn("creep_status", d)
        self.assertIn("insar_anomaly_factor", d)
        self.assertTrue(d["coherence_reliable"])
        print(f"\n[PASS] Test 09: /api/pahad/insar-deformation -> 200 OK (creep: {d['creep_status']})")

    def test_10_post_mlops_feedback_retrain_success(self):
        """POST /api/pahad/mlops/feedback-retrain -> HTTP 200 + updated metrics."""
        payload = {
            "reports": [
                {
                    "report_id": "FLD-2026-0901",
                    "sector_id": "SK-NH10-KM48",
                    "verified_failure": True,
                    "source_tier": "GSI",
                    "features": {"cri_score": 82.5, "predicted_alert": True},
                }
            ]
        }
        resp = self.client.post(
            "/api/pahad/mlops/feedback-retrain",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("metrics", data)
        self.assertIn("version_tag", data)
        print(f"\n[PASS] Test 10: /api/pahad/mlops/feedback-retrain -> 200 OK (tag: {data['version_tag']})")

    def test_11_get_critical_sectors_queries(self):
        """GET /api/pahad/critical-sectors supports both state filtering and proximity search."""
        # 1. State filter
        resp_state = self.client.get("/api/pahad/critical-sectors?state=Sikkim")
        self.assertEqual(resp_state.status_code, 200)
        data_state = json.loads(resp_state.data)
        self.assertEqual(data_state["status"], "SUCCESS")
        self.assertEqual(data_state["query_type"], "STATE_FILTER")
        self.assertGreaterEqual(data_state["total_matches"], 3)

        # 2. Proximity search
        resp_prox = self.client.get("/api/pahad/critical-sectors?lat=27.33&lon=88.61&radius=25")
        self.assertEqual(resp_prox.status_code, 200)
        data_prox = json.loads(resp_prox.data)
        self.assertEqual(data_prox["status"], "SUCCESS")
        self.assertEqual(data_prox["query_type"], "PROXIMITY")
        self.assertGreaterEqual(data_prox["total_matches"], 1)
        self.assertIn("distance_km", data_prox["sectors"][0])
        print(f"\n[PASS] Test 11: /api/pahad/critical-sectors -> 200 OK (State & Proximity verified)")

    def test_12_missing_fields_return_400(self):
        """Missing required fields in POST requests return HTTP 400."""
        resp = self.client.post(
            "/api/pahad/insar-deformation",
            data=json.dumps({"sector_id": "SK-TEST"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ERROR")
        print("\n[PASS] Test 12: Missing fields correctly return HTTP 400.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
