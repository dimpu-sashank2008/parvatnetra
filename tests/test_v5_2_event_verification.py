# -*- coding: utf-8 -*-
"""
tests/test_v5_2_event_verification.py
=====================================
Phase V5.2 Test Suite: Five-Tier Event Verification & Canonical Admission
"""

import pytest
from engine.dataset_expansion_manager import (
    DatasetExpansionManager,
    VERIFIED_PRIMARY,
    VERIFIED_MULTI_SOURCE,
    SECONDARY_VERIFIED,
    UNVERIFIED,
    REJECTED,
    CANONICAL_VERIFICATION_TIERS
)


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52EventVerification:
    """Verifies that only corroborated, tiered events achieve canonical status."""

    def test_canonical_tiers_definition(self):
        assert VERIFIED_PRIMARY in CANONICAL_VERIFICATION_TIERS
        assert VERIFIED_MULTI_SOURCE in CANONICAL_VERIFICATION_TIERS
        assert SECONDARY_VERIFIED in CANONICAL_VERIFICATION_TIERS
        assert UNVERIFIED not in CANONICAL_VERIFICATION_TIERS
        assert REJECTED not in CANONICAL_VERIFICATION_TIERS

    def test_unverified_candidate_not_admitted_to_canonical(self, manager):
        initial_canonical = manager.get_canonical_event_count()
        unverified_rec = {
            "event_id": "TEST-UNVERIFIED-CANDIDATE-01",
            "timestamp": "2024-08-10T14:00:00Z",
            "latitude": 27.50,
            "longitude": 88.50,
            "state": "Sikkim",
            "district": "Mangan",
            "source": "Unverified Social Media Post",
            "source_reference": "POST-XYZ",
            "verification_status": UNVERIFIED
        }
        res = manager.ingest_raw_record(unverified_rec, authorizer_role="GSI_LIAISON")
        assert res["success"] is True
        assert res["admitted_to_canonical"] is False
        assert manager.get_canonical_event_count() == initial_canonical
        assert manager.get_unverified_event_count() >= 1

    def test_tier_distribution_integrity(self, manager):
        tier_counts = manager.get_verification_tier_counts()
        assert tier_counts[VERIFIED_PRIMARY] >= 30
        assert tier_counts[VERIFIED_MULTI_SOURCE] >= 5
        assert tier_counts[SECONDARY_VERIFIED] >= 4
        total_canonical = (
            tier_counts[VERIFIED_PRIMARY] +
            tier_counts[VERIFIED_MULTI_SOURCE] +
            tier_counts[SECONDARY_VERIFIED]
        )
        assert total_canonical == manager.get_canonical_event_count()
