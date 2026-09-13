"""
PHASE 7F — CP 7F-01: Telemetry Contract Audit Tests
Verifies that the telemetry contract enforces the canonical schema,
supports all 4 primary hillslope sensor types, and strictly rejects
malformed, corrupt, impossible, and duplicate/replayed packets.
"""
import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.telemetry_contract import (
    GLOBAL_TELEMETRY_VALIDATOR,
    TelemetryValidator,
    PHYSICAL_SENSOR_LIMITS,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_INVALID,
)


class TestTelemetryContractAudit(unittest.TestCase):
    """CP 7F-01: In-situ telemetry contract schema and validation audits."""

    def setUp(self):
        self.validator = TelemetryValidator()
        self.base_packet = {
            "device_id": "SN-TEST-PIEZ-01",
            "sensor_id": "SITE-NH10-PIEZ-01",
            "sequence_number": 101,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 27.3300,
            "longitude": 88.6100,
            "sensor_type": "piezometer",
            "measurements": {
                "pore_pressure": {"value": 24.5, "unit": "kPa"}
            },
            "battery": 92.0,
            "signal_quality": -72.0,
            "firmware_version": "v1.2.0",
            "transport": "MQTT",
            "provenance": "[SIMULATED]"
        }

    def test_01_valid_packet_accepted(self):
        """A complete valid packet conforming to schema must be ACCEPTED."""
        res = self.validator.validate_and_normalize(self.base_packet)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "ACCEPTED")
        self.assertIsNotNone(res.packet)
        self.assertEqual(res.packet.device_id, "SN-TEST-PIEZ-01")

    def test_02_all_four_primary_sensor_types_supported(self):
        """Must support piezometer, inclinometer, tiltmeter, rain gauge."""
        supported_types = ["piezometer", "inclinometer", "tilt", "rain_gauge"]
        for st in supported_types:
            limits = PHYSICAL_SENSOR_LIMITS.get(st)
            self.assertIsNotNone(limits, f"Sensor type {st} must have physical limits defined")
            min_v, max_v, unit, max_rate = limits
            self.assertLess(min_v, max_v)
            self.assertTrue(unit)
            self.assertGreater(max_rate, 0.0)

    def test_03_reject_missing_device_id(self):
        """Packets without device_id must be REJECTED."""
        pkt = dict(self.base_packet)
        pkt.pop("device_id")
        res = self.validator.validate_and_normalize(pkt)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "REJECTED_MISSING_DEVICE_ID")

    def test_04_reject_corrupt_sequence_number(self):
        """Packets with non-integer or corrupt sequence number must be REJECTED."""
        pkt = dict(self.base_packet)
        pkt["sequence_number"] = "not_a_number"
        res = self.validator.validate_and_normalize(pkt)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "REJECTED_CORRUPT_SEQUENCE")

    def test_05_reject_duplicate_packet(self):
        """Duplicate packets with same sequence and timestamp must be REJECTED."""
        pkt1 = dict(self.base_packet)
        res1 = self.validator.validate_and_normalize(pkt1)
        self.assertTrue(res1.is_valid)

        # Send same packet again
        res2 = self.validator.validate_and_normalize(pkt1)
        self.assertFalse(res2.is_valid)
        self.assertEqual(res2.status, "REJECTED_DUPLICATE")

    def test_06_reject_out_of_bounds_coordinates(self):
        """Packets outside NER bounding box (20-30N, 87-98E) must be REJECTED."""
        pkt = dict(self.base_packet)
        pkt["sequence_number"] = 201
        pkt["latitude"] = 12.9716  # Bangalore (outside NER)
        pkt["longitude"] = 77.5946
        res = self.validator.validate_and_normalize(pkt)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "REJECTED_OUT_OF_BOUNDS")

    def test_07_reject_future_timestamp(self):
        """Packets with timestamp >30s in future must be REJECTED."""
        pkt = dict(self.base_packet)
        pkt["sequence_number"] = 301
        future_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        pkt["timestamp"] = future_time.isoformat()
        res = self.validator.validate_and_normalize(pkt)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "REJECTED_FUTURE_TIMESTAMP")

    def test_08_reject_impossible_pore_pressure(self):
        """Pore pressure exceeding physical range (>250 kPa) must be REJECTED."""
        pkt = dict(self.base_packet)
        pkt["sequence_number"] = 401
        pkt["measurements"] = {"piezometer": {"value": 850.0, "unit": "kPa"}}
        res = self.validator.validate_and_normalize(pkt)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "REJECTED_IMPOSSIBLE_VALUE")

    def test_09_reject_impossible_tilt(self):
        """Tilt exceeding physical range (>45 deg) must be REJECTED."""
        pkt = dict(self.base_packet)
        pkt["sequence_number"] = 501
        pkt["measurements"] = {"tilt": {"value": 89.5, "unit": "deg"}}
        res = self.validator.validate_and_normalize(pkt)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "REJECTED_IMPOSSIBLE_VALUE")

    def test_10_degrade_quality_on_low_battery_or_weak_rssi(self):
        """Low battery (<15%) or weak signal (<-95 dBm) must degrade packet quality."""
        pkt = dict(self.base_packet)
        pkt["sequence_number"] = 601
        pkt["battery"] = 8.0  # Critically low battery
        pkt["signal_quality"] = -98.0  # Poor LoRa RSSI
        res = self.validator.validate_and_normalize(pkt)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.overall_quality, QUALITY_DEGRADED)


if __name__ == "__main__":
    unittest.main()
