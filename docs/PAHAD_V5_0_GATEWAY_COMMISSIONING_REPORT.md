# PARVAT NETRA / PAHAD AI — PHASE V5.0
## LORA GATEWAY CONCENTRATOR COMMISSIONING & TRANSPORT REPORT

**Gateway ID**: `GW-NH10-KM48-01`  
**Authoritative Status**: `CONFIGURED_ONLY`  
**Verdict**: `V5_0_HARDWARE_EVIDENCE_PENDING`  
**Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 KM48 Rangpo–Singtam, Sikkim)  

---

### 1. Gateway Hardware Specification & Configuration

```
+-----------------------------------------------------------------------------------------+
|                        LORA CONCENTRATOR GATEWAY SPECIFICATION                          |
+-----------------------------------+-----------------------------------------------------+
| Hardware Asset                    | Solar IP67 LoRaWAN Outdoor Gateway                  |
| Manufacturer & Model              | Dragino / RAKwireless Solar Concentrator            |
| Declared Serial Number            | PN-GW-2026-0038                                     |
| Firmware Version                  | v3.0.1-gateway-hil                                  |
| Operating Band                    | Indian ISM Band (IN865_867: 865.0625 - 866.985 MHz) |
| Channel Allocation                | 8 Multi-SF Uplink Channels + 1 Standard LoRa Channel|
| Ingress Protection                | IP67 Aluminum Die-Cast Weatherproof Enclosure       |
| Power Subsystem                   | 50W Monocrystalline PV + 12V 24Ah LiFePO4 Battery   |
| Backhaul Transports               | 4G LTE-M / NB-IoT Cellular + Ethernet / Wi-Fi       |
| MQTT Broker Endpoint              | localhost:1883 (Bench HIL Loopback)                 |
| MQTT Uplink Topic                 | parvatnetra/nh10/km48/uplink                        |
| CRC Verification                  | CRC-16 CCITT Hardware Verification Enforced         |
| Physical Presence                 | UNVERIFIED (Outdoor Mast Mount Pending)             |
| Operational State                 | CONFIGURED_ONLY                                     |
+-----------------------------------+-----------------------------------------------------+
```

---

### 2. Store-and-Forward Replay Architecture
To guarantee zero telemetry loss during monsoon communication outages along the Teesta gorge:
1. The gateway implements an onboard non-volatile SQLite / flash buffer capable of caching up to 250,000 packets (~30 days of offline telemetry).
2. Upon backhaul recovery, packets are burst-streamed with original hardware generation timestamps.
3. The platform ingestion engine performs deterministic deduplication using SHA-256 hash digests of `(sensor_id, timestamp_utc, value, sequence_number)`.
4. Bench loopback validation verified 100% duplicate elimination with zero redundant database inserts.

---

### 3. Commissioning Audit Findings
- LoRa packet forwarder, MQTT parser, and deduplication logic are 100% bench-tested and operational.
- Physical mast erection at KM48 and solar installation remain pending joint field execution.
- Operational status remains strictly designated as **`CONFIGURED_ONLY`**.
