# -*- coding: utf-8 -*-
"""
tests/test_mqtt_backhaul.py
===========================
Unit tests for gateway MQTT backhaul throughput, uplink latency, and buffer flush benchmarks.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mqtt_backhaul_validator import MQTTBackhaulValidator


@pytest.fixture
def validator():
    return MQTTBackhaulValidator()


def test_uplink_validation_healthy(validator):
    res = validator.validate_uplink(
        gateway_id="GW-TEST-01",
        test_payload_count=20,
        simulated_loss_rate=0.0,
        simulated_base_latency_ms=150.0
    )
    assert res["verdict"] == "HEALTHY"
    assert res["packet_delivery_ratio"] == 1.0
    assert res["average_latency_ms"] < 1200.0


def test_uplink_validation_degraded(validator):
    res = validator.validate_uplink(
        gateway_id="GW-TEST-02",
        test_payload_count=20,
        simulated_loss_rate=0.15,
        simulated_base_latency_ms=1800.0
    )
    assert res["verdict"] == "DEGRADED"
    assert res["packet_delivery_ratio"] == 0.85


def test_uplink_validation_unstable(validator):
    res = validator.validate_uplink(
        gateway_id="GW-TEST-03",
        test_payload_count=20,
        simulated_loss_rate=0.40,
        simulated_base_latency_ms=4500.0
    )
    assert res["verdict"] == "UNSTABLE"
    assert res["packet_delivery_ratio"] == 0.60


def test_buffer_flush_throughput_pass(validator):
    res = validator.test_buffer_flush(
        gateway_id="GW-TEST-01",
        buffered_count=60,
        flush_duration_s=2.0
    )
    assert res["records_per_second"] == 30.0
    assert res["buffer_flush_status"] == "PASS"


def test_buffer_flush_throughput_fail(validator):
    res = validator.test_buffer_flush(
        gateway_id="GW-TEST-01",
        buffered_count=10,
        flush_duration_s=2.0
    )
    assert res["records_per_second"] == 5.0
    assert res["buffer_flush_status"] == "FAIL"
