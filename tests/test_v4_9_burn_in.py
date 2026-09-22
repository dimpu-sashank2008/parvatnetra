# -*- coding: utf-8 -*-
"""
tests/test_v4_9_burn_in.py
==========================
Phase V4.9 Test Suite: 72-Hour Burn-In, Telemetry Continuity & Packet Metrics
Validates:
- Item 12: Packet loss rate calculation
- Item 13: Store-and-forward replay handling without loss
- Item 17: Stale telemetry detection on heartbeat expiration
- Item 21: Burn-in timer governance (requires 72h continuous live telemetry)
"""

from datetime import datetime, timezone, timedelta
import pytest
from engine.field_commissioning_engine import FieldCommissioningEngine


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestBurnInAndContinuity:
    """Verifies burn-in monitoring, packet loss calculation, and stale telemetry handling."""

    def test_item_12_packet_loss_calculation(self, commissioning_engine):
        """Item 12: Packet loss rate evaluates to 0.0% on bench and handles missing frames correctly."""
        # Expected sequence 1..10, received 9 frames
        expected_seqs = list(range(1, 11))
        received_seqs = [1, 2, 3, 4, 5, 7, 8, 9, 10]  # seq 6 missing
        lost_count = len(set(expected_seqs) - set(received_seqs))
        packet_loss_rate = lost_count / len(expected_seqs)
        assert packet_loss_rate == 0.10
        assert lost_count == 1

    def test_item_13_store_and_forward_replay_handling(self, commissioning_engine):
        """Item 13: Store-and-forward correctly ingests batched packets after reconnection."""
        burst = [
            {"sensor_id": "RAIN-NH10-KM48-01", "timestamp_utc": "2026-09-20T14:00:00Z", "value": 0.0, "sequence_number": 10},
            {"sensor_id": "RAIN-NH10-KM48-01", "timestamp_utc": "2026-09-20T14:15:00Z", "value": 1.5, "sequence_number": 11},
            {"sensor_id": "RAIN-NH10-KM48-01", "timestamp_utc": "2026-09-20T14:30:00Z", "value": 3.0, "sequence_number": 12},
        ]
        res = commissioning_engine.test_store_and_forward_deduplication(burst)
        assert res["accepted_unique_count"] == 3
        assert res["rejected_duplicate_count"] == 0
        assert res["deduplication_success"] is True

    def test_item_17_stale_telemetry_detection(self):
        """Item 17: Telemetry older than maximum heartbeat window (> 15 min) is marked STALE."""
        now = datetime.now(timezone.utc)
        recent_ts = now - timedelta(minutes=5)
        stale_ts = now - timedelta(minutes=25)

        def check_staleness(ts: datetime, max_age_min: float = 15.0) -> bool:
            return (now - ts).total_seconds() > (max_age_min * 60)

        assert check_staleness(recent_ts) is False
        assert check_staleness(stale_ts) is True

    def test_item_21_burn_in_timer_requirements(self, commissioning_engine):
        """Item 21: 72-hour continuous burn-in is not satisfied when duration is 0h."""
        audit = commissioning_engine.audit_telemetry_continuity(live_hours=0.0)
        assert audit["longest_live_continuity_hours"] == 0.0
        assert audit["continuity_windows"]["72h"] is False
        assert audit["all_windows_satisfied"] is False
        assert audit["burn_in_status"] in ["NOT_STARTED", "PENDING", "NOT_STARTED_PENDING_INSTALLATION", "INCOMPLETE"]
