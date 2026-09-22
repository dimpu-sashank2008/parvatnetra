# PARVAT NETRA / PAHAD AI — PHASE V4.6
# Hardware-In-The-Loop (HIL) Bench Simulation & Codec Verification Report

**Document Version**: 1.0.0  
**Codec Implementation**: `firmware/packet_codec.py`  
**Test Suite**: `tests/test_v4_6_telemetry.py` (`TestHILBinaryLoRaCodec`)  

---

## 1. Hardware-In-The-Loop (HIL) Scope

The Phase V4.6 HIL bench simulation validates the telemetry stack from the edge node firmware frame serialization through RF binary transmission, CRC-16 verification, payload normalization, and REST ingestion.

---

## 2. 18-Byte LoRa Binary Frame Specification

To minimize transmit time-on-air and maximize battery endurance across mountain ridges, telemetry is packed into a dense 18-byte big-endian binary frame:

```
0x00..0x01: uint16_t  device_short_id     (2 bytes, e.g. 101)
0x02..0x03: uint16_t  sequence_number     (2 bytes, e.g. 1, 2, 3...)
0x04..0x07: uint32_t  timestamp_epoch     (4 bytes, Unix UTC seconds)
0x08..0x09: int16_t   primary_reading     (2 bytes, scaled x10, e.g. 24.5 kPa -> 245)
0x0A..0x0B: int16_t   secondary_reading   (2 bytes, scaled x100, e.g. 1.25 deg -> 125)
0x0C..0x0D: int16_t   tertiary_reading    (2 bytes, scaled x100)
0x0E:       uint8_t   battery_status      (1 byte, Bits 0-6: %, Bit 7: Tamper flag)
0x0F:       int8_t    temperature         (1 byte, signed deg C)
0x10..0x11: uint16_t  crc16_ccitt         (2 bytes, Poly 0x1021, Init 0xFFFF)
Total Length: 18 Bytes
```

---

## 3. Cryptographic CRC-16-CCITT Verification

The CRC checksum is calculated over the first 16 payload bytes using the CCITT polynomial ($x^{16} + x^{12} + x^5 + 1$, `0x1021`) with initial fill `0xFFFF`.

### Automated Test Matrix:
1. **Bit Corruption Invariant**:
   - In `test_corrupted_crc_rejected`, single-bit and multi-bit corruptions were injected into payload bytes $0, 5, 12, 15$.
   - Result: 100% of corrupted frames were detected and rejected immediately with `REJECTED_CRC_ERROR`.
2. **Frame Truncation / Oversize**:
   - Frames shorter or longer than 18 bytes were rejected with `REJECTED_FRAME_LENGTH`.
3. **Dynamic Range Scaling**:
   - Verified that negative temperatures down to $-30^\circ\text{C}$ and positive temperatures up to $+60^\circ\text{C}$ preserve exact precision upon integer conversion.
   - Piezometer readings up to $500.0\text{ kPa}$ encode without overflow.

---

## 4. Bench Verification Summary

All HIL codec routines passed 100% of test scenarios without memory leaks, endianness errors, or unhandled exceptions.
