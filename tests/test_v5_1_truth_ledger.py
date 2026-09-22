# -*- coding: utf-8 -*-
"""
tests/test_v5_1_truth_ledger.py
===============================
Phase V5.1 Test Suite: Scientific Truth Ledger Integrity & Completeness
"""

import pytest
from engine.scientific_truth_engine import (
    ScientificTruthEngine,
    VERDICT_TRUTH_LEDGER_VERIFIED
)


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestTruthLedgerIntegrity:
    """Verifies that the unified scientific truth ledger is structurally complete."""

    def test_ledger_loads_and_has_required_sections(self, truth_engine):
        ledger = truth_engine.get_ledger()
        assert ledger is not None
        assert ledger.get("ledger_version") == "5.1.0"
        assert ledger.get("overall_verdict") == VERDICT_TRUTH_LEDGER_VERIFIED

        required_sections = [
            "production_model",
            "research_models",
            "data_truth",
            "dataset_registry",
            "metric_registry",
            "warning_lead_registry",
            "physical_field_telemetry_state",
            "calibration_state",
            "institutional_authorization_state",
            "claim_freeze",
            "claim_conflict_matrix",
            "summary_statistics"
        ]
        for sec in required_sections:
            assert sec in ledger, f"Missing section '{sec}' in scientific truth ledger."

    def test_verdict_evaluation_is_truth_ledger_verified(self, truth_engine):
        res = truth_engine.evaluate_v5_1_verdict()
        assert res["overall_verdict"] == VERDICT_TRUTH_LEDGER_VERIFIED
        assert res["models_immutable"] is True
        assert res["resolved_conflicts"] == res["total_conflicts"]
        assert res["unresolved_conflicts"] == 0
