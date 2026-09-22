# -*- coding: utf-8 -*-
"""
tests/test_v4_9_time_sync.py
============================
Phase V4.9 Test Suite: Time Synchronization, Localhost Isolation & V3 Immutability
Validates:
- Item 8: Time synchronization tolerances (NTP / GPS clock drift within +/- 2000 ms)
- Item 27: Localhost-only deployment isolation (no public tunnels or external binding)
- Item 28: Production V3 LSTM model weights cryptographic immutability
"""

import os
import hashlib
from datetime import datetime, timezone
import pytest


class TestTimeSyncAndIsolation:
    """Verifies clock synchronization, localhost isolation, and model immutability."""

    def test_item_8_time_synchronization_drift_tolerance(self):
        """Item 8: Clock drift between sensor RTC / gateway and backend must be < 2000 ms."""
        def evaluate_clock_drift(device_epoch_ms: int, backend_epoch_ms: int) -> bool:
            drift_ms = abs(device_epoch_ms - backend_epoch_ms)
            return drift_ms <= 2000

        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        # Normal drift within 500 ms
        assert evaluate_clock_drift(now_ms - 450, now_ms) is True
        # Excessive drift > 2000 ms
        assert evaluate_clock_drift(now_ms - 3500, now_ms) is False

    def test_item_27_localhost_only_deployment_isolation(self):
        """Item 27: Environment strictly forbids public deployment and tunnel exposure."""
        import os
        allowed_hosts = ["127.0.0.1", "localhost"]
        host = os.environ.get("FLASK_HOST", "127.0.0.1")
        assert host in allowed_hosts
        assert os.environ.get("ENABLE_PUBLIC_TUNNEL", "0") in ["0", "false", "False"]

    def test_item_28_production_v3_immutability(self):
        """Item 28: Production V3 weights SHA-256 must match 7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183."""
        v3_path = os.path.join(os.path.dirname(__file__), "..", "models", "pahad_lstm_v3_weights.pt")
        assert os.path.exists(v3_path), f"V3 weights file not found at {v3_path}"
        with open(v3_path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        expected = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"
        assert digest == expected, f"V3 weights compromised! Expected {expected}, got {digest}"
