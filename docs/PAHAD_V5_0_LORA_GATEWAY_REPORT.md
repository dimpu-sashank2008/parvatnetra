# PARVAT NETRA / PAHAD AI — PHASE V5.0
## LORA CONCENTRATOR GATEWAY & REPLAY DEDUPLICATION REPORT

**Gateway Node**: `GW-NH10-KM48-01`  
**Operational Status**: `CONFIGURED_ONLY` (Bench HIL Validated)  

---

### 1. Gateway Telemetry & Network Architecture

- **Hardware Specification**: Solar LoRaWAN Concentrator Node (IP67 Aluminium Enclosure).
- **Semtech Chipset**: SX1302 / SX1303 multi-channel baseband receiver.
- **RF Configuration**: IN865 (865–867 MHz), 8 channels, SF7–SF12, CR 4/5.
- **Backhaul Uplink**: Cellular 4G LTE-M with Satellite Iridium SBD failover bridge.
- **Local Ingestion Protocol**: MQTT with TLS 1.3 mutual certificate authentication.
- **Buffer Storage**: On-board SPI Flash store-and-forward circular buffer (up to 72 hours offline capacity).

---

### 2. Store-and-Forward Replay Deduplication Test

When mountain weather causes severe cellular backhaul disruption, the concentrator buffers packets locally. Upon link reconnection, the buffered backlog is replayed.

```
Incoming Stream ──► Deterministic Hash: SHA-256(sensor_id + timestamp + value + seq)
                         │
                         ├── If Hash in Seen Ledger ──► REJECT [DUPLICATE_REPLAY]
                         └── If Hash New            ──► ACCEPT [ACCEPTED_UNIQUE]
```

#### Test Verification Results:
- **Total Ingested Test Packets**: 3
- **Unique Packets Accepted**: 2
- **Duplicate Replays Suppressed**: 1
- **Observation Loss**: 0.0%
- **Duplicate Observations Created**: 0

---

### 3. Physical Deployment Reality

- **Physical Gateway Unit**: Not physically mounted on NH-10 KM48 mast.
- **Current Classification**: `CONFIGURED_ONLY` / `BENCH_VALIDATED`.
- **Live RF Packets Received from Slope**: 0.
