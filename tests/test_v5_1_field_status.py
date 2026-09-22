# -*- coding: utf-8 -*-
"""
tests/test_v5_1_field_status.py
===============================
Phase V5.1 Test Suite: Physical Field Telemetry & Hardware Status Audit
Verifies zero fake hardware claims, zero continuous live mountain hours,
and zero installed borehole casings prior to drilling.
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestV51FieldStatus:
    """Verifies physical hardware and deployment reality."""

    def test_physical_hardware_zero_installed(self, truth_engine):
        hw = truth_engine.get_hardware_truth()
        assert hw.get("physical_sensors_verified") == 0
        assert hw.get("borehole_casings_installed") == 0
        assert hw.get("field_installations_verified") == 0
        assert hw.get("field_commissioning_verified") == 0

    def test_live_mountain_telemetry_hours_zero(self, truth_engine):
        hw = truth_engine.get_hardware_truth()
        assert hw.get("live_mountain_observations") == 0
        assert hw.get("continuous_live_telemetry_hours") == 0.0

    def test_bench_hil_observations_tracked(self, truth_engine):
        hw = truth_engine.get_hardware_truth()
        assert hw.get("bench_hil_observations") == 8640
        assert hw.get("telemetry_continuity_windows_status") == "UNAVAILABLE"
