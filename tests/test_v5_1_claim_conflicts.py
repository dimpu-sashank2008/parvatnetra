# -*- coding: utf-8 -*-
"""
tests/test_v5_1_claim_conflicts.py
==================================
Phase V5.1 Test Suite: Claim Conflict Matrix & Historical Claim Reconciliation
"""

import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestClaimConflictMatrix:
    """Verifies that all 9 major cross-phase discrepancies are identified and resolved."""

    def test_all_nine_conflicts_present(self, truth_engine):
        conflicts = truth_engine.get_conflict_matrix()
        assert len(conflicts) == 9
        for c in conflicts:
            assert c["status"] == "RESOLVED"
            assert "RESOLVED" in c["resolution"]

    def test_resolution_of_17_vs_52_events(self, truth_engine):
        conflicts = truth_engine.get_conflict_matrix()
        c1 = next((c for c in conflicts if c["conflict_id"] == "CONF-01"), None)
        assert c1 is not None
        assert "17" in c1["resolution"]
        assert "UNSUPPORTED" in c1["resolution"]

    def test_resolution_of_4_2h_vs_14_5h_lead_time(self, truth_engine):
        conflicts = truth_engine.get_conflict_matrix()
        c4 = next((c for c in conflicts if c["conflict_id"] == "CONF-04"), None)
        assert c4 is not None
        assert "14.5" in c4["resolution"]
        assert "UNSUPPORTED" in c4["resolution"]

    def test_resolution_of_cri_feature_leakage(self, truth_engine):
        conflicts = truth_engine.get_conflict_matrix()
        c7 = next((c for c in conflicts if c["conflict_id"] == "CONF-07"), None)
        assert c7 is not None
        assert "Feature 33" in c7["earlier_claim"]
        assert "strictly excludes CRI" in c7["resolution"]
