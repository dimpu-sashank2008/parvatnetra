# -*- coding: utf-8 -*-
"""
tests/test_v4_9_claim_audit.py
==============================
Phase V4.9 Test Suite: Government Authority Claims Audit, Model Hash Checks & V4.9 Verdict
"""

import os
import hashlib
import pytest
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    VERDICT_FIELD_COMMISSIONING_READY,
    CLAIM_UNSUPPORTED
)


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestInstitutionalClaimsAudit:
    """Audits governmental authority overclaims and evaluates Phase V4.9 final verdict."""

    def test_institutional_claims_audited_and_downgraded(self, commissioning_engine):
        res = commissioning_engine.audit_government_and_institutional_claims()
        assert res["total_claims_audited"] >= 6
        assert "Smart India Hackathon" in res["system_designation"]
        assert "research and decision-support prototype" in res["system_designation"]

        # NDMA placeholder token and NABL certs must be UNSUPPORTED
        unsupported = [c["term"] for c in res["claims"] if c["classification"] == CLAIM_UNSUPPORTED]
        assert any("NDMA" in t for t in unsupported)
        assert any("NABL" in t for t in unsupported)
        assert any("Live" in t for t in unsupported)

    def test_overall_v4_9_verdict_is_field_commissioning_ready(self, commissioning_engine):
        v = commissioning_engine.evaluate_v4_9_overall_verdict()
        assert v["overall_verdict"] == VERDICT_FIELD_COMMISSIONING_READY
        assert v["field_presence_status"] == "NOT_INSTALLED"
        assert v["telemetry_status"] == "PHYSICAL_TELEMETRY_PENDING"
        assert v["verified_live_observations"] == 0
        assert v["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"

    def test_production_v3_hash_unchanged(self):
        v3_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v3_weights.pt")
        with open(v3_path, "rb") as f:
            v3_hash = hashlib.sha256(f.read()).hexdigest()
        assert v3_hash == "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

    def test_research_v4_5_hash_unchanged(self):
        v4_5_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v4_5_research_weights.pt")
        with open(v4_5_path, "rb") as f:
            v4_5_hash = hashlib.sha256(f.read()).hexdigest()
        assert v4_5_hash == "31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f"

    def test_field_commissioning_api_endpoint(self):
        import app
        client = app.app.test_client()
        res = client.get("/api/telemetry/field-commissioning")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert "verdict" in data["data"]
        assert data["data"]["verdict"]["overall_verdict"] == VERDICT_FIELD_COMMISSIONING_READY
