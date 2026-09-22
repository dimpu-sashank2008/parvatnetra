# -*- coding: utf-8 -*-
"""
tests/test_v5_1_localhost_boundary.py
=====================================
Phase V5.1 Test Suite: Localhost Isolation & Public Safety Boundary
Verifies strict localhost enforcement, zero public exposure, dry run siren,
and disabled autonomous public dispatch.
"""

import os
import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestV51LocalhostBoundary:
    """Verifies that the application enforces localhost isolation and public alert safety."""

    def test_localhost_only_invariants(self):
        # Must never expose public host or ports
        disallowed_hosts = ["0.0.0.0", "vercel.app", "render.com", "railway.app"]
        host = os.environ.get("HOST", "127.0.0.1")
        assert host in ["127.0.0.1", "localhost"], f"Host violation: {host}"
        assert host not in disallowed_hosts

    def test_public_dispatch_disabled(self, truth_engine):
        ledger = truth_engine.get_ledger()
        auth_state = ledger.get("institutional_authorization_state", {})
        safety = auth_state.get("public_alert_safety", {})
        assert safety.get("public_dispatch_authorized") is False
        assert safety.get("human_approval_mandatory") is True

    def test_siren_relay_is_dry_run(self, truth_engine):
        ledger = truth_engine.get_ledger()
        auth_state = ledger.get("institutional_authorization_state", {})
        safety = auth_state.get("public_alert_safety", {})
        assert safety.get("siren_relay_hardware") == "DRY_RUN_EMULATOR"
