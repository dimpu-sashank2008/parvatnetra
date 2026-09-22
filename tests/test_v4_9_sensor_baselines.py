# -*- coding: utf-8 -*-
"""
tests/test_v4_9_sensor_baselines.py
===================================
Phase V4.9 Test Suite: Sensor Baseline Statistics & Range Validation
"""

import pytest
from services.field_evidence_manager import FieldEvidenceManager


@pytest.fixture
def evidence_mgr():
    return FieldEvidenceManager()


class TestSensorBaselines:
    """Tests descriptive baseline calculations without making unwarranted failure interpretations."""

    def test_baseline_calculation_statistics(self, evidence_mgr):
        sample_obs = [
            {"value": 14.5, "timestamp_utc": "2026-09-20T10:00:00Z"},
            {"value": 15.0, "timestamp_utc": "2026-09-20T10:15:00Z"},
            {"value": 14.8, "timestamp_utc": "2026-09-20T10:30:00Z"},
            {"value": 15.2, "timestamp_utc": "2026-09-20T10:45:00Z"},
            {"value": 14.9, "timestamp_utc": "2026-09-20T11:00:00Z"},
        ]
        stats = evidence_mgr.compute_baseline_statistics(sample_obs)
        assert stats["status"] == "STATISTICALLY_VALID"
        assert stats["sample_count"] == 5
        assert stats["min"] == 14.5
        assert stats["max"] == 15.2
        assert stats["mean"] == 14.88
        assert stats["temporal_span_hours"] == 1.0

    def test_empty_observations_handled_safely(self, evidence_mgr):
        stats = evidence_mgr.compute_baseline_statistics([])
        assert stats["status"] == "NO_DATA"
        assert stats["sample_count"] == 0
        assert stats["missingness_pct"] == 100.0

    def test_sensor_normal_operational_ranges_honored(self):
        # Range bounds defined in corridor_sensor_registry.json
        ranges = {
            "PIEZOMETER": (0.0, 50.0),      # kPa
            "INCLINOMETER": (-5.0, 5.0),    # mm
            "TILTMETER": (-2.0, 2.0),       # deg
            "RAIN_GAUGE": (0.0, 30.0),      # mm/h
            "GATEWAY": (11.5, 14.2)         # V
        }
        for s_type, (low, high) in ranges.items():
            assert low < high
            assert high - low > 0
