"""
Test Suite: Master Alert & Notification Orchestrator (Phase 3.5)
Validates end-to-end pipeline:
Prediction -> Recommendation -> Deduplication -> Authorization Gate -> Multi-Channel Dispatch -> Audit Log.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_notification_orchestrator import PahadNotificationOrchestrator


class TestNotificationOrchestrator(unittest.TestCase):
    """Tests master notification orchestrator pipeline and safety gates."""

    def setUp(self):
        self.orchestrator = PahadNotificationOrchestrator(dry_run=True)

    def test_process_prediction_creates_recommended_alert(self):
        """High risk prediction creates an OrchestratedAlert ready for authorization."""
        alert = self.orchestrator.process_pahad_prediction(
            sector_id="SK-NH10-TEST",
            cri=84.0,
            event_probability=0.86,
            factor_of_safety=0.91,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            coordinates=[27.200, 88.550],
            geom_type="point",
        )
        self.assertIsNotNone(alert.alert_id)
        self.assertEqual(alert.alert_level, "EXTREME")
        self.assertEqual(alert.lifecycle_state, "READY_FOR_AUTHORIZATION")
        self.assertTrue(alert.authorization_required)
        self.assertIn("zone_aggregates", alert.to_dict())

    def test_full_pipeline_flow(self):
        """Test full sequence: create -> authorize -> dispatch -> acknowledge -> resolve."""
        # 1. Ingest
        alert = self.orchestrator.process_pahad_prediction(
            sector_id="SK-FULL-FLOW",
            cri=79.0,
            event_probability=0.76,
            factor_of_safety=0.98,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            coordinates=[27.180, 88.530],
            geom_type="point",
        )
        alert_id = alert.alert_id

        # 2. Authorize
        auth_res = self.orchestrator.authorize_alert(alert_id, actor="District Magistrate North Sikkim")
        self.assertEqual(auth_res["status"], "AUTHORIZED")
        self.assertEqual(self.orchestrator.get_alert(alert_id)["lifecycle_state"], "AUTHORIZED")

        # 3. Dispatch
        disp_res = self.orchestrator.dispatch_alert(alert_id, actor="SDMA Duty Officer", selected_channels=["push", "sms", "cap"])
        self.assertEqual(disp_res["status"], "DISPATCHED")
        self.assertEqual(self.orchestrator.get_alert(alert_id)["lifecycle_state"], "DISPATCHED")
        self.assertIn("push", disp_res["channels"])
        self.assertIn("sms", disp_res["channels"])
        self.assertIn("cap", disp_res["channels"])

        # 4. Acknowledge
        ack_res = self.orchestrator.acknowledge_alert(alert_id, actor="Rangpo Field Team Lead")
        self.assertEqual(ack_res["status"], "ACKNOWLEDGED")
        self.assertEqual(self.orchestrator.get_alert(alert_id)["lifecycle_state"], "ACKNOWLEDGED")

        # 5. Resolve
        res_res = self.orchestrator.resolve_alert(alert_id, actor="Command Center")
        self.assertEqual(res_res["status"], "RESOLVED")
        self.assertEqual(self.orchestrator.get_alert(alert_id)["lifecycle_state"], "RESOLVED")

    def test_sih_demo_scenario_and_reset(self):
        """Verify SIH demo execution and clean demo reset."""
        demo_res = self.orchestrator.run_sih_demo_scenario(sector_id="SK-SIH-DEMO")
        self.assertEqual(demo_res["demo_scenario"], "SIH_EXTREME_MONSOON_SURGE")
        self.assertEqual(demo_res["provenance"], "[DEMO]")
        self.assertTrue(demo_res["dry_run"])

        # Verify alert was created with is_demo=True
        demo_alert_id = demo_res["alert"]["alert_id"]
        self.assertTrue(self.orchestrator.get_alert(demo_alert_id)["is_demo"])

        # Reset demo alerts
        cleared_count = self.orchestrator.reset_demo_alerts()
        self.assertGreaterEqual(cleared_count, 1)
        self.assertIsNone(self.orchestrator.get_alert(demo_alert_id))

    def test_audit_logging(self):
        """Actions must generate timestamped, tamper-evident audit entries."""
        initial_log_count = len(self.orchestrator.list_audit_logs())
        self.orchestrator.process_pahad_prediction(
            sector_id="SK-AUDIT-TEST",
            cri=55.0,
            event_probability=0.60,
            factor_of_safety=1.12,
            rainfall_trigger=False,
            signal_agreement="1/3",
            coordinates=[27.300, 88.600],
        )
        new_logs = self.orchestrator.list_audit_logs()
        self.assertGreater(len(new_logs), initial_log_count)
        latest = new_logs[0]
        self.assertIn("entry_id", latest)
        self.assertIn("timestamp", latest)
        self.assertIn("event", latest)


if __name__ == "__main__":
    unittest.main()
