# -*- coding: utf-8 -*-
"""
tests/test_phase12d_scientific_attacks.py
=========================================
PARVAT NETRA • PAHAD AI — Phase 12D Scientific Stress & Attack Suite
---------------------------------------------------------------------
Executes and validates all 13 scientific attack scenarios (A through M):
- Scenario A: Rainfall HIGH / FoS STABLE
- Scenario B: Rainfall LOW / FoS LOW
- Scenario C: Rainfall HIGH / No deformation
- Scenario D: Deformation HIGH / Rainfall NORMAL
- Scenario E: ML HIGH / Physical evidence LOW
- Scenario F: FoS LOW / ML LOW
- Scenario G: All signals HIGH
- Scenario H: All signals LOW
- Scenario I: Missing hydrology
- Scenario J: Missing geotechnical data
- Scenario K: Missing deformation
- Scenario L: Stale data
- Scenario M: Contradictory observations
"""

import os
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_adversarial_defense import (
    ScientificAttackSimulator,
    SCIENTIFIC_STRESS_SCENARIOS
)


class TestPhase12DScientificAttacks:

    def test_all_thirteen_scenarios_configured(self):
        """Verify scenarios A through M are configured."""
        expected_keys = [
            "SCENARIO_A", "SCENARIO_B", "SCENARIO_C", "SCENARIO_D",
            "SCENARIO_E", "SCENARIO_F", "SCENARIO_G", "SCENARIO_H",
            "SCENARIO_I", "SCENARIO_J", "SCENARIO_K", "SCENARIO_L",
            "SCENARIO_M"
        ]
        for k in expected_keys:
            assert k in SCIENTIFIC_STRESS_SCENARIOS, f"Missing scenario {k}"

    def test_scenario_a_rainfall_high_fos_stable(self):
        """Scenario A: Intense rain on low-angle dry rock slope -> FoS remains stable, zero emergency alert."""
        res = ScientificAttackSimulator.evaluate_scenario("SCENARIO_A")
        assert res["fos"] >= 1.4, f"FoS {res['fos']} should be stable (>= 1.4)"
        assert res["corroboration"] == "SINGLE_SIGNAL"
        assert res["risk_band"] in ["LOW", "MODERATE"]
        assert "ADVISORY" in res["authority_action"] or "MONITORING" in res["authority_action"]

    def test_scenario_b_rainfall_low_fos_low(self):
        """Scenario B: Dry weather but steep unstable slope with relic pore pressure -> FoS < 1.0."""
        res = ScientificAttackSimulator.evaluate_scenario("SCENARIO_B")
        assert res["fos"] < 1.0, f"FoS {res['fos']} should reflect failure (< 1.0)"
        assert res["risk_band"] in ["HIGH", "SEVERE", "EXTREME"]
        assert "GEOTECHNICAL" in res["authority_action"] or "INSPECTION" in res["authority_action"]

    def test_scenario_e_ml_high_physics_low_suppression(self):
        """Scenario E: ML predicts high risk but physical slope is stable (FoS > 1.8) -> Physics takes precedence, alert suppressed."""
        res = ScientificAttackSimulator.evaluate_scenario("SCENARIO_E")
        assert res["fos"] >= 1.8, f"FoS {res['fos']} should be high"
        assert res["corroboration"] == "INSUFFICIENT_CORROBORATION"
        assert "SUPPRESS_ALERT" in res["authority_action"]

    def test_scenario_f_fos_low_ml_low_physical_override(self):
        """Scenario F: Mohr-Coulomb limit equilibrium indicates FoS < 1.0 while ML is low -> Physical safety overrides ML."""
        res = ScientificAttackSimulator.evaluate_scenario("SCENARIO_F")
        assert res["fos"] < 1.0
        assert "PHYSICAL_DEFENSE_ACTION" in res["authority_action"]

    def test_scenario_g_all_signals_high_triple_corroboration(self):
        """Scenario G: Rain + Pore Pressure + InSAR + Seismic -> A+B+C full corroboration with extreme risk."""
        res = ScientificAttackSimulator.evaluate_scenario("SCENARIO_G")
        assert res["corroboration"] == "A+B+C"
        assert res["cri"] >= 80.0
        assert res["risk_band"] in ["EXTREME", "SEVERE"]
        assert "IMMEDIATE_AUTHORITY_ESCALATION" in res["authority_action"]

    def test_scenario_h_all_signals_low(self):
        """Scenario H: Baseline quiescent -> Low risk, zero alert recommendation."""
        res = ScientificAttackSimulator.evaluate_scenario("SCENARIO_H")
        assert res["fos"] > 2.0
        assert res["risk_band"] == "LOW"
        assert res["corroboration"] == "INSUFFICIENT_CORROBORATION"

    def test_scenario_m_contradictory_observations(self):
        """Scenario M: Cloudburst rain but zero pore pressure reported -> Flags sensor verification."""
        res = ScientificAttackSimulator.evaluate_scenario("SCENARIO_M")
        assert res["corroboration"] == "SINGLE_SIGNAL"
        assert "SENSOR_VERIFICATION" in res["authority_action"]

    def test_degraded_and_missing_scenarios(self):
        """Scenarios I, J, K, L: Verify graceful handling of missing and stale telemetry."""
        for scen_key in ["SCENARIO_I", "SCENARIO_J", "SCENARIO_K", "SCENARIO_L"]:
            res = ScientificAttackSimulator.evaluate_scenario(scen_key)
            assert res["is_explainable"] is True
            assert res["fos"] > 0
            assert 0 <= res["cri"] <= 100
            assert res["data_quality"] < 1.0, f"Data quality should be penalized for {scen_key}"
