# -*- coding: utf-8 -*-
"""
tests/test_hardware_packet.py
=============================
Phase 6C Test Suite: 18-Byte Compact Binary Packet & Codec Verification
"""

import sys
import os
import struct
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firmware.packet_codec import (
    BinaryPacketCodec,
    compute_crc16_ccitt,
    FRAME_LENGTH_BYTES
)


class TestHardwarePacketCodec:

    def test_frame_length_is_strictly_18_bytes(self):
        assert FRAME_LENGTH_BYTES == 18
        frame = BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=1,
            timestamp_epoch=1741618200,
            primary_val=42.8,
            secondary_val=1.25,
            tertiary_val=0.45,
            battery_pct=95.0,
            temperature_c=18.0
        )
        assert len(frame) == 18

    def test_crc16_ccitt_calculation_and_verification(self):
        test_data = b"PARVATNETRA2026"
        crc = compute_crc16_ccitt(test_data)
        assert isinstance(crc, int)
        assert 0 <= crc <= 0xFFFF

        # Test deterministic checksum
        frame = BinaryPacketCodec.encode(
            device_short_id=500,
            sequence_number=10,
            timestamp_epoch=1741618200,
            primary_val=35.0
        )
        decoded = BinaryPacketCodec.decode(frame)
        assert decoded["crc_valid"] is True
        assert decoded["device_short_id"] == 500
        assert decoded["sequence_number"] == 10

    def test_corrupt_crc_rejected(self):
        frame = bytearray(BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=1,
            timestamp_epoch=1741618200,
            primary_val=20.0
        ))
        # Corrupt single payload byte
        frame[5] ^= 0xFF
        with pytest.raises(ValueError, match="CRC mismatch"):
            BinaryPacketCodec.decode(bytes(frame))

    def test_malformed_length_rejected(self):
        short_frame = b"\x00" * 16
        with pytest.raises(ValueError, match="Invalid frame length"):
            BinaryPacketCodec.decode(short_frame)

        long_frame = b"\x00" * 20
        with pytest.raises(ValueError, match="Invalid frame length"):
            BinaryPacketCodec.decode(long_frame)

    def test_scaling_and_rounding_accuracy(self):
        # Primary: 0.1 scaling, Secondary: 0.01, Tertiary: 0.01
        frame = BinaryPacketCodec.encode(
            device_short_id=202,
            sequence_number=45,
            timestamp_epoch=1741618200,
            primary_val=123.4,
            secondary_val=12.34,
            tertiary_val=-5.67,
            battery_pct=88.0,
            temperature_c=-12.0
        )
        dec = BinaryPacketCodec.decode(frame)
        assert dec["primary_reading"] == 123.4
        assert dec["secondary_reading"] == 12.34
        assert dec["tertiary_reading"] == -5.67
        assert dec["temperature_c"] == -12.0
        assert dec["battery_pct"] == 88.0
        assert dec["tamper_flag"] is False

    def test_tamper_flag_bit(self):
        frame = BinaryPacketCodec.encode(
            device_short_id=303,
            sequence_number=99,
            timestamp_epoch=1741618200,
            primary_val=50.0,
            battery_pct=75.0,
            tamper=True
        )
        dec = BinaryPacketCodec.decode(frame)
        assert dec["tamper_flag"] is True
        assert dec["battery_pct"] == 75.0

    def test_conversion_to_canonical_packet(self):
        frame = BinaryPacketCodec.encode(
            device_short_id=105,
            sequence_number=3,
            timestamp_epoch=1741618200,
            primary_val=38.5,
            battery_pct=92.0,
            temperature_c=21.0
        )
        canonical = BinaryPacketCodec.to_canonical_packet(
            frame,
            device_id_map={105: "PZ-NH10-KM48-01"},
            sensor_type="piezometer",
            provenance="[LIVE]"
        )
        assert canonical["device_id"] == "PZ-NH10-KM48-01"
        assert canonical["sequence_number"] == 3
        assert canonical["battery"] == 92.0
        assert "pore_pressure" in canonical["measurements"]
        assert canonical["measurements"]["pore_pressure"]["value"] == 38.5
        assert canonical["measurements"]["pore_pressure"]["unit"] == "kPa"
        assert canonical["measurements"]["temperature"]["value"] == 21.0
