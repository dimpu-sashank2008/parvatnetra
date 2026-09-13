# -*- coding: utf-8 -*-
"""
tests/test_phase7h_recovery.py
==============================
PHASE 7H — CP 7H-16, 7H-21: End-to-End Disaster Recovery Lifecycle,
Recovery Time Objective (RTO) and Recovery Point Objective (RPO) Benchmarking.
"""

import pytest
from services.resilience_metrics import RESILIENCE_METRICS, ResilienceMetricsTracker


def test_recovery_lifecycle_across_components():
    """CP 7H-16 & 7H-21: Measures RTO and RPO across all infrastructure failure domains."""
    components = [
        ("EDGE_GATEWAY_WAN_DISCONNECT", 1.5, 0.2),
        ("POSTGRES_DATABASE_OUTAGE", 2.0, 0.0),
        ("IMD_WEATHER_API_FAILURE", 0.5, 0.0),
        ("NCS_SEISMIC_OUTAGE", 0.5, 0.0),
        ("MODEL_INFERENCE_TIMEOUT", 0.8, 0.1),
        ("AUTHORITY_WORKFLOW_TIMEOUT", 1.0, 0.0)
    ]

    for comp, outage_s, uncommitted_s in components:
        metric = RESILIENCE_METRICS.benchmark_outage_recovery(
            component_name=comp,
            outage_duration_seconds=outage_s,
            uncommitted_window_seconds=uncommitted_s
        )
        assert metric["component"] == comp
        assert metric["status"] == "RECOVERED"
        assert metric["fail_safe"] is True
        assert metric["RTO_seconds"] >= outage_s
        assert metric["RPO_seconds"] == uncommitted_s
        assert "measured_at" in metric


def test_rto_and_rpo_bounds_enforcement():
    """CP 7H-21: Recovery Time Objective stays under 5 seconds for edge and services."""
    metric = RESILIENCE_METRICS.benchmark_outage_recovery("EDGE_BUFFER_REPLAY", outage_duration_seconds=1.2)
    assert metric["RTO_seconds"] < 5.0
    assert metric["RPO_seconds"] <= 1.0
