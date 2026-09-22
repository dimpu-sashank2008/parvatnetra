# -*- coding: utf-8 -*-
"""
tests/test_v5_3_ground_truth.py
===============================
Phase V5.3 Test Suite: Authoritative Ground-Truth Classification & Boundary
Verifies the distinction between AUTHORITATIVE_VERIFIED (37) and
RESEARCH_CANDIDATE (5), and tests negative control stability integrity (20 controls).
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53GroundTruth:
    """Verifies scientific ground-truth partition integrity."""

    def test_ground_truth_classification_counts(self, manager):
        status_info = manager.get_forensic_ground_truth_status()
        assert status_info["total_events_audited"] == 42
        assert status_info["authoritative_verified_count"] == 37
        assert status_info["research_candidate_count"] == 5

    def test_research_candidates_are_quarantined_from_authoritative(self, manager):
        reg = manager.get_v5_3_evidence_registry()
        events = reg.get("events", [])
        candidates = [e for e in events if e["event_status"] == "RESEARCH_CANDIDATE"]
        assert len(candidates) == 5
        cand_ids = {e["event_id"] for e in candidates}
        assert cand_ids == {"EV-07", "EV-25", "EV-29", "EV-32", "EV-35"}

    def test_negative_control_windows_verified(self, manager):
        inv = manager.get_v5_3_inventory()
        controls = inv.get("controls", [])
        assert len(controls) == 20
        for c in controls:
            assert c["stability_status"] == "VERIFIED_STABLE"
            assert c["absence_of_failure_evidence"]
            assert c["start_time"] < c["end_time"]
