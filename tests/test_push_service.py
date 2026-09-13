"""
Test Suite: Web and Mobile Push Notification Service (Phase 3.5)
Validates push subscription lifecycle, payload structure, delivery logging,
and DRY_RUN safety invariants.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from services.push_service import PushService, PushPayload, PushSubscription


class TestPushService(unittest.TestCase):
    """Tests push service subscription registry and dispatch mechanics."""

    def setUp(self):
        # Explicit dry_run=True for safe testing
        self.service = PushService(dry_run=True)

    def test_default_seed_subscriptions(self):
        """Service should initialize with pre-seeded test endpoints."""
        self.assertGreaterEqual(len(self.service._subscriptions), 1)

    def test_subscribe_and_unsubscribe_lifecycle(self):
        """Verify dynamic registration and deactivation of push endpoints."""
        res = self.service.subscribe(
            recipient_id="REC-TEST-USER-99",
            endpoint="https://push.browser.test/user99",
            platform="web",
        )
        self.assertEqual(res["status"], "SUBSCRIBED")
        sub_id = res["subscription_id"]
        self.assertIn(sub_id, self.service._subscriptions)
        self.assertTrue(self.service._subscriptions[sub_id].active)

        # Unsubscribe
        unsub_res = self.service.unsubscribe(sub_id)
        self.assertEqual(unsub_res["status"], "UNSUBSCRIBED")
        self.assertFalse(self.service._subscriptions[sub_id].active)

    def test_send_push_notification_dry_run(self):
        """Verify push payload dispatch returns SIMULATED_SENT and payload integrity under dry-run."""
        # Subscribe an active recipient
        sub_res = self.service.subscribe("REC-ACTIVE-01", "https://push.test/active01", "web")
        sub_id = sub_res["subscription_id"]

        payload = PushPayload(
            title="LANDSLIDE WARNING",
            severity="VERY_HIGH",
            location="NH-10 Km 48",
            short_message="Slope movement detected. Exercise caution.",
            issued_at="2026-09-09T12:00:00Z",
            alert_id="ALT-TEST-001",
        )

        dispatch_res = self.service.send_notification("REC-ACTIVE-01", payload)
        self.assertEqual(dispatch_res["status"], "SIMULATED_SENT")
        self.assertTrue(dispatch_res["dry_run"])
        self.assertEqual(dispatch_res["provenance"], "[DRY RUN]")
        self.assertEqual(dispatch_res["payload"]["alert_id"], "ALT-TEST-001")
        self.assertEqual(dispatch_res["payload"]["severity"], "VERY_HIGH")

        # Verify delivery log
        notif_id = dispatch_res["notification_id"]
        logged = self.service.get_delivery_status(notif_id)
        self.assertIsNotNone(logged)
        self.assertEqual(logged["recipient_id"], "REC-ACTIVE-01")

    def test_send_push_no_active_subscription(self):
        """Target with no active subscriptions returns FAILED_NO_SUBSCRIPTION."""
        payload = PushPayload(
            title="TEST",
            severity="LOW",
            location="Zone X",
            short_message="All normal",
            issued_at="2026-09-09T12:00:00Z",
            alert_id="ALT-NONE",
        )
        res = self.service.send_notification("NON-EXISTENT-RECIPIENT", payload)
        self.assertEqual(res["status"], "FAILED_NO_SUBSCRIPTION")


if __name__ == "__main__":
    unittest.main()
