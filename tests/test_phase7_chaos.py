# -*- coding: utf-8 -*-
"""
tests/test_phase7_chaos.py
==========================
PARVAT NETRA • PAHAD AI — Phase 7 Chaos & Failure Mode Test Battery
-------------------------------------------------------------------
Validates the 28 deterministic chaos and stress scenarios.
Verifies state machine integrity, fail-safe degradation, and zero unauthorized public alerts.
"""

import pytest
from engine.chaos_simulator import GLOBAL_CHAOS_HARNESS, ChaosValidationHarness

def test_all_28_chaos_sequences_execute():
    """Verify that all 28 sequences execute without error and return PASS verdicts."""
    harness = ChaosValidationHarness()
    results = harness.run_all_sequences()
    assert len(results) == 28

    for r in results:
        assert r.pass_verdict is True, f"Sequence {r.sequence_id} ({r.sequence_name}) failed"
        assert r.audit_logged is True
        # CRITICAL SAFETY INVARIANT: None of the chaos sequences must emit public dispatch
        assert r.public_dispatch_emitted is False, f"Unsafe public dispatch in sequence {r.sequence_name}"

def test_heavy_rain_single_signal_corroboration_failure():
    """Sequence 2: Heavy rainfall alone must not trigger corroboration without mechanical distress."""
    res = GLOBAL_CHAOS_HARNESS.run_sequence(2)
    assert res.sequence_name == "HEAVY_RAINFALL"
    assert res.corroboration_pass is False
    assert res.public_dispatch_emitted is False

def test_multiple_simultaneous_streams_requires_human_approval():
    """Sequence 10: Extreme multiple signals must route to authority, never public dispatch."""
    res = GLOBAL_CHAOS_HARNESS.run_sequence(10)
    assert res.sequence_name == "MULTIPLE_SIMULTANEOUS_EVIDENCE_STREAMS"
    assert res.corroboration_pass is True
    assert "AUTHORITY_REVIEW" in res.state_machine_transition
    assert res.public_dispatch_emitted is False

def test_database_and_network_outage_resilience():
    """Sequences 13 and 14: DB and network loss must fallback to local buffering."""
    res_db = GLOBAL_CHAOS_HARNESS.run_sequence(13)
    assert res_db.pass_verdict is True
    assert res_db.public_dispatch_emitted is False

    res_net = GLOBAL_CHAOS_HARNESS.run_sequence(14)
    assert res_net.pass_verdict is True
    assert res_net.public_dispatch_emitted is False

def test_telemetry_corruption_and_duplicates():
    """Sequences 16 and 17: Deduplication and corruption handling."""
    res_dup = GLOBAL_CHAOS_HARNESS.run_sequence(16)
    assert res_dup.pass_verdict is True

    res_corrupt = GLOBAL_CHAOS_HARNESS.run_sequence(17)
    assert res_corrupt.pass_verdict is True

def test_authority_timeout_escalation_does_not_auto_dispatch():
    """Sequence 25: Authority review timeout must escalate internally, not emit public siren."""
    res_timeout = GLOBAL_CHAOS_HARNESS.run_sequence(25)
    assert res_timeout.sequence_name == "AUTHORITY_APPROVAL_TIMEOUT"
    assert "ESCALATED_TIMEOUT" in res_timeout.state_machine_transition
    assert res_timeout.public_dispatch_emitted is False

def test_manual_override_and_rollback():
    """Sequences 26 and 27: Authority override and rollback."""
    res_override = GLOBAL_CHAOS_HARNESS.run_sequence(26)
    assert "REJECTED_FALSE_ALARM" in res_override.state_machine_transition

    res_rollback = GLOBAL_CHAOS_HARNESS.run_sequence(27)
    assert "MONITORING" in res_rollback.state_machine_transition
    assert res_rollback.public_dispatch_emitted is False
