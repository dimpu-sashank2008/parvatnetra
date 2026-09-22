# -*- coding: utf-8 -*-
"""
tests/test_v5_2_security.py
===========================
Phase V5.2 Test Suite: Localhost Isolation, Credential Protection & Public Dispatch Safety
Verifies:
1. Zero API key / secret token exposure in /api/gods-eye/config and /api/data/* endpoints.
2. Absolute Localhost-Only boundary enforcement (no public dispatch, no external host).
3. Public dispatch remains locked and requires human authorization.
"""

import os
import re
import json
import pytest
from app import app
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestV52Security:
    """Security audit for Phase V5.2 endpoints, localhost boundary, and safety locks."""

    SUSPICIOUS_PATTERNS = [
        re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}"),
        re.compile(r"(?i)(?:api_key|token|secret|password)\s*[:=]\s*['\"][a-zA-Z0-9_\-\.]{16,}['\"]"),
        re.compile(r"(?i)AIzaSy[a-zA-Z0-9_-]{33}"),  # Google API key format
        re.compile(r"(?i)ghp_[a-zA-Z0-9]{36}"),
        re.compile(r"(?i)eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}")  # JWT pattern
    ]

    def test_gods_eye_config_does_not_expose_raw_keys(self, client):
        """Ensure /api/gods-eye/config exposes only booleans for keys, never raw tokens."""
        res = client.get("/api/gods-eye/config")
        assert res.status_code == 200
        data = res.get_json()
        assert "google_maps_api_key_configured" in data
        assert isinstance(data["google_maps_api_key_configured"], bool)
        assert "cesium_ion_token_configured" in data
        assert isinstance(data["cesium_ion_token_configured"], bool)

        # Verify text payload does not contain raw API keys
        raw_text = res.get_data(as_text=True)
        for pattern in self.SUSPICIOUS_PATTERNS:
            matches = pattern.findall(raw_text)
            assert len(matches) == 0, f"Potential credential leak in /api/gods-eye/config: {matches}"

    def test_data_expansion_endpoints_zero_credentials(self, client):
        """Ensure all /api/data/* endpoints contain zero leaked keys or bearer tokens."""
        endpoints = [
            "/api/data/events",
            "/api/data/events/EVT-2023-10-04-001",
            "/api/data/events/status",
            "/api/data/events/provenance",
            "/api/data/events/statistics",
            "/api/data/ground-truth/status"
        ]
        for ep in endpoints:
            res = client.get(ep)
            assert res.status_code in [200, 404]
            raw_text = res.get_data(as_text=True)
            for pattern in self.SUSPICIOUS_PATTERNS:
                matches = pattern.findall(raw_text)
                assert len(matches) == 0, f"Potential secret leak in {ep}: {matches}"

    def test_localhost_only_boundary_flags(self):
        """Assert environment and engine prohibit public exposure and external binding."""
        host = os.environ.get("HOST", "127.0.0.1")
        assert host in ["127.0.0.1", "localhost"], f"Non-localhost host binding detected: {host}"

        public_deploy = os.environ.get("PUBLIC_DEPLOYMENT", "0").lower() in ["1", "true"]
        assert not public_deploy, "PUBLIC_DEPLOYMENT flag must be disabled."

        public_expose = os.environ.get("PUBLIC_EXPOSURE", "0").lower() in ["1", "true"]
        assert not public_expose, "PUBLIC_EXPOSURE flag must be disabled."

    def test_public_dispatch_safety_locks(self):
        """Verify public alert dispatch is locked and requires human sign-off."""
        engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
        verdict = engine.evaluate_v5_2_verdict()
        assert verdict["public_dispatch_enabled"] is False, "Public dispatch must be FALSE"
        assert verdict["human_authorization_required"] is True, "Human authorization lock missing"
        assert verdict["siren_relay_hardware"] == "DRY_RUN_EMULATOR"
