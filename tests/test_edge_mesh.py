# -*- coding: utf-8 -*-
"""
tests/test_edge_mesh.py
=======================
Unit tests for LoRa Wireless Mesh Network Coordinator (Phase 3.4 Section 16 & 17).
Validates:
  - Node registration, role assignment (SENSOR, RELAY), and removal
  - Multi-hop relay forwarding topology (1-hop direct vs 2-hop ridge relay)
  - Duplicate packet detection and dropping
  - Link health evaluation (HEALTHY vs DEGRADED based on RSSI/battery)
  - Network status aggregation
"""

import unittest
from backend.edge.mesh import LoRaMesh


class TestEdgeMesh(unittest.TestCase):

    def setUp(self):
        self.mesh = LoRaMesh(gateway_id="GW-01", frequency_mhz=865.2)

    def test_default_node_topology(self):
        """Default Himalayan network should contain standard sensor and ridge relay nodes."""
        status = self.mesh.get_network_status()
        self.assertGreaterEqual(status["total_nodes_registered"], 5)
        self.assertIn("RN-RIDGE-RELAY-01", self.mesh.relays)

    def test_register_and_remove_node(self):
        """Custom nodes must be registered and removable."""
        node = self.mesh.register_node(
            node_id="SN-CUSTOM-01",
            role="SENSOR",
            location="Teesta KM 45",
            initial_rssi=-74.0,
            initial_battery=95
        )
        self.assertEqual(node["node_id"], "SN-CUSTOM-01")
        self.assertIn("SN-CUSTOM-01", self.mesh.nodes)

        # Remove
        removed = self.mesh.remove_node("SN-CUSTOM-01")
        self.assertTrue(removed)
        self.assertNotIn("SN-CUSTOM-01", self.mesh.nodes)

    def test_packet_ingestion_and_metrics_update(self):
        """Ingesting a packet must update last_seen, sequence, RSSI, and packet count."""
        packet = {
            "node_id": "SN-NH10-KM48-01",
            "sequence": 10,
            "battery": 89
        }
        res = self.mesh.receive_packet(packet, rssi_dbm=-75.0, snr_db=10.2)
        self.assertEqual(res["status"], "INGESTED")
        self.assertEqual(res["node_id"], "SN-NH10-KM48-01")
        self.assertEqual(res["hops"], 1)

        node = self.mesh.nodes["SN-NH10-KM48-01"]
        self.assertEqual(node["last_sequence"], 10)
        self.assertEqual(node["battery_pct"], 89)
        self.assertEqual(node["rssi_dbm"], -75.0)

    def test_duplicate_packet_drop(self):
        """Duplicate packets with identical (node_id, sequence) must be dropped."""
        packet = {
            "node_id": "SN-NH10-KM48-01",
            "sequence": 55
        }
        res1 = self.mesh.receive_packet(packet)
        self.assertEqual(res1["status"], "INGESTED")

        res2 = self.mesh.receive_packet(packet)
        self.assertEqual(res2["status"], "DUPLICATE_DROPPED")
        self.assertGreaterEqual(self.mesh.total_duplicates_dropped, 1)

    def test_multihop_relay_topology(self):
        """Packets from nodes linked via ridge relay must report 2 hops."""
        # SN-DEEP-GORGE-01 is configured in default_network with via_relay="RN-RIDGE-RELAY-01"
        packet = {
            "node_id": "SN-DEEP-GORGE-01",
            "sequence": 1,
            "battery": 80
        }
        res = self.mesh.receive_packet(packet, rssi_dbm=-88.0)
        self.assertEqual(res["status"], "INGESTED")
        self.assertEqual(res["hops"], 2)
        self.assertEqual(res["via_relay"], "RN-RIDGE-RELAY-01")

    def test_degraded_link_health(self):
        """Weak signal (< -105 dBm) or critically low battery must flag DEGRADED health."""
        packet = {
            "node_id": "SN-NH10-KM48-02",
            "sequence": 99,
            "battery": 15 # Critically low battery
        }
        self.mesh.receive_packet(packet, rssi_dbm=-110.0) # Very weak signal
        node = self.mesh.nodes["SN-NH10-KM48-02"]
        self.assertEqual(node["health"], "DEGRADED")


if __name__ == "__main__":
    unittest.main()
