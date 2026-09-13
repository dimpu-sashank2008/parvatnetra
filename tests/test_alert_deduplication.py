"""
Test Suite: Deterministic Alert Fingerprinting & Deduplication (Phase 3.5)
Validates alert deduplication windows, suppression of repeated identical alerts,
and immediate escalation when risk severity increases.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_notification_orchestrator import PahadNotificationOrchestrator


class TestAlertDeduplication(unittest.TestCase):
    """Tests deterministic deduplication mechanics to prevent alert fatigue and notification storms."""

    def setUp(self):
        self.orchestrator = PahadNotificationOrchestrator(dry_run=True)

    def test_repeated_prediction_within_window_updates_existing_alert(self):
        """Repeated prediction for the same sector and severity should update the same alert_id."""
        # First reading
        alert1 = self.orchestrator.process_pahad_prediction(
            sector_id="SK-DEDUP-01",
            cri=78.0,
            event_probability=0.75,
            factor_of_safety=0.95,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            coordinates=[27.200, 88.550],
        )
        alert1_id = alert1.alert_id

        # Second reading 1 minute later with slightly updated CRI
        alert2 = self.orchestrator.process_pahad_prediction(
            sector_id="SK-DEDUP-01",
            cri=79.5,
            event_probability=0.76,
            factor_of_safety=0.94,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            coordinates=[27.200, 88.550],
        )
        alert2_id = alert2.alert_id

        # Must be the exact same alert ID
        self.assertEqual(alert1_id, alert2_id)
        self.assertEqual(alert2.cri, 79.5)

    def test_different_sectors_produce_different_fingerprints(self):
        """Different sectors must produce distinct alerts even with identical risk scores."""
        alert_a = self.orchestrator.process_pahad_prediction(
            sector_id="SK-SECTOR-A",
            cri=80.0,
            event_probability=0.80,
            factor_of_safety=0.90,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            coordinates=[27.200, 88.550],
        )
        alert_b = self.orchestrator.process_pahad_prediction(
            sector_id="SK-SECTOR-B",
            cri=80.0,
            event_probability=0.80,
            factor_of_safety=0.90,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            coordinates=[27.300, 88.600],
        )
        self.assertNotEqual(alert_a.alert_id, alert_b.alert_id)
        self.assertNotEqual(alert_a.fingerprint, alert_b.fingerprint)

    def test_severity_escalation_bypasses_dedup(self):
        """When risk level escalates (e.g. MODERATE -> EXTREME), a new alert is generated."""
        # Reading 1: MODERATE
        alert_mod = self.orchestrator.process_pahad_prediction(
            sector_id="SK-ESCALATE-01",
            cri=35.0,
            event_probability=0.40,
            factor_of_safety=1.35,
            rainfall_trigger=False,
            signal_agreement="0/3",
            coordinates=[27.200, 88.550],
        )
        self.assertEqual(alert_mod.alert_level, "MODERATE")

        # Reading 2: Sudden surge to EXTREME
        alert_ext = self.orchestrator.process_pahad_prediction(
            sector_id="SK-ESCALATE-01",
            cri=88.0,
            event_probability=0.88,
            factor_of_safety=0.72,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            coordinates=[27.200, 88.550],
        )
        self.assertEqual(alert_ext.alert_level, "EXTREME")

        # Must have different fingerprints and alert IDs
        self.assertNotEqual(alert_mod.alert_id, alert_ext.alert_id)
        self.assertNotEqual(alert_mod.fingerprint, alert_ext.fingerprint)


if __name__ == "__main__":
    unittest.main()
