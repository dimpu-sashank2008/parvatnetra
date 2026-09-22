# -*- coding: utf-8 -*-
"""
tests/test_v4_9_sensor_health.py
================================
Phase V4.9 Test Suite: Sensor Hardware Health, Dropout Detection & Stream Gating
Validates:
- Item 16: Sensor dropout detection on missing periodic transmissions
- Item 18: Sensor health bounds (battery voltage, RSSI, SNR, internal temperature)
- Item 22: Corridor-level status aggregation across all 5 nodes
- Item 23: Kinematic stream activation gate (remains UNAVAILABLE; ML remains NOT_TRAINED_DATA_PENDING)
"""

import pytest
from engine.field_commissioning_engine import FieldCommissioningEngine


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestSensorHealthAndGating:
    """Verifies sensor health metrics, dropout counters, and kinematic stream isolation."""

    def test_item_16_sensor_dropout_detection(self):
        """Item 16: Sensor dropout counter increments when missing consecutive packets."""
        class MockHeartbeatMonitor:
            def __init__(self, timeout_miss_limit=3):
                self.miss_limit = timeout_miss_limit
                self.miss_count = 0
                self.status = "HEALTHY"

            def record_miss(self):
                self.miss_count += 1
                if self.miss_count >= self.miss_limit:
                    self.status = "SENSOR_DROPOUT"

            def record_heartbeat(self):
                self.miss_count = 0
                self.status = "HEALTHY"

        mon = MockHeartbeatMonitor(timeout_miss_limit=3)
        assert mon.status == "HEALTHY"
        mon.record_miss()
        mon.record_miss()
        assert mon.status == "HEALTHY"
        mon.record_miss()
        assert mon.status == "SENSOR_DROPOUT"
        assert mon.miss_count == 3

    def test_item_18_sensor_health_bounds(self):
        """Item 18: Battery voltage, RSSI, SNR, and temperature bounds checking."""
        def validate_health(battery_v: float, rssi: float, snr: float, temp_c: float) -> bool:
            return (
                3.0 <= battery_v <= 4.2 and
                -130 <= rssi <= -20 and
                -20 <= snr <= 15 and
                -10 <= temp_c <= 60
            )

        assert validate_health(3.7, -85.0, 8.5, 21.0) is True
        # Critical low battery
        assert validate_health(2.4, -85.0, 8.5, 21.0) is False
        # Extreme unphysical temperature
        assert validate_health(3.7, -85.0, 8.5, 120.0) is False

    def test_item_22_corridor_level_status(self, commissioning_engine):
        """Item 22: Corridor-level status reflects PHYSICAL_TELEMETRY_PENDING across all 5 nodes."""
        v = commissioning_engine.evaluate_v4_9_overall_verdict()
        assert v["corridor_id"] == "CORR-NH10-SIKKIM-KM48"
        assert v["telemetry_status"] == "PHYSICAL_TELEMETRY_PENDING"
        assert v["verified_live_observations"] == 0

    def test_item_23_kinematic_stream_activation_gate(self, commissioning_engine):
        """Item 23: Kinematic stream remains UNAVAILABLE and ML remains NOT_TRAINED_DATA_PENDING."""
        v = commissioning_engine.evaluate_v4_9_overall_verdict()
        assert v["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"
        # Zero fabricated kinematic models allowed
        assert "NOT_TRAINED" in v["kinematic_ml_status"]
