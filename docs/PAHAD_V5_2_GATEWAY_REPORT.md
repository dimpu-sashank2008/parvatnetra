# PARVAT NETRA / PAHAD AI — PHASE V5.2
## LORA CONCENTRATOR GATEWAY TRANSPORT & STORE-AND-FORWARD REPLAY AUDIT

**Gateway Designation**: `GW-NH10-KM48-01`  
**Site**: NH-10 KM 48.2 (Pakyong District, Sikkim)  
**Authority**: PARVAT NETRA Communications & Telemetry Infrastructure Group  
**Date**: September 2026  
**Verdict**: `V5_2_PHYSICAL_DEPLOYMENT_PENDING`  
**Classification**: `OFFICIAL USE ONLY / LOCALHOST AUDIT`  

---

### 1. Gateway Hardware Specification
The corridor edge concentrator gateway is configured as follows:
- **Hardware Architecture**: Semtech SX1302 8-channel multi-SF LoRa concentrator core with ESP32-S3 host MCU.
- **Regional Frequency Plan**: `IN865_867` (865.0625 MHz – 866.9875 MHz per DoT / WPC India regulatory guidelines).
- **Channels Active**: 8 Multi-SF channels (SF7 to SF12, 125 kHz bandwidth).
- **Physical Mast**: Planned 6m galvanized mast with 50W monocrystalline solar PV and 12V 40Ah LiFePO4 battery pack.

### 2. Physical Deployment vs. Bench Prototype Audit

| Dimension | Bench Hardware Prototype | Mountain Slope Field Installation |
|---|---|---|
| Hardware Presence | SX1302 concentrator on dev board | 0 physical outdoor enclosures installed |
| Firmware | `v2.4.0-lora-concentrator` tested on bench | Not deployed to mountain mast |
| RF Link Test | Attenuated coaxial loopback / bench RF | No mountain-line-of-sight RF packets received |
| Validation Status | `BENCH_VALIDATED` | `FIELD_VALIDATION_PENDING` |

### 3. Store-and-Forward Replay Deduplication Engine
During mountain monsoon events, cellular/fiber backhaul links may drop. The gateway firmware caches packets in non-volatile flash storage and flushes them sequentially upon link restoration.

To protect the geotechnical pipeline from replay attacks or duplicate observation ingestion, the `PhysicalDeploymentEngine` enforces cryptographic deduplication:
- **Unique Packet Key**: `(sensor_id, timestamp_utc, payload_sha256)`
- **Evaluation Mechanism**: Ingested packets are evaluated against `_store_forward_buffer`.
- **First Delivery**: Accepted and stamped `STORE_FORWARD_FIRST_SEEN`.
- **Subsequent Replays**: Quarantined and stamped `STORE_FORWARD_DUPLICATE_REJECTED`.
- **Boundary Invariant**: Replayed packets cannot retroactively generate real-time emergency sirens or public alerts.
