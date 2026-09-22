# -*- coding: utf-8 -*-
"""
tests/test_v5_2_first_live_packet.py
====================================
Phase V5.2 Test Suite: First Live Physical Packet Gate
Verifies that only genuine LIVE_PHYSICAL packets from deployed mountain nodes qualify,
and strictly rejects BENCH_HARDWARE, SIMULATED, or REPLAYED_REAL packets.
"""

import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_first_live_packet_status_awaiting_deployment():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    res = engine.evaluate_v5_2_verdict()
    assert res["first_live_packet_id"] is None
    assert res["first_live_sensor_id"] is None
    assert res["first_live_timestamp"] is None


def test_reject_simulated_packet_as_first_live():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    sim_packet = {
        "packet_id": "SIM-PKT-001",
        "sensor_id": "BH-KM48-PZ01",
        "source_classification": "SIMULATED",
        "sequence_number": 1,
        "timestamp_utc": "2026-09-21T12:00:00Z"
    }
    is_live, msg, det = engine.evaluate_first_live_packet_candidate(sim_packet)
    assert is_live is False
    assert det["qualified"] is False
    assert any("SIMULATED" in r or "SOURCE" in r for r in det["reasons"])


def test_reject_bench_hardware_packet_as_first_live():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    bench_packet = {
        "packet_id": "BENCH-PKT-001",
        "sensor_id": "BH-KM48-INC01",
        "source_classification": "BENCH_HARDWARE",
        "sequence_number": 1,
        "timestamp_utc": "2026-09-21T12:00:00Z"
    }
    is_live, msg, det = engine.evaluate_first_live_packet_candidate(bench_packet)
    assert is_live is False
    assert det["qualified"] is False
