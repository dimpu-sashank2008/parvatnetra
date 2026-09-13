# PARVAT NETRA / PAHAD AI — PHASE 6C
## In-Situ Sensor Telemetry Packet Specification & Binary Framing

**Document**: `docs/PHASE6C_PACKET_SPECIFICATION.md`  
**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**AI Engine**: PAHAD AI  
**Status**: APPROVED SPECIFICATION  
**Standard**: SIH 26001 / Phase 6C Packet Protocol  
**Date**: 2026-09-10  

---

## 1. Overview & Protocol Stratification

To operate reliably in deep Himalayan river valleys with minimal battery consumption and zero airtime congestion, field telemetry is stratified into two complementary representations:

1. **Compact Binary Frame (OTA Over-the-Air)**: 18-byte packed binary payload optimized for LoRaWAN IN865 transmissions. Delivers maximum range at SF10–SF12 with minimal transmission duration ($<250\text{ ms}$).
2. **Canonical JSON Payload (Ingress & Inter-Service)**: Normalized, fully self-describing JSON telemetry object with ISO-8601 timestamps, explicit engineering units, calibration provenance, and data quality indicators. Used over MQTT, HTTP REST, and the SQLite ObservationStore.

---

## 2. 18-Byte Compact Binary OTA Frame

### 2.1 Byte Layout & Bit Field Specification

The binary payload is strictly packed in **Big-Endian (Network Byte Order)** format without padding bytes:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Device Short ID         |        Sequence Number        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      UNIX Epoch Seconds                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        Primary Reading        |       Secondary Reading       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        Tertiary Reading       | Battery & Stat|  Temperature  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         CRC-16 / CCITT        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 2.2 Field Definitions & Scaling Factors

| Byte Range | Field Name | Type | Scaling / Unit | Range | Physical Meaning |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **0x00 .. 0x01** | `device_short_id` | `uint16_t` | Raw integer | $0\text{--}65535$ | Numeric short ID assigned during commissioning |
| **0x02 .. 0x03** | `sequence_number` | `uint16_t` | Monotonic counter | $0\text{--}65535$ | Roll-over sequence count for deduplication |
| **0x04 .. 0x07** | `timestamp_epoch` | `uint32_t` | Unix seconds (UTC) | $0\text{--}4294967295$ | Precise RTC timestamp at sensor acquisition |
| **0x08 .. 0x09** | `primary_reading` | `int16_t` | Multiplied by 10 | $-3276.8\text{--}+3276.7$ | Pore press ($0.1\text{ kPa}$) or Displacement ($0.1\text{ mm}$) |
| **0x0A .. 0x0B** | `secondary_reading`| `int16_t` | Multiplied by 100 | $-327.68\text{--}+327.67$ | Tilt X ($0.01^\circ$) or Rain accumulation ($0.1\text{ mm}$) |
| **0x0C .. 0x0D** | `tertiary_reading` | `int16_t` | Multiplied by 100 | $-327.68\text{--}+327.67$ | Tilt Y ($0.01^\circ$) or Soil moisture ($0.1\%\text{ VWC}$) |
| **0x0E** | `battery_status` | `uint8_t` | Bitfield | $0\text{--}255$ | Bit 0..6: Battery % ($0\text{--}100\%$); Bit 7: Tamper/Error flag |
| **0x0F** | `temperature` | `int8_t` | $1^\circ\text{C}$ steps | $-40\text{--}+87^\circ\text{C}$ | Ambient or downhole transducer temperature |
| **0x10 .. 0x11** | `crc16` | `uint16_t` | CRC-16-CCITT | $0\text{--}65535$ | Polynomial `0x1021`, initial `0xFFFF` over bytes 0x00..0x0F |

### 2.3 Sensor Channel Mapping by Transducer Type

Depending on the sensor type registered during commissioning, the three 16-bit measurement fields map as follows:

