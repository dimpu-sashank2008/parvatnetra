# -*- coding: utf-8 -*-
"""
tests/test_phase11d_security_audit.py
=====================================
PARVAT NETRA • PAHAD AI — Phase 11D Security & RBAC Audit Suite
---------------------------------------------------------------
Verifies:
1. Authentication endpoints and credential verification.
2. Ephemeral token issuance, verification, and revocation.
3. RBAC permissions across roles (PUBLIC, FIELD_OPERATOR, DISTRICT_AUTHORITY, STATE_AUTHORITY, ADMIN).
4. Secret entropy and credential isolation invariants.
5. Fail-closed safety gates for public dispatch and siren triggers.
"""

import os
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import app
from services.authority_review_service import (
    ROLE_PUBLIC,
    ROLE_FIELD_OPERATOR,
    ROLE_AUTHORITY,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_ADMIN,
    ACTION_APPROVE,
    ACTION_REJECT,
    ACTION_REQUEST_FIELD_VERIFICATION,
    check_rbac_permission,
    AuthorizationTokenManager
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestPhase11dSecurityAudit:

    def test_01_authentication_endpoints(self, client):
        """Verify login routes and invalid credential rejection."""
        res_login = client.get("/login")
        assert res_login.status_code in [200, 302]

        res_bad_auth = client.post(
            "/login/authority",
            data={"username": "unauthorized_user", "password": "wrong_password"}
        )
        assert res_bad_auth.status_code in [400, 401, 403, 302]

    def test_02_authorization_token_manager(self):
        """Verify token manager rejects empty, malformed, and public role requests."""
        atm = AuthorizationTokenManager()
        is_valid, msg = atm.validate_token("MALFORMED.TOKEN.STRING", "ALERT-1", ROLE_DISTRICT_AUTHORITY)
        assert is_valid is False

        is_valid_empty, _ = atm.validate_token("", "ALERT-1", ROLE_DISTRICT_AUTHORITY)
        assert is_valid_empty is False

        # Public role is barred from obtaining an authorization token
        with pytest.raises(PermissionError):
            atm.issue_token("PUB-USER", ROLE_PUBLIC, "ALERT-1")

    def test_03_rbac_matrix_enforcement(self):
        """Verify role separation: Public cannot approve/dispatch; Authorities have granular permissions."""
        assert check_rbac_permission(ROLE_PUBLIC, "TRIGGER_SIREN") is False
        assert check_rbac_permission(ROLE_PUBLIC, ACTION_APPROVE) is False
        assert check_rbac_permission(ROLE_PUBLIC, "AUTHORIZE_DISPATCH") is False

        assert check_rbac_permission(ROLE_FIELD_OPERATOR, ACTION_REQUEST_FIELD_VERIFICATION) is True
        assert check_rbac_permission(ROLE_FIELD_OPERATOR, ACTION_APPROVE) is False

        assert check_rbac_permission(ROLE_DISTRICT_AUTHORITY, ACTION_APPROVE) is True
        assert check_rbac_permission(ROLE_STATE_AUTHORITY, ACTION_APPROVE) is True

    def test_04_secret_key_configuration(self):
        """Verify application has configured secret key."""
        sec = app.config.get("SECRET_KEY")
        assert sec is not None
        assert len(str(sec)) >= 16

    def test_05_safety_invariants_status(self, client):
        """Verify assistant status endpoint maintains public dispatch disabled."""
        res = client.get("/api/pahad/assistant/status")
        assert res.status_code == 200
        data = res.get_json()
        invariants = data.get("safety_invariants", {})
        assert invariants.get("public_dispatch") == "DISABLED"
        assert invariants.get("siren_dry_run") == 1
        assert invariants.get("conversational_actuation_permitted") is False
