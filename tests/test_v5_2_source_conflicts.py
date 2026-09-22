# -*- coding: utf-8 -*-
"""
tests/test_v5_2_source_conflicts.py
===================================
Phase V5.2 Test Suite: Inter-Source Conflict Matrix & Arbitration Logic
"""

import pytest
from engine.external_data_engine import ExternalDataEngine


@pytest.fixture
def engine():
    return ExternalDataEngine.get_instance()


class TestV52SourceConflicts:
    """Verifies that inter-source discrepancies (SCON-01 to SCON-04) are systematically documented."""

    EXPECTED_CONFLICT_IDS = {"SCON-01", "SCON-02", "SCON-03", "SCON-04"}

    def test_all_four_conflicts_present(self, engine):
        conflicts = engine.get_source_conflicts()
        ids = {c["conflict_id"] for c in conflicts}
        assert ids == self.EXPECTED_CONFLICT_IDS, f"Expected {self.EXPECTED_CONFLICT_IDS}, got {ids}"

    def test_conflict_structure_and_resolution(self, engine):
        conflicts = engine.get_source_conflicts()
        for c in conflicts:
            assert c["conflict_id"] in self.EXPECTED_CONFLICT_IDS
            assert c["source_a"]
            assert c["source_b"]
            assert c["difference_summary"]
            assert c["resolution_method"]
            assert c["confidence"] >= 0.90
            assert "human_review_needed" in c
            assert c["status"] == "RESOLVED"

    def test_scon01_tupul_coordinates_resolution(self, engine):
        conflicts = engine.get_source_conflicts()
        scon01 = next(c for c in conflicts if c["conflict_id"] == "SCON-01")
        assert "Tupul" in scon01["dimension"]
        assert scon01["resolved_value"]["lat"] == 24.7865
        assert scon01["resolved_value"]["lon"] == 93.6394
        assert "GSI" in scon01["resolution_method"]
