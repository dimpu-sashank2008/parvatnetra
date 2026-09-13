# -*- coding: utf-8 -*-
"""
tests/test_shadow_operations.py
===============================
Phase 6B Test Suite: Supervised Shadow Operations & Alert Suppression Safety Guardrail
"""

import sys
import os
import sqlite3
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "observations", "pahad_observations.db")
)


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


class TestShadowOperationsMode:

    def test_broadcast_trigger_suppressed_under_env_flag(self, client):
        payload = {
            "region_name": "NH-10 Km 48 Corridor",
            "severity": "RED"
        }
        with patch.dict(os.environ, {"PAHAD_SHADOW_MODE": "1"}, clear=False):
            with patch("app.ALERT_BUS.broadcast") as mock_broadcast:
                resp = client.post("/api/alerts/broadcast-trigger", json=payload)
                assert resp.status_code == 201
                data = resp.get_json()
                assert data["status"] == "SUPPRESSED_SHADOW_OPERATIONS"
                assert data["shadow_mode"] is True
                assert data["public_dispatch_suppressed"] is True
                # Critical guardrail: ALERT_BUS.broadcast must NEVER be called in shadow mode
                mock_broadcast.assert_not_called()

    def test_broadcast_trigger_suppressed_under_header_flag(self, client):
        payload = {
            "region_name": "Singtam Teesta Corridor",
            "severity": "ORANGE"
        }
        with patch.dict(os.environ, {"PAHAD_SHADOW_MODE": "0"}, clear=False):
            with patch("app.ALERT_BUS.broadcast") as mock_broadcast:
                resp = client.post(
                    "/api/alerts/broadcast-trigger",
                    json=payload,
                    headers={"X-Shadow-Mode": "1"}
                )
                assert resp.status_code == 201
                data = resp.get_json()
                assert data["status"] == "SUPPRESSED_SHADOW_OPERATIONS"
                mock_broadcast.assert_not_called()

    def test_broadcast_trigger_normal_mode_dispatches(self, client):
        payload = {
            "region_name": "Rangpo Checkpoint",
            "severity": "YELLOW"
        }
        with patch.dict(os.environ, {"PAHAD_SHADOW_MODE": "0"}, clear=False):
            with patch("app.ALERT_BUS.broadcast") as mock_broadcast:
                resp = client.post("/api/alerts/broadcast-trigger", json=payload)
                assert resp.status_code == 201
                data = resp.get_json()
                assert data["status"] == "SUCCESS"
                mock_broadcast.assert_called_once()

    def test_shadow_inference_endpoint(self, client):
        payload = {
            "sector_id": "SK-NH10-KM48",
            "latitude": 27.3300,
            "longitude": 88.6100,
            "forecast_horizon_hours": 24
        }
        resp = client.post("/api/pahad/shadow-inference", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "SUPPRESSED_SHADOW_OPERATIONS"
        assert data["shadow_mode"] is True
        assert data["public_dispatch_suppressed"] is True
        assert "inference" in data
        assert "event_probability" in data["inference"]
        assert "fos_physical" in data["inference"]
        assert "cri" in data["inference"]
        assert "recommendations" in data
        assert "alert_level" in data["recommendations"]
        assert data["recommendations"]["alert_level"] in ("GREEN", "YELLOW", "ORANGE", "RED")
        assert "corridor_route_impact" in data["recommendations"]
        assert data["suppression_policy"]["public_siren_activated"] is False
        assert data["suppression_policy"]["cap_broadcast_dispatched"] is False

    def test_shadow_alert_log_persistence(self, client):
        payload = {
            "sector_id": "SK-NH10-KM48",
            "latitude": 27.3300,
            "longitude": 88.6100
        }
        resp = client.post("/api/pahad/shadow-inference", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        trail_id = data.get("decision_trail_id")
        assert trail_id is not None

        # Verify entry in SQLite DB
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, sector_id, status FROM shadow_alert_log WHERE id = ?", (trail_id,))
        row = cur.fetchone()
        conn.close()

        assert row is not None
        assert row[1] == "SK-NH10-KM48"
        assert row[2] == "SUPPRESSED_SHADOW_OPERATIONS"
