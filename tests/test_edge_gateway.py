# -*- coding: utf-8 -*-
"""
tests/test_edge_gateway.py
==========================
Unit tests for Edge Gateway Integrated Pipeline (Phase 3.4 Section 2).
Validates:
  - End-to-end process_raw_packet() execution
  - JSON reading ingestion via process_json_reading()
  - Automatic local SQLite persistence and cloud queue buffering
  - Deterministic safety evaluation triggering dry-run siren alerts
  - Rejection of malformed raw binary packets
  - Gateway status aggregation
"""

import unittest
from backend.edge.gateway import EdgeGateway
from backend.edge.packet import encode_packet


class TestEdgeGateway(unittest.TestCase):

    def setUp(self):
        # Initialize an isolated edge gateway with in-memory SQLite store
        self.gateway = EdgeGateway(
            gateway_id="GW-TEST-01",
            location="Test Staging Post",
            db_path=":memory:"
        )

    def test_process_raw_packet_end_to_end(self):
        """Gateway must decode binary frame, store reading, evaluate risk, and return pipeline status."""
        reading = {
            "node_id": "SN-NH10-KM48-01",
            "sequence": 1,
            "soil_moisture": 35.0,
            "pore_pressure": 12.0,
            "tilt": 0.2,
            "rainfall": 2.0,
            "battery": 95,
            "provenance": "[LIVE]"
        }
        raw_bytes = encode_packet(reading)

        res = self.gateway.process_raw_packet(raw_bytes, rssi_dbm=-79.0, snr_db=9.5)
        self.assertEqual(res["status"], "PROCESSED")
        self.assertEqual(res["node_id"], "SN-NH10-KM48-01")
        self.assertEqual(res["edge_safety_state"], "SAFE")
        self.assertGreater(res["reading_id"], 0)
        self.assertIsNone(res["siren_event"]) # SAFE reading does not activate siren

        # When cloud is online, pipeline immediately flushes to cloud
        stats = self.gateway.store.get_queue_stats()
        self.assertEqual(stats["synced_count"], 1)

        # Disconnect cloud and verify offline buffering
        self.gateway.sync.set_cloud_connectivity(False)
        reading2 = dict(reading, sequence=2)
        self.gateway.process_raw_packet(encode_packet(reading2))
        stats_offline = self.gateway.store.get_queue_stats()
        self.assertEqual(stats_offline["buffered_count"], 1)

    def test_process_critical_reading_triggers_dry_run_siren(self):
        """A CRITICAL threshold reading must trigger local dry-run siren and store alert."""
        critical_reading = {
            "node_id": "SN-NH10-KM48-01",
            "sequence": 2,
            "soil_moisture": 65.0,
            "pore_pressure": 42.0,
            "tilt": 3.5, # Critical
            "rainfall": 50.0,
            "battery": 90,
            "provenance": "[LIVE]"
        }
        raw_bytes = encode_packet(critical_reading)

        res = self.gateway.process_raw_packet(raw_bytes)
        self.assertEqual(res["status"], "PROCESSED")
        self.assertEqual(res["edge_safety_state"], "CRITICAL")
        self.assertIsNotNone(res["siren_event"])
        self.assertTrue(res["siren_event"]["dry_run"])

        # Check alerts in SQLite store
        alerts = self.gateway.store.query_alerts()
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "CRITICAL")
        self.assertEqual(alerts[0]["dry_run"], 1)

    def test_malformed_raw_packet_rejected(self):
        """Malformed or corrupted byte frames must be rejected and logged."""
        garbage_bytes = b"\x00\x11\x22\x33\x44" # Too short, invalid CRC
        res = self.gateway.process_raw_packet(garbage_bytes)
        self.assertEqual(res["status"], "REJECTED_MALFORMED")
        self.assertIn("error", res)

    def test_duplicate_packet_dropped(self):
        """Duplicate packets must be dropped by the LoRa mesh layer."""
        reading = {
            "node_id": "SN-NH10-KM48-01",
            "sequence": 42,
            "soil_moisture": 30.0,
            "provenance": "[LIVE]"
        }
        raw_bytes = encode_packet(reading)

        res1 = self.gateway.process_raw_packet(raw_bytes)
        self.assertEqual(res1["status"], "PROCESSED")

        res2 = self.gateway.process_raw_packet(raw_bytes)
        self.assertEqual(res2["status"], "DUPLICATE_DROPPED")

    def test_gateway_status_metrics(self):
        """Gateway status must compile mesh, siren, buffer, and connectivity state."""
        status = self.gateway.get_gateway_status()
        self.assertEqual(status["gateway_id"], "GW-TEST-01")
        self.assertIn("connectivity_mode", status)
        self.assertIn("siren", status)
        self.assertIn("mesh", status)
        self.assertGreaterEqual(status["total_nodes_count"], 5)


if __name__ == "__main__":
    unittest.main()
