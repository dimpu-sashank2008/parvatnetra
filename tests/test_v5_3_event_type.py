# -*- coding: utf-8 -*-
"""
tests/test_v5_3_event_type.py
=============================
Phase V5.3 Test Suite: Geomorphic Kinematic Event Type Classification
Verifies that all 42 events comply with the standardized kinematic landslide taxonomy.
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager, VALID_EVENT_TYPES


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53EventType:
    """Verifies that events use strictly controlled kinematic taxonomy."""

    def test_all_event_types_in_controlled_vocabulary(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        for e in events:
            et = e.get("event_type")
            assert et in VALID_EVENT_TYPES, f"Invalid event_type in {e['event_id']}: {et}"

    def test_kinematic_type_distribution(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        types_found = {e["event_type"] for e in events}
        # Multi-modal distribution expected across diverse slope mechanics
        assert len(types_found) >= 4
        assert "DEBRIS_FLOW" in types_found
        assert "ROCK_FALL" in types_found
        assert "ROTATIONAL_SLIDE" in types_found
