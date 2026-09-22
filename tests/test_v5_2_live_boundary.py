# -*- coding: utf-8 -*-
"""
tests/test_v5_2_live_boundary.py
================================
Phase V5.2 Test Suite: Live Data Boundary Gate
Verifies that telemetry sources are strictly classified into:
LIVE_PHYSICAL, BENCH_HARDWARE, SIMULATED, REPLAYED_REAL, CACHED, DERIVED, UNAVAILABLE.
Enforces zero automatic promotion to LIVE_PHYSICAL.
"""

import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_source_boundary_classes():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    boundaries = engine.audit_telemetry_stream_boundaries()
    allowed = boundaries["allowed_source_classes"]
    expected = [
        "LIVE_PHYSICAL",
        "BENCH_HARDWARE",
        "SIMULATED",
        "REPLAYED_REAL",
        "CACHED",
        "DERIVED",
        "UNAVAILABLE"
    ]
    for c in expected:
        assert c in allowed, f"Missing source classification: {c}"


def test_zero_automatic_promotion_of_bench_to_live():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    bench_payload = {
        "sensor_id": "BH-KM48-INC01",
        "source_classification": "BENCH_HARDWARE",
        "timestamp_utc": "2026-09-21T10:00:00Z",
        "displacement_mm": 1.25
    }
    is_live, fail_reasons = engine.evaluate_live_field_boundary(bench_payload)
    assert is_live is False
    assert any("BENCH" in r or "SOURCE" in r for r in fail_reasons)


def test_zero_automatic_promotion_of_replayed_to_live():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    replayed_payload = {
        "sensor_id": "BH-KM48-PZ01",
        "source_classification": "REPLAYED_REAL",
        "timestamp_utc": "2026-09-21T10:00:00Z",
        "pore_pressure_kpa": 145.2
    }
    is_live, fail_reasons = engine.evaluate_live_field_boundary(replayed_payload)
    assert is_live is False
    assert any("REPLAY" in r or "SOURCE" in r for r in fail_reasons)
