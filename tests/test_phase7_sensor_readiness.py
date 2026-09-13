# -*- coding: utf-8 -*-
"""
tests/test_phase7_sensor_readiness.py
=====================================
Tests for Phase 7F Physical Sensor Pilot Readiness & Acceptance.
Verifies acceptance criteria, telemetry range checks, and zero fabrication of on-slope installation.
"""

import pytest
from engine.sensor_pilot_readiness import SensorPilotReadinessHarness

def test_all_four_primary_transducers_specified():
    transducers = SensorPilotReadinessHarness.TRANSDUCERS
    assert "VW_PIEZOMETER" in transducers
    assert "IN_PLACE_INCLINOMETER" in transducers
    assert "MEMS_TILTMETER" in transducers
    assert "TIPPING_BUCKET_RAIN" in transducers

def test_sensor_bounds_validation_piezometer():
    # Valid reading
    res_valid = SensorPilotReadinessHarness.validate_reading("VW_PIEZOMETER", 45.5)
    assert res_valid["valid"] is True
    assert res_valid["quality"] == "GOOD"
    assert res_valid["unit"] == "kPa"

    # Out of range reading
    res_invalid = SensorPilotReadinessHarness.validate_reading("VW_PIEZOMETER", 750.0)
    assert res_invalid["valid"] is False
    assert res_invalid["quality"] == "OUT_OF_RANGE"

def test_sensor_bounds_validation_tilt():
    # Valid reading
    res_valid = SensorPilotReadinessHarness.validate_reading("MEMS_TILTMETER", 1.85)
    assert res_valid["valid"] is True
    assert res_valid["quality"] == "GOOD"

    # Extreme out of range tilt
    res_invalid = SensorPilotReadinessHarness.validate_reading("MEMS_TILTMETER", 45.0)
    assert res_invalid["valid"] is False
    assert res_invalid["quality"] == "OUT_OF_RANGE"

def test_edge_gateway_specifications():
    gtw = SensorPilotReadinessHarness.GATEWAY
    assert gtw.buffer_capacity_hours >= 72
    assert gtw.autonomy_days >= 14
    assert "LoRaWAN" in gtw.uplink_protocol

def test_honest_pilot_readiness_audit():
    audit = SensorPilotReadinessHarness.get_pilot_readiness_audit()
    assert audit["pilot_corridor"] == "CORR-NH10-SIKKIM-KM48"
    assert audit["field_deployment_status"] == "PHYSICAL_DEPLOYMENT_PENDING"
    assert audit["overall_hardware_readiness"] == "SOFTWARE_TESTBENCH_READY"
    assert audit["controlled_pilot_criteria_met"] is False
    assert "drilling" in audit["reason"].lower() or "installed" in audit["reason"].lower()
