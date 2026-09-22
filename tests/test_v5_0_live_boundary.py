# -*- coding: utf-8 -*-
"""
tests/test_v5_0_live_boundary.py
================================
Phase V5.0 Test Suite: Live-vs-Simulated Boundary Isolation & Sensor QC Range Filtering
"""

import pytest
from engine.physical_deployment_engine import PhysicalDeploymentEngine


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestLiveBoundaryAndSensorQC:
    """Verifies strict boundary separation and geotechnical sensor QC ranges."""

    def test_sensor_qc_range_piezometer(self, deployment_engine):
        # Valid range [-50, +500] kPa
        ok, msg = deployment_engine.evaluate_sensor_qc_range("PIEZOMETER", 45.0)
        assert ok is True

        # Negative suction valid down to -50 kPa
        ok, msg = deployment_engine.evaluate_sensor_qc_range("PIEZOMETER", -20.0)
        assert ok is True

        # Severe negative suction invalid
        ok, msg = deployment_engine.evaluate_sensor_qc_range("PIEZOMETER", -85.0)
        assert ok is False
        assert "OUT OF PHYSICAL BOUNDS" in msg

        # Unrealistic pore pressure (>500 kPa)
        ok, msg = deployment_engine.evaluate_sensor_qc_range("PIEZOMETER", 750.0)
        assert ok is False
        assert "OUT OF PHYSICAL BOUNDS" in msg

    def test_sensor_qc_range_inclinometer(self, deployment_engine):
        # Valid range [-100, +100] mm
        ok, msg = deployment_engine.evaluate_sensor_qc_range("INCLINOMETER", 12.5)
        assert ok is True

        # Excessive displacement (>100 mm)
        ok, msg = deployment_engine.evaluate_sensor_qc_range("INCLINOMETER", 150.0)
        assert ok is False
        assert "OUT OF PHYSICAL BOUNDS" in msg

    def test_sensor_qc_range_tiltmeter(self, deployment_engine):
        # Valid range [-45, +45] degrees
        ok, msg = deployment_engine.evaluate_sensor_qc_range("TILTMETER", 3.2)
        assert ok is True

        # Unrealistic tilt (>45 deg)
        ok, msg = deployment_engine.evaluate_sensor_qc_range("TILTMETER", 65.0)
        assert ok is False
        assert "OUT OF PHYSICAL BOUNDS" in msg

    def test_sensor_qc_range_rain_gauge(self, deployment_engine):
        # Valid range [0, 250] mm/h
        ok, msg = deployment_engine.evaluate_sensor_qc_range("RAIN_GAUGE", 35.0)
        assert ok is True

        # Negative rain invalid
        ok, msg = deployment_engine.evaluate_sensor_qc_range("RAIN_GAUGE", -5.0)
        assert ok is False
        assert "OUT OF PHYSICAL BOUNDS" in msg

        # Extreme cloudburst beyond 250 mm/h
        ok, msg = deployment_engine.evaluate_sensor_qc_range("RAIN_GAUGE", 300.0)
        assert ok is False
        assert "OUT OF PHYSICAL BOUNDS" in msg

    def test_simulated_marker_string_fails_criterion_10(self, deployment_engine):
        obs = {
            "observation_id": "OBS-SIM-99",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": "2026-09-21T12:00:00Z",
            "value": 20.0,
            "provenance": "LIVE",
            "source": "SIMULATED_MONTE_CARLO_PROFILE",
            "transport": "FIELD_LORA",
            "crc_valid": True
        }
        is_live, reasons = deployment_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        assert any("CRITERION_10_FAIL" in r for r in reasons)
