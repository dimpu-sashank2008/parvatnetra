# -*- coding: utf-8 -*-
"""
tests/test_v5_1_claim_consistency.py
====================================
Phase V5.1 Test Suite: Claim Consistency & Governance
Verifies the four-tier Claim Freeze governance and 9-point Conflict Matrix.
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestV51ClaimConsistency:
    """Verifies four-tier claim categorization and resolution of cross-phase conflicts."""

    def test_claim_freeze_categories_exist(self, truth_engine):
        claim_ledger = truth_engine.get_claim_ledger()
        assert "supported_claims" in claim_ledger
        assert "partially_supported_claims" in claim_ledger
        assert "unsupported_claims" in claim_ledger
        assert "forbidden_claims" in claim_ledger

    def test_unsupported_claims_audited(self, truth_engine):
        claim_ledger = truth_engine.get_claim_ledger()
        unsupported = claim_ledger.get("unsupported_claims", [])
        joined = " ".join(unsupported)
        assert "52 real historical events" in joined
        assert "41 training, 11 validation, 11 test" in joined
        assert "ROC-AUC 0.81" in joined
        assert "4.2 hours median warning lead time" in joined

    def test_forbidden_claims_enforce_engineering_integrity(self, truth_engine):
        claim_ledger = truth_engine.get_claim_ledger()
        forbidden = claim_ledger.get("forbidden_claims", [])
        joined = " ".join(forbidden)
        assert "sensors are installed in the field before drilling" in joined
        assert "live mountain field telemetry is streaming" in joined
        assert "Kinematic In-Situ ML is trained" in joined

    def test_conflict_matrix_fully_resolved(self, truth_engine):
        conflicts = truth_engine.get_conflict_matrix()
        assert len(conflicts) == 9
        for c in conflicts:
            assert c.get("status") == "RESOLVED"
            assert "RESOLVED" in c.get("resolution", "")
            assert c.get("authoritative_artifact") is not None
