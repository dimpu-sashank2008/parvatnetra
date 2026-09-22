# -*- coding: utf-8 -*-
"""
tests/test_v5_0_live_telemetry.py
=================================
Phase V5.0 Test Suite: 10-Criteria LIVE_FIELD_TELEMETRY Boundary Gate
"""

from datetime import datetime, timezone, timedelta
import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestLiveTelemetryBoundary:
    """Verifies the 10 mandatory criteria for assigning LIVE_FIELD_TELEMETRY."""

    def test_bench_observation_fails_live_criteria(self, deployment_engine):
        obs = {
            "observation_id": "OBS-TEST-001",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "value": 18.5,
            "unit": "kPa",
            "source": "BENCH_TEST_FIXTURE",
            "transport": "USB_SERIAL",
            "provenance": "BENCH",
            "crc_valid": True
        }
        is_live, reasons = deployment_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        assert len(reasons) > 0
        # Should fail on physical sensor identity, field presence, bench source, transport, etc.
        reasons_str = " ".join(reasons)
        assert "CRITERION_1_FAIL" in reasons_str
        assert "CRITERION_2_FAIL" in reasons_str
        assert "CRITERION_3_FAIL" in reasons_str
        assert "CRITERION_4_FAIL" in reasons_str

    def test_future_timestamp_rejected(self, deployment_engine):
        future_time = datetime.now(timezone.utc) + timedelta(minutes=10)
        obs = {
            "observation_id": "OBS-TEST-002",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": future_time.isoformat(),
            "value": 18.5,
            "unit": "kPa",
            "source": "FIELD_SENSOR",
            "transport": "FIELD_LORA",
            "provenance": "LIVE",
            "crc_valid": True
        }
        is_live, reasons = deployment_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        reasons_str = " ".join(reasons)
        assert "CRITERION_5_FAIL" in reasons_str

    def test_crc_failure_rejected(self, deployment_engine):
        obs = {
            "observation_id": "OBS-TEST-003",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "value": 18.5,
            "unit": "kPa",
            "source": "FIELD_SENSOR",
            "transport": "FIELD_LORA",
            "provenance": "LIVE",
            "crc_valid": False
        }
        is_live, reasons = deployment_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        reasons_str = " ".join(reasons)
        assert "CRITERION_6_FAIL" in reasons_str

    def test_verified_live_observations_count_is_zero(self, deployment_engine):
        v = deployment_engine.evaluate_v5_0_overall_verdict()
        assert v["live_mountain_observations"] == 0
        assert v["continuous_live_telemetry_hours"] == 0.0
