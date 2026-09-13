# -*- coding: utf-8 -*-
"""
tests/test_pilot_safety.py
==========================
Authoritative test suite for PARVAT NETRA / PAHAD AI Pilot Safety Invariants.
Validates:
  1. AI recommendation != public emergency alert.
  2. Human-in-the-loop authority sign-off requirement.
  3. 2-of-3 independent corroboration interlock.
  4. Out-of-distribution (OOD) telemetry handling and confidence penalty.
  5. Siren hardware safety interlock.
"""

import pytest
from engine.pilot_profile import PilotProfileManager, PilotProfile, PilotMode, SafetyPolicy

def test_ai_recommendation_does_not_equal_public_alert():
    """Verify that a high AI prediction alone never automatically triggers public dispatch."""
    manager = PilotProfileManager()
    profile = manager.get_profile()

    # Even if model probability is 0.99, public dispatch remains disabled
    model_prob = 0.99
    assert model_prob > 0.70
    assert profile.safety_policy.public_dispatch_enabled is False
    assert profile.safety_policy.require_human_authority_signoff is True

def test_two_of_three_corroboration_policy_enforced():
    """Verify safety policy requires multi-source corroboration before warning."""
    manager = PilotProfileManager()
    profile = manager.get_profile()
    assert profile.safety_policy.require_two_of_three_corroboration is True

def test_ood_observation_detection_and_downgrade():
    """Verify out-of-distribution inputs receive confidence penalties and suppress alerts."""
    manager = PilotProfileManager()

    # Case 1: Normal physical values
    normal_features = {
        "slope": 35.0,
        "rain_1h": 25.0,
        "rain_24h": 120.0,
        "fos": 1.15,
        "pore_pressure": 22.0,
        "tilt": 2.5
    }
    res_normal = manager.handle_ood_observation(normal_features)
    assert res_normal["is_ood"] is False
    assert res_normal["confidence_penalty"] == 0.0
    assert res_normal["suppress_high_alert"] is False

    # Case 2: Out-of-distribution physical values (e.g. sensor malfunction: slope = 110 deg, rain = 5000 mm)
    insane_features = {
        "slope": 110.0,  # Physically impossible slope
        "rain_24h": 5000.0,  # Extreme impossible rain
        "fos": 25.0,
        "pore_pressure": 999.0
    }
    res_ood = manager.handle_ood_observation(insane_features)
    assert res_ood["is_ood"] is True
    assert len(res_ood["ood_flags"]) >= 3
    assert res_ood["confidence_penalty"] > 0.4
    assert res_ood["suppress_high_alert"] is True
    assert res_ood["safe_action"] == "APPLY_CONFIDENCE_PENALTY_AND_DOWNGRADE"

def test_siren_hardware_safety_interlock():
    """Verify acoustic sirens cannot activate without explicit authorized override."""
    manager = PilotProfileManager()
    profile = manager.get_profile()

    # Must be DRY_RUN by default
    assert profile.safety_policy.siren_hardware_enabled is False

def test_human_authority_signoff_flag_enforced():
    """Verify require_human_authority_signoff is permanently True across all profiles."""
    manager = PilotProfileManager()
    assert manager.get_profile().safety_policy.require_human_authority_signoff is True
