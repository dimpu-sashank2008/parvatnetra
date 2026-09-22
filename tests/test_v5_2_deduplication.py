# -*- coding: utf-8 -*-
"""
tests/test_v5_2_deduplication.py
================================
Phase V5.2 Test Suite: Spatio-Temporal Deduplication & Cross-Source Merging
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52Deduplication:
    """Verifies that duplicate reports within 1km and 48h are merged rather than inflated."""

    def test_haversine_distance_calculation(self, manager):
        # Pakyong (27.24, 88.58) to Gangtok (27.33, 88.61) is approx 10.4 km
        d = manager._haversine_km(27.24, 88.58, 27.33, 88.61)
        assert 9.0 < d < 12.0

    def test_spatio_temporal_duplicate_is_merged(self, manager):
        events = manager.list_canonical_events()
        assert len(events) > 0
        target = events[0]
        initial_count = manager.get_canonical_event_count()

        # Create a duplicate event 200m away and 2 hours after target
        duplicate_record = {
            "event_id": f"DUP-{target['event_id']}",
            "timestamp": target["timestamp"],
            "latitude": target["latitude"] + 0.001,  # ~110m north
            "longitude": target["longitude"] + 0.001, # ~100m east
            "state": target["state"],
            "district": target["district"],
            "source": "State Disaster Management Authority Communique",
            "source_reference": f"SDMA-CROSSREF-{target['event_id']}",
            "verification_status": "VERIFIED_PRIMARY"
        }

        res = manager.ingest_raw_record(duplicate_record, authorizer_role="SDMA_DIRECTOR")
        assert res["success"] is True
        assert res["status"] == "MERGED_DUPLICATE"
        assert res["canonical_event_id"] == target["event_id"]
        # Canonical event count must NOT increment
        assert manager.get_canonical_event_count() == initial_count
