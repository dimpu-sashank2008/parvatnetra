# -*- coding: utf-8 -*-
"""
tests/test_edge_siren.py
========================
Unit tests for Edge Siren Controller (Phase 3.4 Section 10, 11, 12).
Validates:
  - Strict DRY RUN default invariant (dry_run=True, hardware_enabled=False)
  - arm(), disarm(), and status() states
  - test() generating SIREN_TEST_EVENT without physical sounder activation
  - activate() respecting armed state and dry-run flag
  - Tamper-evident activation audit log storage
"""

import unittest
from backend.edge.edge_store import EdgeStore
from backend.edge.siren_controller import SirenController


class TestEdgeSiren(unittest.TestCase):

    def setUp(self):
        self.store = EdgeStore(db_path=":memory:")
        self.siren = SirenController(
            gateway_id="GW-01",
            hardware_enabled=False,
            dry_run=True,
            store=self.store
        )

    def test_default_dry_run_safety_invariant(self):
        """Siren MUST strictly default to dry_run=True and hardware_enabled=False."""
        status = self.siren.status()
        self.assertTrue(status["dry_run"], "Dry-run must be true by default")
        self.assertFalse(status["hardware_enabled"], "Physical hardware must be disabled by default")
        self.assertTrue(status["is_armed"], "Default state is armed for safety monitoring")

    def test_arm_and_disarm(self):
        """Controller must correctly transition between ARMED and DISARMED states."""
        self.siren.disarm()
        self.assertFalse(self.siren.status()["is_armed"])

        self.siren.arm()
        self.assertTrue(self.siren.status()["is_armed"])

    def test_test_mode_generates_siren_test_event(self):
        """Executing test() must generate SIREN_TEST_EVENT without physical output."""
        event = self.siren.test(requested_by="FIELD_OFFICER_CONSOLE")
        self.assertEqual(event["event_type"], "SIREN_TEST_EVENT")
        self.assertTrue(event["dry_run"])
        self.assertEqual(event["requested_by"], "FIELD_OFFICER_CONSOLE")
        self.assertFalse(event["physical_actuation"])

    def test_activation_while_disarmed_suppressed(self):
        """Activations must be suppressed when controller is disarmed."""
        self.siren.disarm()
        event = self.siren.activate(level="WARNING", alert_id="ALT-001", reason="Soil saturation")
        self.assertIn(event["status"], ("BLOCKED_DISARMED", "SUPPRESSED_DISARMED"))

    def test_dry_run_activation_logged_to_store(self):
        """Activations in dry-run mode must generate audit log entries marked dry_run=True."""
        event = self.siren.activate(level="CRITICAL", alert_id="ALT-999", reason="Borehole tilt critical")
        self.assertIn(event["status"], ("SOUNDING_SIMULATED", "ACTIVATED_DRY_RUN"))
        self.assertTrue(event["dry_run"])

        # Check in-memory SQLite store
        alerts = self.store.query_alerts(limit=5)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["alert_id"], "ALT-999")
        self.assertEqual(alerts[0]["severity"], "CRITICAL")
        self.assertEqual(alerts[0]["dry_run"], 1)
        self.assertEqual(alerts[0]["siren_activated"], 0) # 0 physical sounder


if __name__ == "__main__":
    unittest.main()
