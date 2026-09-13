# -*- coding: utf-8 -*-
"""
firmware/packet_codec.py
========================
PARVAT NETRA • In-Situ LoRa Telemetry Binary Frame Codec
--------------------------------------------------------
Implements the 18-byte packed binary Over-The-Air (OTA) telemetry frame for
LoRaWAN IN865 transmissions per docs/PHASE6C_PACKET_SPECIFICATION.md.

Frame Byte Layout (18 Bytes Total, Big-Endian):
  0x00..0x01: uint16_t  device_short_id     (0-65535)
  0x02..0x03: uint16_t  sequence_number     (0-65535)
  0x04..0x07: uint32_t  timestamp_epoch     (Unix UTC seconds)
  0x08..0x09: int16_t   primary_reading     (x10 scaling)
  0x0A..0x0B: int16_t   secondary_reading   (x100 scaling)
  0x0C..0x0D: int16_t   tertiary_reading    (x100 scaling)
  0x0E:       uint8_t   battery_status      (Bits 0-6: %, Bit 7: Tamper)
  0x0F:       int8_t    temperature         (Signed deg C)
  0x10..0x11: uint16_t  crc16_ccitt         (Poly 0x1021, Init 0xFFFF)
"""

from __future__ import annotations

import struct
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

FRAME_LENGTH_BYTES = 18
FRAME_FORMAT_NO_CRC = ">HHIhhhBb"
FRAME_FORMAT_WITH_CRC = ">HHIhhhBbH"

CRC16_CCITT_POLY = 0x1021
CRC16_CCITT_INIT = 0xFFFF


def compute_crc16_ccitt(data: bytes) -> int:
    """
    Computes standard CRC-16-CCITT checksum over input bytes.
    Polynomial: 0x1021, Initial: 0xFFFF, No reflection, Final XOR: 0x0000.
    """
    crc = CRC16_CCITT_INIT
    for byte in data:
        crc ^= (byte << 8) & 0xFFFF
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ CRC16_CCITT_POLY) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


