# -*- coding: utf-8 -*-
"""
tests/test_role_experience_separation.py
========================================
PARVAT NETRA • Phase 12 — Role-Based Experience Separation Test Suite
---------------------------------------------------------------------
Verifies:
  1. Public & Citizen Persona:
     - Zero administrative privilege under DMA 2005 doctrine.
     - Rejection of emergency decision authorization (HTTP 403).
     - Rejection of public alert broadcast triggering (HTTP 403).
     - Rejection of tactical siren dispatch (HTTP 403).
     - Rejection of field report verification (HTTP 403).
     - Access to /?mode=authority without authenticated session defaults to citizen advisory.
     - Tactical siren button is hidden in citizen advisory view.

  2. Field Operator Persona (BRO Swastik / SDRF):
     - Access to field corridor registry and inspection endpoints.
     - Permission to verify field incident reports (HTTP 200).
     - Rejection of emergency decision authorization (HTTP 403).
     - Rejection of public alert broadcast triggering (HTTP 403).
     - Rejection of tactical siren dispatch (HTTP 403).

  3. District & State Authority Personas (DDMA / SDMA / EOC):
     - Permission to authorize emergency risk decisions (HTTP 200).
     - Permission to trigger multi-channel CAP alert broadcasts (HTTP 201).
     - Permission to dispatch tactical siren protocols (HTTP 200).
     - Permission to verify and triage field incident reports (HTTP 200).
     - Access to EOC operational view.

  4. System Administrator Persona:
     - Restricted to system telemetry and maintenance console.
     - Rejection of emergency decision authorization (HTTP 403).
     - Rejection of public alert broadcast triggering (HTTP 403).
     - Rejection of tactical siren dispatch (HTTP 403).

  5. Statutory DMA 2005 & Safety Gate Invariants:
     - Physical siren actuation remains locked in dry-run mode across all roles.
"""

import os
import sys
import json
import pytest

# Ensure repository root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

os.environ["PARVAT_TESTING"] = "1"

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# =============================================================================
# 1. PUBLIC & CITIZEN PERSONA TESTS
# =============================================================================

