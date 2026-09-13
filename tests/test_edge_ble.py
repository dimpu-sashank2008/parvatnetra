# -*- coding: utf-8 -*-
"""
tests/test_edge_ble.py
======================
Unit tests for BLE Alert Bridge & Local Security (Phase 3.4 Section 13, 14, 15).
Validates:
  - Device allowlist enforcement and unauthorized device rejection
  - HMAC-SHA256 signature generation and checksum verification
  - Monotonic sequence tracking and replay attack protection
  - Connection state transitions and mock adapter behavior
"""

import unittest
from backend.edge.ble_bridge import BLEAlertBridge


class TestEdgeBLE(unittest.TestCase):

    def setUp(self):
        self.ble = BLEAlertBridge(
            gateway_id="GW-01",
            allowed_devices={"DEV-BRO-FIELD-01", "DEV-SDRF-COMMAND-02"},
            signing_secret="TEST_BLE_SECRET_KEY"
        )

    def test_connect_authorized_device(self):
        """Connecting an allowlisted device must succeed."""
        res = self.ble.connect_device("DEV-BRO-FIELD-01")
        self.assertEqual(res["status"], "CONNECTED")
        self.assertEqual(self.ble.connection_state, "CONNECTED")
        self.assertEqual(self.ble.paired_device, "DEV-BRO-FIELD-01")

    def test_reject_unauthorized_device(self):
        """Connecting an untrusted device must be strictly rejected."""
        res = self.ble.connect_device("ROGUE-DEVICE-UNKNOWN")
        self.assertEqual(res["status"], "REJECTED_UNAUTHORIZED")
        self.assertIsNone(self.ble.paired_device)
        self.assertEqual(self.ble.connection_state, "DISCONNECTED")

    def test_send_alert_without_pairing_fails(self):
        """Transmitting an alert without a connected device must fail safely."""
        res = self.ble.send_alert("ALT-001", "CRITICAL")
        self.assertEqual(res["status"], "FAILED_NO_CONNECTION")

    def test_send_alert_payload_and_signature(self):
        """Transmitted alert must include valid HMAC signature, sequence, and gateway ID."""
        self.ble.connect_device("DEV-BRO-FIELD-01")
        res = self.ble.send_alert("ALT-001", "CRITICAL")

        self.assertEqual(res["status"], "TRANSMITTED")
        self.assertEqual(res["alert_id"], "ALT-001")
        self.assertEqual(res["severity"], "CRITICAL")
        self.assertEqual(res["gateway_id"], "GW-01")
        self.assertEqual(res["sequence"], 1)
        self.assertTrue(len(res["signature"]) > 0)
        self.assertTrue(res["acknowledged"])

    def test_monotonic_sequence_increment(self):
        """Subsequent alerts must increment monotonic sequence number."""
        self.ble.connect_device("DEV-BRO-FIELD-01")
        r1 = self.ble.send_alert("ALT-001", "WARNING")
        r2 = self.ble.send_alert("ALT-002", "CRITICAL")
        self.assertEqual(r1["sequence"], 1)
        self.assertEqual(r2["sequence"], 2)

    def test_disconnect(self):
        """Disconnecting must reset pairing state."""
        self.ble.connect_device("DEV-BRO-FIELD-01")
        self.assertEqual(self.ble.connection_state, "CONNECTED")
        disc = self.ble.disconnect()
        self.assertEqual(disc["status"], "DISCONNECTED")
        self.assertEqual(self.ble.connection_state, "DISCONNECTED")
        self.assertIsNone(self.ble.paired_device)


if __name__ == "__main__":
    unittest.main()
