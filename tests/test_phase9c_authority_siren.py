# -*- coding: utf-8 -*-
"""
tests/test_phase9c_authority_siren.py
=====================================
Phase 9C: PAHAD Autonomous Siren Access & Safety Invariant Test Suite.

Verifies:
1. GET /api/authority/siren-access returns initial DISABLED state.
2. POST /api/authority/siren-access enforces strict role-based access:
   - Citizen role returns 403 Forbidden.
   - Authority role can transition between DISABLED and ARMED FOR AUTHORITY USE.
3. Strict Safety Invariants:
   - human_authorization_required: True
   - two_of_three_corroboration_required: True
   - AI model CANNOT independently sound sirens.
4. UI elements:
   - #pahad-autonomous-siren-card
   - #siren-access-badge
   - #btn-toggle-siren-access
   - #siren-state-display
   - Statutory safety warning text.
"""

import os
import json
import pytest
from app import app as flask_app

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")


@pytest.fixture
def client():
    """Flask test client."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def index_html():
    """Load index.html content."""
    assert os.path.exists(TEMPLATE_PATH), f"Template not found at {TEMPLATE_PATH}"
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


class TestPhase9cSirenBackendAPI:
    """Verifies backend API security and safety invariant checks."""

    def test_get_siren_access_status(self, client):
        """GET /api/authority/siren-access returns 200 with safety invariants."""
        res = client.get("/api/authority/siren-access")
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data.get("success") is True
        assert data.get("state") in ["DISABLED", "ARMED FOR AUTHORITY USE"]
        assert data.get("human_authorization_required") is True
        assert data.get("two_of_three_corroboration_required") is True

    def test_post_siren_access_citizen_forbidden(self, client):
        """POST /api/authority/siren-access returns 403 for citizen role."""
        with client.session_transaction() as sess:
            sess["role"] = "citizen"
        
        res = client.post(
            "/api/authority/siren-access",
            data=json.dumps({"action": "ARM"}),
            content_type="application/json"
        )
        assert res.status_code == 403
        data = json.loads(res.data)
        assert data.get("error") == "FORBIDDEN_AUTHORITY_ROLE_REQUIRED"

    def test_post_siren_access_authority_arm_and_disarm(self, client):
        """POST /api/authority/siren-access allows authorized authority to arm and disarm."""
        with client.session_transaction() as sess:
            sess["role"] = "authority"

        # Arm
        res_arm = client.post(
            "/api/authority/siren-access",
            data=json.dumps({"action": "ARM"}),
            content_type="application/json"
        )
        assert res_arm.status_code == 200
        data_arm = json.loads(res_arm.data)
        assert data_arm.get("success") is True
        assert data_arm["siren_access"]["state"] == "ARMED FOR AUTHORITY USE"
        assert data_arm["siren_access"]["human_authorization_required"] is True

        # Disarm
        res_disarm = client.post(
            "/api/authority/siren-access",
            data=json.dumps({"action": "DISARM"}),
            content_type="application/json"
        )
        assert res_disarm.status_code == 200
        data_disarm = json.loads(res_disarm.data)
        assert data_disarm.get("success") is True
        assert data_disarm["siren_access"]["state"] == "DISABLED"


class TestPhase9cSirenUI:
    """Verifies siren access card elements and safety copy in index.html."""

    def test_siren_card_and_badges_present(self, index_html):
        """Card, badges, and arming buttons must be defined."""
        assert 'id="pahad-autonomous-siren-card"' in index_html
        assert 'id="siren-access-badge"' in index_html
        assert 'id="btn-toggle-siren-access"' in index_html
        assert 'id="siren-state-display"' in index_html
        assert 'id="btn-manual-emergency-siren"' in index_html

    def test_siren_safety_invariant_warnings(self, index_html):
        """Must state that AI CANNOT independently sound sirens and requires 2-of-3 corroboration."""
        assert "Safety Invariants &amp; Statutory Authority Protocol" in index_html or "Safety Invariants" in index_html
        assert "CANNOT" in index_html
        assert "2-of-3 independent sensor corroboration" in index_html or "2-of-3" in index_html

    def test_siren_client_functions(self, index_html):
        """Client functions initAutonomousSirenAccess and toggleAutonomousSirenAccessState exist."""
        assert "function initAutonomousSirenAccess(" in index_html
        assert "function toggleAutonomousSirenAccessState(" in index_html
        assert "window.initAutonomousSirenAccess = initAutonomousSirenAccess;" in index_html
        assert "window.toggleAutonomousSirenAccessState = toggleAutonomousSirenAccessState;" in index_html
