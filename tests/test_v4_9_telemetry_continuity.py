# -*- coding: utf-8 -*-
"""
tests/test_v4_9_telemetry_continuity.py
=======================================
Phase V4.9 Test Suite: Telemetry Continuity Windows & Timestamp Monotonicity
"""

import pytest
from engine.telemetry_evidence_audit_engine import TelemetryEvidenceAuditEngine


@pytest.fixture
def audit_engine():
    return TelemetryEvidenceAuditEngine()


class TestTelemetryContinuity:
    """Verifies that live field telemetry continuity remains honestly evaluated as unavailable."""

    def test_all_live_continuity_windows_unavailable_when_zero(self, audit_engine):
        windows = audit_engine.evaluate_continuity_windows(0.0)
        required_horizons = ["1h", "6h", "12h", "24h", "48h", "72h", "168h"]
        for h in required_horizons:
            assert h in windows
            assert windows[h]["available"] is False
            assert windows[h]["status"] == "UNAVAILABLE"

    def test_corridor_audit_continuity_windows(self, audit_engine):
        res = audit_engine.perform_full_corridor_audit()
        assert "continuity_windows" in res
        for h, meta in res["continuity_windows"].items():
            assert meta["available"] is False
            assert meta["status"] == "UNAVAILABLE"

    def test_continuity_windows_with_duration(self, audit_engine):
        # With 8.0h continuous telemetry, 1h and 6h are satisfied, 12h+ are not
        windows = audit_engine.evaluate_continuity_windows(8.0)
        assert windows["1h"]["available"] is True
        assert windows["6h"]["available"] is True
        assert windows["12h"]["available"] is False
        assert windows["24h"]["available"] is False
        assert windows["48h"]["available"] is False
        assert windows["72h"]["available"] is False
        assert windows["168h"]["available"] is False
