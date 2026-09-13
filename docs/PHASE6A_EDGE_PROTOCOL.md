# PARVAT NETRA / PAHAD AI — PHASE 6A
## Edge Gateway Concentrator, LoRaWAN & Telemetry Protocol Specification

**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**Document**: `docs/PHASE6A_EDGE_PROTOCOL.md`  
**Standard**: SIH 26001 / Phase 6A Telemetry Protocol  
**Status**: APPROVED SPECIFICATION  

---

## 1. Network Topology & Physical Layer Protocols

The PARVAT NETRA field edge architecture operates in a hierarchical 3-tier topology:

```
[ Tier 1: Hillslope Transducers ]
   Piezometer (VW)      Inclinometer (MEMS)     Tiltmeter (Biaxial)     Rain Gauge (Bucket)
         │                     │                       │                      │
         └─────────────┬───────┴───────────────┬───────┴──────────────────────┘
                       ▼                       ▼
            [ LoRaWAN 865-867 MHz (IN865) / RS-485 Modbus RTU ]
                       │
                       ▼
[ Tier 2: Edge Concentrator Gateway (Singtam / Pakyong Staging Posts) ]
   - RPi CM4 / Industrial NXP i.MX8 Gateway with SX1302/SX1303 LoRa Baseband
   - Persistent Local SQLite Buffer (edge_buffer.db)
   - Autonomous Edge Corridor Alert Policy (Zero-latency siren actuation)
                       │
                       ├────────────────────────────┐
                       ▼ (Primary: Fiber/4G)        ▼ (Autonomous Fallback)
[ Tier 3: Central Cloud / Regional EOC ]     [ Local Acoustic Siren Horn ]
   - PAHAD Predictive AI Engine                - Solenoid Valve & Audio Relay
   - Common Alerting Protocol (CAP v1.2)       - 110 dB Dual-Tone Siren Horn
   - Multi-Modal Observation Store             - Zero Cloud Dependency
```

---

## 2. Radio Frequency Specification (India IN865 ISM Band)

Field sensor uplinks comply with the Wireless Planning & Coordination (WPC) regulatory framework for India:
- **Frequency Band**: $865.0\text{--}867.0\text{ MHz}$ (License-exempt ISM band).
- **Channels**: 3 default mandatory channels ($865.0625\text{ MHz}$, $865.4025\text{ MHz}$, $865.9850\text{ MHz}$) + 5 dynamically configured sub-band channels.
- **Modulation**: LoRa Chirp Spread Spectrum (CSS) with Spreading Factors $\text{SF7}$ to $\text{SF12}$.
- **Bandwidth**: $125\text{ kHz}$ uplink; $500\text{ kHz}$ downlink.
- **Maximum EIRP**: $+30\text{ dBm}$ ($1\text{ Watt}$) maximum; operational node output set to $+14\text{ dBm}$ ($25\text{ mW}$) to conserve battery.
- **Duty Cycle**: Unrestricted under Indian regulations, but throttled to $<1\%$ by firmware to prevent co-channel interference.
- **Airtime Budget**: SF7 packet $\approx 45\text{ ms}$; SF10 packet $\approx 280\text{ ms}$; SF12 packet $\approx 980\text{ ms}$.

---

## 3. Telemetry Ingress Packet Formats

