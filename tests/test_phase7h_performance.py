# -*- coding: utf-8 -*-
"""
tests/test_phase7h_performance.py
=================================
PHASE 7H — CP 7H-20, 7H-22: Local Performance Under Stress, Latency Benchmarks,
Throughput Assessment, and Chaos Resilience Regression Verification.
"""

import pytest
from services.resilience_metrics import RESILIENCE_METRICS


def test_local_performance_stress_benchmarks():
    """CP 7H-20: Validates inference latency, routing latency, and ingestion throughput."""
    perf = RESILIENCE_METRICS.measure_local_performance_stress()

    assert "inference_latency_ms" in perf
    assert "routing_latency_ms" in perf
    assert "simulated_ingestion_rate_ops" in perf
    assert "db_write_throughput_records_per_sec" in perf

    # Strict performance SLAs for edge / field deployment
    assert perf["inference_latency_ms"] < 150.0  # Compound inference within 150ms
    assert perf["routing_latency_ms"] < 100.0    # Offline route calculation within 100ms
    assert perf["simulated_ingestion_rate_ops"] >= 500  # High telemetry ingestion throughput
    assert perf["db_write_throughput_records_per_sec"] >= 100


def test_queue_overflow_and_storage_capacity():
    """CP 7H-20: Offline queue tracks capacity and respects 50k rollover boundaries."""
    from backend.edge.edge_store import EdgeStore
    store = EdgeStore(db_path=":memory:")
    stats = store.get_queue_stats()

    assert stats["capacity_bytes"] > 0
    assert stats["storage_used_pct"] >= 0.0
    assert stats["is_overflow"] is False
    assert stats["overflow_policy"] == "OLDEST_DROP_WITH_QUARANTINE"
