# -*- coding: utf-8 -*-
"""
tests/test_phase7g_corroboration.py
===================================
PHASE 7G — Checkpoint 7G-06: Independent Multi-Source Corroboration Gate
Verifies:
  1. Independent display of PHYSICAL, RAINFALL, ML modalities.
  2. Signal status states: CONFIRMED, NOT_CONFIRMED, UNAVAILABLE, STALE, SIMULATED.
  3. 0/3 agreement -> alert_eligible = False.
  4. 1/3 agreement -> alert_eligible = False, cannot dispatch.
  5. 2/3 agreement -> alert_eligible = True, requires authority review, cannot auto-dispatch.
  6. 3/3 agreement -> alert_eligible = True, highest_confidence = True, still requires human authority approval.
  7. Simulated signals remain visibly tagged [SIMULATED].
"""

import pytest
from services.authority_review_service import (
    evaluate_corroboration_display,
    AuthorityReviewService
)
from engine.pahad_decision_store import DecisionRecordStore
from engine.operational_state_machine import OperationalStateMachine


def test_zero_of_three_agreement():
    """0/3 signals: slope stable, low rain, low ML -> no alert eligibility."""
    res = evaluate_corroboration_display(
        fos=1.45,
        rainfall_24h=25.0,
        event_probability=0.15
    )
    assert res["confirmed_count"] == 0
    assert res["agreement_fraction"] == "0/3"
    assert res["alert_eligible"] is False
    assert res["can_dispatch"] is False
    assert res["signals"]["PHYSICAL"]["state"] == "NOT_CONFIRMED"
    assert res["signals"]["RAINFALL"]["state"] == "NOT_CONFIRMED"
    assert res["signals"]["ML"]["state"] == "NOT_CONFIRMED"


def test_one_of_three_agreement():
    """1/3 signals: isolated rainfall exceedance cannot trigger alert eligibility or dispatch."""
    res = evaluate_corroboration_display(
        fos=1.35,
        rainfall_24h=195.0,  # Rain > 150mm (Confirmed)
        event_probability=0.25
    )
    assert res["confirmed_count"] == 1
    assert res["agreement_fraction"] == "1/3"
    assert res["alert_eligible"] is False
    assert res["can_dispatch"] is False
    assert res["signals"]["RAINFALL"]["state"] == "CONFIRMED"
    assert res["signals"]["PHYSICAL"]["state"] == "NOT_CONFIRMED"
    assert res["signals"]["ML"]["state"] == "NOT_CONFIRMED"


def test_two_of_three_agreement():
    """2/3 signals: critical FoS + heavy rain -> alert eligible for review, but CANNOT auto-dispatch."""
    res = evaluate_corroboration_display(
        fos=1.04,          # FoS < 1.10 (Confirmed)
        rainfall_24h=180.0, # Rain > 150mm (Confirmed)
        event_probability=0.45
    )
    assert res["confirmed_count"] == 2
    assert res["agreement_fraction"] == "2/3"
    assert res["alert_eligible"] is True
    assert res["requires_authority_approval"] is True
    assert res["can_dispatch"] is False, "2-of-3 agreement still requires explicit human authority approval"


def test_three_of_three_agreement():
    """3/3 signals: all converging -> highest confidence, but STILL requires human authority approval."""
    res = evaluate_corroboration_display(
        fos=0.85,          # FoS < 1.10 (Confirmed)
        rainfall_24h=210.0, # Rain > 150mm (Confirmed)
        event_probability=0.88 # ML > 0.70 (Confirmed)
    )
    assert res["confirmed_count"] == 3
    assert res["agreement_fraction"] == "3/3"
    assert res["alert_eligible"] is True
    assert res["highest_confidence"] is True
    assert res["requires_authority_approval"] is True
    assert res["can_dispatch"] is False, "Even 3/3 convergence requires human authority review before dispatch"


def test_signal_state_unavailable():
    """Missing signals are correctly tagged UNAVAILABLE."""
    res = evaluate_corroboration_display(
        fos=None,
        rainfall_24h=None,
        event_probability=0.75
    )
    assert res["signals"]["PHYSICAL"]["state"] == "UNAVAILABLE"
    assert res["signals"]["RAINFALL"]["state"] == "UNAVAILABLE"
    assert res["signals"]["ML"]["state"] == "CONFIRMED"
    assert res["confirmed_count"] == 1


def test_signal_state_stale():
    """Stale telemetry is tagged STALE and excluded from confirmed count."""
    res = evaluate_corroboration_display(
        fos=0.95,
        rainfall_24h=180.0,
        event_probability=0.75,
        provenance_map={"fos": "STALE", "rainfall_24h": "LIVE", "event_probability": "MODELLED"}
    )
    assert res["signals"]["PHYSICAL"]["state"] == "STALE"
    assert res["signals"]["RAINFALL"]["state"] == "CONFIRMED"
    assert res["signals"]["ML"]["state"] == "CONFIRMED"
    assert res["confirmed_count"] == 2


def test_signal_state_simulated_preservation():
    """Simulated telemetry is explicitly tagged SIMULATED and visibly distinct."""
    res = evaluate_corroboration_display(
        fos=0.92,
        rainfall_24h=165.0,
        event_probability=0.82,
        provenance_map={"fos": "SIMULATED", "rainfall_24h": "SIMULATED", "event_probability": "SIMULATED"}
    )
    assert res["signals"]["PHYSICAL"]["state"] == "SIMULATED"
    assert res["signals"]["RAINFALL"]["state"] == "SIMULATED"
    assert res["signals"]["ML"]["state"] == "SIMULATED"
    assert res["confirmed_count"] == 3
    assert res["alert_eligible"] is True
    assert res["can_dispatch"] is False
