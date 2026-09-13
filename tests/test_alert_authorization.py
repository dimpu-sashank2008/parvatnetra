"""
Test Suite: Alert Authorization & Safety Invariants (Phase 3.5)
Validates the constitutional safety gate:
Prediction != Recommendation != Authorized Alert != Dispatch.
Public emergency warnings REQUIRE explicit authority authorization.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_notification_orchestrator import PahadNotificationOrchestrator


class TestAlertAuthorization(unittest.TestCase):
    """Tests authorization sign-off workflows and rejection of unauthorized dispatches."""

    def setUp(self):
        self.orchestrator = PahadNotificationOrchestrator(dry_run=True)

    def test_unauthorized_alert_dispatch_rejected(self):
        """Dispatching an alert in READY_FOR_AUTHORIZATION without prior sign-off must be rejected."""
        alert = self.orchestrator.process_pahad_prediction(
            sector_id="SK-AUTH-GATE-01",
            cri=85.0,
            event_probability=0.85,
            factor_of_safety=0.88,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            coordinates=[27.200, 88.550],
        )
        self.assertTrue(alert.authorization_required)
        self.assertEqual(alert.lifecycle_state, "READY_FOR_AUTHORIZATION")

        # Attempt dispatch without authorization
        res = self.orchestrator.dispatch_alert(alert.alert_id, actor="Unauthorized Field Bot")
        self.assertEqual(res["status"], "REJECTED_UNAUTHORIZED")
        self.assertIn("requires explicit authority authorization", res["message"])

        # Alert state must remain READY_FOR_AUTHORIZATION
        fresh = self.orchestrator.get_alert(alert.alert_id)
        self.assertEqual(fresh["lifecycle_state"], "READY_FOR_AUTHORIZATION")

    def test_authorized_alert_dispatch_succeeds(self):
        """Once authorized by a named actor, dispatch succeeds immediately."""
        alert = self.orchestrator.process_pahad_prediction(
            sector_id="SK-AUTH-GATE-02",
            cri=85.0,
            event_probability=0.85,
            factor_of_safety=0.88,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            coordinates=[27.200, 88.550],
        )

        # 1. Authority signs off
        auth_res = self.orchestrator.authorize_alert(
            alert.alert_id,
            actor="District Magistrate (DM)",
            authorization_notes="Reviewed telemetry and geotechnical FoS breach."
        )
        self.assertEqual(auth_res["status"], "AUTHORIZED")
        self.assertEqual(auth_res["authorized_by"], "District Magistrate (DM)")

        # 2. Dispatch now succeeds
        disp_res = self.orchestrator.dispatch_alert(
            alert.alert_id,
            actor="Operations Room Lead",
            selected_channels=["push", "sms", "cap"]
        )
        self.assertEqual(disp_res["status"], "DISPATCHED")
        fresh = self.orchestrator.get_alert(alert.alert_id)
        self.assertEqual(fresh["lifecycle_state"], "DISPATCHED")
        self.assertIsNotNone(fresh["authorized_at"])

    def test_authorization_non_existent_alert(self):
        """Authorizing an invalid alert ID returns error status."""
        res = self.orchestrator.authorize_alert("NON-EXISTENT-ID", actor="DM")
        self.assertEqual(res["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
