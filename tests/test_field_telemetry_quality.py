# -*- coding: utf-8 -*-
"""
tests/test_field_telemetry_quality.py
=====================================
Unit tests for field telemetry quality scoring, power subsystem validation,
and provenance tagging.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.power_validator import PowerValidator, POWER_VALIDATOR
from engine.sensor_registry import GLOBAL_SENSOR_REGISTRY


@pytest.fixture
def power_val():
    return PowerValidator()


def test_soc_curve_estimation(power_val):
    assert power_val.calculate_soc_from_voltage(13.8) == 100.0
    assert power_val.calculate_soc_from_voltage(10.2) == 0.0
    soc_nom = power_val.calculate_soc_from_voltage(12.8)
    assert 65.0 <= soc_nom <= 75.0


def test_autonomous_reserve_days_calculation(power_val):
    # 20 Ah battery, 100% SoC, 45 mA average load
    days = power_val.calculate_autonomous_reserve_days(battery_ah=20.0, soc_pct=100.0, average_load_ma=45.0)
    assert days > 10.0  # More than 10 days autonomy


def test_low_battery_warning(power_val):
    telemetry = {
        "battery_voltage_v": 11.5,
        "battery_capacity_ah": 20.0,
        "load_current_ma": 50.0
    }
    res = power_val.validate_power_telemetry(telemetry, provenance="FIELD-MEASURED")
    assert res["power_status"] == "LOW_BATTERY_WARNING"
    assert res["provenance"] == "FIELD-MEASURED"


def test_critical_battery_shutdown(power_val):
    telemetry = {
        "battery_voltage_v": 10.2,
        "battery_capacity_ah": 20.0,
        "load_current_ma": 50.0
    }
    res = power_val.validate_power_telemetry(telemetry, provenance="BENCH")
    assert res["power_status"] == "CRITICAL_SHUTDOWN"
    assert res["provenance"] == "BENCH"


def test_optimal_power_status(power_val):
    telemetry = {
        "battery_voltage_v": 13.2,
        "battery_capacity_ah": 30.0,
        "solar_pv_v": 18.5,
        "solar_current_ma": 850.0,
        "load_current_ma": 40.0
    }
    res = power_val.validate_power_telemetry(telemetry, provenance="FIELD-MEASURED")
    assert res["power_status"] == "OPTIMAL"
    assert res["is_solar_charging"] is True
    assert res["provenance"] == "FIELD-MEASURED"
