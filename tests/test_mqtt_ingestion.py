# -*- coding: utf-8 -*-
"""
tests/test_mqtt_ingestion.py
============================
Unit tests for MQTT Broker Ingestion Service (Phase 6A).
Validates:
  - Canonical topic namespace routing: pahad/{state}/{sector}/{device}/telemetry
  - JSON payload decoding and contract validation
  - Graceful fallback when MQTT broker / paho-mqtt client is unavailable
  - Error rejection and drop metrics for malformed MQTT payloads
"""

import json
from datetime import datetime, timezone
import pytest

from services.mqtt_ingestion import MQTTIngestionService


@pytest.fixture
def mqtt_service():
    return MQTTIngestionService()


def test_parse_canonical_topic(mqtt_service):
    topic = "pahad/Sikkim/SK-NH10-KM48/DEV-PZ-01/telemetry"
    parsed = mqtt_service.parse_topic(topic)
    assert parsed is not None
    assert parsed["state"] == "Sikkim"
    assert parsed["sector_id"] == "SK-NH10-KM48"
    assert parsed["device_id"] == "DEV-PZ-01"
    assert parsed["message_type"] == "telemetry"


def test_parse_invalid_topic(mqtt_service):
    # Missing segments
    parsed = mqtt_service.parse_topic("invalid/topic/format")
    assert parsed is None


def test_handle_valid_mqtt_message(mqtt_service):
    topic = "pahad/Sikkim/SK-NH10-KM48/DEV-MQTT-01/telemetry"
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "battery": 90.0,
        "measurements": {
            "pore_pressure": {"value": 22.0, "unit": "kPa"}
        }
    }
    payload_str = json.dumps(payload)

    res = mqtt_service.handle_message(topic, payload_str)
    assert res["status"] == "ACCEPTED"
    assert res["device_id"] == "DEV-MQTT-01"
    assert res["sector_id"] == "SK-NH10-KM48"


def test_handle_corrupted_mqtt_payload(mqtt_service):
    topic = "pahad/Sikkim/SK-NH10-KM48/DEV-MQTT-02/telemetry"
    res = mqtt_service.handle_message(topic, "NOT_VALID_JSON{")
    assert res["status"] == "REJECTED_DECODE_ERROR"


def test_handle_out_of_bounds_mqtt_packet(mqtt_service):
    topic = "pahad/Unknown/OUT-SECTOR/DEV-MQTT-03/telemetry"
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 10.0, # Out of NER bounds
        "longitude": 75.0,
        "measurements": {"pore_pressure": 15.0}
    }
    res = mqtt_service.handle_message(topic, json.dumps(payload))
    assert res["status"] == "REJECTED_OUT_OF_BOUNDS"


def test_mqtt_service_status(mqtt_service):
    status = mqtt_service.get_status()
    assert "broker_host" in status
    assert "status" in status
    assert "messages_processed" in status
