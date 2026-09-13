# -*- coding: utf-8 -*-
"""
tests/test_phase10j_retry.py
============================
PARVAT NETRA • Phase 10J — Exponential Backoff & Idempotency Tests
------------------------------------------------------------------
Verifies:
  1. Exponential backoff mathematical delay calculation.
  2. Bounded retries: strict termination at max_attempts (no infinite loop).
  3. Distinction between transient errors (retried) and permanent errors (fail-fast).
  4. Deterministic idempotency key derivation.
  5. Duplicate suppression for identical dispatches within time window.
"""

import pytest
from services.retry_manager import RetryManager


def test_exponential_backoff_calculation():
    """Verifies backoff delays increase exponentially and respect cap."""
    mgr = RetryManager(initial_backoff=1.0, multiplier=2.0, max_backoff=8.0)

    assert mgr.compute_backoff(1) == 0.0
    assert mgr.compute_backoff(2) == 1.0
    assert mgr.compute_backoff(3) == 2.0
    assert mgr.compute_backoff(4) == 4.0
    assert mgr.compute_backoff(5) == 8.0  # Capped at max_backoff


def test_bounded_retries_termination():
    """Verifies that transient errors terminate strictly at max_attempts."""
    mgr = RetryManager(max_attempts=3, initial_backoff=0.01)
    call_count = 0

    def failing_function():
        nonlocal call_count
        call_count += 1
        return {"success": False, "status": "FAILED", "error": "Gateway connection timeout (504)"}

    result = mgr.execute_with_retry(failing_function)
    assert call_count == 3
    assert result["success"] is False
    assert result["attempt_count"] == 3
    assert result["retry_exhausted"] is True


def test_permanent_error_fails_fast():
    """Verifies that permanent errors (e.g. invalid syntax) do NOT retry."""
    mgr = RetryManager(max_attempts=3, initial_backoff=0.01)
    call_count = 0

    def bad_syntax_function():
        nonlocal call_count
        call_count += 1
        return {"success": False, "status": "FAILED", "error": "Invalid recipient email format"}

    result = mgr.execute_with_retry(bad_syntax_function)
    assert call_count == 1, "Permanent error must fail fast on attempt 1 without retry!"
    assert result["success"] is False


def test_idempotency_key_determinism_and_collision_resistance():
    """Verifies that identical inputs yield identical keys, and distinct inputs differ."""
    k1 = RetryManager.generate_idempotency_key("INC-01", "user@sih.gov.in", "EMAIL", "TEST_ALERT")
    k2 = RetryManager.generate_idempotency_key("INC-01", "user@sih.gov.in", "EMAIL", "TEST_ALERT")
    assert k1 == k2
    assert k1.startswith("IDEMP-EMA-")

    # Different recipient
    k3 = RetryManager.generate_idempotency_key("INC-01", "other@sih.gov.in", "EMAIL", "TEST_ALERT")
    assert k1 != k3

    # Different channel
    k4 = RetryManager.generate_idempotency_key("INC-01", "user@sih.gov.in", "SMS", "TEST_ALERT")
    assert k1 != k4


def test_duplicate_dispatch_suppression():
    """Verifies that subsequent dispatches with the same key are suppressed."""
    mgr = RetryManager(max_attempts=3)
    key = "IDEMP-TEST-UNIQUE-KEY-001"
    calls = 0

    def sample_dispatch():
        nonlocal calls
        calls += 1
        return {"success": True, "status": "SENT", "provider_reference": "REF-001"}

    # First call
    r1 = mgr.execute_with_retry(sample_dispatch, idempotency_key=key)
    assert r1["success"] is True
    assert calls == 1

    # Second call with same key
    r2 = mgr.execute_with_retry(sample_dispatch, idempotency_key=key)
    assert r2["success"] is True
    assert r2["is_duplicate"] is True
    assert calls == 1, "Duplicate dispatch was executed instead of suppressed!"
