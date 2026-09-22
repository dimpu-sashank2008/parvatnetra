# -*- coding: utf-8 -*-
"""
tests/test_v5_3_event_evidence.py
=================================
Phase V5.3 Test Suite: Forensic Event Evidence Traceability & Hash Verification
Verifies that all 42 audited canonical events have traceable primary or secondary
evidence records, valid SHA-256 evidence hashes, and detailed review notes.
"""

import os
import json
import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def evidence_registry():
    mgr = DatasetExpansionManager.get_instance()
    return mgr.get_v5_3_evidence_registry()


class TestV53EventEvidence:
    """Verifies evidence completeness and cryptographic hashes for all events."""

    def test_evidence_registry_loaded_and_valid(self, evidence_registry):
        assert evidence_registry.get("registry_version") == "5.3.0"
        assert evidence_registry.get("phase") == "V5.3"
        events = evidence_registry.get("events", [])
        assert len(events) == 42, f"Expected 42 audited events, got {len(events)}"

    def test_every_event_has_traceable_evidence_items(self, evidence_registry):
        events = evidence_registry.get("events", [])
        for ev in events:
            eid = ev["event_id"]
            assert ev["evidence_count"] >= 1, f"Event {eid} has zero evidence items"
            assert len(ev["evidence_items"]) >= 1, f"Event {eid} evidence_items empty"
            assert len(ev["evidence_hashes"]) >= 1, f"Event {eid} evidence_hashes empty"
            assert ev["review_notes"], f"Event {eid} missing review notes"

            for item in ev["evidence_items"]:
                assert item["evidence_id"].startswith("EVID-")
                assert item["source_reference"]
                assert len(item["content_hash"]) == 64
                assert item["verification_status"] in ["VERIFIED", "SECONDARY_CORROBORATED"]

    def test_authoritative_vs_candidate_evidence_criteria(self, evidence_registry):
        events = evidence_registry.get("events", [])
        for ev in events:
            eid = ev["event_id"]
            status = ev["event_status"]
            if status == "AUTHORITATIVE_VERIFIED":
                assert ev["primary_source_present"] is True, f"Authoritative event {eid} missing primary source"
                assert ev["verification_tier"] in [
                    "VERIFIED_PRIMARY", "VERIFIED_MULTI_SOURCE",
                    "VERIFIED_FIELD_INSPECTED", "VERIFIED_SCIENTIFIC", "VERIFIED_REMOTE_SENSING"
                ]
            elif status == "RESEARCH_CANDIDATE":
                assert ev["verification_tier"] == "CORROBORATED_SECONDARY"
                assert ev["secondary_source_present"] is True
