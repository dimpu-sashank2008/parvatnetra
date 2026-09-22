# -*- coding: utf-8 -*-
"""
tests/test_v5_2_event_lineage.py
================================
Phase V5.2 Test Suite: Event Cryptographic Lineage & Hashing
"""

import os
import json
import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager, compute_sha256_string


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52EventLineage:
    """Verifies that all canonical events maintain cryptographic provenance and lineage."""

    def test_canonical_events_have_hashes(self, manager):
        events = manager.list_canonical_events()
        assert len(events) == 42
        for ev in events:
            assert ev.get("raw_record_hash"), f"Event {ev.get('event_id')} missing raw_record_hash"
            assert ev.get("canonical_hash"), f"Event {ev.get('event_id')} missing canonical_hash"
            assert len(ev["raw_record_hash"]) == 64
            assert len(ev["canonical_hash"]) == 64
            assert ev.get("provenance") == "[HISTORICAL]"

    def test_lineage_file_persisted_and_valid(self, manager):
        lineage_path = manager.storage_path
        assert os.path.exists(lineage_path), f"Lineage file {lineage_path} not found"
        with open(lineage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("schema_version") == "5.2.0"
        assert data.get("canonical_events_count") == 42
        assert len(data.get("events", [])) >= 42

    def test_hash_reproducibility(self):
        s = "EV-TEST|2024-01-01T00:00:00Z|27.33|88.61|GSI|GSI-REP-01"
        h1 = compute_sha256_string(s)
        h2 = compute_sha256_string(s)
        assert h1 == h2
        assert len(h1) == 64
