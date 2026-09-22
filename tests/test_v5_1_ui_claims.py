# -*- coding: utf-8 -*-
"""
tests/test_v5_1_ui_claims.py
=============================
Tests the four-tier Claim Freeze system (SUPPORTED, PARTIALLY_SUPPORTED,
UNSUPPORTED, FORBIDDEN) and verified resolution across all 9 scientific conflicts.
"""

import pytest
from engine.scientific_truth_engine import GLOBAL_SCIENTIFIC_TRUTH_ENGINE


def test_claim_freeze_categories_exist():
    ledger = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_ledger()
    freeze = ledger.get("claim_freeze", {})
    assert "supported_claims" in freeze
    assert "partially_supported_claims" in freeze
    assert "unsupported_claims" in freeze
    assert "forbidden_claims" in freeze


def test_unsupported_claims_contain_untraced_metrics():
    ledger = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_ledger()
    unsupported = ledger.get("claim_freeze", {}).get("unsupported_claims", [])
    joined = " ".join(unsupported)

    # 52 events must be flagged unsupported
    assert "52 real historical events" in joined
    # 41/11/11 must be flagged unsupported
    assert "41 training, 11 validation, 11 test" in joined
    # 0.81 metrics must be flagged unsupported
    assert "ROC-AUC 0.81" in joined
    # 4.2h median warning lead time must be flagged unsupported
    assert "4.2 hours median warning lead time" in joined


def test_supported_claims_contain_canonical_facts():
    ledger = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_ledger()
    supported = ledger.get("claim_freeze", {}).get("supported_claims", [])
    joined = " ".join(supported)

    assert "strictly 17" in joined
    assert "strictly 20" in joined
    assert "105 continuous 168-hour" in joined
    assert "36 real observation samples" in joined
    assert "25 synthetic sequences is strictly quarantined" in joined
    assert "7cb82388" in joined


def test_forbidden_claims_enforce_boundaries():
    ledger = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_ledger()
    forbidden = ledger.get("claim_freeze", {}).get("forbidden_claims", [])
    joined = " ".join(forbidden)

    # Forbids claiming field sensors installed before drilling
    assert "sensors are installed in the field before drilling" in joined
    # Forbids claiming live mountain telemetry streaming
    assert "live mountain field telemetry is streaming" in joined
    # Forbids claiming kinematic ML is trained
    assert "Kinematic In-Situ ML is trained" in joined


def test_all_conflicts_resolved():
    conflicts = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_conflict_matrix()
    assert len(conflicts) == 9
    for c in conflicts:
        assert c.get("status") == "RESOLVED"
        assert "resolution" in c
        assert "authoritative_artifact" in c
