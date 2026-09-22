# -*- coding: utf-8 -*-
"""
tests/test_v5_2_gateway.py
==========================
Phase V5.2 Test Suite: LoRa Concentrator Gateway Commissioning
Verifies ESP32/SX1302 concentrator identity, IN865_867 frequency plan,
store-and-forward deduplication, and distinction between bench and field validation.
"""

import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_gateway_identity_and_frequency_plan():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    gw = engine.audit_gateway_transport()
    assert gw["gateway_id"] == "GW-NH10-KM48-01"
    assert gw["frequency_plan"] == "IN865_867"
    assert gw["hardware_concentrator"] == "SX1302"
    assert gw["microcontroller"] == "ESP32-S3"


def test_bench_validation_distinguished_from_field_validation():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    gw = engine.audit_gateway_transport()
    assert gw["radio_validation_status"] == "BENCH_VALIDATED"
    assert gw["field_validation_status"] == "FIELD_VALIDATION_PENDING"


def test_store_and_forward_deduplication():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    test_payload = {
        "gateway_id": "GW-NH10-KM48-01",
        "sensor_id": "BH-KM48-INC01",
        "sequence_number": 42,
        "payload_hex": "010203040506"
    }
    # Initial insertion
    first_result = engine.evaluate_store_and_forward_replay(test_payload)
    assert first_result["is_duplicate"] is False
    assert first_result["stored_successfully"] is True

    # Duplicate insertion must be detected and rejected
    second_result = engine.evaluate_store_and_forward_replay(test_payload)
    assert second_result["is_duplicate"] is True
    assert second_result["stored_successfully"] is False