| Sensor Type | Primary Reading (`0x08..0x09`) | Secondary Reading (`0x0A..0x0B`) | Tertiary Reading (`0x0C..0x0D`) |
| :--- | :--- | :--- | :--- |
| `piezometer` | Pore Pressure ($0.1\text{ kPa}$) | Resonant Frequency ($0.1\text{ Hz}$) | Barometric Pressure ($0.1\text{ kPa}$) |
| `inclinometer` | Cumulative Deflection ($0.1\text{ mm}$)| Creep Velocity ($0.01\text{ mm/day}$) | Deflection Rate ($0.01\text{ mm/hr}$) |
| `tilt` | Downslope Angle $\theta_X$ ($0.01^\circ$)| Cross-slope Angle $\theta_Y$ ($0.01^\circ$)| Resultant Deflection $\theta_R$ ($0.01^\circ$) |
| `rain_gauge` | Current Hour Accumulation ($0.1\text{ mm}$)| Instantaneous Intensity ($0.1\text{ mm/hr}$)| 24h Rolling Accumulation ($0.1\text{ mm}$) |
| `soil_moisture`| Volumetric Water Content ($0.1\%$) | Electrical Conductivity ($0.1\text{ dS/m}$) | Soil Temperature ($0.1^\circ\text{C}$) |
| `crack_sensor` | Joint Aperture ($0.01\text{ mm}$) | Dilation Rate ($0.01\text{ mm/day}$) | Reserved / Status Flag |

### 2.4 Integrity Checksum: CRC-16-CCITT
The final two bytes (`0x10..0x11`) contain the standard CCITT 16-bit cyclic redundancy check calculated over the first 16 bytes of the payload:
- **Generator Polynomial**: $x^{16} + x^{12} + x^5 + 1$ (`0x1021`)
- **Initial Vector**: `0xFFFF`
- **Reflect In**: `False`
- **Reflect Out**: `False`
- **XOR Out**: `0x0000`

Frames failing the CRC-16 check are discarded immediately at the edge gateway concentrator before queuing or decoding.

---

## 3. Canonical JSON Ingress Schema

When decoded by the edge gateway concentrator or transmitted directly over MQTT / HTTP REST backhaul, the telemetry packet expands into the authoritative schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PahadTelemetryPacket",
  "type": "object",
  "required": [
    "packet_id",
    "device_id",
    "sensor_id",
    "sequence_number",
    "timestamp",
    "received_at",
    "latitude",
    "longitude",
    "measurements",
    "battery",
    "signal_quality",
    "provenance"
  ],
  "properties": {
    "packet_id": { "type": "string", "example": "PZ-NH10-KM48-01_104_1741618200" },
    "device_id": { "type": "string", "example": "PZ-NH10-KM48-01" },
    "sensor_id": { "type": "string", "example": "PZ-NH10-KM48-01" },
    "gateway_id": { "type": "string", "example": "GW-NH10-KM48-01" },
    "sequence_number": { "type": "integer", "minimum": 0, "example": 104 },
    "timestamp": { "type": "string", "format": "date-time", "example": "2026-09-10T14:50:00Z" },
    "received_at": { "type": "string", "format": "date-time", "example": "2026-09-10T14:50:01.210Z" },
    "latitude": { "type": "number", "minimum": 20.0, "maximum": 30.0, "example": 27.3302 },
    "longitude": { "type": "number", "minimum": 87.0, "maximum": 98.0, "example": 88.6104 },
    "battery": { "type": "number", "minimum": 0.0, "maximum": 100.0, "example": 94.5 },
    "signal_quality": { "type": "number", "minimum": -140.0, "maximum": 0.0, "example": -78.0 },
    "firmware_version": { "type": "string", "example": "v2.1.0-lora" },
    "transport": { "type": "string", "enum": ["LORA", "MQTT", "HTTP", "BLE", "EDGE_BUFFER_REPLAY"] },
    "provenance": { "type": "string", "enum": ["[LIVE]", "[SIMULATED]"] },
    "clock_offset_ms": { "type": "number", "example": 12.5 },
    "checksum": { "type": "string", "example": "0x4F8A" },
    "measurements": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["value", "unit", "quality"],
        "properties": {
          "value": { "type": "number", "example": 42.8 },
          "unit": { "type": "string", "example": "kPa" },
          "raw_value": { "type": "number", "example": 42.8 },
          "calibrated_value": { "type": "number", "example": 42.8 },
          "quality": { "type": "string", "enum": ["GOOD", "DEGRADED", "SUSPECT", "INVALID"] }
        }
      }
    }
  }
}
```

---

## 4. Deduplication & Idempotent Sequencing

1. **Unique Packet Identifier**:
   $$\text{packet\_id} = \text{device\_id} + \text{"\_"} + \text{sequence\_number} + \text{"\_"} + \text{timestamp}$$
2. **Replay Filtering**: Inbound packets are cross-checked against the gateway's circular ring of the last 5,000 processed `packet_id` hashes.
3. **Buffer Replay Exception**: Packets tagged with `transport = "EDGE_BUFFER_REPLAY"` are exempt from duplicate rejection if their sequence was previously accepted into the buffer but not yet flushed to the central observation store.