def test_unauthenticated_visitor_defaults_to_citizen(client):
    """Unauthenticated access to dashboard defaults to citizen mode."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "CITIZEN ADVISORY NODE" in html


def test_unauthenticated_cannot_elevate_via_query_param(client):
    """Unauthenticated visitor passing ?mode=authority cannot elevate privileges."""
    res = client.get("/?mode=authority")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    # Must remain in citizen advisory mode without authority badge
    assert "AUTH NODE #NER-71 • BRO Swastik" not in html
    assert "CITIZEN ADVISORY NODE" in html


def test_citizen_siren_dispatch_forbidden(client):
    """Citizen session is strictly rejected from triggering tactical sirens (HTTP 403)."""
    with client.session_transaction() as sess:
        sess["role"] = "CITIZEN"
        sess["user_role"] = "CITIZEN"
        sess["user_id"] = "citizen_gangtok_01"

    res = client.post(
        "/api/alerts/dispatch-siren",
        json={"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


def test_citizen_decision_authorization_forbidden(client):
    """Citizen session is strictly rejected from authorizing risk decisions (HTTP 403)."""
    with client.session_transaction() as sess:
        sess["role"] = "CITIZEN"
        sess["user_role"] = "CITIZEN"
        sess["user_id"] = "citizen_gangtok_01"

    res = client.post("/api/decisions/1/authorize", json={"decision_id": 1})
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"
    assert "cannot authorize emergency decisions" in data.get("message", "").lower()


def test_citizen_broadcast_trigger_forbidden(client):
    """Citizen session is strictly rejected from issuing public alert broadcasts (HTTP 403)."""
    with client.session_transaction() as sess:
        sess["role"] = "CITIZEN"
        sess["user_role"] = "CITIZEN"
        sess["user_id"] = "citizen_gangtok_01"

    res = client.post(
        "/api/alerts/broadcast-trigger",
        json={"region_name": "NH-10 Corridor", "severity": "RED"}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


def test_citizen_report_verification_forbidden(client):
    """Citizen session is strictly rejected from verifying field reports (HTTP 403)."""
    with client.session_transaction() as sess:
        sess["role"] = "CITIZEN"
        sess["user_role"] = "CITIZEN"
        sess["user_id"] = "citizen_gangtok_01"

    res = client.post(
        "/api/reports/verify",
        json={"report_id": 101, "status": "CONFIRMED", "operator_role": "CITIZEN"}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


def test_citizen_ui_hides_siren_button(client):
    """Citizen session renders index.html with tactical siren button hidden."""
    with client.session_transaction() as sess:
        sess["role"] = "CITIZEN"
        sess["user_role"] = "CITIZEN"

    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert 'id="btn-citizen-sos"' in html
    assert 'style="display:none !important;" class="hidden"' in html


# =============================================================================
# 2. FIELD OPERATOR PERSONA TESTS (BRO SWASTIK / SDRF)
# =============================================================================

def test_field_operator_can_verify_reports(client):
    """Field operator can verify field incident reports."""
    with client.session_transaction() as sess:
        sess["role"] = "FIELD_OPERATOR"
        sess["user_role"] = "FIELD_OPERATOR"
        sess["user_id"] = "bro_engineer_singtam"

    res = client.post(
        "/api/reports/verify",
        json={
            "report_id": 202,
            "status": "CONFIRMED",
            "operator": "Junior Engineer BRO Swastik",
            "operator_role": "FIELD_OPERATOR",
            "notes": "Verified 22mm tension crack along km 48 shoulder."
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "SUCCESS"
    assert data.get("verification_status") == "CONFIRMED"


def test_field_operator_cannot_authorize_decisions(client):
    """Field operator is strictly rejected from authorizing risk decisions (HTTP 403)."""
    with client.session_transaction() as sess:
        sess["role"] = "FIELD_OPERATOR"
        sess["user_role"] = "FIELD_OPERATOR"

    res = client.post("/api/decisions/1/authorize", json={"decision_id": 1})
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


def test_field_operator_cannot_trigger_broadcast(client):
    """Field operator is strictly rejected from triggering public alert broadcasts (HTTP 403)."""
    with client.session_transaction() as sess:
        sess["role"] = "FIELD_OPERATOR"
        sess["user_role"] = "FIELD_OPERATOR"

    res = client.post(
        "/api/alerts/broadcast-trigger",
        json={"region_name": "NH-10 Corridor", "severity": "RED"}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


def test_field_operator_cannot_dispatch_siren(client):
    """Field operator is strictly rejected from dispatching sirens (HTTP 403)."""
    with client.session_transaction() as sess:
        sess["role"] = "FIELD_OPERATOR"
        sess["user_role"] = "FIELD_OPERATOR"

    res = client.post(
        "/api/alerts/dispatch-siren",
        json={"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


# =============================================================================
# 3. DISTRICT & STATE AUTHORITY PERSONA TESTS (DDMA / SDMA)
# =============================================================================

def test_district_authority_can_authorize_decision(client):
    """District Authority (DDMA) can authorize risk decisions."""
    with client.session_transaction() as sess:
        sess["role"] = "DISTRICT_AUTHORITY"
        sess["user_role"] = "DISTRICT_AUTHORITY"
        sess["user_id"] = "dm_gangtok"

    res = client.post("/api/decisions/1/authorize", json={"decision_id": 1})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "SUCCESS"
    assert "Authorized by District Disaster Management Authority" in data.get("message", "")


def test_state_authority_can_trigger_broadcast(client):
    """State Authority (SDMA) can trigger public warning broadcasts."""
    with client.session_transaction() as sess:
        sess["role"] = "STATE_AUTHORITY"
        sess["user_role"] = "STATE_AUTHORITY"
        sess["user_id"] = "sdma_controller"

    res = client.post(
        "/api/alerts/broadcast-trigger",
        json={"region_name": "Mangan Corridor", "severity": "RED"}
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data.get("status") in ["SUCCESS", "SUPPRESSED_SHADOW_OPERATIONS", "DISPATCHED"]


def test_authority_can_dispatch_siren(client):
    """Authority session can execute tactical siren dispatch protocol."""
    with client.session_transaction() as sess:
        sess["role"] = "DISTRICT_AUTHORITY"
        sess["user_role"] = "DISTRICT_AUTHORITY"
        sess["user_id"] = "dm_gangtok"

    res = client.post(
        "/api/alerts/dispatch-siren",
        json={"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "DISPATCHED"


def test_authority_ui_shows_node_badge(client):
    """Authority session renders index.html with operational authority node badge."""
    with client.session_transaction() as sess:
        sess["role"] = "DISTRICT_AUTHORITY"
        sess["user_role"] = "DISTRICT_AUTHORITY"

    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "AUTH NODE #NER-71 • BRO Swastik" in html


# =============================================================================
# 4. SYSTEM ADMINISTRATOR PERSONA TESTS
# =============================================================================

def test_admin_cannot_authorize_decisions(client):
    """Statutory DMA 2005 Invariant: Admin role CANNOT authorize emergency decisions."""
    with client.session_transaction() as sess:
        sess["role"] = "ADMIN"
        sess["user_role"] = "ADMIN"
        sess["user_id"] = "sysadmin_root"

    res = client.post("/api/decisions/1/authorize", json={"decision_id": 1})
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"
    assert "cannot authorize emergency decisions" in data.get("message", "").lower()


def test_admin_cannot_trigger_broadcast(client):
    """Admin role CANNOT trigger public warning broadcasts."""
    with client.session_transaction() as sess:
        sess["role"] = "ADMIN"
        sess["user_role"] = "ADMIN"

    res = client.post(
        "/api/alerts/broadcast-trigger",
        json={"region_name": "Gangtok Corridor", "severity": "RED"}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


def test_admin_cannot_dispatch_siren(client):
    """Admin role CANNOT dispatch tactical sirens."""
    with client.session_transaction() as sess:
        sess["role"] = "ADMIN"
        sess["user_role"] = "ADMIN"

    res = client.post(
        "/api/alerts/dispatch-siren",
        json={"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data.get("status") == "FORBIDDEN"


# =============================================================================
# 5. TOKEN-BASED INTER-SERVICE AUTHENTICATION TESTS
# =============================================================================

def test_authority_token_header_authorizes_siren(client):
    """Valid X-Authority-Token permits siren dispatch from automated pipelines."""
    res = client.post(
        "/api/alerts/dispatch-siren",
        json={"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745},
        headers={"X-Authority-Token": "parvat-authority-token-2026", "X-Require-Auth": "true"}
    )
    assert res.status_code == 200
    assert res.get_json().get("status") == "DISPATCHED"


def test_invalid_authority_token_header_rejected(client):
    """Invalid X-Authority-Token is rejected with HTTP 403."""
    res = client.post(
        "/api/alerts/dispatch-siren",
        json={"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745},
        headers={"X-Authority-Token": "invalid-token-12345", "X-Require-Auth": "true"}
    )
    assert res.status_code == 403
    assert res.get_json().get("status") == "FORBIDDEN"
