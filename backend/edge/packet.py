# -*- coding: utf-8 -*-
"""
backend/edge/packet.py
======================
PARVAT NETRA • Local Edge & LoRa Mesh Packet Serialization Engine
-----------------------------------------------------------------
Implements Section 4 & 5: Compact versioned payload serialization.
Provides:
  1. Logical JSON representation
  2. Ultra-compact binary encoding (< 36 bytes) suitable for LoRa SF7/SF8 airtime
  3. CRC-16-CCITT integrity verification and malformed packet rejection

Packet Binary Layout (34 Bytes Total):
  [0]    Version (uint8)
  [1]    Flags (uint8: bit 0=DEMO, bit 1=RELAY_HOP, bit 2=ALERT_TRIGGERED)
  [2:4]  Node Identifier Hash (uint16 big-endian)
  [4:8]  Monotonic Sequence Number (uint32 big-endian)
  [8:12] Timestamp Epoch Seconds (uint32 big-endian)
  [12:16] Soil Moisture VWC % (float32 IEEE 754)
  [16:20] Pore-water Pressure kPa (float32 IEEE 754)
  [20:24] Borehole Tilt Degrees (float32 IEEE 754)
  [24:28] Rainfall Intensity mm/h (float32 IEEE 754)
  [28]   Battery Percentage (uint8: 0 - 100)
  [29:31] Temperature C * 10 (int16 big-endian)
  [31]   Relative Humidity % (uint8: 0 - 100)
  [32:34] CRC-16-CCITT Checksum (uint16 big-endian over bytes [0:32])

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import struct
import time
import math
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional

PROTOCOL_VERSION = 1
PACKET_BINARY_LENGTH = 34
PACKET_SIZE_BYTES = PACKET_BINARY_LENGTH
PACKET_STRUCT_FORMAT = ">BBHIIffffBhB"
PACKET_MAGIC = 0x50

# Bit flags
FLAG_DEMO = 0x01
FLAG_RELAY_HOP = 0x02
FLAG_ALERT_TRIGGERED = 0x04


def crc16_ccitt(data: bytes, poly: int = 0x1021, init: int = 0xFFFF) -> int:
    """
    Computes CRC-16-CCITT checksum over byte array.
    Standard high-reliability CRC used in aerospace and industrial telemetry.
    """
    crc = init
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def node_id_to_hash16(node_id: str) -> int:
    """Converts string node_id (e.g. 'SN-NH10-01') deterministically to 16-bit uint."""
    return crc16_ccitt(node_id.encode('utf-8'))


class EdgePacket:
    """
    Normalized Edge Packet representation supporting both JSON and binary serialization.
    """

    def __init__(
        self,
        node_id: str,
        sequence: int,
        timestamp: Optional[str] = None,
        soil_moisture: float = 0.0,
        pore_pressure: float = 0.0,
        tilt: float = 0.0,
        rainfall: float = 0.0,
        battery: int = 100,
        temperature: float = 20.0,
        humidity: int = 70,
        is_demo: bool = False,
        is_relay: bool = False,
        is_alert: bool = False,
        version: int = PROTOCOL_VERSION,
        source: str = "LORA_RF",
        provenance: str = "[LIVE]"
    ) -> None:
        self.version = version
        self.node_id = str(node_id)
        self.sequence = int(sequence)
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.soil_moisture = float(soil_moisture)
        self.pore_pressure = float(pore_pressure)
        self.tilt = float(tilt)
        self.rainfall = float(rainfall)
        self.battery = max(0, min(100, int(battery)))
        self.temperature = float(temperature)
        self.humidity = max(0, min(100, int(humidity)))
        self.is_demo = bool(is_demo)
        self.is_relay = bool(is_relay)
        self.is_alert = bool(is_alert)
        self.source = source
        self.provenance = "[DEMO]" if self.is_demo else provenance

    def to_dict(self) -> Dict[str, Any]:
        """Returns logical JSON dictionary."""
        return {
            "version": self.version,
            "node_id": self.node_id,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "soil_moisture": round(self.soil_moisture, 2),
            "pore_pressure": round(self.pore_pressure, 2),
            "tilt": round(self.tilt, 2),
            "rainfall": round(self.rainfall, 2),
            "battery": self.battery,
            "temperature": round(self.temperature, 1),
            "humidity": self.humidity,
            "is_demo": self.is_demo,
            "is_relay": self.is_relay,
            "is_alert": self.is_alert,
            "source": self.source,
            "provenance": self.provenance
        }

    def encode_binary(self) -> bytes:
        """
        Serializes packet into 34-byte compact binary struct.
        Format:
          >BBHIdffffBhB H (Big Endian)
        """
        flags = 0
        if self.is_demo:
            flags |= FLAG_DEMO
        if self.is_relay:
            flags |= FLAG_RELAY_HOP
        if self.is_alert:
            flags |= FLAG_ALERT_TRIGGERED

        node_hash = node_id_to_hash16(self.node_id)

        # Parse timestamp to epoch seconds
        try:
            if isinstance(self.timestamp, str):
                dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
                epoch_sec = int(dt.timestamp())
            else:
                epoch_sec = int(time.time())
        except Exception:
            epoch_sec = int(time.time())

        # Scale temperature by 10 for int16
        temp_scaled = max(-32768, min(32767, int(self.temperature * 10)))

        # Pack header + payload (32 bytes)
        raw_body = struct.pack(
            ">BBHIIffffBhB",
            self.version,
            flags,
            node_hash,
            self.sequence,
            epoch_sec,
            self.soil_moisture,
            self.pore_pressure,
            self.tilt,
            self.rainfall,
            self.battery,
            temp_scaled,
            self.humidity
        )

        # Compute CRC-16 over the 32 bytes
        chk = crc16_ccitt(raw_body)
        return raw_body + struct.pack(">H", chk)

    @classmethod
    def from_binary(cls, raw: bytes, node_id_lookup: Optional[Dict[int, str]] = None) -> EdgePacket:
        """
        Deserializes compact 34-byte binary payload into EdgePacket.
        Raises ValueError if packet is truncated, corrupted, or version mismatch.
        """
        if len(raw) != PACKET_BINARY_LENGTH:
            raise ValueError(f"Invalid packet length: expected {PACKET_BINARY_LENGTH} bytes, got {len(raw)}")

        raw_body = raw[:32]
        expected_crc = struct.unpack(">H", raw[32:34])[0]
        actual_crc = crc16_ccitt(raw_body)

        if expected_crc != actual_crc:
            raise ValueError(f"CRC-16 mismatch: expected 0x{expected_crc:04X}, computed 0x{actual_crc:04X}")

        (
            version,
            flags,
            node_hash,
            sequence,
            epoch_sec,
            soil_moisture,
            pore_pressure,
            tilt,
            rainfall,
            battery,
            temp_scaled,
            humidity
        ) = struct.unpack(">BBHIIffffBhB", raw_body)

        if version != PROTOCOL_VERSION:
            raise ValueError(f"Unsupported packet protocol version: {version} (expected {PROTOCOL_VERSION})")

        is_demo = bool(flags & FLAG_DEMO)
        is_relay = bool(flags & FLAG_RELAY_HOP)
        is_alert = bool(flags & FLAG_ALERT_TRIGGERED)

        node_id = f"NODE-0x{node_hash:04X}"
        if node_id_lookup and node_hash in node_id_lookup:
            node_id = node_id_lookup[node_hash]

        ts = datetime.fromtimestamp(epoch_sec, tz=timezone.utc).isoformat()

        return cls(
            node_id=node_id,
            sequence=sequence,
            timestamp=ts,
            soil_moisture=soil_moisture,
            pore_pressure=pore_pressure,
            tilt=tilt,
            rainfall=rainfall,
            battery=battery,
            temperature=temp_scaled / 10.0,
            humidity=humidity,
            is_demo=is_demo,
            is_relay=is_relay,
            is_alert=is_alert,
            version=version,
            source="LORA_BINARY",
            provenance="[DEMO]" if is_demo else "[LIVE]"
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EdgePacket:
        """Constructs EdgePacket from JSON dictionary."""
        node_id = data.get("node_id")
        if not node_id:
            raise ValueError("Missing mandatory field 'node_id' in packet payload")

        return cls(
            node_id=str(node_id),
            sequence=int(data.get("sequence", 0)),
            timestamp=data.get("timestamp"),
            soil_moisture=float(data.get("soil_moisture", 0.0)),
            pore_pressure=float(data.get("pore_pressure", 0.0)),
            tilt=float(data.get("tilt", 0.0)),
            rainfall=float(data.get("rainfall", 0.0)),
            battery=int(data.get("battery", 100)),
            temperature=float(data.get("temperature", 20.0)),
            humidity=int(data.get("humidity", 70)),
            is_demo=bool(data.get("is_demo", False) or "[DEMO]" in str(data.get("provenance", ""))),
            is_relay=bool(data.get("is_relay", False)),
            is_alert=bool(data.get("is_alert", False)),
            version=int(data.get("version", PROTOCOL_VERSION)),
            source=data.get("source", "JSON_API"),
            provenance=data.get("provenance", "[LIVE]")
        )


def encode_packet(data: Dict[str, Any]) -> bytes:
    """Convenience functional encoder conforming to Section 5."""
    packet = EdgePacket.from_dict(data)
    return packet.encode_binary()


def decode_packet(raw: bytes, node_id_lookup: Optional[Dict[int, str]] = None) -> Dict[str, Any]:
    """Convenience functional decoder conforming to Section 5."""
    packet = EdgePacket.from_binary(raw, node_id_lookup=node_id_lookup)
    return packet.to_dict()
