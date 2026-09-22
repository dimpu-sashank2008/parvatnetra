# -*- coding: utf-8 -*-
"""
tests/test_v4_7_time_sync.py
============================
Phase V4.7 Test Suite: 3-Tier Time Synchronization & Clock Drift Diagnostics
"""

from datetime import datetime, timezone, timedelta
import pytest

from engine.telemetry_trust_engine import (
    TelemetryTrustEngine,
    TRUST_VERIFIED,
    TRUST_DEGRADED,
    TRUST_UNVERIFIED,
    REASON_FUTURE_TIMESTAMP,
    REASON_CLOCK_DRIFT
)


@pytest.fixture
def trust_engine():
    return TelemetryTrustEngine()


class TestThreeTierTimeSync:
    """Tests latency, clock offset, and drift calculations across sensor -> gateway -> backend."""

    def test_nominal_latency_and_offset(self, trust_engine):
        now = datetime.now(timezone.utc)
        sensor_t = (now - timedelta(seconds=5)).isoformat()
        gw_t = (now - timedelta(seconds=2)).isoformat()
        backend_t = now.isoformat()

        metrics = trust_engine.compute_3tier_time_sync(
            sensor_timestamp_str=sensor_t,
            gateway_received_at_str=gw_t,
            backend_received_at_str=backend_t
        )
        assert metrics.transport_latency_ms >= 1900.0  # ~2 seconds
        assert metrics.clock_offset_ms >= 2900.0        # ~3 seconds
        assert metrics.is_future_drift is False
        assert metrics.is_excessive_drift is False

    def test_future_timestamp_detected(self, trust_engine):
        now = datetime.now(timezone.utc)
        # Sensor timestamp is 60 seconds into the future
        future_sensor_t = (now + timedelta(seconds=60)).isoformat()

        metrics = trust_engine.compute_3tier_time_sync(
            sensor_timestamp_str=future_sensor_t,
            gateway_received_at_str=now.isoformat(),
            backend_received_at_str=now.isoformat()
        )
        assert metrics.is_future_drift is True

    def test_excessive_clock_drift_detected(self, trust_engine):
        now = datetime.now(timezone.utc)
        # Sensor timestamp is 300 seconds behind gateway clock (> 120s threshold)
        lagging_sensor_t = (now - timedelta(seconds=300)).isoformat()

        metrics = trust_engine.compute_3tier_time_sync(
            sensor_timestamp_str=lagging_sensor_t,
            gateway_received_at_str=now.isoformat(),
            backend_received_at_str=now.isoformat()
        )
        assert metrics.is_excessive_drift is True
        assert metrics.is_future_drift is False
