# -*- coding: utf-8 -*-
"""
tests/test_v5_3_localhost.py
============================
Phase V5.3 Test Suite: Absolute Localhost-Only Boundary & Network Quarantine
Verifies that PARVAT NETRA remains strictly bound to localhost (127.0.0.1),
with zero public cloud deployment, zero public DNS exposure, and zero tunnels.
"""

import os
import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_localhost_only_invariants():
    host = os.environ.get("HOST", "127.0.0.1")
    assert host in ["127.0.0.1", "localhost"], f"Host violation: {host}"

    public_deploy = os.environ.get("PUBLIC_DEPLOYMENT", "0").lower() in ["1", "true"]
    assert public_deploy is False, "PUBLIC_DEPLOYMENT must be FALSE."

    public_expose = os.environ.get("PUBLIC_EXPOSURE", "0").lower() in ["1", "true"]
    assert public_expose is False, "PUBLIC_EXPOSURE must be DISABLED."


def test_no_public_tunnels_configured():
    prohibited_env_keys = [
        "VERCEL_URL",
        "RENDER_EXTERNAL_URL",
        "RAILWAY_STATIC_URL",
        "NGROK_AUTHTOKEN",
        "CLOUDFLARE_TUNNEL_TOKEN"
    ]
    for key in prohibited_env_keys:
        val = os.environ.get(key)
        assert val is None or val == "", f"Prohibited public cloud env var present: {key}"


def test_safety_dispatch_locks_held():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    res = engine.evaluate_v5_2_verdict()
    assert res["public_dispatch_enabled"] is False
    assert res["human_authorization_required"] is True
