# -*- coding: utf-8 -*-
"""
tests/test_phase7_dataset_expansion.py
======================================
Tests for Phase 7D Dataset Expansion Framework and Lineage Tracking.
"""

import os
import pytest
from engine.dataset_expansion_manager import (
    DatasetExpansionManager,
    CanonicalLandslideEvent,
    VALID_VERIFICATION_STATUSES,
    VALID_EVENT_TYPES,
    VALID_SEVERITIES
)

@pytest.fixture
def manager(tmp_path):
    storage_file = str(tmp_path / "test_canonical_lineage.json")
    mgr = DatasetExpansionManager(storage_path=storage_file)
    return mgr

def test_baseline_loads_canonical_events(manager):
    """Verifies pre-existing canonical events are loaded into lineage registry."""
    count = manager.get_event_count()
    assert count >= 17, f"Expected at least 17 baseline canonical events, got {count}"
    # Verify one canonical event
    ev = manager.get_event("EV-SK-2023-10-04-01")
    if ev:
        assert ev.state in {"Sikkim", "NER"}
        assert ev.provenance == "[HISTORICAL]"

def test_unauthorized_role_rejected(manager):
    """Verifies that an unauthorized role cannot admit records."""
    candidate = {
        "event_id": "TEST-EV-001",
        "timestamp": "2024-05-15T12:00:00Z",
        "latitude": 27.35,
        "longitude": 88.62,
        "state": "Sikkim",
        "district": "Gangtok",
        "source": "GSI Report 2024",
        "source_url_reference": "https://gsi.gov.in/rep/2024-sk-01",
        "verification_status": "OFFICIAL_GOVERNMENT_REPORT",
        "event_type": "DEBRIS_FLOW",
        "severity": "MAJOR"
    }
    res = manager.validate_and_ingest(
        event_dict=candidate,
        authorizer_role="CITIZEN_REPORTER",
        authority_token="valid_token_12345"
    )
    assert res["success"] is False
    assert "Unauthorized role" in res["error"]

def test_missing_authority_token_rejected(manager):
    """Verifies that empty/short authority token is rejected."""
    candidate = {
        "event_id": "TEST-EV-002",
        "timestamp": "2024-05-15T12:00:00Z",
        "latitude": 27.35,
        "longitude": 88.62,
        "state": "Sikkim",
        "district": "Gangtok",
        "source": "GSI Report 2024",
        "source_url_reference": "https://gsi.gov.in/rep/2024-sk-01",
        "verification_status": "OFFICIAL_GOVERNMENT_REPORT",
        "event_type": "DEBRIS_FLOW",
        "severity": "MAJOR"
    }
    res = manager.validate_and_ingest(
        event_dict=candidate,
        authorizer_role="GSI_LIAISON",
        authority_token=""
    )
    assert res["success"] is False
    assert "authority token" in res["error"].lower()

def test_outside_ner_bounding_box_rejected(manager):
    """Verifies events outside NER region are rejected."""
    candidate = {
        "event_id": "TEST-EV-DELHI",
        "timestamp": "2024-05-15T12:00:00Z",
        "latitude": 28.6139,
        "longitude": 77.2090,  # New Delhi - outside NER
        "state": "Delhi",
        "district": "New Delhi",
        "source": "GSI Report",
        "source_url_reference": "https://gsi.gov.in/rep/delhi",
        "verification_status": "OFFICIAL_GOVERNMENT_REPORT",
        "event_type": "ROCK_FALL",
        "severity": "MINOR"
    }
    res = manager.validate_and_ingest(
        event_dict=candidate,
        authorizer_role="SDMA_DIRECTOR",
        authority_token="sdma_director_auth_token_secure"
    )
    assert res["success"] is False
    assert "NER bounding box" in res["error"]

def test_spatio_temporal_collision_rejected(manager):
    """Verifies duplicate event within 1km and 48 hours is rejected."""
    # Find an existing event's coords and timestamp
    existing_events = manager.list_events()
    assert len(existing_events) > 0
    ref_event = existing_events[0]

    duplicate = {
        "event_id": "TEST-DUP-001",
        "timestamp": ref_event.timestamp,
        "latitude": ref_event.latitude + 0.001,  # ~110 meters away
        "longitude": ref_event.longitude + 0.001,
        "state": ref_event.state,
        "district": ref_event.district,
        "source": "GSI Report",
        "source_url_reference": "https://gsi.gov.in/rep/collision",
        "verification_status": "COMMISSIONED_INSTITUTIONAL_RECORD",
        "event_type": "DEBRIS_FLOW",
        "severity": "CRITICAL"
    }
    res = manager.validate_and_ingest(
        event_dict=duplicate,
        authorizer_role="GSI_LIAISON",
        authority_token="gsi_liaison_token_9999"
    )
    assert res["success"] is False
    assert "collision" in res["error"].lower()

def test_valid_expansion_event_admitted_without_fabrication(manager):
    """Verifies a genuinely distinct event with verified citation is successfully admitted."""
    initial_count = manager.get_event_count()
    new_event = {
        "event_id": "GSI-SK-2025-06-15-KM72",
        "timestamp": "2025-06-15T09:30:00Z",
        "latitude": 27.65,
        "longitude": 88.45,
        "state": "Sikkim",
        "district": "Mangan",
        "source": "GSI Sikkim Field Unit Post-Disaster Bulletin 2025/12",
        "source_url_reference": "https://gsi.gov.in/bulletins/2025/mangan_km72.pdf",
        "verification_status": "VERIFIED_FIELD",
        "event_type": "ROCK_FALL",
        "severity": "MAJOR"
    }
    res = manager.validate_and_ingest(
        event_dict=new_event,
        authorizer_role="GSI_LIAISON",
        authority_token="gsi_liaison_token_9999"
    )
    assert res["success"] is True
    assert manager.get_event_count() == initial_count + 1

    stored = manager.get_event("GSI-SK-2025-06-15-KM72")
    assert stored is not None
    assert stored.provenance == "[HISTORICAL]"
    # Ensure missing contextual features remain None, not fabricated
    assert stored.rainfall_context is None
    assert stored.deformation_context is None
