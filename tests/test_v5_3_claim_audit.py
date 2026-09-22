# -*- coding: utf-8 -*-
"""
tests/test_v5_3_claim_audit.py
==============================
Phase V5.3 Test Suite: Unsupported Claim Detection & Evidence Traceability
Verifies that all claimed canonical events possess concrete evidence records,
and flags any unsupported assertions.
"""

import os
import json
import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53ClaimAudit:
    """Verifies that every claim maps to verifiable evidence."""

    def test_zero_unsupported_primary_claims(self, manager):
        reg = manager.get_v5_3_evidence_registry()
        events = reg.get("events", [])
        for ev in events:
            tier = ev["verification_tier"]
            if tier in ["VERIFIED_PRIMARY", "VERIFIED_FIELD_INSPECTED"]:
                assert ev["primary_source_present"] is True, f"Unsupported primary claim in {ev['event_id']}"
                assert any(
                    any(prefix in item["source_reference"] for prefix in ["GSI", "BRO", "SDMA", "SK-", "MN-", "MZ-", "AS-", "ML-", "NL-", "AR-", "TR-", "KAL-"])
                    for item in ev["evidence_items"]
                ), f"Missing official source reference in {ev['event_id']}"

    def test_no_fabricated_scientific_claims(self, manager):
        reg = manager.get_v5_3_evidence_registry()
        events = reg.get("events", [])
        for ev in events:
            if ev.get("scientific_source_present"):
                # Only verified major disasters with published literature may claim scientific verification
                assert ev["event_id"] in {"EV-03", "EV-04", "EV-06", "EV-08"}

    def test_no_claims_of_in_situ_sensors_active(self, manager):
        inv = manager.get_v5_3_inventory()
        # Ensure that no events claim they were detected by physical in-situ inclinometers
        for ev in inv.get("events", []):
            assert "in-situ" not in ev.get("source", "").lower()
