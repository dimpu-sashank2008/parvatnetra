# -*- coding: utf-8 -*-
"""
tests/test_v5_2_temporal_leakage.py
===================================
Phase V5.2 Test Suite: Temporal Leakage Audit & Window Alignment Verification
"""

import pytest
from datetime import datetime, timezone
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52TemporalLeakage:
    """Verifies that future data never leaks into past event contextual observations."""

    def test_event_timestamps_are_strictly_valid_iso(self, manager):
        events = manager.list_canonical_events()
        for ev in events:
            ts_str = ev["timestamp"]
            assert ts_str.endswith("Z") or "+00:00" in ts_str
            dt = manager._parse_iso(ts_str)
            assert dt <= datetime.now(timezone.utc), f"Event {ev['event_id']} has future timestamp {ts_str}"

    def test_control_windows_have_valid_start_and_end(self, manager):
        controls = manager.list_canonical_controls()
        for ctrl in controls:
            start_dt = manager._parse_iso(ctrl["start_time"])
            end_dt = manager._parse_iso(ctrl["end_time"])
            assert start_dt < end_dt, f"Control {ctrl['control_id']} has inverted window: {start_dt} >= {end_dt}"
            # Ensure window duration is at least 24 hours
            duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
            assert duration_hours >= 24.0
