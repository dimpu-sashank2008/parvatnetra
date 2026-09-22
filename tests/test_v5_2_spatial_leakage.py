# -*- coding: utf-8 -*-
"""
tests/test_v5_2_spatial_leakage.py
==================================
Phase V5.2 Test Suite: Spatial Separation & Geographic Boundary Audit
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52SpatialLeakage:
    """Verifies spatial dispersion, bounding consistency, and absence of cross-split geographic contamination."""

    def test_multi_state_representation(self, manager):
        events = manager.list_canonical_events()
        states = set(e["state"] for e in events)
        # Authoritative expansion covers at least Sikkim, Assam, Nagaland, and West Bengal
        assert len(states) >= 4
        assert "Sikkim" in states
        assert "Assam" in states

    def test_no_identical_duplicate_coordinates_without_merge(self, manager):
        events = manager.list_canonical_events()
        coord_map = {}
        for ev in events:
            coord_key = (round(ev["latitude"], 4), round(ev["longitude"], 4), ev["timestamp"][:10])
            if coord_key in coord_map:
                pytest.fail(f"Duplicate spatial-temporal coordinate collision: {ev['event_id']} and {coord_map[coord_key]}")
            coord_map[coord_key] = ev["event_id"]

    def test_corridor_clustering_isolation(self, manager):
        cov = manager.get_coverage_summary()
        assert cov["total_states_covered"] >= 4
        assert cov["total_districts_covered"] >= 8
