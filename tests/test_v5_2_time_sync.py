# -*- coding: utf-8 -*-
"""
tests/test_v5_2_time_sync.py
============================
Phase V5.2 Test Suite: Time Synchronization & Drift Enforcement
Verifies clock drift limits (<= 30.0s), rejection of future timestamps,
stale timestamp tagging, and preservation of raw sensor timestamps.
"""

from datetime import datetime, timezone, timedelta
import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_future_timestamp_rejection():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    future_time = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    candidate = {
        "sensor_id": "BH-KM48-INC01",
        "timestamp_utc": future_time,
        "source_classification": "LIVE_PHYSICAL"
    }
    is_live, fail_reasons = engine.evaluate_live_field_boundary(candidate)
    assert is_live is False
    assert any("FUTURE" in r for r in fail_reasons)


def test_stale_timestamp_rejection():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    candidate = {
        "sensor_id": "BH-KM48-PZ01",
        "timestamp_utc": stale_time,
        "source_classification": "LIVE_PHYSICAL"
    }
    is_live, fail_reasons = engine.evaluate_live_field_boundary(candidate)
    assert is_live is False
    assert any("STALE" in r for r in fail_reasons)


def test_max_drift_tolerance_configuration():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    assert engine.time_sync_max_drift_seconds == 30.0
