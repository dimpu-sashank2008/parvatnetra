# -*- coding: utf-8 -*-
"""
tests/test_edge_store.py
========================
Unit tests for Edge SQLite Persistent Storage & Sync Queue (Phase 3.4 Section 6 & 7).
Validates:
  - Table initialization (all 5 tables)
  - Sensor reading insertion and querying with filtering
  - Local alert storage, querying, and acknowledgment
  - Raw packet logging (CRC valid and invalid)
  - Offline sync queue buffering, retry tracking, and queue statistics
"""

import unittest
from backend.edge.edge_store import EdgeStore


class TestEdgeStore(unittest.TestCase):

    def setUp(self):
        # Use an isolated in-memory SQLite store for every test
        self.store = EdgeStore(db_path=":memory:")

    def test_table_initialization(self):
        """All 5 mandatory tables must exist upon initialization."""
        tables = [
            "edge_devices",
            "edge_sensor_readings",
            "edge_alerts",
            "edge_packets",
            "edge_sync_queue"
        ]
        with self.store._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            found_tables = {row[0] for row in cursor.fetchall()}

        for tbl in tables:
            self.assertIn(tbl, found_tables, f"Table {tbl} must be present in SQLite store")

    def test_insert_and_query_reading(self):
        """Readings must be inserted and queried with accurate field fidelity."""
        reading = {
            "node_id": "SN-NH10-KM48-01",
            "sequence": 101,
            "soil_moisture": 55.4,
            "pore_pressure": 26.8,
            "tilt": 1.25,
            "rainfall": 12.0,
            "battery": 88,
            "temperature": 19.2,
            "humidity": 82,
            "source": "LORA_TEST",
            "provenance": "[LIVE]"
        }
        rec_id = self.store.insert_reading(reading, buffer_for_cloud=True)
        self.assertGreater(rec_id, 0)

        results = self.store.query_readings(node_id="SN-NH10-KM48-01", limit=10)
        self.assertEqual(len(results), 1)
        r = results[0]
        self.assertEqual(r["node_id"], "SN-NH10-KM48-01")
        self.assertAlmostEqual(r["soil_moisture"], 55.4, places=1)
        self.assertAlmostEqual(r["pore_pressure"], 26.8, places=1)
        self.assertAlmostEqual(r["tilt"], 1.25, places=2)
        self.assertEqual(r["battery"], 88)

    def test_device_registration_and_last_seen(self):
        """Registered edge devices must track last_seen and battery status."""
        self.store.register_device("SN-NH10-01", role="SENSOR", location="Ridge A")
        self.store.update_device_last_seen("SN-NH10-01", battery=94, rssi=-79.0)

        with self.store._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT node_id, role, battery, rssi FROM edge_devices WHERE node_id=?", ("SN-NH10-01",))
            row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["node_id"], "SN-NH10-01")
        self.assertEqual(row["role"], "SENSOR")
        self.assertEqual(row["battery"], 94)
        self.assertEqual(row["rssi"], -79.0)

    def test_alert_insert_and_acknowledge(self):
        """Local alerts must be stored and acknowledged."""
        alert_payload = {
            "alert_id": "ALT-TEST-001",
            "severity": "CRITICAL",
            "trigger_source": "TEST_HARNESS",
            "node_id": "SN-NH10-01",
            "gateway_id": "GW-01",
            "reason": "Tilt exceeds critical 2.0 deg threshold",
            "siren_activated": 0,
            "dry_run": 1,
            "acknowledged": 0
        }
        self.store.insert_alert(alert_payload, buffer_for_cloud=True)

        alerts = self.store.query_alerts(limit=5)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["alert_id"], "ALT-TEST-001")
        self.assertEqual(alerts[0]["acknowledged"], 0)

        # Acknowledge
        ack_res = self.store.acknowledge_alert("ALT-TEST-001")
        self.assertTrue(ack_res)

        alerts_after = self.store.query_alerts(limit=5)
        self.assertEqual(alerts_after[0]["acknowledged"], 1)

    def test_offline_sync_queue_buffering_and_stats(self):
        """Items flagged for cloud must populate edge_sync_queue and report stats."""
        # Insert 3 readings with cloud buffering
        for seq in (1, 2, 3):
            self.store.insert_reading({
                "node_id": "SN-01",
                "sequence": seq,
                "soil_moisture": 30.0 + seq,
                "provenance": "[LIVE]"
            }, buffer_for_cloud=True)

        stats = self.store.get_queue_stats()
        self.assertEqual(stats["buffered_count"], 3)
        self.assertEqual(stats["synced_count"], 0)

        # Retrieve pending
        pending = self.store.get_pending_sync_items(limit=2)
        self.assertEqual(len(pending), 2)

        # Mark first as synced
        self.store.mark_synced([pending[0]["queue_id"]])
        stats_updated = self.store.get_queue_stats()
        self.assertEqual(stats_updated["buffered_count"], 2)
        self.assertEqual(stats_updated["synced_count"], 1)

    def test_raw_packet_logging(self):
        """Raw binary frames must be logged with CRC validity status."""
        raw_frame = b"\x01\x00\x12\x34\x00\x00"
        self.store.log_raw_packet(raw_frame, node_id="SN-01", sequence=5, rssi=-81.5, crc_valid=True)
        self.store.log_raw_packet(b"\xFF\xFF", crc_valid=False)

        with self.store._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM edge_packets WHERE crc_valid=1")
            valid_cnt = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM edge_packets WHERE crc_valid=0")
            invalid_cnt = cursor.fetchone()[0]

        self.assertEqual(valid_cnt, 1)
        self.assertEqual(invalid_cnt, 1)


if __name__ == "__main__":
    unittest.main()
