# -*- coding: utf-8 -*-
"""
backend/edge/mesh.py
====================
PARVAT NETRA • Himalayan LoRa Wireless Mesh Network Coordinator
--------------------------------------------------------------
Implements Section 16 & 17: LoRa sub-GHz ad-hoc telemetry mesh.
Supports:
  1. Direct Sensor-to-Gateway links (Star-of-Stars).
  2. Multi-Hop Relay Links (Sensor -> Ridge Relay -> Gateway) for deep gorge penetration.
  3. Dynamic health metrics: RSSI (dBm), SNR (dB), battery levels, and packet deduplication.

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger("LORA_MESH_COORDINATOR")


class LoRaMesh:
    """Manages regional LoRa telemetry topology, packet ingestion, and node health."""

    def __init__(self, gateway_id: str = "GW-01", frequency_mhz: float = 865.2) -> None:
        self.gateway_id = gateway_id
        self.frequency_mhz = frequency_mhz
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.relays: Set[str] = set()
        self._processed_packets: Set[str] = set() # (node_id:sequence) deduplication
        self.total_packets_received = 0
        self.total_packets_forwarded = 0
        self.total_duplicates_dropped = 0
        self.recent_packets: List[Dict[str, Any]] = []

        # Register standard demonstration nodes (NH-10 / Teesta River Gorge)
        self._init_default_nodes()

    def _init_default_nodes(self) -> None:
        default_network = [
            {"node_id": "SN-NH10-KM48-01", "role": "SENSOR", "location": "Likhu Veer Cliff", "rssi": -78.4, "battery": 94},
            {"node_id": "SN-NH10-KM48-02", "role": "SENSOR", "location": "29th Mile Road Verge", "rssi": -82.1, "battery": 88},
            {"node_id": "SN-NH10-KM49-01", "role": "SENSOR", "location": "Teesta Scour Reach", "rssi": -89.5, "battery": 76},
            {"node_id": "RN-RIDGE-RELAY-01", "role": "RELAY", "location": "Kalimpong Ridge Mast", "rssi": -65.2, "battery": 99},
            {"node_id": "SN-DEEP-GORGE-01", "role": "SENSOR", "location": "Dikchu Toe Slopes", "rssi": -92.0, "battery": 81, "via_relay": "RN-RIDGE-RELAY-01"}
        ]
        for n in default_network:
            self.register_node(
                node_id=n["node_id"],
                role=n["role"],
                location=n.get("location", "NER Corridor"),
                initial_rssi=n.get("rssi", -80.0),
                initial_battery=n.get("battery", 100),
                via_relay=n.get("via_relay")
            )

    def register_node(
        self,
        node_id: str,
        role: str = "SENSOR",
        location: str = "Monitored Slope",
        initial_rssi: float = -80.0,
        initial_battery: int = 100,
        via_relay: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a sensor or repeater node in the local mesh topology."""
        now_iso = datetime.now(timezone.utc).isoformat()
        node_info = {
            "node_id": node_id,
            "role": role.upper(),
            "location": location,
            "gateway_id": self.gateway_id,
            "registered_at": now_iso,
            "last_seen": now_iso,
            "last_seen_epoch": time.time(),
            "last_sequence": 0,
            "rssi_dbm": initial_rssi,
            "snr_db": 9.5,
            "battery_pct": initial_battery,
            "packet_count": 0,
            "health": "HEALTHY",
            "via_relay": via_relay,
            "hops": 2 if via_relay else 1
        }
        self.nodes[node_id] = node_info
        if role.upper() == "RELAY":
            self.relays.add(node_id)

        logger.info(f"[LoRaMesh] Node registered: {node_id} (role={role}, hops={node_info['hops']}).")
        return node_info

    def remove_node(self, node_id: str) -> bool:
        """Removes a node from active topology."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.relays.discard(node_id)
            return True
        return False

    def receive_packet(
        self,
        packet_data: Dict[str, Any],
        rssi_dbm: float = -80.0,
        snr_db: float = 9.0
    ) -> Dict[str, Any]:
        """
        Ingests a received LoRa packet.
        Applies sequence deduplication, hop tracking, and updates node metrics.
        """
        self.total_packets_received += 1
        node_id = str(packet_data.get("node_id", "UNKNOWN"))
        seq = int(packet_data.get("sequence", 0))

        # Replay / Duplicate filtering
        token = f"{node_id}:{seq}"
        if token in self._processed_packets:
            self.total_duplicates_dropped += 1
            logger.info(f"[LoRaMesh] Dropped duplicate packet {token}.")
            return {
                "status": "DUPLICATE_DROPPED",
                "node_id": node_id,
                "sequence": seq
            }
        self._processed_packets.add(token)

        # Register auto-discovered node if unseen
        if node_id not in self.nodes:
            self.register_node(node_id, role="SENSOR", initial_rssi=rssi_dbm)

        # Update node telemetry metrics
        node = self.nodes[node_id]
        now_iso = datetime.now(timezone.utc).isoformat()
        node["last_seen"] = now_iso
        node["last_seen_epoch"] = time.time()
        node["last_sequence"] = max(node["last_sequence"], seq)
        node["rssi_dbm"] = rssi_dbm
        node["snr_db"] = snr_db
        if "battery" in packet_data:
            node["battery_pct"] = int(packet_data["battery"])
        node["packet_count"] += 1

        # Evaluate link health
        if rssi_dbm < -105.0 or node["battery_pct"] < 20:
            node["health"] = "DEGRADED"
        else:
            node["health"] = "HEALTHY"

        is_relay = packet_data.get("is_relay", False) or (node.get("via_relay") is not None)

        # Synthetic 18-byte hex payload representation for diagnostic inspector
        payload_hex = f"0x{abs(int(rssi_dbm)) & 0xFF:02X}{seq & 0xFFFF:04X}{int(packet_data.get('tilt', 0.5) * 100) & 0xFFFF:04X}{int(packet_data.get('soil_moisture', 30.0) * 10) & 0xFFFF:04X}"

        record = {
            "status": "INGESTED",
            "node_id": node_id,
            "sequence": seq,
            "gateway_id": self.gateway_id,
            "hops": 2 if is_relay else 1,
            "via_relay": node.get("via_relay"),
            "health": node["health"],
            "rssi_dbm": rssi_dbm,
            "snr_db": snr_db,
            "battery_pct": node.get("battery_pct", 100),
            "payload_hex": payload_hex,
            "location": node.get("location", "NER Slope"),
            "provenance": "[SIMULATED / MESH]",
            "timestamp": now_iso
        }
        self.recent_packets.insert(0, record)
        if len(self.recent_packets) > 50:
            self.recent_packets.pop()

        return record

    def get_recent_packets(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Returns the most recent received LoRa mesh packets."""
        return self.recent_packets[:limit]

    def simulate_burst(self, count: int = 3) -> List[Dict[str, Any]]:
        """Simulates an emergency sub-GHz LoRa transmission burst from gorge nodes."""
        burst_nodes = [
            ("SN-NH10-KM48-01", "Likhu Veer Cliff", -78.4, 9.2, 1),
            ("RN-RIDGE-RELAY-01", "Kalimpong Ridge Mast", -64.5, 11.4, 1),
            ("SN-DEEP-GORGE-01", "Dikchu Toe Slopes", -91.2, 6.8, 2)
        ]
        results = []
        for i in range(min(count, len(burst_nodes))):
            nid, loc, rssi, snr, hops = burst_nodes[i]
            node = self.nodes.get(nid, {})
            next_seq = node.get("last_sequence", 0) + 1
            pkt = {
                "node_id": nid,
                "sequence": next_seq,
                "tilt": 1.2 + (i * 0.4),
                "soil_moisture": 42.0 + (i * 5.0),
                "pore_pressure": 18.5 + (i * 6.0),
                "rainfall": 45.0,
                "battery": max(40, node.get("battery_pct", 90) - 1),
                "is_relay": hops > 1
            }
            res = self.receive_packet(pkt, rssi_dbm=rssi, snr_db=snr)
            results.append(res)
        return results

    def forward_packet(self, packet_data: Dict[str, Any], relay_id: str) -> Dict[str, Any]:
        """Simulates multi-hop forwarding across a mountain ridge relay node."""
        if relay_id not in self.relays and relay_id not in self.nodes:
            self.register_node(relay_id, role="RELAY")

        self.total_packets_forwarded += 1
        enriched = dict(packet_data)
        enriched["is_relay"] = True
        enriched["relay_node"] = relay_id
        enriched["ttl_remaining"] = max(0, int(packet_data.get("ttl", 3)) - 1)

        logger.info(f"[LoRaMesh] Forwarded packet {packet_data.get('sequence')} via relay {relay_id}.")
        return enriched

    def ack_packet(self, node_id: str, sequence: int) -> Dict[str, Any]:
        """Generates downlink acknowledgement for confirmed transmissions."""
        return {
            "gateway_id": self.gateway_id,
            "target_node": node_id,
            "ack_sequence": sequence,
            "status": "ACK_QUEUED_DOWNLINK",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_network_status(self) -> Dict[str, Any]:
        """Returns topology, active node counts, and RF metrics."""
        now = time.time()
        active_count = 0
        healthy_count = 0

        # Node activity timeout (considered offline if silent > 300 seconds)
        for n in self.nodes.values():
            silent_sec = now - n["last_seen_epoch"]
            if silent_sec < 300:
                active_count += 1
                if n["health"] == "HEALTHY":
                    healthy_count += 1
            else:
                n["health"] = "OFFLINE"

        return {
            "gateway_id": self.gateway_id,
            "frequency_mhz": self.frequency_mhz,
            "modulation": "LoRa CSS (Spreading Factor: SF7, Bandwidth: 125 kHz, CR: 4/5)",
            "total_nodes_registered": len(self.nodes),
            "active_nodes_count": active_count,
            "healthy_nodes_count": healthy_count,
            "relay_count": len(self.relays),
            "total_packets_received": self.total_packets_received,
            "total_packets_forwarded": self.total_packets_forwarded,
            "total_duplicates_dropped": self.total_duplicates_dropped,
            "nodes": list(self.nodes.values()),
            "provenance": "[SIMULATED] Local LoRa Mesh Ad-Hoc RF Subsystem"
        }
