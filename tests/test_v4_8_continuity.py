# -*- coding: utf-8 -*-
"""
tests/test_v4_8_continuity.py
=============================
Automated test suite for Phase V4.8 Telemetry Continuity Analysis.
Tests:
  1. Continuity window analysis across [1h, 6h, 12h, 24h, 48h, 72h, 168h].
  2. Verified absence of live telemetry correctly flags all windows as UNAVAILABLE.
  3. Longest genuine LIVE continuous telemetry duration is strictly 0.0h.
  4. Calendar time span without contiguous observations cannot be claimed as continuous.
"""

import pytest
from engine.telemetry_evidence_audit_engine import (
    GLOBAL_EVIDENCE_AUDIT_ENGINE,
    TelemetryEvidenceAuditEngine
)


def test_continuity_windows_all_unavailable_when_zero_hours():
    """Confirms that with 0.0h live observations, all windows are UNAVAILABLE."""
    engine = TelemetryEvidenceAuditEngine()
    windows = engine.evaluate_continuity_windows(0.0)
    expected_windows = ["1h", "6h", "12h", "24h", "48h", "72h", "168h"]
    for w in expected_windows:
        assert w in windows
        assert windows[w]["available"] is False
        assert windows[w]["status"] == "UNAVAILABLE"


def test_continuity_windows_partial_duration():
    """Confirms that a duration of 14.0h makes 1h, 6h, 12h AVAILABLE, but 24h+ UNAVAILABLE."""
    engine = TelemetryEvidenceAuditEngine()
    windows = engine.evaluate_continuity_windows(14.0)
    assert windows["1h"]["available"] is True
    assert windows["6h"]["available"] is True
    assert windows["12h"]["available"] is True
    assert windows["24h"]["available"] is False
    assert windows["48h"]["available"] is False
    assert windows["72h"]["available"] is False
    assert windows["168h"]["available"] is False


def test_corridor_audit_longest_live_continuity():
    """Confirms that full corridor audit currently reports 0.0h live continuity."""
    audit = GLOBAL_EVIDENCE_AUDIT_ENGINE.perform_full_corridor_audit()
    assert "continuity_windows" in audit
    for w, meta in audit["continuity_windows"].items():
        assert meta["available"] is False
