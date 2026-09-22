# -*- coding: utf-8 -*-
"""
tests/test_v5_0_burn_in.py
==========================
Phase V5.0 Test Suite: Store-and-Forward Replay & 24h/72h Burn-In Verification
"""

import pytest
from engine.physical_deployment_engine import PhysicalDeploymentEngine


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestBurnInAndStoreAndForward:
    """Verifies store-and-forward deduplication and 24h/72h burn-in thresholds."""

    def test_store_and_forward_packet_deduplication(self, deployment_engine):
        packets = [
            {"sensor_id": "TILT-01", "timestamp_utc": "2026-09-21T10:00:00Z", "value": 1.2, "sequence_number": 10},
            {"sensor_id": "TILT-01", "timestamp_utc": "2026-09-21T10:00:00Z", "value": 1.2, "sequence_number": 10}, # Dupe
            {"sensor_id": "TILT-01", "timestamp_utc": "2026-09-21T10:05:00Z", "value": 1.3, "sequence_number": 11},
            {"sensor_id": "TILT-01", "timestamp_utc": "2026-09-21T10:05:00Z", "value": 1.3, "sequence_number": 11}, # Dupe
        ]
        res = deployment_engine.test_store_and_forward_deduplication(packets)
        assert res["total_packets"] == 4
        assert res["accepted_count"] == 2
        assert res["duplicate_count"] == 2
        assert res["zero_duplicate_observations_created"] is True

    def test_current_burn_in_status_is_pending(self, deployment_engine):
        b = deployment_engine.evaluate_burn_in_status(observation_hours=0.0, pdr_pct=0.0)
        assert b["burn_in_status"] == "BURN_IN_PENDING"
        assert b["burn_in_24h_achieved"] is False
        assert b["burn_in_72h_achieved"] is False
        assert b["active_alarming_permitted"] is False

    def test_burn_in_24h_threshold(self, deployment_engine):
        b = deployment_engine.evaluate_burn_in_status(observation_hours=24.5, pdr_pct=98.5)
        assert b["burn_in_24h_achieved"] is True
        assert b["burn_in_status"] == "BURN_IN_24H_COMPLETE"
        # 72h still pending
        assert b["burn_in_72h_achieved"] is False
        assert b["active_alarming_permitted"] is False

    def test_burn_in_72h_threshold(self, deployment_engine):
        b = deployment_engine.evaluate_burn_in_status(observation_hours=72.1, pdr_pct=99.2)
        assert b["burn_in_24h_achieved"] is True
        assert b["burn_in_72h_achieved"] is True
        assert b["burn_in_status"] == "BURN_IN_72H_COMPLETE"
        assert b["active_alarming_permitted"] is True

    def test_continuity_windows_all_unavailable(self, deployment_engine):
        cont = deployment_engine.audit_telemetry_continuity()
        assert cont["longest_continuous_live_telemetry_hours"] == 0.0
        assert cont["total_verified_live_observations"] == 0
        for w, data in cont["continuity_windows"].items():
            assert data["status"] == "UNAVAILABLE"
            assert data["verified_live_packets"] == 0
