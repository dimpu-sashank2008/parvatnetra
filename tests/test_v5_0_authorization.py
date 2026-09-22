# -*- coding: utf-8 -*-
"""
tests/test_v5_0_authorization.py
================================
Phase V5.0 Test Suite: Institutional Authority Credentials & Public Warning Safety
"""

import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    AUTH_MISSING
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestInstitutionalAuthorization:
    """Verifies authority credentials and alert dispatch safety."""

    def test_authority_status_is_missing(self, deployment_engine):
        claims = deployment_engine.audit_authority_and_claims()
        assert claims["authorization_status"] == AUTH_MISSING

    def test_placeholder_token_demoted(self, deployment_engine):
        claims = deployment_engine.audit_authority_and_claims()
        ndma_claim = next((c for c in claims["claims"] if "NDMA" in c["term"]), None)
        assert ndma_claim is not None
        assert ndma_claim["classification"] == "UNSUPPORTED"
        assert "AUTHORIZATION_UNVERIFIED" in ndma_claim["remedy"]

    def test_public_dispatch_locked(self, deployment_engine):
        claims = deployment_engine.audit_authority_and_claims()
        ssdma_claim = next((c for c in claims["claims"] if "SSDMA" in c["term"]), None)
        assert ssdma_claim is not None
        assert "public_dispatch=False" in ssdma_claim["remedy"]
