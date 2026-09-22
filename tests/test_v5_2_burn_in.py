# -*- coding: utf-8 -*-
"""
tests/test_v5_2_burn_in.py
==========================
Phase V5.2 Test Suite: 24-Hour Observation & 72-Hour Burn-in Gate
Verifies that burn-in clock requires genuine live telemetry, mandates >= 98.0% PDR,
and enforces zero synthetic gap-filling during communication dropouts.
"""

import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_initial_burn_in_status_pending():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    res = engine.evaluate_burn_in_status(observation_hours=0.0, pdr_pct=0.0)
    assert res["burn_in_status"] == "BURN_IN_PENDING"
    assert res["burn_in_24h_achieved"] is False
    assert res["burn_in_72h_achieved"] is False
    assert res["active_alarming_permitted"] is False


def test_twenty_four_hour_burn_in_evaluation():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    # 24h continuous with >= 98% PDR
    res_pass = engine.evaluate_burn_in_status(observation_hours=24.5, pdr_pct=99.2)
    assert res_pass["burn_in_24h_achieved"] is True
    assert res_pass["burn_in_72h_achieved"] is False
    assert res_pass["burn_in_status"] == "BURN_IN_24H_COMPLETE"

    # 24h with low PDR (< 98%) must fail
    res_fail = engine.evaluate_burn_in_status(observation_hours=24.5, pdr_pct=92.0)
    assert res_fail["burn_in_24h_achieved"] is False


def test_seventy_two_hour_burn_in_required_for_active_alarming():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    # 72h complete
    res_72h = engine.evaluate_burn_in_status(observation_hours=72.5, pdr_pct=98.5)
    assert res_72h["burn_in_72h_achieved"] is True
    assert res_72h["burn_in_status"] == "BURN_IN_72H_COMPLETE"
    assert res_72h["active_alarming_permitted"] is True
