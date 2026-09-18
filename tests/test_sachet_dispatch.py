"""Unit tests for Phase 12C: NDMA SACHET Cell-Broadcast & Siren Dispatch Engine."""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app


class TestSachetDispatch(unittest.TestCase):
    """Test suite for authorized NDMA SACHET cell-broadcast and siren dispatch."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_dispatch_unauthorized_pin(self):
        """Verify invalid PIN is rejected with HTTP 401."""
        res = self.client.post("/api/alerts/dispatch-sachet", json={
            "commander_pin": "WRONG-PIN",
            "sector_id": "SK-NH10-KM48",
            "corroborated_signals": 3
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("status"), "UNAUTHORIZED")

    def test_dispatch_safety_gate_insufficient_signals(self):
        """Verify dispatch rejected if 2-of-3 safety gate is not met (signals < 2)."""
        res = self.client.post("/api/alerts/dispatch-sachet", json={
            "commander_pin": "NDMA-2026",
            "sector_id": "SK-NH10-KM48",
            "corroborated_signals": 1
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("status"), "SAFETY_GATE_REJECTED")

    def test_dispatch_authorized_success(self):
        """Verify valid authorized dispatch triggers cell-broadcast and siren dry-run."""
        res = self.client.post("/api/alerts/dispatch-sachet", json={
            "commander_pin": "NDMA-2026",
            "sector_id": "SK-NH10-KM48",
            "corroborated_signals": 3,
            "target_subscribers": 5000
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "DISPATCHED")
        self.assertTrue(data.get("dispatch_id").startswith("CAP-CDAC-"))
        self.assertIn("cdac_cell_broadcast", data)
        self.assertGreaterEqual(data["cdac_cell_broadcast"]["delivered_acknowledgments"], 4900)
        self.assertIn("siren_actuation", data)
        self.assertTrue(data["siren_actuation"]["dry_run"])
        self.assertEqual(data["siren_actuation"]["relay_state"], "ACTUATED_DRY_RUN")


if __name__ == "__main__":
    unittest.main()
