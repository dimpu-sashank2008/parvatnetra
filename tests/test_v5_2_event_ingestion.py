# -*- coding: utf-8 -*-
"""
tests/test_v5_2_event_ingestion.py
==================================
Phase V5.2 Test Suite: Historical Event Ingestion Pipeline & Boundary Validation
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager, REJECTED


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52EventIngestion:
    """Verifies that events pass through strict schema and spatial boundary filters."""

    def test_canonical_event_count_is_forty_two(self, manager):
        count = manager.get_canonical_event_count()
        assert count == 42, f"Expected exactly 42 canonical verified events (17 baseline + 25 expansion), got {count}"

    def test_missing_mandatory_fields_rejected(self, manager):
        incomplete_record = {
            "event_id": "TEST-INCOMPLETE-01",
            "timestamp": "2024-06-01T00:00:00Z",
            # Missing latitude, longitude, state, district, source
        }
        res = manager.ingest_raw_record(incomplete_record, authorizer_role="GSI_LIAISON")
        assert res["success"] is False
        assert res["status"] == REJECTED
        assert "Missing mandatory" in res["error"]

    def test_outside_ner_bounding_box_rejected(self, manager):
        out_of_bounds = {
            "event_id": "TEST-MUMBAI-01",
            "timestamp": "2024-07-15T12:00:00Z",
            "latitude": 19.0760,  # Mumbai - outside NER latitude range [20.0, 30.5]
            "longitude": 72.8777, # Mumbai - outside NER longitude range [87.0, 98.0]
            "state": "Maharashtra",
            "district": "Mumbai City",
            "source": "State Geological Bulletin",
            "source_reference": "BUL-MH-2024-01"
        }
        res = manager.ingest_raw_record(out_of_bounds, authorizer_role="SDMA_DIRECTOR")
        assert res["success"] is False
        assert res["status"] == REJECTED
        assert "outside NER bounding box" in res["error"]

    def test_unauthorized_authorizer_rejected(self, manager):
        valid_event = {
            "event_id": "TEST-UNAUTH-01",
            "timestamp": "2024-08-01T10:00:00Z",
            "latitude": 27.33,
            "longitude": 88.61,
            "state": "Sikkim",
            "district": "Gangtok",
            "source": "GSI Field Inspection",
            "source_reference": "GSI-SK-2024-999"
        }
        res = manager.ingest_raw_record(valid_event, authorizer_role="ANONYMOUS_ACTOR")
        assert res["success"] is False
        assert "Unauthorized ingestion role" in res["error"]
