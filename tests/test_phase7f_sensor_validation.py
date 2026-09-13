"""
PHASE 7F — CP 7F-02: Sensor Range & Quality Rules Tests
Verifies physical bounds and status classification:
LIVE, SIMULATED, HIL, STALE, QUARANTINED, REJECTED.
"""
import os
import sys
import time
import unittest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.telemetry_contract import (
    TelemetryValidator,
    PHYSICAL_SENSOR_LIMITS,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_INVALID,
)
from engine.sensor_pilot_readiness import SensorPilotReadinessHarness


class TestSensorValidation(unittest.TestCase):
    """CP 7F-02: Sensor range, physical bounds, and quality categorization."""

    def setUp(self):
        self.validator = TelemetryValidator()

    def test_01_piezometer_bounds(self):
        """Piezometer bounds [-10, 250] kPa: normal reading accepted, extreme rejected."""
        good = SensorPilotReadinessHarness.validate_reading("VW_PIEZOMETER", 45.0)
        self.assertTrue(good["valid"])
        self.assertEqual(good["quality"], "GOOD")

        bad = SensorPilotReadinessHarness.validate_reading("VW_PIEZOMETER", 600.0)
        self.assertFalse(bad["valid"])
        self.assertEqual(bad["quality"], "OUT_OF_RANGE")

    def test_02_inclinometer_bounds(self):
        """Inclinometer bounds [-500, 500] mm."""
        good = SensorPilotReadinessHarness.validate_reading("IN_PLACE_INCLINOMETER", -12.4)
        self.assertTrue(good["valid"])

        bad = SensorPilotReadinessHarness.validate_reading("IN_PLACE_INCLINOMETER", 999.0)
        self.assertFalse(bad["valid"])

    def test_03_tiltmeter_bounds(self):
        """Tiltmeter bounds [-15, 15] deg in harness; [-45, 45] deg in contract."""
        good = SensorPilotReadinessHarness.validate_reading("MEMS_TILTMETER", 3.2)
        self.assertTrue(good["valid"])

        bad = SensorPilotReadinessHarness.validate_reading("MEMS_TILTMETER", 40.0)
        self.assertFalse(bad["valid"])

    def test_04_rain_gauge_bounds(self):
        """Rain gauge bounds [0, 250] mm."""
        good = SensorPilotReadinessHarness.validate_reading("TIPPING_BUCKET_RAIN", 35.0)
        self.assertTrue(good["valid"])

        bad = SensorPilotReadinessHarness.validate_reading("TIPPING_BUCKET_RAIN", -5.0)
        self.assertFalse(bad["valid"])

    def test_05_unregistered_sensor_type_rejected(self):
        """Unregistered sensor type must return UNKNOWN_SENSOR."""
        res = SensorPilotReadinessHarness.validate_reading("GAMMA_SPECTROMETER", 100.0)
        self.assertFalse(res["valid"])
        self.assertEqual(res["quality"], "UNKNOWN_SENSOR")

    def test_06_simulated_packet_provenance_preserved(self):
        """HIL or simulated packets must have [SIMULATED] provenance, never [LIVE]."""
        pkt = {
            "device_id": "SN-HIL-TEST-01",
            "sequence_number": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 27.3300,
            "longitude": 88.6100,
            "simulated": True,
            "measurements": {"piezometer": {"value": 30.0, "unit": "kPa"}}
        }
        res = self.validator.validate_and_normalize(pkt)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.packet.provenance, "[SIMULATED]")

    def test_07_quarantine_abnormal_rate_of_change(self):
        """Rate of change exceeding 3x max physical delta must degrade packet quality."""
        dev_id = "SN-RATE-TEST-01"
        now = datetime.now(timezone.utc)

        # First reading: 10.0 kPa (current timestamp)
        pkt1 = {
            "device_id": dev_id,
            "sequence_number": 1,
            "timestamp": now.isoformat(),
            "latitude": 27.3300,
            "longitude": 88.6100,
            "measurements": {"piezometer": {"value": 10.0, "unit": "kPa"}}
        }
        res1 = self.validator.validate_and_normalize(pkt1)
        self.assertEqual(res1.overall_quality, QUALITY_GOOD)

        # Second reading immediately after: 180 kPa (jump of 170 kPa vs max 40 kPa/h * 3 = 120 kPa/h)
        pkt2 = {
            "device_id": dev_id,
            "sequence_number": 2,
            "timestamp": now.isoformat(),
            "latitude": 27.3300,
            "longitude": 88.6100,
            "measurements": {"piezometer": {"value": 180.0, "unit": "kPa"}}
        }
        res2 = self.validator.validate_and_normalize(pkt2)
        self.assertTrue(res2.is_valid)
        # Quality must be degraded due to abnormal velocity
        self.assertEqual(res2.overall_quality, QUALITY_DEGRADED)


if __name__ == "__main__":
    unittest.main()
