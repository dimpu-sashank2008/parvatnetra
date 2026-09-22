# -*- coding: utf-8 -*-
"""
tests/test_v5_2_event_deduplication.py
======================================
Phase V5.2 Test Suite: Deterministic Event Deduplication & Merge Lineage
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager, VERIFIED_PRIMARY


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52EventDeduplication:
    """Verifies deterministic spatio-temporal deduplication and merge lineage."""

    def test_spatio_temporal_duplicate_detection(self, manager):
        initial_count = manager.get_canonical_event_count()

        # Near EV-01 (within 0.2 km and exact same time)
        dup_record = {
            "event_id": "TEST-DUP-OF-EV01",
            "timestamp": "2024-01-01T00:00:00Z",
            "latitude": 27.3305,
            "longitude": 88.6105,
            "state": "Sikkim",
            "district": "Pakyong",
            "source": "State Disaster Management Authority Communique",
            "source_reference": "SDMA-CROSSREF-EV-01",
            "verification_status": VERIFIED_PRIMARY
        }

        res = manager.ingest_raw_record(dup_record, authorizer_role="GSI_LIAISON")
        assert res["success"] is True
        assert res["is_duplicate"] is True
        assert res["canonical_event_id"] == "EV-01"
        # Canonical event count must NOT increase
        assert manager.get_canonical_event_count() == initial_count

        # EV-01 merged_sources must include the duplicate record
        ev01 = manager.get_event("EV-01")
        assert len(ev01.merged_sources) >= 1
        last_merge = ev01.merged_sources[-1]
        assert last_merge["duplicate_reference"] == "SDMA-CROSSREF-EV-01"
        assert last_merge["distance_km"] < 1.0

    def test_distant_event_is_not_flagged_as_duplicate(self, manager):
        # Different location (> 10 km)
        distant_record = {
            "event_id": "TEST-DISTANT-01",
            "timestamp": "2024-01-01T00:00:00Z",
            "latitude": 27.4500,
            "longitude": 88.7500,
            "state": "Sikkim",
            "district": "Pakyong",
            "source": "BRO Road Inspection",
            "source_reference": "BRO-TEST-01",
            "verification_status": VERIFIED_PRIMARY
        }
        try:
            res = manager.ingest_raw_record(distant_record, authorizer_role="GSI_LIAISON")
            assert res["success"] is True
            assert res["is_duplicate"] is False
        finally:
            with manager._lock:
                if "TEST-DISTANT-01" in manager._events:
                    del manager._events["TEST-DISTANT-01"]
                manager._persist_lineage()
