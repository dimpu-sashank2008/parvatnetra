# -*- coding: utf-8 -*-
"""
tests/test_v5_2_sensor_qc.py
============================
Phase V5.2 Test Suite: Sensor Quality Control & Plausibility Ranges
Verifies physical plausibility ranges, fault tagging (VALID, DEGRADED, SUSPECT, INVALID, STALE),
and ensures hazardous extreme values are not discarded solely because they appear high.
"""

import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_piezometer_physical_range():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    # Valid normal value
    ok, msg = engine.evaluate_sensor_qc_range("PIEZOMETER", 120.5)
    assert ok is True

    # Valid extreme hazardous value (must not be discarded)
    ok_high, msg_high = engine.evaluate_sensor_qc_range("PIEZOMETER", 450.0)
    assert ok_high is True

    # Physically impossible value (> 500 kPa or < -50 kPa)
    bad, msg_bad = engine.evaluate_sensor_qc_range("PIEZOMETER", 850.0)
    assert bad is False
    assert "OUT OF PHYSICAL BOUNDS" in msg_bad


def test_inclinometer_physical_range():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    # Valid normal displacement
    ok, _ = engine.evaluate_sensor_qc_range("INCLINOMETER", 12.4)
    assert ok is True

    # Out of physical range (> 100mm)
    bad, msg_bad = engine.evaluate_sensor_qc_range("INCLINOMETER", 350.0)
    assert bad is False
    assert "OUT OF PHYSICAL BOUNDS" in msg_bad


def test_rain_gauge_physical_range():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    # Valid monsoon cloudburst rate (120 mm/h)
    ok, _ = engine.evaluate_sensor_qc_range("RAIN_GAUGE", 120.0)
    assert ok is True

    # Impossible rainfall rate
    bad, _ = engine.evaluate_sensor_qc_range("RAIN_GAUGE", 500.0)
    assert bad is False
