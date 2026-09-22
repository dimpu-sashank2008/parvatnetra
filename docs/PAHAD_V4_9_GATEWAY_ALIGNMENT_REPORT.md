# PARVAT NETRA / PAHAD AI — PHASE V4.9 GATEWAY ALIGNMENT REPORT
## LoRa Concentrator Gateway Configuration, Regional Radio Settings & Edge Transport

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Gateway ID**: `GW-NH10-KM48-01`  
**Phase**: V4.9 — Joint Field Installation, LoRa Gateway Alignment & First Live Telemetry Commissioning  
**Gateway Status**: `CONFIGURED_ONLY`  
**Transport Mode**: `LoRaWAN Class A / C to Local Edge MQTT Broker`  

---

### 1. Executive Summary
This report details the architectural and RF alignment of the primary edge gateway `GW-NH10-KM48-01` designed to collect wireless telemetry from slope-mounted sensor nodes across the Teesta River gorge at KM48. The gateway firmware, regional frequency allocation, channel plan, store-and-forward persistence, and MQTT forwarder have been configured and bench-validated; however, physical tower erection and live field telemetry linking remain pending on-site deployment.

---

### 2. Regional Radio & RF Channel Plan (Sections 12 & 13)
The gateway is configured strictly for the **IN865–867** Indian Telecommunications Regulatory Band:
- **Frequency Plan**: `IN865_867` (865.0625 MHz to 867.0000 MHz)
- **Modulation**: Chirp Spread Spectrum (CSS) LoRaWAN 1.0.3 Class A
- **Channel Allocation**:
  - Upstream 1: 865.0625 MHz (BW 125 kHz, DR0–DR5 / SF12–SF7)
  - Upstream 2: 865.4025 MHz (BW 125 kHz, DR0–DR5 / SF12–SF7)
  - Upstream 3: 865.9850 MHz (BW 125 kHz, DR0–DR5 / SF12–SF7)
  - Upstream 4: 866.3850 MHz (BW 125 kHz, DR0–DR5 / SF12–SF7)
  - Upstream 5: 866.7850 MHz (BW 125 kHz, DR0–DR5 / SF12–SF7)
  - Upstream 6–8: Configured for dynamic adaptation (ADR disabled for critical slope telemetry to maintain fixed high link margin SF10).
- **ERP Limit**: $+30\text{ dBm}$ compliant with Wireless Planning & Coordination (WPC) India rules.
- **Hardware Concentrator**: Semtech SX1302/SX1303 baseband processor with dual SX1250 front-ends.

---

### 3. Store-and-Forward Replay Architecture (Section 21)
Due to severe monsoon atmospheric attenuation and potential fiber/cellular backhaul outages along the Teesta Gorge:
1. **Local SQLite Ring Buffer**: The edge gateway maintains a local encrypted FIFO database capable of storing up to 500,000 telemetry packets (over 90 days of offline observation).
2. **Backhaul Reconnection Replay**: Upon network restoration, packets are forwarded in chronological bursts tagged with original hardware capture timestamps.
3. **Deduplication Engine**: The ingest pipeline checks `(sensor_id, timestamp_utc, sequence_number)` tuples. Tested with 5-packet burst containing 2 replayed duplicates:
   - Total Replayed: 5
   - Unique Accepted: 3
   - Duplicates Dropped: 2
   - Zero duplicate records created in operational storage.

---

### 4. Gateway Commissioning Status
- **Firmware Image**: `v3.0.1-gateway-hil` bench validated.
- **Physical Installation**: Mast bracket and solar power module pending deployment.
- **Operational Classification**: `CONFIGURED_ONLY` (not live).
