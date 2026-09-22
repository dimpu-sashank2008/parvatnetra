# -*- coding: utf-8 -*-
"""
tests/test_v5_2_event_schema.py
===============================
Phase V5.2 Test Suite: Canonical Event Schema Compliance & Validation
"""

import pytest
from engine.dataset_expansion_manager import (
    DatasetExpansionManager,
    CanonicalLandslideEvent,
    VALID_EVENT_TYPES,
    VALID_SEVERITIES,
    REJECTED
)


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52EventSchema:
    """Verifies that all canonical events adhere to the mandatory schema."""

    def test_canonical_events_mandatory_fields(self, manager):
        events = manager.list_canonical_events()
        assert len(events) >= 42
        mandatory_keys = [
            "event_id", "timestamp", "latitude", "longitude",
            "state", "district", "source", "source_reference",
            "verification_status", "event_type", "severity",
            "provenance", "raw_record_hash", "canonical_hash"
        ]
        for ev in events:
            for key in mandatory_keys:
                assert key in ev, f"Event {ev.get('event_id')} missing key '{key}'"
                assert ev[key] is not None, f"Event {ev.get('event_id')} key '{key}' is None"

    def test_canonical_events_geographic_bounds(self, manager):
        events = manager.list_canonical_events()
        for ev in events:
            lat = ev["latitude"]
            lon = ev["longitude"]
            assert 20.0 <= lat <= 30.5, f"Event {ev['event_id']} latitude {lat} outside NER (20-30.5)"
            assert 87.0 <= lon <= 98.0, f"Event {ev['event_id']} longitude {lon} outside NER (87-98)"

    def test_canonical_events_vocabulary(self, manager):
        events = manager.list_canonical_events()
        valid_types = {
            "DEBRIS_FLOW", "ROCK_FALL", "ROTATIONAL_SLIDE", "PLANAR_SLIP",
            "MUD_FLOW", "GLOF_TRIGGERED", "COMPLEX_MASS_MOVEMENT"
        }
        valid_severities = {"CRITICAL", "MAJOR", "MODERATE", "MINOR", "SEVERE"}
        for ev in events:
            assert ev["event_type"] in valid_types, f"Invalid event_type: {ev['event_type']}"
            assert ev["severity"] in valid_severities, f"Invalid severity: {ev['severity']}"

    def test_invalid_event_rejection_missing_fields(self, manager):
        invalid_rec = {
            "event_id": "TEST-BAD-01",
            "timestamp": "2024-05-01T12:00:00Z"
            # Missing latitude, longitude, state, district, source
        }
        res = manager.ingest_raw_record(invalid_rec, authorizer_role="GSI_LIAISON")
        assert res["success"] is False
        assert res["status"] == REJECTED

    def test_invalid_event_rejection_oob_coordinates(self, manager):
        oob_rec = {
            "event_id": "TEST-OOB-01",
            "timestamp": "2024-05-01T12:00:00Z",
            "latitude": 13.0827,  # Chennai (outside NER)
            "longitude": 80.2707,
            "state": "Tamil Nadu",
            "district": "Chennai",
            "source": "Non-NER Source",
            "source_reference": "REF-OOB"
        }
        res = manager.ingest_raw_record(oob_rec, authorizer_role="GSI_LIAISON")
        assert res["success"] is False
        assert res["status"] == REJECTED