class BinaryPacketCodec:
    """Encodes and decodes 18-byte LoRa telemetry frames."""

    @staticmethod
    def encode(
        device_short_id: int,
        sequence_number: int,
        timestamp_epoch: int,
        primary_val: float,
        secondary_val: float = 0.0,
        tertiary_val: float = 0.0,
        battery_pct: float = 100.0,
        temperature_c: float = 20.0,
        tamper: bool = False
    ) -> bytes:
        """
        Packs telemetry into an 18-byte binary frame with CRC-16-CCITT.
        """
        # Clamp & scale
        dev_id = max(0, min(65535, int(device_short_id)))
        seq = max(0, min(65535, int(sequence_number)))
        ts = max(0, min(0xFFFFFFFF, int(timestamp_epoch)))

        # Primary scaled x10 (e.g. 42.8 kPa -> 428)
        prim = max(-32768, min(32767, int(round(primary_val * 10.0))))
        # Secondary scaled x100 (e.g. 1.25 deg -> 125)
        sec = max(-32768, min(32767, int(round(secondary_val * 100.0))))
        # Tertiary scaled x100
        tert = max(-32768, min(32767, int(round(tertiary_val * 100.0))))

        # Battery 0-100 in bits 0-6, tamper in bit 7
        bat_clamped = max(0, min(100, int(round(battery_pct))))
        bat_status = (bat_clamped & 0x7F) | (0x80 if tamper else 0x00)

        temp_clamped = max(-40, min(87, int(round(temperature_c))))

        # Pack payload without CRC (16 bytes)
        payload_16 = struct.pack(
            FRAME_FORMAT_NO_CRC,
            dev_id,
            seq,
            ts,
            prim,
            sec,
            tert,
            bat_status,
            temp_clamped
        )

        crc = compute_crc16_ccitt(payload_16)
        frame = payload_16 + struct.pack(">H", crc)
        assert len(frame) == FRAME_LENGTH_BYTES
        return frame

    @staticmethod
    def decode(frame: bytes) -> Dict[str, Any]:
        """
        Decodes an 18-byte binary frame, verifying CRC-16-CCITT integrity.
        Raises ValueError if frame length is invalid or CRC mismatch occurs.
        """
        if len(frame) != FRAME_LENGTH_BYTES:
            raise ValueError(
                f"Invalid frame length: expected {FRAME_LENGTH_BYTES} bytes, got {len(frame)}"
            )

        payload_16 = frame[:16]
        received_crc = struct.unpack(">H", frame[16:18])[0]
        calculated_crc = compute_crc16_ccitt(payload_16)

        if received_crc != calculated_crc:
            raise ValueError(
                f"CRC mismatch: expected 0x{calculated_crc:04X}, received 0x{received_crc:04X}"
            )

        dev_id, seq, ts, prim_raw, sec_raw, tert_raw, bat_stat, temp_c = struct.unpack(
            FRAME_FORMAT_NO_CRC,
            payload_16
        )

        bat_pct = float(bat_stat & 0x7F)
        tamper = bool(bat_stat & 0x80)

        primary_val = round(prim_raw / 10.0, 2)
        secondary_val = round(sec_raw / 100.0, 3)
        tertiary_val = round(tert_raw / 100.0, 3)

        ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc)

        return {
            "device_short_id": dev_id,
            "sequence_number": seq,
            "timestamp_epoch": ts,
            "timestamp_iso": ts_dt.isoformat(),
            "primary_reading": primary_val,
            "secondary_reading": secondary_val,
            "tertiary_reading": tertiary_val,
            "battery_pct": bat_pct,
            "tamper_flag": tamper,
            "temperature_c": float(temp_c),
            "crc16_hex": f"0x{received_crc:04X}",
            "crc_valid": True
        }

    @classmethod
    def to_canonical_packet(
        cls,
        frame: bytes,
        device_id_map: Optional[Dict[int, str]] = None,
        sensor_type: str = "piezometer",
        gateway_id: str = "GW-NH10-KM48-01",
        latitude: float = 27.3302,
        longitude: float = 88.6104,
        rssi: float = -75.0,
        provenance: str = "[LIVE]",
        sector_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Converts a raw 18-byte binary frame into the authoritative JSON packet schema
        used by TelemetryContract and ObservationStore.
        """
        decoded = cls.decode(frame)
        short_id = decoded["device_short_id"]

        if device_id_map and short_id in device_id_map:
            device_id = device_id_map[short_id]
        else:
            device_id = f"SN-NODE-{short_id:04d}"

        seq = decoded["sequence_number"]
        ts_iso = decoded["timestamp_iso"]
        packet_id = f"{device_id}_{seq}_{decoded['timestamp_epoch']}"

        # Map channel values by sensor type
        measurements: Dict[str, Any] = {}
        st = sensor_type.lower()

        if st == "piezometer":
            measurements["pore_pressure"] = {
                "value": decoded["primary_reading"],
                "unit": "kPa",
                "quality": "GOOD"
            }
        elif st == "tilt":
            measurements["tilt"] = {
                "value": decoded["primary_reading"],
                "unit": "deg",
                "quality": "GOOD"
            }
            measurements["tilt_x"] = {
                "value": decoded["secondary_reading"],
                "unit": "deg",
                "quality": "GOOD"
            }
            measurements["tilt_y"] = {
                "value": decoded["tertiary_reading"],
                "unit": "deg",
                "quality": "GOOD"
            }
        elif st == "inclinometer":
            measurements["ground_displacement"] = {
                "value": decoded["primary_reading"],
                "unit": "mm",
                "quality": "GOOD"
            }
        elif st == "rain_gauge":
            measurements["rain_1h"] = {
                "value": decoded["primary_reading"],
                "unit": "mm",
                "quality": "GOOD"
            }
        elif st == "soil_moisture":
            measurements["soil_moisture"] = {
                "value": decoded["primary_reading"],
                "unit": "m3/m3",
                "quality": "GOOD"
            }
        else:
            measurements[st] = {
                "value": decoded["primary_reading"],
                "unit": "raw",
                "quality": "GOOD"
            }

        # Include temperature
        measurements["temperature"] = {
            "value": decoded["temperature_c"],
            "unit": "C",
            "quality": "GOOD"
        }

        now_iso = datetime.now(timezone.utc).isoformat()

        return {
            "packet_id": packet_id,
            "device_id": device_id,
            "sensor_id": device_id,
            "gateway_id": gateway_id,
            "sequence_number": seq,
            "timestamp": ts_iso,
            "received_at": now_iso,
            "latitude": latitude,
            "longitude": longitude,
            "battery": decoded["battery_pct"],
            "signal_quality": rssi,
            "firmware_version": "v2.1.0-lora-binary",
            "transport": "LORA",
            "provenance": provenance,
            "checksum": decoded["crc16_hex"],
            "measurements": measurements
        }
