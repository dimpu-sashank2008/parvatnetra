# PARVAT NETRA / PAHAD AI — PHASE 3.4
## Sub-GHz LoRa Binary Packet & Network Protocol Specification

**Document Reference**: `PAHAD_EDGE_PROTOCOL.md`  
**Problem Statement ID**: SIH 26001 (Smart India Hackathon)  
**Standard**: Compact Industrial Telemetry Protocol (34-Byte Binary Frame)

---

## 1. Protocol Rationale & Airtime Constraints

In rugged mountainous terrain, LoRa operates under strict physical link constraints:
- **Bandwidth**: 125 kHz
- **Carrier**: 865.2 MHz (India ISM Band)
- **Spreading Factor**: SF7 / SF8 (balance between receiver sensitivity and transmission airtime)
- **Airtime Budget**: Total airtime per packet must remain below $50\,\text{ms}$ to prevent radio collisions across dense multi-node slope deployments.

Standard JSON strings ($> 200\,\text{bytes}$) violate this airtime budget. Phase 3.4 implements an ultra-compact **34-byte binary serialization frame**.

---

## 2. 34-Byte Binary Packet Specification

```
struct format: ">BBHIIffffBhB" (Big-Endian, Network Byte Order)
Total Frame Length: 34 Bytes
```

| Byte Offset | Field Name | Data Type | Encoding / Units | Range / Description |
|---|---|---|---|---|
| `[0]` | `version` | `uint8` | Unsigned integer | Protocol version (current = `1`). |
| `[1]` | `flags` | `uint8` | Bitfield | Bit 0: `DEMO` (`0x01`), Bit 1: `RELAY_HOP` (`0x02`), Bit 2: `ALERT_TRIGGERED` (`0x04`). |
| `[2:4]` | `node_hash` | `uint16` | CRC-16 of Node ID | Deterministic 16-bit hash of node identifier string (e.g., CRC-16 of `SN-NH10-01`). |
| `[4:8]` | `sequence` | `uint32` | Monotonic Counter | Per-node incremental sequence counter for replay protection and packet loss tracking. |
| `[8:12]` | `timestamp` | `uint32` | Unix Epoch Seconds | UTC timestamp seconds. |
| `[12:16]` | `soil_moisture` | `float32` | IEEE 754 float | Volumetric Water Content (VWC) percentage ($0.0 - 100.0\%$). |
| `[16:20]` | `pore_pressure` | `float32` | IEEE 754 float | Pore-water pressure in kilopascals ($0.0 - 200.0\,\text{kPa}$). |
| `[20:24]` | `tilt_degrees` | `float32` | IEEE 754 float | Continuous borehole inclinometer tilt angle ($0.0 - 45.0^\circ$). |
| `[24:28]` | `rainfall_intensity` | `float32` | IEEE 754 float | Instantaneous precipitation rate in millimeters per hour ($0.0 - 300.0\,\text{mm/h}$). |
| `[28]` | `battery_pct` | `uint8` | Percentage | Battery level ($0 - 100\%$). |
| `[29:31]` | `temperature_c` | `int16` | Fixed point ($^\circ\text{C} \times 10$) | Ambient temperature (e.g. $24.5^\circ\text{C} \to 245$). |
| `[31]` | `humidity_pct` | `uint8` | Percentage | Relative humidity ($0 - 100\%$). |
| `[32:34]` | `crc16` | `uint16` | CRC-16-CCITT | Checksum calculated over bytes `[0:32]` with polynomial `0x1021`, init `0xFFFF`. |

---

## 3. CRC-16-CCITT Integrity Check

Every packet is validated before ingest:
```python
def crc16_ccitt(data: bytes, poly: int = 0x1021, init: int = 0xFFFF) -> int:
    crc = init
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc
```
If the received checksum does not match bytes `[32:34]`, the packet is dropped immediately with `[REJECTED_CHECKSUM_MISMATCH]` and logged to security telemetry.

---

## 4. LoRa Mesh Topology & Replay Protection

1. **Topology Support**:
   - Direct link: `Sensor Node → Gateway`
   - Single-relay mesh: `Sensor Node → Intermediate Relay Node → Gateway`
2. **Deduplication**:
   - The gateway maintains a sliding window of recent `(node_hash, sequence)` pairs.
   - Repeated transmissions or multi-path relay echoes are dropped as duplicate frames.
3. **Health Tracking**:
   - Nodes missing for $> 300\,\text{seconds}$ transition to `OFFLINE` status.
   - Battery levels $< 20\%$ trigger a maintenance dispatch alert.

---

## 5. Edge REST API Surface

| Endpoint | Method | Role | Output / Behavior |
|---|---|---|---|
| `/api/edge/status` | `GET` | Gateway Health | Returns gateway ID, mesh health, siren state, BLE state, buffer size, cloud connectivity. |
| `/api/edge/nodes` | `GET` | Node Telemetry | Returns active/offline nodes, last seen timestamps, signal RSSI, battery levels. |
| `/api/edge/network` | `GET` | Mesh Topology | Returns network topology nodes, edges, gateways, packet throughput. |
| `/api/edge/readings` | `GET` | Sensor Buffer | Returns recent buffered physical readings from SQLite store. |
| `/api/edge/alerts` | `GET` | Edge Alerts | Returns edge-triggered safety alerts (`WATCH`, `WARNING`, `CRITICAL`). |
| `/api/edge/siren/status` | `GET` | Siren State | Returns arming state, active level, test events, dry run status. |
| `/api/edge/siren/test` | `POST` | Fire Test Event | Fires `SIREN_TEST_EVENT` strictly without physical acoustic output. |
| `/api/edge/demo/inject` | `POST` | Demo Injection | Injects custom sensor packets marked `[DEMO]` for SIH evaluation. |
| `/api/edge/toggle-cloud` | `POST` | Disconnect Simulation | Toggles simulated cloud link to demonstrate offline SQLite buffering. |
| `/api/edge/sync/flush` | `POST` | Force Resync | Manually flushes SQLite sync queue to central cloud. |
