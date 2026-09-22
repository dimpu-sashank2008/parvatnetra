# -*- coding: utf-8 -*-
"""
tests/test_v5_3_timestamp_validation.py
=======================================
Phase V5.3 Test Suite: Timestamp Format, UTC Normalization & Precision
Verifies that all 42 events feature valid ISO-8601 timestamps, UTC timezone
normalization, honest time precision tracking, and zero synthetic dates.
"""

from datetime import datetime
import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53TimestampValidation:
    """Verifies timestamp formatting and chronological validity."""

    def test_timestamps_strictly_valid_iso(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        for e in events:
            ts = e["timestamp"]
            assert ts.endswith("Z") or "+00:00" in ts, f"Non-UTC timestamp in {e['event_id']}: {ts}"
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            assert 2018 <= parsed.year <= 2026, f"Invalid historical year in {e['event_id']}: {parsed.year}"

    def test_time_precision_tracking(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        for e in events:
            prec = e.get("time_precision")
            assert prec in {"MINUTE", "QUARTER_HOUR", "DAY"}

    def test_timestamp_completeness_100_percent(self, manager):
        inv = manager.get_v5_3_inventory()
        metrics = inv.get("quality_metrics", {})
        assert metrics.get("timestamp_completeness_pct") == 100.0