### 3.1 Canonical JSON Schema (HTTP / MQTT)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PahadTelemetryPacket",
  "type": "object",
  "required": ["device_id", "sequence_number", "timestamp", "measurements"],
  "properties": {
    "packet_id": { "type": "string" },
    "device_id": { "type": "string", "minLength": 3, "maxLength": 64 },
    "sensor_id": { "type": "string" },
    "gateway_id": { "type": "string" },
    "sequence_number": { "type": "integer", "minimum": 0 },
    "timestamp": { "type": "string", "format": "date-time" },
    "latitude": { "type": "number", "minimum": 20.0, "maximum": 30.0 },
    "longitude": { "type": "number", "minimum": 87.0, "maximum": 98.0 },
    "battery": { "type": "number", "minimum": 0.0, "maximum": 100.0 },
    "signal_quality": { "type": "number", "minimum": -140.0, "maximum": 0.0 },
    "firmware_version": { "type": "string" },
    "transport": { "type": "string", "enum": ["LORA", "MQTT", "HTTP", "BLE", "EDGE_BUFFER_REPLAY"] },
    "provenance": { "type": "string", "enum": ["[LIVE]", "[SIMULATED]"] },
    "checksum": { "type": "string" },
    "measurements": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["value"],
        "properties": {
          "value": { "type": "number" },
          "unit": { "type": "string" },
          "raw_value": { "type": "number" },
          "quality": { "type": "string", "enum": ["GOOD", "DEGRADED", "SUSPECT", "INVALID"] }
        }
      }
    }
  }
}
```

### 3.2 Compact Binary Over-the-Air (OTA) Frame (LoRaWAN Payload)
To maximize battery life and minimize airtime over deep mountain canyons, field sensor nodes transmit an 18-byte packed binary frame:

```
 Byte Offset   Field Name            Type          Unit / Scaling / Description
 ─────────────────────────────────────────────────────────────────────────────
  0x00..0x01   Device Short ID       uint16_t      Unique 16-bit node ID (0–65535)
  0x02..0x03   Sequence Number       uint16_t      Monotonic rollover counter (0–65535)
  0x04..0x07   UNIX Epoch Seconds    uint32_t      GPS/NTP synced timestamp (UTC)
  0x08..0x09   Primary Reading       int16_t       Pore press (0.1 kPa) / Inclinometer (0.1 mm)
  0x0A..0x0B   Secondary Reading     int16_t       Tilt X (0.01 deg) / Rain accumulation (0.1 mm)
  0x0C..0x0D   Tertiary Reading      int16_t       Tilt Y (0.01 deg) / Soil moisture (0.1% VWC)
  0x0E         Battery & Status      uint8_t       Bit 0..6: Battery % (0–100); Bit 7: Tamper flag
  0x0F         Temperature           int8_t        Signed celsius (-40°C to +87°C)
  0x10..0x11   CRC-16 / CCITT        uint16_t      Polynomial: 0x1021, Init: 0xFFFF
```

---

## 4. Local SQLite Buffering & FIFO Reconnection Sync

When heavy monsoons cause physical landslides that sever fiber backhaul and cellular towers, the on-site edge gateway acts as an autonomous data silo:

1. **Local Persistent Storage**: All inbound packets are stored immediately in `data/edge/edge_buffer.db` table `edge_buffer`.
2. **Idempotent Primary Key**: `packet_id` consists of `{device_id}_{sequence_number}_{timestamp}`. If the same packet is received twice via multipath LoRa, the duplicate is dropped at insert (`INSERT OR IGNORE`).
3. **Replay Preservation**: When backhaul connectivity is restored, `flush_buffer()` queries the pending packets in strict ascending order of `sequence_number` and `timestamp`.
4. **Exponential Backoff**: If central cloud transmission fails during backhaul restoration, retry delays follow:
   $$t_{\text{retry}} = \min(2^k \times 1.5, 60)\text{ seconds}$$
   Where $k$ is the attempt count. Packets are not evicted until HTTP 200/202 confirmation is received from the central observation store.

---

## 5. Security Architecture & Digital Siren Authorization

### 5.1 Wireless Transmission Security (LoRaWAN)
- **AppKey & NwkKey**: 128-bit cryptographic root keys flashed during factory provisioning.
- **Session Keys**: Over-The-Air Activation (OTAA) produces unique `AppSKey` (payload encryption) and `NwkSKey` (network message integrity code).
- **AES-128-CCM**: Guarantees zero eavesdropping or spoofing of raw transducer telemetry.

### 5.2 Backhaul Transport Security
- **MQTT**: Mutual TLS (mTLS) with X.509 client certificates issued by PARVAT NETRA Private CA.
- **REST APIs**: TLS 1.3 with strict `HSTS` enforcement.

### 5.3 Acoustic Siren Command Authorization
Because false acoustic siren evacuations on mountain corridors can induce panic, remote web actuation requires a digital authorization token:
- **Token Format**: HMAC-SHA256 signature generated over the action payload (`"ACTIVATE"` or `"TEST"`) using the high-security secret `SIREN_AUTH_SECRET`.
- **Default Invariant**: Physical siren relays are disabled by default (`dry_run = True`, `hardware_enabled = False`).
- **Autonomous Edge Exemption**: The on-site edge gateway policy is permitted to sound the local corridor horn **without remote cloud authorization** if and only if two independent physical sensors cross acute hazard thresholds (e.g., Pore Water Pressure $>45\text{ kPa}$ AND Inclinometer creep $>15\text{ mm/day}$).
