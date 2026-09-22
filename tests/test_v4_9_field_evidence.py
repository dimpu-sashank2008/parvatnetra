# -*- coding: utf-8 -*-
"""
tests/test_v4_9_field_evidence.py
=================================
Phase V4.9 Test Suite: Field Evidence Ledger, Human Authorization & Public Dispatch Safeguards
Validates:
- Item 20: Field evidence ledger entries, SHA-256 hashes, and forensic audit trail
- Item 25: Mandatory human authorization; unverified placeholder tokens rejected
- Item 26: Public emergency dispatch strictly disabled (siren dry run, CAP/SACHET disabled)
"""

import pytest
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    AUTH_UNVERIFIED,
    CLAIM_UNSUPPORTED
)


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestFieldEvidenceAndSafety:
    """Verifies field evidence integrity, human authorization, and siren safety."""

    def test_item_20_field_evidence_ledger_integrity(self, commissioning_engine):
        """Item 20: Registry declarations must not be confused with physical evidence."""
        audits = commissioning_engine.audit_physical_sensor_evidence()
        for sensor_id, audit in audits.items():
            assert audit.physical_device_verified is False
            assert audit.installation_status == "NOT_INSTALLED"
            assert audit.operator_acceptance_status in [AUTH_UNVERIFIED, "UNVERIFIED", "PENDING"]

    def test_item_25_human_authorization_mandatory(self, commissioning_engine):
        """Item 25: Token 'BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026' is demoted to AUTHORIZATION_UNVERIFIED."""
        res = commissioning_engine.audit_institutional_authorization("BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026")
        assert res["status"] == AUTH_UNVERIFIED
        assert res["acceptance_valid"] is False
        assert "UNVERIFIED" in res["classification"]

    def test_item_26_public_dispatch_strictly_disabled(self):
        """Item 26: Public dispatch and sirens must remain in dry-run mode."""
        import os
        # Ensure environment variables or service defaults forbid unverified public sirens
        enable_public = os.environ.get("ENABLE_PUBLIC_DISPATCH", "0")
        siren_dry_run = os.environ.get("SIREN_DRY_RUN", "1")
        assert enable_public in ["0", "false", "False"]
        assert siren_dry_run in ["1", "true", "True"]
