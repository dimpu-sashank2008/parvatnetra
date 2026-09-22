# -*- coding: utf-8 -*-
"""
tests/test_v5_3_event_identity.py
=================================
Phase V5.3 Test Suite: Event Identity & Baseline-Expansion Separation
Verifies that all 42 events possess distinct identities, unique event IDs,
proper geographic identifiers, and zero uncontrolled collisions.
"""

import os
import json
import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53EventIdentity:
    """Verifies distinct event identities and absence of duplicate IDs."""

    def test_all_event_ids_unique(self, manager):
        events = manager.list_canonical_events()
        event_ids = [e["event_id"] for e in events]
        assert len(event_ids) == len(set(event_ids)), "Duplicate event_id detected in canonical events"

    def test_baseline_and_expansion_events_separated(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        assert len(events) == 42
        baseline_eids = {f"EV-{i:02d}" for i in range(1, 18)}
        expansion_eids = {f"EV-{i:02d}" for i in range(18, 43)}

        found_baseline = {e["event_id"] for e in events if e["event_id"] in baseline_eids}
        found_expansion = {e["event_id"] for e in events if e["event_id"] in expansion_eids}

        assert len(found_baseline) == 17
        assert len(found_expansion) == 25
        assert found_baseline.isdisjoint(found_expansion)

    def test_event_descriptions_informative(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        for e in events:
            desc = e.get("description", "")
            geomorphic_terms = [
                "landslide", "hillslope", "rockfall", "slump", "slide", "slope", 
                "breach", "washout", "collapse", "flow", "debris", "failure", 
                "shear", "avalanche", "slippage", "detachment", "sinking", "bluff", "rock", "mud", "slip"
            ]
            assert any(k in desc.lower() for k in geomorphic_terms) or e["district"] in desc or e["state"] in desc
