#!/usr/bin/env python3
"""
PARVAT NETRA -- Automated Verification Suite for Sprint 2
Tests:
1. evaluate_rainfall_threshold_ensemble:
   - 24h intensity of 2.5 mm/h breaches North Sikkim curve (I = 4.045 * 24^-0.25 ≈ 1.828 mm/h)
   - Cumulative 140 mm breaches the 24h threshold (>= 130 mm)
   - Normal condition when below watch thresholds
2. calculate_toe_erosion_degradation:
   - River distance > 250m produces 0% degradation
   - Water stage approaching danger level (218.4m / 220.0m) causes h_toe reduction
   - Passive resistance drops quadratically with h_toe^2 (Pp = 0.5 * gamma * h_toe^2 * Kp)
3. Live pipeline verification:
   - run_risk_fusion_pipeline() executes and populates Teesta Valley with rainfall
     threshold status and toe degradation metrics.
"""

import os
import sys
import unittest

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.risk_engine import (
    evaluate_rainfall_threshold_ensemble,
    calculate_toe_erosion_degradation,
    calculate_factor_of_safety,
    run_risk_fusion_pipeline
)


class TestSprint2RainfallAndToeScour(unittest.TestCase):

    def test_01_rainfall_threshold_ensemble(self):
        """Tests the North Sikkim I-D curve (I = 4.045 * D^-0.25) and cumulative antecedent limits."""
        # 1. 24h duration with 2.5 mm/h (intensity breach)
        res_intensity = evaluate_rainfall_threshold_ensemble(
            intensity_mm_h=2.5,
            duration_h=24.0,
            rain_24h=60.0,
            rain_72h=90.0,
            rain_15d=120.0
        )
        print(f"\n[Rainfall Test 1] 2.5 mm/h over 24h:")
        print(f"  -> Threshold Intensity : {res_intensity['threshold_intensity']:.3f} mm/h")
        print(f"  -> Observed Intensity  : {res_intensity['intensity_mm_h']} mm/h")
        print(f"  -> I-D Breached        : {res_intensity['is_id_breached']}")
        print(f"  -> Trigger Status      : {res_intensity['trigger_status']}")

        # Verify North Sikkim threshold value: 4.045 * (24 ^ -0.25) ≈ 1.828 mm/h
        self.assertAlmostEqual(res_intensity['threshold_intensity'], 1.828, delta=0.01)
        self.assertTrue(res_intensity['is_id_breached'], "2.5 mm/h must breach the 1.828 mm/h threshold")
        self.assertEqual(res_intensity['trigger_status'], "WARNING_BREACH")

        # 2. Cumulative 24h limit breach (140 mm >= 130 mm limit)
        res_cum24 = evaluate_rainfall_threshold_ensemble(
            intensity_mm_h=1.0,
            duration_h=24.0,
            rain_24h=140.0,
            rain_72h=150.0,
            rain_15d=180.0
        )
        print(f"\n[Rainfall Test 2] Cumulative 140 mm / 24h:")
        print(f"  -> 24h Cumulative Breached: {res_cum24['is_cum_24h_breached']}")
        print(f"  -> Trigger Status         : {res_cum24['trigger_status']}")

        self.assertTrue(res_cum24['is_cum_24h_breached'], "140 mm must breach the 130 mm 24h cumulative limit")
        self.assertEqual(res_cum24['trigger_status'], "WARNING_BREACH")

        # 3. Normal / Non-breached condition
        res_normal = evaluate_rainfall_threshold_ensemble(
            intensity_mm_h=0.4,
            duration_h=24.0,
            rain_24h=25.0,
            rain_72h=40.0,
            rain_15d=60.0
        )
        print(f"\n[Rainfall Test 3] Low rain (0.4 mm/h, 25 mm 24h):")
        print(f"  -> Trigger Status: {res_normal['trigger_status']}")
        self.assertEqual(res_normal['trigger_status'], "NORMAL")

    def test_02_toe_erosion_degradation_hydraulics(self):
        """Tests Teesta basal shear stress coupling to passive toe earth resistance."""
        # 1. Distant slope (> 250m from river): Zero degradation
        toe_distant = calculate_toe_erosion_degradation(
            water_level_m=218.4,
            danger_level_m=220.0,
            discharge_cusecs=42500,
            river_distance_m=12000.0,
            initial_toe_height_m=5.0
        )
        print(f"\n[Toe Scour Test 1] Distant slope (12,000m from river):")
        print(f"  -> Toe Resistance Loss: {toe_distant.toe_resistance_loss_pct}%")
        print(f"  -> Effective Toe Height: {toe_distant.effective_toe_height_m} m")
        self.assertEqual(toe_distant.toe_resistance_loss_pct, 0.0)
        self.assertEqual(toe_distant.effective_toe_height_m, 5.0)

        # 2. Near-river slope (0m from Teesta) at danger level stage (218.4m / 220.0m):
        toe_scour = calculate_toe_erosion_degradation(
            water_level_m=218.4,
            danger_level_m=220.0,
            discharge_cusecs=42500,
            river_distance_m=0.0,
            initial_toe_height_m=5.0
        )
        print(f"\n[Toe Scour Test 2] Teesta Gorge at High Stage (218.4m / 220m Danger):")
        print(f"  -> Basal Shear Stress   : {toe_scour.basal_shear_pa:.2f} Pa (Critical: 45 Pa)")
        print(f"  -> Excess Shear Ratio   : {toe_scour.excess_shear:.2f}")
        print(f"  -> Scour Reduction Factor: {toe_scour.scour_factor:.3f}")
        print(f"  -> Degraded Toe Height  : {toe_scour.h_toe:.2f} m (Initial: 5.0m)")
        print(f"  -> Initial Passive Pp   : {toe_scour.initial_passive_resistance_kn:.2f} kN/m")
        print(f"  -> Degraded Passive Pp  : {toe_scour.passive_resistance_kn:.2f} kN/m")
        print(f"  -> Passive Resistance Loss: {toe_scour.toe_resistance_loss_pct:.2f}%")

        # Confirm toe height reduces and passive resistance drops quadratically with h_toe^2
        self.assertLess(toe_scour.h_toe, 5.0, "High stage scour must reduce toe buttress height")
        self.assertGreater(toe_scour.toe_resistance_loss_pct, 50.0, "Extreme basal shear must induce >50% passive loss")
        
        # Test quadratic scaling: Pp_degraded / Pp_initial == (h_toe / 5.0)^2
        ratio_h = (toe_scour.h_toe / 5.0) ** 2
        ratio_pp = toe_scour.passive_resistance_kn / toe_scour.initial_passive_resistance_kn
        self.assertAlmostEqual(ratio_h, ratio_pp, delta=0.02, msg="Passive resistance must scale quadratically with h_toe^2")

    def test_03_factor_of_safety_toe_coupling(self):
        """Tests that calculate_factor_of_safety reduces properly under toe resistance loss."""
        # Baseline saturated slope at 28 deg (Teesta Valley)
        fs_no_scour = calculate_factor_of_safety(
            cohesion_kpa=12.0,
            phi_deg=32.0,
            gamma_kn_m3=19.0,
            depth_m=3.5,
            slope_beta_deg=28.0,
            suction_kpa=0.64,
            is_saturated=True,
            toe_resistance_loss_pct=0.0
        )

        # Coupled with 96% toe resistance loss
        fs_coupled_scour = calculate_factor_of_safety(
            cohesion_kpa=12.0,
            phi_deg=32.0,
            gamma_kn_m3=19.0,
            depth_m=3.5,
            slope_beta_deg=28.0,
            suction_kpa=0.64,
            is_saturated=True,
            toe_resistance_loss_pct=96.0
        )

        print(f"\n[FoS Coupling Test] Teesta Valley Slope (28 deg):")
        print(f"  -> FS without Toe Scour : {fs_no_scour:.3f} (ORANGE)")
        print(f"  -> FS with Toe Scour    : {fs_coupled_scour:.3f} (RED)")

        self.assertGreater(fs_no_scour, 1.0, "Without scour, 28 deg slope is marginally stable (FS > 1.0)")
        self.assertLess(fs_coupled_scour, 1.0, "With hydrodynamic toe undercut, slope must drop into active failure (FS < 1.0)")

    def test_04_live_pipeline_integration(self):
        """Tests run_risk_fusion_pipeline() to confirm Teesta Valley metrics are persisted."""
        evals = run_risk_fusion_pipeline()
        self.assertGreaterEqual(len(evals), 2, "Expected at least 2 evaluated regions")

        teesta_eval = next((e for e in evals if e['region_name'] == 'Teesta Valley'), None)
        self.assertIsNotNone(teesta_eval, "Teesta Valley must be present in evaluations")

        print(f"\n[Live Pipeline Test] Teesta Valley Live Results:")
        print(f"  -> Physical FoS          : {teesta_eval['factor_of_safety']}")
        print(f"  -> Rain Threshold Status : {teesta_eval['rainfall_threshold_status']}")
        print(f"  -> Toe Resistance Loss   : -{teesta_eval['toe_resistance_loss_pct']}%")
        print(f"  -> Effective Toe Height  : {teesta_eval['effective_toe_height_m']} m")
        print(f"  -> Passive Resistance Pp : {teesta_eval['passive_resistance_kn']} kN/m")
        print(f"  -> Severity Label        : {teesta_eval['severity_label']}")
        print(f"  -> Composite Risk Score  : {teesta_eval['risk_index']}")

        self.assertEqual(teesta_eval['rainfall_threshold_status'], "WARNING_BREACH")
        self.assertGreater(teesta_eval['toe_resistance_loss_pct'], 50.0)
        self.assertLess(teesta_eval['effective_toe_height_m'], 5.0)
        self.assertLess(teesta_eval['factor_of_safety'], 1.0)
        self.assertEqual(teesta_eval['severity_label'], "RED")


if __name__ == "__main__":
    unittest.main()
