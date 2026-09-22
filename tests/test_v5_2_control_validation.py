# -*- coding: utf-8 -*-
"""
tests/test_v5_2_control_validation.py
=====================================
Phase V5.2 Test Suite: Negative Control Stability Verification & Window Non-Overlap
"""

import pytest
from engine.dataset_expansion_manager import (
    DatasetExpansionManager,
    CONTROL_VERIFIED_STABLE
)


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52ControlValidation:
    """Verifies that negative controls are independently certified stable and non-colliding."""

    def test_canonical_control_count_is_twenty(self, manager):
        count = manager.get_canonical_control_count()
        assert count == 20, f"Expected exactly 20 verified negative controls, got {count}"

    def test_all_controls_are_verified_stable(self, manager):
        controls = manager.list_canonical_controls()
        for c in controls:
            assert c["stability_status"] == CONTROL_VERIFIED_STABLE
            assert c["absence_of_failure_evidence"]
            assert c["verification_evidence"]
            assert c["control_hash"]
            assert len(c["control_hash"]) == 64

    def test_controls_do_not_overlap_with_positive_events_in_space_time(self, manager):
        controls = manager.list_canonical_controls()
        events = manager.list_canonical_events()

        for c in controls:
            c_lat = c["latitude"]
            c_lon = c["longitude"]
            c_start = manager._parse_iso(c["start_time"])
            c_end = manager._parse_iso(c["end_time"])

            for e in events:
                e_lat = e["latitude"]
                e_lon = e["longitude"]
                e_dt = manager._parse_iso(e["timestamp"])

                dist_km = manager._haversine_km(c_lat, c_lon, e_lat, e_lon)
                # If within 2 km spatial buffer, verify time window does not overlap
                if dist_km < 2.0:
                    assert not (c_start <= e_dt <= c_end), (
                        f"Control window {c['control_id']} overlaps positive event {e['event_id']} "
                        f"at {dist_km:.2f} km distance"
                    )
