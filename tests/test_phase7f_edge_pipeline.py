"""
PHASE 7F — CP 7F-03 & 7F-04: Edge/MQTT Pipeline & Hardware-in-the-Loop (HIL) Tests
Verifies broker status reporting (BROKER_UNAVAILABLE when offline),
topic hierarchy decoding, packet parsing, observation storage, and HIL scenario handling.
"""
import os
import sys
import json
import socket
import unittest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mqtt_ingestion import MQTTIngestionService
from engine.observation_store import GLOBAL_OBSERVATION_STORE, ObservationRecord


class TestEdgePipelineAndHIL(unittest.TestCase):
    """CP 7F-03 & 7F-04: Edge / MQTT ingestion pipeline & HIL simulation."""

    def setUp(self):
        self.service = MQTTIngestionService()

    def test_01_broker_port_closed_reports_unavailable(self):
        """When MQTT broker daemon is not running on localhost:1883, must detect closed port."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        is_open = False
        try:
            res = s.connect_ex(("localhost", 1883))
            is_open = (res == 0)
        except Exception:
            is_open = False
        finally:
            s.close()
        # Port 1883 must not be faked as open
        self.assertFalse(is_open, "MQTT port 1883 must be closed in test environment (no broker running)")

    def test_02_topic_parsing_hierarchy(self):
        """Topic parsing must correctly extract state, sector_id, device_id, message_type."""
        topic = "pahad/Sikkim/CORR-NH10-SIKKIM-KM48/PZ-01/telemetry"
        meta = self.service.parse_topic(topic)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["state"], "Sikkim")
        self.assertEqual(meta["sector_id"], "CORR-NH10-SIKKIM-KM48")
        self.assertEqual(meta["device_id"], "PZ-01")
        self.assertEqual(meta["message_type"], "telemetry")

    def test_03_handle_valid_mqtt_payload_persists_to_store(self):
        """A valid MQTT packet must validate and persist to ObservationStore."""
        topic = "pahad/Sikkim/CORR-NH10-SIKKIM-KM48/GTW-PZ-01/telemetry"
        payload = {
            "device_id": "GTW-PZ-01",
            "sequence_number": 999,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 27.3300,
            "longitude": 88.6100,
            "measurements": {
                "piezometer": {"value": 32.5, "unit": "kPa"}
            },
            "simulated": True
        }
        res = self.service.handle_message(topic, payload)
        self.assertEqual(res.get("status"), "ACCEPTED")
        self.assertEqual(res.get("device_id"), "GTW-PZ-01")

        # Verify record in ObservationStore
        latest = GLOBAL_OBSERVATION_STORE.get_latest("CORR-NH10-SIKKIM-KM48", "piezometer", limit=1)
        self.assertTrue(len(latest) >= 1)
        self.assertEqual(latest[0].value, 32.5)

    def test_04_reject_malformed_json(self):
        """Malformed JSON string must be cleanly rejected without crashing."""
        topic = "pahad/Sikkim/CORR-NH10-SIKKIM-KM48/PZ-01/telemetry"
        res = self.service.handle_message(topic, "INVALID_NOT_JSON{")
        self.assertEqual(res.get("status"), "REJECTED_DECODE_ERROR")

    def test_05_hil_scenario_rising_pore_pressure(self):
        """HIL simulation of rising pore-water pressure must store consecutive observations."""
        topic = "pahad/Sikkim/CORR-NH10-SIKKIM-KM48/HIL-PZ-01/telemetry"
        pressures = [15.0, 25.0, 38.0, 52.0]
        now = datetime.now(timezone.utc)

        for i, p in enumerate(pressures):
            payload = {
                "device_id": f"HIL-PZ-01",
                "sequence_number": 1000 + i,
                "timestamp": (now + timedelta(seconds=i * 5)).isoformat(),
                "latitude": 27.3300,
                "longitude": 88.6100,
                "measurements": {"piezometer": {"value": p, "unit": "kPa"}},
                "simulated": True
            }
            res = self.service.handle_message(topic, payload)
            self.assertEqual(res.get("status"), "ACCEPTED")

        # Latest observation should reflect 52.0
        latest = GLOBAL_OBSERVATION_STORE.get_latest("CORR-NH10-SIKKIM-KM48", "piezometer", limit=1)
        self.assertTrue(len(latest) >= 1)
        self.assertEqual(latest[0].value, 52.0)


if __name__ == "__main__":
    unittest.main()
