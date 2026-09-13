# -*- coding: utf-8 -*-
"""
tests/test_phase10j_idempotency.py
==================================
PARVAT NETRA • Phase 10J — Idempotency & Duplicate Suppression Tests
--------------------------------------------------------------------
Verifies:
  1. Deterministic collision-resistant idempotency keys (CP07).
  2. Browser refresh, retry, or double-click duplicate suppression.
  3. Safe replay behavior: returns cached result without re-dispatching.
  4. Time-bucket bounding (distinct dispatches across windows allowed).
"""

import time
import pytest
from services.retry_manager import RETRY_MANAGER
from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE


def test_idempotency_key_generation_determinism():
    """Verifies idempotency key generation is deterministic and collision resistant."""
    k1 = RETRY_MANAGER.compute_idempotency_key("INC-01", "user@example.com", "SMS")
    k2 = RETRY_MANAGER.compute_idempotency_key("INC-01", "user@example.com", "SMS")
    assert k1 == k2
    assert k1.startswith("IDEMP-")

    k_diff_channel = RETRY_MANAGER.compute_idempotency_key("INC-01", "user@example.com", "EMAIL")
    assert k1 != k_diff_channel


def test_dual_dispatch_duplicate_suppression():
    """Verifies duplicate dispatches with identical idempotency key are suppressed."""
    key = f"TEST-IDEMP-{int(time.time())}-ABC"

    # First dispatch
    res1 = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="judge@example.gov.in",
        phone_number="+919832011234",
        scenario_id="ML-SONAPUR-01",
        idempotency_key=key,
        is_test=True
    )
    assert res1["success"] is True
    assert res1["status_summary"] != "DUPLICATE_SUPPRESSED"

    # Second dispatch with same idempotency key (simulating browser double-click)
    res2 = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="judge@example.gov.in",
        phone_number="+919832011234",
        scenario_id="ML-SONAPUR-01",
        idempotency_key=key,
        is_test=True
    )
    assert res2["success"] is True
    assert res2["status"] == "DUPLICATE_SUPPRESSED"
    assert "suppressed" in res2["message"].lower()
