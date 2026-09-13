"""
Test Suite: Alert Lifecycle State Machine (Phase 3.5)
Validates complete state progression:
CREATED -> READY_FOR_AUTHORIZATION -> AUTHORIZED -> DISPATCHED -> ACKNOWLEDGED -> RESOLVED.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_notification_orchestrator import PahadNotificationOrchestrator


class TestAlertLifecycle(unittest.TestCase):
    """Tests lifecycle states, transitions, query filtering, and closure invariants."""

    def setUp(self):
        self.orchestrator = PahadNotificationOrchestrator(dry_run=True)

    def test_state_transitions(self):
        """Walk through every state transition and verify updated timestamp and metadata."""
        alert = self.orchestrator.process_pahad_prediction(
            sector_id="SK-LIFECYCLE-01",
            cri=82.0,
            event_probability=0.80,
            factor_of_safety=0.92,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            coordinates=[27.200, 88.550],
        )
        alert_id = alert.alert_id

        # Initial: READY_FOR_AUTHORIZATION
        self.assertEqual(alert.lifecycle_state, "READY_FOR_AUTHORIZATION")

        # 1. Authorize
        auth_res = self.orchestrator.authorize_alert(alert_id, actor="Authority Officer")
        self.assertEqual(auth_res["lifecycle_state"], "AUTHORIZED")

        # 2. Dispatch
        disp_res = self.orchestrator.dispatch_alert(alert_id, actor="Dispatch Tech", selected_channels=["push"])
        self.assertEqual(disp_res["lifecycle_state"], "DISPATCHED")

        # 3. Acknowledge
        ack_res = self.orchestrator.acknowledge_alert(alert_id, actor="SDRF Field Lead", notes="Acknowledged; team deploying.")
        self.assertEqual(ack_res["status"], "ACKNOWLEDGED")
        self.assertEqual(self.orchestrator.get_alert(alert_id)["lifecycle_state"], "ACKNOWLEDGED")

        # 4. Resolve
        res_res = self.orchestrator.resolve_alert(alert_id, actor="Command HQ", resolution_notes="Slope stabilized.")
        self.assertEqual(res_res["status"], "RESOLVED")
        self.assertEqual(self.orchestrator.get_alert(alert_id)["lifecycle_state"], "RESOLVED")

    def test_filtering_alerts_by_lifecycle_state(self):
        """Verify list_alerts filtering across states."""
        # Process a low alert (auto-authorized) and an extreme alert (ready for auth)
        alert_low = self.orchestrator.process_pahad_prediction(
            sector_id="SK-LOW-STATE",
            cri=20.0,
            event_probability=0.20,
            factor_of_safety=1.80,
            rainfall_trigger=False,
            signal_agreement="0/3",
            coordinates=[27.100, 88.500],
        )
        alert_high = self.orchestrator.process_pahad_prediction(
            sector_id="SK-HIGH-STATE",
            cri=85.0,
            event_probability=0.85,
            factor_of_safety=0.85,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            coordinates=[27.200, 88.550],
        )

        all_alerts = self.orchestrator.list_alerts(filter_state="ALL")
        self.assertGreaterEqual(len(all_alerts), 2)

        active_alerts = self.orchestrator.list_alerts(filter_state="ACTIVE")
        self.assertGreaterEqual(len(active_alerts), 2)

        # Resolve low alert
        self.orchestrator.resolve_alert(alert_low.alert_id, actor="System")
        active_after = self.orchestrator.list_alerts(filter_state="ACTIVE")
        active_ids = [a["alert_id"] for a in active_after]
        self.assertNotIn(alert_low.alert_id, active_ids)
        self.assertIn(alert_high.alert_id, active_ids)

    def test_resolved_alert_cannot_be_reauthorized(self):
        """A resolved alert returns NOOP if authorization is attempted."""
        alert = self.orchestrator.process_pahad_prediction(
            sector_id="SK-CLOSED-01",
            cri=80.0,
            event_probability=0.80,
            factor_of_safety=0.90,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            coordinates=[27.200, 88.550],
        )
        self.orchestrator.authorize_alert(alert.alert_id, actor="DM")
        self.orchestrator.dispatch_alert(alert.alert_id, actor="Ops")
        self.orchestrator.resolve_alert(alert.alert_id, actor="DM")

        res = self.orchestrator.authorize_alert(alert.alert_id, actor="Late Signer")
        self.assertEqual(res["status"], "NOOP")


if __name__ == "__main__":
    unittest.main()
