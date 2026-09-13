# -*- coding: utf-8 -*-
"""
backend/edge/gateway.py
=======================
PARVAT NETRA • Integrated Edge Gateway Coordinator
--------------------------------------------------
Implements Section 2: Central Edge Gateway integrating:
  - LoRa Mesh Ingestion
  - Binary Packet Decoding & CRC Verification
  - Local SQLite Store (Offline Buffering)
  - Edge Risk Evaluator (Deterministic Safety State)
  - Siren Controller (Acoustic Evacuation Relay)
  - BLE Alert Bridge (Local Device Pairing)
  - Edge Sync (Automatic Central Cloud Handoff)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.edge.packet import decode_packet, EdgePacket
from backend.edge.edge_store import EdgeStore
from backend.edge.risk_evaluator import EdgeRiskEvaluator
from backend.edge.siren_controller import SirenController
from backend.edge.ble_bridge import BLEAlertBridge
from backend.edge.mesh import LoRaMesh
from backend.edge.sync import EdgeSync

logger = logging.getLogger("EDGE_GATEWAY_CORE")


class EdgeGateway:
    """Autonomous regional edge processor running at chokepoints along strategic corridors."""

    def __init__(
        self,
        gateway_id: str = "GW-01",
        location: str = "Singtam Staging Depo (NH-10 Corridor)",
        db_path: Optional[str] = None
    ) -> None:
        self.gateway_id = gateway_id
        self.location = location

        # Initialize modular subsystems
        self.store = EdgeStore(db_path=db_path)
        self.evaluator = EdgeRiskEvaluator()
        self.siren = SirenController(gateway_id=self.gateway_id, store=self.store)
        self.ble = BLEAlertBridge(gateway_id=self.gateway_id)
        self.mesh = LoRaMesh(gateway_id=self.gateway_id)
        self.sync = EdgeSync(store=self.store)

        self.last_evaluation_state = "SAFE"
        self.total_processed_packets = 0

    def process_raw_packet(self, raw_bytes: bytes, rssi_dbm: float = -80.0, snr_db: float = 9.0) -> Dict[str, Any]:
        """
        End-to-End Pipeline: Ingests raw radio bytes, validates CRC-16,
        decodes packet, records telemetry, evaluates safety, triggers sirens/BLE,
        and manages cloud sync queue.
        """
        self.total_processed_packets += 1

        # 1. Decode binary struct
        try:
            from backend.edge.packet import node_id_to_hash16
            lookup = {node_id_to_hash16(nid): nid for nid in self.mesh.nodes}
            reading = decode_packet(raw_bytes, node_id_lookup=lookup)
            crc_valid = True
        except Exception as e:
            self.store.log_raw_packet(raw_bytes, rssi=rssi_dbm, crc_valid=False)
            return {
                "status": "REJECTED_MALFORMED",
                "error": str(e),
                "gateway_id": self.gateway_id,
                "bytes_received": len(raw_bytes)
            }

        node_id = reading["node_id"]
        seq = reading.get("sequence", 0)

        # 2. Log raw packet buffer
        self.store.log_raw_packet(raw_bytes, node_id=node_id, sequence=seq, rssi=rssi_dbm, crc_valid=True)

        # 3. LoRa Mesh Ingestion & Deduplication
        mesh_result = self.mesh.receive_packet(reading, rssi_dbm=rssi_dbm, snr_db=snr_db)
        if mesh_result.get("status") == "DUPLICATE_DROPPED":
            return {
                "status": "DUPLICATE_DROPPED",
                "node_id": node_id,
                "sequence": seq
            }

        # 4. Pipeline processing of decoded reading
        return self._process_decoded_reading(reading, mesh_result=mesh_result)

    def process_json_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Processes JSON telemetry (from HTTP injection, demo, or local serial)."""
        self.total_processed_packets += 1
        mesh_result = self.mesh.receive_packet(reading)
        return self._process_decoded_reading(reading, mesh_result=mesh_result)

    def _process_decoded_reading(self, reading: Dict[str, Any], mesh_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Internal processing pipeline after packet decoding."""
        node_id = str(reading.get("node_id", "UNKNOWN"))

        # 1. Local Safety Risk Evaluation
        eval_result = self.evaluator.evaluate_reading(reading)
        safety_state = eval_result["edge_safety_state"]
        self.last_evaluation_state = safety_state

        # 2. Local SQLite Persistence (Buffers for cloud automatically)
        reading_id = self.store.insert_reading(reading, buffer_for_cloud=True)

        alert_dispatched = None
        siren_event = None

        # 3. Local Alert Actuation (WARNING or CRITICAL)
        if safety_state in ("WARNING", "CRITICAL"):
            alert_id = f"ALT-EDGE-{int(datetime.now().timestamp() * 1000)}"
            reason = f"Local threshold breach: {', '.join([x['sensor'] for x in eval_result['exceeded_indicators']])}"

            # Activate siren according to configured policy (dry_run by default)
            siren_event = self.siren.activate(level=safety_state, alert_id=alert_id, reason=reason)

            # Transmit alert over local BLE if device is paired
            if self.ble.paired_device:
                alert_dispatched = self.ble.send_alert(alert_id, safety_state)

            # Record alert in store
            self.store.insert_alert({
                "alert_id": alert_id,
                "severity": safety_state,
                "trigger_source": "EDGE_RISK_EVALUATOR",
                "node_id": node_id,
                "gateway_id": self.gateway_id,
                "reason": reason,
                "siren_activated": 1 if (siren_event and not siren_event.get("dry_run")) else 0,
                "dry_run": self.siren.dry_run,
                "acknowledged": 0
            }, buffer_for_cloud=True)

        # 4. Asynchronous Cloud Synchronization Handoff
        sync_result = self.sync.flush_sync_queue(batch_size=20)

        return {
            "status": "PROCESSED",
            "gateway_id": self.gateway_id,
            "node_id": node_id,
            "reading_id": reading_id,
            "edge_safety_state": safety_state,
            "anomaly_score": eval_result["anomaly_score"],
            "exceeded_indicators": eval_result["exceeded_indicators"],
            "mesh_status": mesh_result,
            "siren_event": siren_event,
            "ble_alert": alert_dispatched,
            "cloud_sync": sync_result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_gateway_status(self) -> Dict[str, Any]:
        """Returns comprehensive edge network health and telemetry status (Section 18)."""
        queue_stats = self.store.get_queue_stats()
        mesh_status = self.mesh.get_network_status()

        return {
            "gateway_id": self.gateway_id,
            "location": self.location,
            "connectivity_mode": "CLOUD_CONNECTED" if self.sync.is_cloud_connected else "EDGE_OFFLINE_AUTONOMOUS",
            "is_cloud_connected": self.sync.is_cloud_connected,
            "last_evaluation_state": self.last_evaluation_state,
            "total_processed_packets": self.total_processed_packets,
            "buffered_readings_count": queue_stats["buffered_count"],
            "synced_readings_count": queue_stats["synced_count"],
            "failed_sync_count": queue_stats["failed_count"],
            "last_cloud_sync": queue_stats["last_cloud_sync"],
            "mesh": mesh_status,
            "siren": self.siren.status(),
            "ble": self.ble.status(),
            "active_nodes_count": mesh_status["active_nodes_count"],
            "total_nodes_count": mesh_status["total_nodes_registered"],
            "provenance": "[LIVE]" if not self.mesh.nodes.get("SN-NH10-KM48-01", {}).get("is_demo") else "[DEMO]",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
