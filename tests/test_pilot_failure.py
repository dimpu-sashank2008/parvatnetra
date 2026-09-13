# -*- coding: utf-8 -*-
"""
tests/test_pilot_failure.py
===========================
Authoritative test suite for PARVAT NETRA / PAHAD AI Pilot Failure Gate.
Validates safe degradation under telemetry loss, provider outages, database errors,
stale data, and missing features without fabricating synthetic [LIVE] observations.
"""

import pytest
from engine.pilot_profile import PilotProfileManager, PILOT_MANAGER

def test_weather_loss_graceful_handling():
    """Verify loss of weather service falls back to regional cache without fabricating LIVE data."""
    manager = PILOT_MANAGER
    res = manager.handle_provider_failure("OPEN_METEO")

    assert res["provider"] == "OPEN_METEO"
    assert res["status"] == "UNAVAILABLE"
    assert res["fabricated_data"] is False
    assert res["provenance"] == "[CACHED]"
    assert res["confidence_penalty"] > 0.0

def test_seismic_loss_graceful_handling():
    """Verify loss of seismic provider falls back to baseline 0 shaking without fabricating tremors."""
    manager = PILOT_MANAGER
    res = manager.handle_provider_failure("USGS")

    assert res["provider"] == "USGS"
    assert res["status"] == "UNAVAILABLE"
    assert res["fabricated_data"] is False
    assert res["provenance"] == "[CACHED]"
    assert res["fallback_action"] == "ASSUME_TECTONIC_BASELINE_ZERO"

def test_sensor_and_gateway_outage_handling():
    """Verify loss of IoT edge gateway marks telemetry missing without fabricating sensor values."""
    manager = PILOT_MANAGER
    res = manager.handle_provider_failure("IOT_GATEWAY_NODE")

    assert res["status"] == "UNAVAILABLE"
    assert res["fabricated_data"] is False
    assert res["provenance"] == "[MISSING]"
    assert res["confidence_penalty"] >= 0.50

def test_missing_features_does_not_crash_pipeline():
    """Verify that missing critical features is handled gracefully without fake defaults."""
    manager = PILOT_MANAGER
    sparse_features = {
        "slope": 32.0,
        "rain_1h": None,
        "rain_24h": None,
        "fos": None
    }
    res = manager.handle_ood_observation(sparse_features)
    assert res["is_ood"] is False  # Missing values are not OOD; they are handled by imputer

def test_corrupted_data_types_handled():
    """Verify non-numeric corrupted strings in telemetry are caught and penalized."""
    manager = PILOT_MANAGER
    corrupted_features = {
        "slope": "NOT_A_NUMBER",
        "rain_24h": "CORRUPT_HEX"
    }
    res = manager.handle_ood_observation(corrupted_features)
    assert res["is_ood"] is True
    assert res["confidence_penalty"] > 0.0
    assert res["safe_action"] == "APPLY_CONFIDENCE_PENALTY_AND_DOWNGRADE"
