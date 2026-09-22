# PARVAT NETRA / PAHAD AI — PHASE V4.9 FIRST LIVE PACKET REPORT
## First Physical Telemetry Packet Inspection & Decoding Protocol

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Phase**: V4.9 — Joint Field Installation, LoRa Gateway Alignment & First Live Telemetry Commissioning  
**Live Telemetry Status**: `PHYSICAL_TELEMETRY_PENDING`  
**First Live Packet Timestamp**: `NONE (Null)`  
**Verified Live Observations**: `0`  

---

### 1. Executive Summary
Phase V4.9 establishes the rigorous protocol and decoding requirements for the first live telemetry packet transmitted from an on-slope physical sensor node. In strict compliance with Section 15 of the Master Engineering Prompt:
- Zero simulated, bench-generated, or replay packets may be promoted to `LIVE`.
- The first live packet timestamp remains `null` until an authenticated physical device sends a valid frame over the air from the KM48 corridor.

---

### 2. Physical Telemetry Packet Schema & Decoding Specification
Each physical telemetry frame conforms to the 28-byte compact binary LoRaWAN payload format:

| Byte Offset | Field Name | Data Type | Encoding / Units | Range / Description |
| :--- | :--- | :--- | :--- | :--- |
| `0x00–0x03` | `device_eui_prefix` | `uint32` | Hex identifier | Matches registered sensor node |
| `0x04–0x07` | `sequence_number` | `uint32` | Big-endian unsigned int | Monotonic sequence (1 to $2^{32}-1$) |
| `0x08–0x0B` | `device_timestamp` | `uint32` | Unix epoch seconds (UTC) | Device RTC capture timestamp |
| `0x0C–0x0F` | `primary_reading` | `float32` | IEEE 754 float | Pore pressure (kPa), Displ (mm), Tilt (deg), Rain (mm/h) |
| `0x10–0x11` | `battery_millivolts`| `uint16` | mV ($3000–4200$) | LiFePO4 / Li-ion battery health |
| `0x12` | `internal_temp_c` | `int8` | Degrees Celsius ($-40$ to $+85$) | Enclosure environmental sensor |
| `0x13` | `rssi_snr_byte` | `uint8` | Packed RSSI/SNR | RF link budget metric |
| `0x14–0x17` | `status_flags` | `uint32` | Bitmask | Tamper, tilt alarm, water ingress, sensor fault |
| `0x18–0x19` | `crc16_ccitt` | `uint16` | CRC-16 CCITT (0x1021) | Bit error detection check |

---

### 3. Acceptance Verification Checklist (Section 15)
To transition a received frame into a verified `FIRST_LIVE_PACKET`:
1. **Physical Sensor Presence**: Node must have completed Stage 6 (`INSTALLED`) with verified borehole log.
2. **CRC-16 Validation**: Payload CRC must match computed CRC-16 CCITT polynomial exactly.
3. **Timestamp Window**: Device timestamp must be within $\pm 60$ seconds of gateway system clock; future timestamps are rejected (`CRITERION_5_FAIL`).
4. **Physical Engineering Units**:
   - Piezometer: $0–500\text{ kPa}$
   - Inclinometer: $-100\text{ to }+100\text{ mm}$ cumulative shear displacement
   - Tiltmeter: $-45^\circ\text{ to }+45^\circ$ biaxial angle
   - Rain Gauge: $0–250\text{ mm/h}$ instantaneous intensity
5. **Zero Simulation Strings**: Packet must be free of `"BENCH"`, `"HIL"`, `"SIMULATED"`, `"SYNTHETIC"` markers.

---

### 4. Current Reality
- **Field Telemetry Packets**: `0`
- **Bench / HIL Packets**: `8,640`
- **First Live Packet ID**: `None`
- **First Live Timestamp**: `None`
- **Integrity Status**: Fully compliant with Zero-Fabrication Directive.
