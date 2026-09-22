# -*- coding: utf-8 -*-
"""
tests/test_v5_3_deduplication.py
================================
Phase V5.3 Test Suite: Spatio-Temporal Deduplication & Progression Verification
Verifies that all 42 events maintain valid spatio-temporal separation,
and that genuine secondary communiques are merged into parent lineage.
"""

import os
import json
import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53Deduplication:
    """Verifies that no unintentional duplicate disaster events exist."""

    def test_pairwise_spatio_temporal_separation(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                e1 = events[i]
                e2 = events[j]
                d = manager._haversine_km(e1["latitude"], e1["longitude"], e2["latitude"], e2["longitude"])
                dt1 = manager._parse_iso(e1["timestamp"])
                dt2 = manager._parse_iso(e2["timestamp"])
                hrs = abs((dt1 - dt2).total_seconds()) / 3600.0

                # If within 1.0 km, time difference must be >= 48 hours to be distinct events
                if d < 1.0:
                    assert hrs >= 48.0, (
                        f"Unmerged duplicate collision detected between {e1['event_id']} and {e2['event_id']}: "
                        f"Distance={d:.2f}km, TimeDiff={hrs:.1f}h"
                    )

    def test_duplicate_merge_into_lineage(self, manager):
        ev01 = manager.get_event("EV-01")
        dup_candidate = {
            "event_id": "TEST-MERGE-DUP-EV01",
            "timestamp": ev01.timestamp,
            "latitude": ev01.latitude + 0.001,
            "longitude": ev01.longitude + 0.001,
            "state": ev01.state,
            "district": ev01.district,
            "source": "State Disaster Management Authority Incident Log",
            "source_reference": "SDMA-TEST-DUP-01",
            "verification_status": "VERIFIED_PRIMARY"
        }
        res = manager.ingest_raw_record(dup_candidate, authorizer_role="SDMA_DIRECTOR")
        assert res["success"] is True
        assert res["is_duplicate"] is True
        assert res["canonical_event_id"] == "EV-01"
