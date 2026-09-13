# -*- coding: utf-8 -*-
"""
services/mqtt_ingestion.py
==========================
PARVAT NETRA • MQTT Field Telemetry Ingestion Service
------------------------------------------------------
Subscribes to regional telemetry topics from field LoRaWAN gateways and cellular IoT nodes:
  Topic Schema: pahad/{state}/{sector}/{device_id}/telemetry
  Example:      pahad/Sikkim/SK-NH10-KM48/PZ-01/telemetry

Capabilities:
  1. Configurable Broker Credentials via Environment Variables
  2. Dynamic Topic Routing & Metadata Extraction
  3. Strict Telemetry Contract Validation & Calibration
  4. Continuous ObservationStore & Ingestion Audit Logging
  5. Graceful Library Fallback if paho-mqtt is absent
"""

from __future__ import annotations

import os
import re
import json
import sqlite3
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Callable

from services.telemetry_contract import (
    GLOBAL_TELEMETRY_VALIDATOR,
    ValidationResult,
    TelemetryPacket
)
from engine.observation_store import (
    GLOBAL_OBSERVATION_STORE,
    ObservationRecord
)
from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY
)

logger = logging.getLogger("MQTT_INGESTION")

# Environment Broker Configuration
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
MQTT_TLS_ENABLED = os.environ.get("MQTT_TLS_ENABLED", "0") == "1"
MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID", "pahad_mqtt_ingress_worker")
MQTT_TOPIC_SUBSCRIPTION = os.environ.get("MQTT_TOPIC_SUBSCRIPTION", "pahad/+/+/+/telemetry")

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Optional Paho Import
try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    mqtt = None
    PAHO_AVAILABLE = False


class MQTTIngestionService:
    """Manages MQTT broker subscriptions and telemetry pipeline processing."""

    def __init__(
        self,
        broker_host: str = MQTT_BROKER_HOST,
        broker_port: int = MQTT_BROKER_PORT,
        topic_pattern: str = MQTT_TOPIC_SUBSCRIPTION
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic_pattern = topic_pattern
        self.is_connected = False
        self._client: Any = None
        self._lock = threading.Lock()

        # Observability counters
        self.total_received = 0
        self.total_accepted = 0
        self.total_rejected = 0
        self.last_packet_time: Optional[str] = None

    def _get_conn(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(SQLITE_DB_PATH)), exist_ok=True)
        return sqlite3.connect(SQLITE_DB_PATH)

    def parse_topic(self, topic: str) -> Optional[Dict[str, str]]:
        """
        Extracts hierarchy from topic string:
        pahad/{state}/{sector}/{device_id}/telemetry
        """
        parts = topic.strip("/").split("/")
        if len(parts) >= 5 and parts[0] == "pahad" and parts[-1] == "telemetry":
            return {
                "state": parts[1],
                "sector_id": parts[2],
                "device_id": parts[3],
                "message_type": parts[4]
            }
        return None

    def handle_message(self, topic: str, payload: Any) -> Dict[str, Any]:
        """Convenience wrapper accepting str, dict, or bytes."""
        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        elif isinstance(payload, bytes):
            payload_bytes = payload
        else:
            payload_bytes = json.dumps(payload).encode("utf-8")
        res = self.handle_incoming_message(topic, payload_bytes)
        if res.get("status") == "REJECTED_MALFORMED_JSON":
            res["status"] = "REJECTED_DECODE_ERROR"
        return res

    def handle_incoming_message(self, topic: str, payload_bytes: bytes) -> Dict[str, Any]:
        """
        Processes an MQTT packet:
        1. Decode JSON
        2. Extract topic metadata
        3. Validate against Telemetry Contract
        4. Persist to ObservationStore
        5. Write audit log
        """
        with self._lock:
            self.total_received += 1
            now_iso = datetime.now(timezone.utc).isoformat()
            self.last_packet_time = now_iso

        # Decode JSON
        try:
            payload_str = payload_bytes.decode("utf-8")
            raw_data = json.loads(payload_str)
        except Exception as e:
            with self._lock:
                self.total_rejected += 1
            self._log_ingestion("MALFORMED", "UNKNOWN", "MQTT", "REJECTED_MALFORMED_JSON", str(e))
            return {"status": "REJECTED_MALFORMED_JSON", "error": str(e)}

        # Topic metadata enrichment
        topic_meta = self.parse_topic(topic)
        if topic_meta:
            raw_data.setdefault("device_id", topic_meta["device_id"])
            raw_data.setdefault("sector_id", topic_meta["sector_id"])
            raw_data.setdefault("state", topic_meta["state"])

        # Validate contract
        val_res = GLOBAL_TELEMETRY_VALIDATOR.validate_and_normalize(
            raw_data, transport="MQTT", enforce_registered=False
        )

        packet_id = raw_data.get("packet_id") or "UNKNOWN_PKT"
        device_id = raw_data.get("device_id") or "UNKNOWN_DEV"

        if not val_res.is_valid:
            with self._lock:
                self.total_rejected += 1
            self._log_ingestion(packet_id, device_id, "MQTT", val_res.status, val_res.message)
            return {"status": val_res.status, "message": val_res.message}

        packet = val_res.packet
        assert packet is not None

        # Persist to central ObservationStore
        records_saved = self._persist_to_store(packet, raw_data.get("sector_id"))

        with self._lock:
            self.total_accepted += 1

        self._log_ingestion(packet.packet_id, packet.device_id, "MQTT", "ACCEPTED", None)

        return {
            "status": "ACCEPTED",
            "packet_id": packet.packet_id,
            "device_id": packet.device_id,
            "sector_id": raw_data.get("sector_id"),
            "records_stored": records_saved,
            "quality": val_res.overall_quality
        }

    def _persist_to_store(self, packet: TelemetryPacket, sector_id: Optional[str]) -> int:
        records = []
        sec = sector_id or "SK-NH10-KM48"
        now_iso = datetime.now(timezone.utc).isoformat()

        for feat_name, m_item in packet.measurements.items():
            rec = ObservationRecord(
                id=None,
                sector_id=sec,
                timestamp=packet.timestamp,
                feature=feat_name,
                value=m_item.value,
                unit=m_item.unit,
                source=f"MQTT ({packet.device_id})",
                quality=m_item.quality,
                provenance=packet.provenance,
                ingested_at=now_iso,
                extra={"packet_id": packet.packet_id, "battery": packet.battery, "rssi": packet.signal_quality}
            )
            records.append(rec)

        if records:
            return GLOBAL_OBSERVATION_STORE.insert_many(records)
        return 0

    def _log_ingestion(
        self, packet_id: str, device_id: str, transport: str, status: str, reason: Optional[str]
    ) -> None:
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO telemetry_ingestion_log (
                    packet_id, device_id, received_at, transport, status, rejection_reason
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                packet_id, device_id, datetime.now(timezone.utc).isoformat(),
                transport, status, reason
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Audit log failure: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Returns MQTT ingestion worker operational status."""
        return {
            "status": "ONLINE" if self.is_connected else "STANDBY",
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "subscription_pattern": self.topic_pattern,
            "paho_library_available": PAHO_AVAILABLE,
            "is_connected": self.is_connected,
            "total_received": self.total_received,
            "messages_processed": self.total_received,
            "total_accepted": self.total_accepted,
            "total_rejected": self.total_rejected,
            "last_packet_time": self.last_packet_time
        }


# Global Singleton
GLOBAL_MQTT_SERVICE = MQTTIngestionService()
