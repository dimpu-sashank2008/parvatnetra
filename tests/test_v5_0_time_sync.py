# -*- coding: utf-8 -*-
"""
tests/test_v5_0_time_sync.py
============================
Phase V5.0 Test Suite: GPS / NTP Time Synchronization & Drift Tolerance
"""

from datetime import datetime, timezone, timedelta
import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestTimeSynchronization:
    """Verifies timing constraints, drift tolerances, and future timestamp rejection."""

    def test_acceptable_drift_within_thirty_seconds(self, deployment_engine):
        ref_now = datetime.now(timezone.utc)
        valid_ts = (ref_now + timedelta(seconds=15)).isoformat()
        ok, drift, msg = deployment_engine.check_time_synchronization(valid_ts, reference_time=ref_now)
        assert ok is True
        assert drift <= 30.0
        assert "accepted" in msg.lower()

    def test_future_timestamp_beyond_thirty_seconds_rejected(self, deployment_engine):
        ref_now = datetime.now(timezone.utc)
        future_ts = (ref_now + timedelta(seconds=45)).isoformat()
        ok, drift, msg = deployment_engine.check_time_synchronization(future_ts, reference_time=ref_now)
        assert ok is False
        assert drift > 30.0
        assert "rejected" in msg.lower()

    def test_stale_timestamp_beyond_twenty_four_hours_rejected(self, deployment_engine):
        ref_now = datetime.now(timezone.utc)
        stale_ts = (ref_now - timedelta(hours=25)).isoformat()
        ok, drift, msg = deployment_engine.check_time_synchronization(stale_ts, reference_time=ref_now)
        assert ok is False
        assert "rejected" in msg.lower()
