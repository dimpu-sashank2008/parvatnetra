"""
Test Suite: Notification Center REST APIs & Web Views (Phase 3.5)
Validates endpoints:
- GET  /notifications (Mission Control UI)
- GET  /api/notifications
- GET  /api/notifications/status
- GET  /api/notifications/active
- GET  /api/notifications/<id>
- POST /api/notifications/<id>/authorize
- POST /api/notifications/<id>/dispatch
- POST /api/notifications/<id>/acknowledge
- GET  /api/notifications/<id>/delivery-status
- POST /api/push/subscribe & unsubscribe
- GET  /api/alert-policy/<sector_id>
- GET  /api/geofence/<id>
- POST /api/notifications/demo/trigger & reset
"""
import os
import json
import unittest

os.environ["PARVAT_TESTING"] = "1"
os.environ["PAHAD_DEMO_MODE"] = "1"

from app import app
from engine.pahad_notification_orchestrator import NOTIFICATION_ORCHESTRATOR


class TestNotificationAPI(unittest.TestCase):
    """Tests all Notification Center web views and REST APIs."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_notification_center_web_view(self):
        """GET /notifications renders mission control HTML template."""
        res = self.client.get("/notifications")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("NOTIFICATION CENTER & ALERT DISPATCH", html)
        self.assertIn("15 km Geofence", html)

    def test_list_notifications(self):
        """GET /api/notifications returns list of alerts and filter."""
        res = self.client.get("/api/notifications?state=ALL")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("alerts", data)
        self.assertIn("count", data)

    def test_get_notifications_status(self):
        """GET /api/notifications/status returns operational parameters and channel readiness."""
        res = self.client.get("/api/notifications/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        status = data["status"]
        self.assertIn("total_tracked", status)
        self.assertIn("active_count", status)
        self.assertEqual(status["alert_radius_km"], 15.0)
        self.assertTrue(status["dry_run"])

    def test_get_active_notifications(self):
        """GET /api/notifications/active returns active alerts list."""
        res = self.client.get("/api/notifications/active")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIsInstance(data["alerts"], list)

    def test_notification_detail_and_lifecycle_api(self):
        """Test detail, authorization, dispatch, and acknowledgment via REST API."""
        # 1. Create alert via orchestrator
        alert = NOTIFICATION_ORCHESTRATOR.process_pahad_prediction(
            sector_id="SK-REST-TEST",
            cri=83.0,
            event_probability=0.81,
            factor_of_safety=0.91,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            coordinates=[27.200, 88.550],
        )
        alert_id = alert.alert_id

        # 2. GET detail
        res_det = self.client.get(f"/api/notifications/{alert_id}")
        self.assertEqual(res_det.status_code, 200)
        det_data = res_det.get_json()
        self.assertEqual(det_data["alert"]["alert_id"], alert_id)
        self.assertIn("audit_logs", det_data)

        # 3. Unauthorized dispatch attempt -> 403
        res_unauth = self.client.post(
            f"/api/notifications/{alert_id}/dispatch",
            json={"actor": "Premature Runner", "channels": ["push"]}
        )
        self.assertEqual(res_unauth.status_code, 403)

        # 4. POST authorize -> 200
        res_auth = self.client.post(
            f"/api/notifications/{alert_id}/authorize",
            json={"actor": "District Magistrate", "notes": "Approved for public advisory."}
        )
        self.assertEqual(res_auth.status_code, 200)
        self.assertEqual(res_auth.get_json()["status"], "AUTHORIZED")

        # 5. POST dispatch -> 200
        res_disp = self.client.post(
            f"/api/notifications/{alert_id}/dispatch",
            json={"actor": "Duty Officer", "channels": ["push", "sms", "cap"]}
        )
        self.assertEqual(res_disp.status_code, 200)
        self.assertEqual(res_disp.get_json()["status"], "DISPATCHED")

        # 6. GET delivery status -> 200
        res_deliv = self.client.get(f"/api/notifications/{alert_id}/delivery-status")
        self.assertEqual(res_deliv.status_code, 200)
        deliv_data = res_deliv.get_json()
        self.assertEqual(deliv_data["lifecycle_state"], "DISPATCHED")

        # 7. POST acknowledge -> 200
        res_ack = self.client.post(
            f"/api/notifications/{alert_id}/acknowledge",
            json={"actor": "Field Patrol 04", "notes": "Evacuation corridor established."}
        )
        self.assertEqual(res_ack.status_code, 200)
        self.assertEqual(res_ack.get_json()["status"], "ACKNOWLEDGED")

    def test_push_subscribe_and_unsubscribe_api(self):
        """POST /api/push/subscribe and /api/push/unsubscribe."""
        # Subscribe
        sub_res = self.client.post(
            "/api/push/subscribe",
            json={"recipient_id": "REC-API-USER", "endpoint": "https://push.gov.in/test01", "platform": "web"}
        )
        self.assertEqual(sub_res.status_code, 200)
        sub_data = sub_res.get_json()
        self.assertEqual(sub_data["status"], "SUBSCRIBED")
        sub_id = sub_data["subscription_id"]

        # Missing endpoint -> 400
        bad_sub = self.client.post("/api/push/subscribe", json={"recipient_id": "REC-API-USER"})
        self.assertEqual(bad_sub.status_code, 400)

        # Unsubscribe
        unsub_res = self.client.post("/api/push/unsubscribe", json={"subscription_id": sub_id})
        self.assertEqual(unsub_res.status_code, 200)
        self.assertEqual(unsub_res.get_json()["status"], "UNSUBSCRIBED")

    def test_alert_policy_evaluation_endpoint(self):
        """GET /api/alert-policy/<sector_id> dynamically evaluates policy."""
        res = self.client.get("/api/alert-policy/SK-NH10-KM48?cri=82.0&event_probability=0.85&fos=0.92")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("policy_decision", data)
        self.assertEqual(data["policy_decision"]["recommended_alert_level"], "EXTREME")

    def test_geofence_endpoint(self):
        """GET /api/geofence/<alert_id> returns geometry and aggregates."""
        alert = NOTIFICATION_ORCHESTRATOR.process_pahad_prediction(
            sector_id="SK-GEO-API",
            cri=75.0,
            event_probability=0.70,
            factor_of_safety=1.02,
            rainfall_trigger=True,
            signal_agreement="2/3",
            coordinates=[27.200, 88.550],
        )
        res = self.client.get(f"/api/geofence/{alert.alert_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("impact_geometry", data)
        self.assertIn("zone_aggregates", data)

    def test_demo_trigger_and_reset_endpoints(self):
        """POST /api/notifications/demo/trigger and /api/notifications/demo/reset."""
        trig_res = self.client.post("/api/notifications/demo/trigger")
        self.assertEqual(trig_res.status_code, 200)
        trig_data = trig_res.get_json()
        self.assertEqual(trig_data["demo_scenario"], "SIH_EXTREME_MONSOON_SURGE")

        reset_res = self.client.post("/api/notifications/demo/reset")
        self.assertEqual(reset_res.status_code, 200)
        reset_data = reset_res.get_json()
        self.assertEqual(reset_data["status"], "SUCCESS")
        self.assertIn("Cleared", reset_data["message"])


if __name__ == "__main__":
    unittest.main()
