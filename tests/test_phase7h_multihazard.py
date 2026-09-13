# -*- coding: utf-8 -*-
"""
tests/test_phase7h_multihazard.py
=================================
PHASE 7H — CP 7H-06, 7H-07: Multi-Hazard Cascading Disasters, Earthquake-Rainfall Interaction,
Dynamic FoS Reduction, 7-Stage Cascade Pipeline Trace, and 2-of-3 Corroboration Gate Invariance.
"""

import pytest
from engine.pahad_multihazard import MULTI_HAZARD_ENGINE, MultiHazardEngine


def test_earthquake_pga_attenuation_and_fos_reduction():
    """CP 7H-07: Pseudo-static seismic acceleration reduces static Factor of Safety."""
    # Magnitude 5.0 at 15 km hypocentral distance
    pga = MultiHazardEngine.calculate_seismic_pga_proxy(magnitude=5.0, distance_km=15.0, depth_km=10.0)
    assert 0.05 < pga < 0.80

    # Static FoS = 1.20 should drop under ground acceleration
    dynamic_fos = MultiHazardEngine.calculate_seismic_fos_reduction(base_fos=1.20, pga_g=pga, slope_deg=38.0)
    assert dynamic_fos < 1.20
    assert dynamic_fos > 0.30


def test_earthquake_alone_cannot_bypass_corroboration_gate():
    """CP 7H-07: Tremor without rainfall saturation or critical FoS fails 2-of-3 corroboration."""
    # Strong tremor M5.2, but dry weather (rain = 10mm) and high static FoS (1.60)
    eval_res = MULTI_HAZARD_ENGINE.evaluate_earthquake_rainfall_interaction(
        base_fos=1.60,
        rainfall_24h_mm=10.0,
        earthquake_mag=5.2,
        epicenter_dist_km=20.0
    )

    corrob = eval_res["corroboration"]
    assert corrob["rainfall_confirmed"] is False
    # Cannot auto-dispatch
    assert corrob["can_auto_dispatch"] is False
    assert corrob["requires_authority_review"] is True


def test_compound_monsoon_and_seismic_triggers_corroboration():
    """CP 7H-07: Coincident extreme rainfall (>150mm) and seismic tremor confirms 2-of-3 signals."""
    eval_res = MULTI_HAZARD_ENGINE.evaluate_earthquake_rainfall_interaction(
        base_fos=1.05,
        rainfall_24h_mm=190.0,
        earthquake_mag=4.5,
        epicenter_dist_km=18.0
    )

    corrob = eval_res["corroboration"]
    assert corrob["rainfall_confirmed"] is True
    assert corrob["physical_confirmed"] is True
    assert corrob["alert_eligible"] is True
    # Human authority review is still mandatory
    assert corrob["requires_authority_review"] is True
    assert corrob["can_auto_dispatch"] is False


def test_monsoon_multihazard_7_stage_cascade_trace():
    """CP 7H-06: Traces the full 7-stage disaster lifecycle from ingestion to recovery."""
    drill = MULTI_HAZARD_ENGINE.run_monsoon_multihazard_cascade(
        sector_id="CORR-NH10-SIKKIM-KM48",
        rainfall_24h_mm=195.0,
        pore_pressure_kpa=88.0,
        earthquake_mag=4.3,
        river_rise_m=2.8
    )

    assert drill["verdict"] == "DRILL_SUCCESSFUL"
    assert drill["provenance"] == "[SIMULATED / HIL]"
    assert drill["public_dispatch_emitted"] is False
    assert drill["siren_hardware_activated"] is False

    stages = [s["stage"] for s in drill["trace_pipeline"]]
    expected_stages = [
        "DATA_INGESTION",
        "PAHAD_INFERENCE",
        "CORROBORATION",
        "AUTHORITY_REVIEW",
        "FIELD_TASK",
        "ROUTE_RECALCULATION",
        "RECOVERY"
    ]
    assert stages == expected_stages
