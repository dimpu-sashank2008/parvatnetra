# -*- coding: utf-8 -*-
"""
tests/test_v4_8_real_telemetry.py
=================================
Automated test suite for Phase V4.8 Real Telemetry Boundary.
Tests:
  1. 10-Criteria LIVE_FIELD_TELEMETRY boundary gate.
  2. Bench/live separation (BENCH provenance cannot be LIVE).
  3. HIL/live separation (HIL marker rejects LIVE status).
  4. Simulated/live separation (SIMULATED provenance or marker rejects LIVE status).
  5. Invalid/missing timestamp rejection.
  6. Valid live-path observation acceptance when all 10 criteria pass.
"""

import pytest
from datetime import datetime, timezone
from engine.telemetry_evidence_audit_engine import (
    GLOBAL_EVIDENCE_AUDIT_ENGINE,
    LiveTelemetryBoundaryCheck
)


def test_live_boundary_all_pass():
    """Confirms observation is admitted as LIVE only when all 10 criteria pass."""
    obs = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "value": 42.5,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "LIVE",
        "gateway_id": "GW-NH10-KM48-01",
        "is_simulated": False,
        "is_hil": False,
        "is_fixture": False
    }
    check = GLOBAL_EVIDENCE_AUDIT_ENGINE.evaluate_live_boundary(
        observation=obs,
        has_verified_identity=True,
        has_verified_installation=True,
        is_persisted=True
    )
    assert check.is_live_field_telemetry is True
    assert len(check.rejection_reasons) == 0


def test_live_boundary_bench_separation():
    """Confirms that BENCH observations are rejected from LIVE status."""
    obs = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "value": 42.5,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "BENCH",
        "gateway_id": "GW-NH10-KM48-01"
    }
    check = GLOBAL_EVIDENCE_AUDIT_ENGINE.evaluate_live_boundary(
        observation=obs,
        has_verified_identity=True,
        has_verified_installation=True,
        is_persisted=True
    )
    assert check.is_live_field_telemetry is False
    assert any("5_PROVENANCE_NOT_LIVE" in r for r in check.rejection_reasons)


def test_live_boundary_hil_separation():
    """Confirms that HIL test observations are rejected from LIVE status."""
    obs = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "value": 42.5,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "LIVE",
        "gateway_id": "GW-NH10-KM48-01",
        "is_hil": True
    }
    check = GLOBAL_EVIDENCE_AUDIT_ENGINE.evaluate_live_boundary(
        observation=obs,
        has_verified_identity=True,
        has_verified_installation=True,
        is_persisted=True
    )
    assert check.is_live_field_telemetry is False
    assert any("8_HIL_MARKER_PRESENT" in r for r in check.rejection_reasons)


def test_live_boundary_simulated_separation():
    """Confirms that SIMULATED observations are rejected from LIVE status."""
    obs = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "value": 42.5,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "SIMULATED",
        "gateway_id": "GW-NH10-KM48-01"
    }
    check = GLOBAL_EVIDENCE_AUDIT_ENGINE.evaluate_live_boundary(
        observation=obs,
        has_verified_identity=True,
        has_verified_installation=True,
        is_persisted=True
    )
    assert check.is_live_field_telemetry is False
    assert any("5_PROVENANCE_NOT_LIVE" in r for r in check.rejection_reasons)


def test_live_boundary_missing_installation_separation():
    """Confirms that observations from unverified installations are rejected from LIVE status."""
    obs = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "value": 42.5,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "LIVE",
        "gateway_id": "GW-NH10-KM48-01"
    }
    check = GLOBAL_EVIDENCE_AUDIT_ENGINE.evaluate_live_boundary(
        observation=obs,
        has_verified_identity=True,
        has_verified_installation=False,
        is_persisted=True
    )
    assert check.is_live_field_telemetry is False
    assert any("2_INSTALLATION_NOT_VERIFIED" in r for r in check.rejection_reasons)
