# -*- coding: utf-8 -*-
"""
tests/test_edge_packet.py
=========================
Unit tests for Edge Compact Binary Packet Encoding/Decoding (Phase 3.4 Section 4 & 5).
Validates:
  - Binary struct serialization (34 bytes budget)
  - CRC-16-CCITT checksum calculation and verification
  - Version, sequence number, and timestamp round-trip
  - Rejection of malformed, truncated, or corrupted packets
"""

import unittest
from datetime import datetime, timezone
from backend.edge.packet import (
    encode_packet,
    decode_packet,
    EdgePacket,
    PROTOCOL_VERSION,
    PACKET_SIZE_BYTES,
    crc16_ccitt,
    node_id_to_hash16,
)


class TestEdgePacket(unittest.TestCase):

    def setUp(self):
        self.sample_reading = {
            "version": 1,
            "node_id": "SN-NH10-KM48-01",
            "sequence": 1234,
            "timestamp": "2026-09-09T18:30:00+00:00",
            "soil_moisture": 62.3,
            "pore_pressure": 31.2,
            "tilt": 2.45,
            "rainfall": 18.3,
            "battery": 91,
            "temperature": 18.5,
            "humidity": 75,
            "source": "LORA_SENSOR_STATION",
            "provenance": "[LIVE]"
        }
        self.node_hash = node_id_to_hash16(self.sample_reading["node_id"])
        self.lookup = {self.node_hash: self.sample_reading["node_id"]}

    def test_packet_size_budget(self):
        """Packet binary layout must strictly match 34 bytes for LoRa SF7/SF8 airtime efficiency."""
        raw_bytes = encode_packet(self.sample_reading)
        self.assertEqual(len(raw_bytes), PACKET_SIZE_BYTES)
        self.assertEqual(len(raw_bytes), 34)

    def test_encode_decode_roundtrip(self):
        """Encoding and subsequent decoding must preserve geotechnical readings with high precision."""
        raw_bytes = encode_packet(self.sample_reading)
        decoded = decode_packet(raw_bytes, node_id_lookup=self.lookup)

        self.assertEqual(decoded["version"], 1)
        self.assertEqual(decoded["node_id"], "SN-NH10-KM48-01")
        self.assertEqual(decoded["sequence"], 1234)
        self.assertAlmostEqual(decoded["soil_moisture"], 62.3, places=1)
        self.assertAlmostEqual(decoded["pore_pressure"], 31.2, places=1)
        self.assertAlmostEqual(decoded["tilt"], 2.45, places=1)
        self.assertAlmostEqual(decoded["rainfall"], 18.3, places=1)
        self.assertEqual(decoded["battery"], 91)
        self.assertAlmostEqual(decoded["temperature"], 18.5, places=1)
        self.assertEqual(decoded["humidity"], 75)

    def test_crc16_integrity(self):
        """Checksum verification must detect single-bit corruptions."""
        raw_bytes = bytearray(encode_packet(self.sample_reading))
        
        # Corrupt a single telemetry byte (e.g., rainfall byte)
        raw_bytes[20] ^= 0xFF

        with self.assertRaises(ValueError) as ctx:
            decode_packet(bytes(raw_bytes))
        self.assertIn("CRC", str(ctx.exception).upper())

    def test_invalid_version_rejection(self):
        """Packets with unsupported version must be rejected."""
        raw_bytes = bytearray(encode_packet(self.sample_reading))
        raw_bytes[0] = 0x99 # Unsupported version 153
        # Recalculate CRC for the corrupt payload so it fails on version, not CRC
        crc = crc16_ccitt(bytes(raw_bytes[:32]))
        raw_bytes[32] = (crc >> 8) & 0xFF
        raw_bytes[33] = crc & 0xFF

        with self.assertRaises(ValueError) as ctx:
            decode_packet(bytes(raw_bytes))
        self.assertIn("VERSION", str(ctx.exception).upper())

    def test_truncated_packet_rejection(self):
        """Packets shorter than 34 bytes must be rejected."""
        raw_bytes = encode_packet(self.sample_reading)
        truncated = raw_bytes[:20]

        with self.assertRaises(ValueError) as ctx:
            decode_packet(truncated)
        self.assertIn("LENGTH", str(ctx.exception).upper())

    def test_missing_node_id_rejection(self):
        """Packet construction without node_id must be rejected."""
        invalid_reading = dict(self.sample_reading)
        del invalid_reading["node_id"]

        with self.assertRaises(ValueError) as ctx:
            encode_packet(invalid_reading)
        self.assertIn("node_id", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
