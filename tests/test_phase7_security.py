# -*- coding: utf-8 -*-
"""
tests/test_phase7_security.py
=============================
Tests for Phase 7I Security, RBAC & Penetration Audit.
Verifies zero hardcoded secrets, SQL injection resistance, and safety interlocks.
"""

import os
import pytest
from scripts.security_audit import (
    audit_secret_leakage,
    audit_sql_parameterization,
    audit_safety_interlocks,
    run_comprehensive_security_audit
)
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_security_audit_verdict_compliant():
    rep = run_comprehensive_security_audit()
    assert rep["overall_security_verdict"] == "COMPLIANT"
    assert rep["checks"]["secret_leakage"]["status"] == "PASSED"
    assert rep["checks"]["sql_injection_resistance"]["status"] == "PASSED"
    assert rep["checks"]["safety_interlocks"]["status"] == "PASSED"

def test_zero_hardcoded_secrets():
    res = audit_secret_leakage()
    assert res["status"] == "PASSED"
    assert res["findings_count"] == 0, f"Found hardcoded secrets: {res['findings']}"

def test_sql_parameterization_clean():
    res = audit_sql_parameterization()
    assert res["status"] == "PASSED"
    assert res["unsafe_queries_found"] == 0

def test_safety_interlocks_active():
    res = audit_safety_interlocks()
    assert res["siren_dry_run_active"] is True
    assert res["public_dispatch_enabled"] is False

def test_path_traversal_blocked(client):
    """Verifies that path traversal payloads are rejected by web server."""
    # Attempt directory traversal on static file route
    res = client.get("/static/../../../etc/passwd")
    assert res.status_code in {400, 404}

    res2 = client.get("/static/..\\..\\..\\windows\\win.ini")
    assert res2.status_code in {400, 404}
