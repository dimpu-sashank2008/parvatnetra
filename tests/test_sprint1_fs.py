#!/usr/bin/env python3
"""
PARVAT NETRA -- Automated Verification Suite for Sprint 1 (Physical Factor of Safety)
Tests:
1. vwc_to_suction with low moisture (25% VWC) vs high moisture (48% VWC),
   confirming suction decreases as saturation increases.
2. calculate_factor_of_safety confirming steep slopes (45 deg) with saturated conditions
   produce FS < 1.0, while gentle slopes (25 deg) with suction produce FS > 1.3.
3. Queries live backend/risk_engine.py pipeline and asserts that computed Factor of Safety
   is returned for Gangtok Corridor and Teesta Valley.
"""

import os
import sys
import unittest

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.risk_engine import (
    vwc_to_suction,
    green_ampt_wetting_front,
    calculate_factor_of_safety,
    LandslideRiskEngine5M
)


class TestPhysicalFactorOfSafety(unittest.TestCase):

    def test_01_vwc_to_suction_curve(self):
        """Tests van Genuchten SWCC matric suction behavior with low vs high moisture."""
        # Low moisture: 25% VWC
        suction_dry = vwc_to_suction(25.0)
        # High moisture: 48% VWC
        suction_wet = vwc_to_suction(48.0)

        print(f"\n[SWCC Test] Dry soil (25% VWC) Suction: {suction_dry:.2f} kPa")
        print(f"[SWCC Test] Saturated soil (48% VWC) Suction: {suction_wet:.2f} kPa")

        # Confirm suction decreases as saturation increases
        self.assertGreater(suction_dry, suction_wet, "Dry soil suction must exceed wet soil suction")
        self.assertGreater(suction_dry, 50.0, "Dry soil matric suction should be elevated (> 50 kPa)")
        self.assertLess(suction_wet, 5.0, "Near-saturated soil matric suction must approach 0 (< 5 kPa)")

    def test_02_infinite_slope_factor_of_safety(self):
        """Tests limit equilibrium Mohr-Coulomb model under steep saturated vs gentle unsaturated conditions."""
        c_prime = 12.0      # kPa
        phi_prime = 32.0    # deg
        gamma = 19.0        # kN/m^3
        z = 3.5             # m

        # Steep slope (45 deg) with perched saturation (hydrostatic pore pressure)
        fs_steep_sat = calculate_factor_of_safety(
            cohesion_kpa=c_prime,
            phi_deg=phi_prime,
            gamma_kn_m3=gamma,
            depth_m=z,
            slope_beta_deg=45.0,
            suction_kpa=0.0,
            is_saturated=True
        )

        # Gentle slope (25 deg) with matric suction (unsaturated regime)
        fs_gentle_unsat = calculate_factor_of_safety(
            cohesion_kpa=c_prime,
            phi_deg=phi_prime,
            gamma_kn_m3=gamma,
            depth_m=z,
            slope_beta_deg=25.0,
            suction_kpa=25.0,
            is_saturated=False
        )

        print(f"[FoS Test] Steep saturated slope (45 deg) FS: {fs_steep_sat:.3f}")
        print(f"[FoS Test] Gentle unsaturated slope (25 deg) FS: {fs_gentle_unsat:.3f}")

        # Assert steep saturated condition produces critical active failure (FS < 1.0)
        self.assertLess(fs_steep_sat, 1.0, "Steep saturated slope must fail limit equilibrium with FS < 1.0")
        
        # Assert gentle slope with suction produces stable condition (FS > 1.3)
        self.assertGreater(fs_gentle_unsat, 1.3, "Gentle unsaturated slope with suction must be stable with FS > 1.3")

    def test_03_green_ampt_wetting_front(self):
        """Tests Green-Ampt infiltration wetting front depth over antecedent rainfall."""
        # 24h duration (86400s)
        lf_24h = green_ampt_wetting_front(Ks=1e-5, psi_f=0.20, delta_theta=0.15, t_seconds=86400)
        # 1h duration (3600s)
        lf_1h = green_ampt_wetting_front(Ks=1e-5, psi_f=0.20, delta_theta=0.15, t_seconds=3600)

        print(f"[Green-Ampt Test] Wetting front at 1 hour: {lf_1h:.2f} m")
        print(f"[Green-Ampt Test] Wetting front at 24 hours: {lf_24h:.2f} m")

        self.assertGreater(lf_24h, lf_1h, "24h wetting front must be deeper than 1h wetting front")
        self.assertGreater(lf_24h, 3.5, "24h continuous infiltration must penetrate slip plane depth (>= 3.5m)")

    def test_04_live_risk_engine_pipeline(self):
        """Queries live backend/risk_engine.py pipeline and asserts that Factor of Safety is returned for regions."""
        engine = LandslideRiskEngine5M()
        data = engine.fetch_fused_geodata()
        self.assertGreaterEqual(len(data), 2, "Expected at least 2 terrain regions from static_terrain")

        evals = engine.evaluate_5m_risk(data)
        self.assertGreaterEqual(len(evals), 2, "Expected at least 2 evaluations")

        region_names = [e['region_name'] for e in evals]
        self.assertIn('Gangtok Corridor', region_names, "Gangtok Corridor must be present in evaluations")
        self.assertIn('Teesta Valley', region_names, "Teesta Valley must be present in evaluations")

        for e in evals:
            r_name = e['region_name']
            fs_val = e.get('factor_of_safety')
            fs_level = e.get('fs_operational_level')
            suction = e.get('suction_kpa')
            lf = e.get('wetting_front_m')

            print(f"\n[Live Pipeline Test] Region: {r_name}")
            print(f"  -> Factor of Safety (FS): {fs_val} ({fs_level})")
            print(f"  -> Matric Suction      : {suction} kPa")
            print(f"  -> Wetting Front       : {lf} m (Saturated: {e.get('is_saturated')})")
            print(f"  -> Severity Label      : {e.get('severity_label')}")
            print(f"  -> Composite Risk Score: {e.get('risk_index')}")

            self.assertIsNotNone(fs_val, f"factor_of_safety missing for {r_name}")
            self.assertIsInstance(fs_val, float, f"factor_of_safety must be a float for {r_name}")
            self.assertGreater(fs_val, 0.0, f"factor_of_safety must be positive for {r_name}")
            self.assertIn(fs_level, ['RED', 'ORANGE', 'YELLOW', 'GREEN'], f"Invalid fs_operational_level for {r_name}")


if __name__ == "__main__":
    unittest.main()
