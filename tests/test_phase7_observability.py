# -*- coding: utf-8 -*-
"""
tests/test_phase7_observability.py
==================================
Tests for Phase 7J Observability, Health Telemetry & Heartbeat Monitoring.
"""

import time
import pytest
from engine.observability import SystemObservabilityTracker

@pytest.fixture
def obs():
    return SystemObservabilityTracker()

def test_recording_requests_and_latency(obs):
    obs.record_request("/api/pahad/live-inference", latency_seconds=0.045, success=True)
    obs.record_request("/api/pahad/live-inference", latency_seconds=0.055, success=True)
    obs.record_request("/api/authority/review", latency_seconds=0.020, success=False)

    health = obs.get_system_health()
    assert health["counters"]["inference_requests_total"] == 3
    assert health["counters"]["failed_requests_total"] == 1
    assert health["latency_metrics"]["avg_latency_s"] > 0

def test_heartbeat_and_dead_man_switch(obs):
    device_id = "EDGE-GTW-KM48"
    obs.record_heartbeat(device_id)

    # Immediately alive
    status_alive = obs.check_heartbeat(device_id, timeout_seconds=300.0)
    assert status_alive["status"] == "ALIVE"
    assert status_alive["last_seen_seconds_ago"] < 2.0

    # With very short timeout, triggers dead-man
    time.sleep(0.05)
    status_dead = obs.check_heartbeat(device_id, timeout_seconds=0.01)
    assert status_dead["status"] == "DEAD_MAN_TRIGGERED"

def test_prometheus_metrics_export(obs):
    obs.record_request("/api/test", 0.01)
    prom_text = obs.export_prometheus_metrics()
    assert "pahad_uptime_seconds" in prom_text
    assert "pahad_inference_requests_total" in prom_text
    assert "pahad_failed_requests_total" in prom_text
