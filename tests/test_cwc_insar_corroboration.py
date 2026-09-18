# -*- coding: utf-8 -*-
"""
tests/test_cwc_insar_corroboration.py
======================================
Comprehensive verification suite for InSAR Persistent Scatterer (PS) time-series
and Central Water Commission (CWC) Teesta River 5-station hydrodynamic cascade telemetry,
including coupled slope stability (FoS) and compound hydro-geomorphic failure corroboration.

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

import os
os.environ["PARVAT_TESTING"] = "1"

import unittest
import json
from app import app
from services.cwc_sync import CWCTeestaHydroService, CWC_TEESTA_SERVICE, TEESTA_STATION_DEFINITIONS
from engine.pahad_insar import InSARDeformationProcessor, PERSISTENT_SCATTERER_POINTS
from engine.pahad_fusion import PahadFusionEngine


class TestCWCInSARCorroboration(unittest.TestCase):
    """Integration & unit tests for CWC hydrodynamic cascade and InSAR persistent scatterers."""

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.cwc_service = CWCTeestaHydroService()
        self.insar_proc = InSARDeformationProcessor()
        self.fusion = PahadFusionEngine()

    # ─────────────────────────────────────────────────────────────────────────
    # 1. CWC 5-STATION HYDRODYNAMIC CASCADE TESTS
    # ─────────────────────────────────────────────────────────────────────────

    def test_cwc_5_station_definitions_and_chainage(self):
        """Verify that all 5 cascade stations are defined in monotonic chainage down the Teesta gorge."""
        stations = self.cwc_service.get_all_stations()
        self.assertEqual(len(stations), 5)

        expected_ids = [
            "CWC-TEESTA-01",  # Chungthang (42 km)
            "CWC-TEESTA-03",  # Dikchu (88 km)
            "CWC-TEESTA-05",  # Singtam (114 km)
            "CWC-TEESTA-07",  # Melli (138 km)
            "CWC-TEESTA-08"   # Sevoke (162 km)
        ]
        actual_ids = [s["station_id"] for s in stations]
        self.assertEqual(actual_ids, expected_ids)

        # Monotonically increasing chainage
        chainages = [s["chainage_km"] for s in stations]
        self.assertEqual(chainages, sorted(chainages))
        self.assertEqual(chainages[0], 42.0)
        self.assertEqual(chainages[-1], 162.0)

        # Monotonically decreasing datum elevation down the mountain
        datums = [TEESTA_STATION_DEFINITIONS[sid]["gauge_datum_m"] for sid in expected_ids]
        for i in range(len(datums) - 1):
            self.assertGreater(datums[i], datums[i + 1])

    def test_cwc_station_hydraulics_and_shear_stress(self):
        """Verify hydrodynamic basal shear stress (tau_b = rho * g * R * S) for all stations."""
        for sid in TEESTA_STATION_DEFINITIONS.keys():
            hyd = self.cwc_service.compute_station_hydraulics(sid)
            self.assertIn("basal_shear_stress_pa", hyd)
            self.assertIn("excess_shear_ratio", hyd)
            self.assertIn("toe_resistance_loss_pct", hyd)
            self.assertIn("scour_risk_level", hyd)

            self.assertGreater(hyd["basal_shear_stress_pa"], 0.0)
            self.assertGreaterEqual(hyd["excess_shear_ratio"], 0.0)
            self.assertGreaterEqual(hyd["toe_resistance_loss_pct"], 0.0)
            self.assertLessEqual(hyd["toe_resistance_loss_pct"], 100.0)
            self.assertIn(hyd["scour_risk_level"], ["CRITICAL", "HIGH", "MODERATE", "LOW"])

    def test_cwc_coupled_fos_monotonicity_all_stations(self):
        """Verify that rising river stage strictly degrades slope FoS across cascade stations."""
        for sid in ["CWC-TEESTA-01", "CWC-TEESTA-05", "CWC-TEESTA-08"]:
            defn = TEESTA_STATION_DEFINITIONS[sid]
            base_stage = defn["default_water_level_m"]
            stages = [base_stage - 2.0, base_stage, base_stage + 2.0, base_stage + 4.0]

            prev_fos = float("inf")
            for stage in stages:
                coupled = self.cwc_service.compute_station_coupled_fos(sid, water_level_m=stage)
                fos = coupled["factor_of_safety"]
                self.assertLess(fos, prev_fos, f"Station {sid} FoS did not decrease at stage {stage}: {fos} >= {prev_fos}")
                prev_fos = fos

    def test_cwc_longitudinal_scour_profile(self):
        """Verify corridor-wide longitudinal hydraulic scour profile generation."""
        profile = self.cwc_service.compute_longitudinal_scour_profile()
        self.assertEqual(profile["status"], "SUCCESS")
        self.assertEqual(profile["station_count"], 5)
        self.assertEqual(profile["total_chainage_km"], 162.0)
        self.assertIn("summary", profile)
        self.assertIn("max_shear_stress_pa", profile["summary"])
        self.assertIn("max_toe_loss_pct", profile["summary"])
        self.assertIn("corridor_status", profile["summary"])

    # ─────────────────────────────────────────────────────────────────────────
    # 2. INSAR PERSISTENT SCATTERER DATASET & TIME-SERIES TESTS
    # ─────────────────────────────────────────────────────────────────────────

    def test_insar_8_persistent_scatterers_dataset(self):
        """Verify 8 persistent scatterers covering NH-10 and North Sikkim corridor."""
        points = self.insar_proc.get_persistent_scatterers()
        self.assertEqual(len(points), 8)

        point_ids = [p["point_id"] for p in points]
        self.assertEqual(set(point_ids), {501, 502, 503, 504, 505, 506, 507, 508})

        for p in points:
            self.assertIn("point_id", p)
            self.assertIn("station_code", p)
            self.assertIn("los_velocity_mm_yr", p)
            self.assertIn("velocity_uncertainty_mm_yr", p)
            self.assertIn("cumulative_disp_mm", p)
            self.assertIn("coherence", p)
            self.assertIn("deformation_classification", p)
            self.assertIn("geometry", p)
            self.assertGreaterEqual(p["coherence"], 0.70)
            self.assertIn(p["track_direction"], ["Ascending", "Descending"])

    def test_insar_24_epoch_timeseries_and_fukuzono_voight(self):
        """Verify 24-epoch interferometric displacement time-series and Fukuzono 1/v curve."""
        ts = self.insar_proc.generate_ps_timeseries(501, num_epochs=24, interval_days=12.0)
        self.assertEqual(ts["point_id"], 501)
        self.assertEqual(ts["total_epochs"], 24)
        self.assertEqual(ts["repeat_cycle_days"], 12.0)
        self.assertEqual(len(ts["epochs"]), 24)

        # First epoch has 0 days elapsed, last epoch has 276 days
        self.assertEqual(ts["epochs"][0]["days_elapsed"], 0.0)
        self.assertEqual(ts["epochs"][-1]["days_elapsed"], 276.0)

        # Inverse velocity (1/v) should be populated for valid velocities
        valid_inv_v = [e["inverse_velocity_day_mm"] for e in ts["epochs"] if e["inverse_velocity_day_mm"] is not None]
        self.assertTrue(len(valid_inv_v) > 0)

        # Check creep analysis result
        self.assertIn("creep_analysis", ts)
        analysis = ts["creep_analysis"]
        self.assertIn("velocity_mm_year", analysis)
        self.assertIn("creep_status", analysis)

    def test_insar_point_details_retrieval(self):
        """Verify detailed scatterer query for known and unknown points."""
        details = self.insar_proc.get_ps_point_details(501)
        self.assertIsNotNone(details)
        self.assertEqual(details["status"], "SUCCESS")
        self.assertEqual(details["point"]["point_id"], 501)

        invalid = self.insar_proc.get_ps_point_details(9999)
        self.assertIsNone(invalid)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. COMPOUND HYDRO-GEOMORPHIC FAILURE CORROBORATION TESTS
    # ─────────────────────────────────────────────────────────────────────────

    def test_compound_hydro_geomorphic_trigger_positive(self):
        """
        Verify that severe CWC toe scour coupled with active InSAR subsidence
        triggers compound hydro-geomorphic failure in PAHAD Fusion.
        """
        res = self.fusion.fuse(
            sector_id="SK-NH10-KM48",
            rainfall_mm=120.0,
            rainfall_threshold_exceeded=True,
            fos_physical=0.88,
            event_probability_24h=0.85,
            features_override={
                "toe_loss_pct": 75.0,
                "basal_shear_pa": 4500.0,
                "los_velocity_mm_yr": -32.5,
                "displacement_rate_mm_day": 2.8,
                "insar_deformation_mm": 18.0
            }
        )
        self.assertTrue(res["compound_hydro_geomorphic_trigger"])
        self.assertEqual(res["cwc_toe_loss_pct"], 75.0)
        self.assertEqual(res["cwc_basal_shear_pa"], 4500.0)
        self.assertEqual(res["insar_los_velocity_mm_yr"], -32.5)

        # Check explainability driver
        driver_signals = [d["signal"] for d in res["top_drivers"]]
        self.assertIn("Compound Hydro-Geomorphic Failure Corroboration", driver_signals)

    def test_compound_hydro_geomorphic_trigger_quiescent(self):
        """Verify that benign river stage and stable InSAR do not trip compound failure."""
        res = self.fusion.fuse(
            sector_id="WB-SEVOKE-01",
            rainfall_mm=10.0,
            rainfall_threshold_exceeded=False,
            fos_physical=1.45,
            event_probability_24h=0.05,
            features_override={
                "toe_loss_pct": 2.0,
                "basal_shear_pa": 120.0,
                "los_velocity_mm_yr": -2.1,
                "displacement_rate_mm_day": 0.05,
                "insar_deformation_mm": 1.0
            }
        )
        self.assertFalse(res["compound_hydro_geomorphic_trigger"])

    # ─────────────────────────────────────────────────────────────────────────
    # 4. REST API ENDPOINTS VERIFICATION
    # ─────────────────────────────────────────────────────────────────────────

    def test_api_cwc_stations_overview(self):
        """GET /api/cwc/stations returns 200 OK and 5 stations."""
        resp = self.client.get("/api/cwc/stations")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["count"], 5)
        self.assertEqual(len(data["stations"]), 5)

    def test_api_cwc_station_details(self):
        """GET /api/cwc/station/<id> returns 200 for valid and 404 for invalid."""
        resp = self.client.get("/api/cwc/station/CWC-TEESTA-05")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["station_id"], "CWC-TEESTA-05")
        self.assertIn("basal_shear_stress_pa", data)
        self.assertIn("coupled_fos", data)

        err_resp = self.client.get("/api/cwc/station/INVALID-STATION")
        self.assertEqual(err_resp.status_code, 404)

    def test_api_cwc_scour_profile(self):
        """GET /api/cwc/scour-profile returns 200 OK with longitudinal profile."""
        resp = self.client.get("/api/cwc/scour-profile")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["station_count"], 5)
        self.assertIn("profile", data)
        self.assertIn("summary", data)

    def test_api_insar_points(self):
        """GET /api/insar/points returns 200 OK and at least 8 persistent scatterers."""
        resp = self.client.get("/api/insar/points")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertGreaterEqual(data["count"], 8)
        self.assertGreaterEqual(len(data["features"]), 8)

    def test_api_insar_timeseries(self):
        """GET /api/insar/timeseries/<point_id> returns 200 for valid and 404 for invalid."""
        resp = self.client.get("/api/insar/timeseries/501")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["point_id"], 501)
        self.assertEqual(data["total_epochs"], 24)
        self.assertEqual(len(data["epochs"]), 24)
        self.assertIn("creep_analysis", data)

        err_resp = self.client.get("/api/insar/timeseries/9999")
        self.assertEqual(err_resp.status_code, 404)

    def test_api_hydrology_teesta_status_backward_compatibility(self):
        """GET /api/hydrology/teesta-status maintains backward compatibility with cascade summary."""
        resp = self.client.get("/api/hydrology/teesta-status")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["station_id"], "CWC-TEESTA-05")
        self.assertIn("water_level_m", data)
        self.assertIn("discharge_cumecs", data)
        self.assertIn("basal_shear_stress_pa", data)
        self.assertIn("coupled_fos", data)
        self.assertIn("cascade_summary", data)
        self.assertEqual(len(data["cascade_summary"]), 5)


if __name__ == "__main__":
    unittest.main()
