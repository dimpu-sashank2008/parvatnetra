# PARVAT NETRA / PAHAD AI — PHASE 3.4
## Local Edge Network & Autonomous Sub-GHz Mesh Architecture

**Document Reference**: `PAHAD_EDGE_ARCHITECTURE.md`  
**Problem Statement ID**: SIH 26001 (Smart India Hackathon)  
**Target Region**: Eastern Himalaya (Sikkim & Kalimpong/Darjeeling Corridors)  
**System Classification**: Last-Mile Autonomous Disaster Warning & Offline Telemetry Buffer  
**Binding Role**: Supplementary warning path (does not replace official NDMA/SDMA CAP channels)

---

## 1. System Mission & Core Principle

In extreme mountain environments (such as the Teesta River Valley and NH-10 corridor), torrential monsoon storms, rockfalls, and debris flows routinely sever fiber-optic lines, microwave backhauls, and cellular towers simultaneously.

Phase 3.4 provides an **autonomous last-mile edge sentinel** capable of:
1. Receiving continuous sensor telemetry over sub-GHz LoRa radio regardless of cloud reachability.
2. Evaluating local hillslope instability using deterministic physical threshold formulas.
3. Actuating local tactical alerting devices (acoustic siren horn and point-to-point BLE beacons) within milliseconds of threshold breach.
4. Buffering all sensor packets locally in SQLite when disconnected from the central server.
5. Automatically flushing buffered records to the cloud once connectivity is restored to update central PAHAD AI models.

---

## 2. End-to-End Information Flow

```
[ IN-SITU SENSOR CLUSTERS ]
  (Piezometer, Inclinometer, Moisture VWC, Rain Gauge)
          |
          |  34-Byte Binary Packets (LoRa Sub-GHz 865-867 MHz)
          v
[ LORA MESH TOPOLOGY ]
  (Direct Hop & Single-Relay Repeater with CRC-16 Checksum)
          |
          v
[ LOCAL EDGE GATEWAY (GW-01 / Singtam Depot) ]
  ├── EdgeStore: SQLite Local Buffer (edge_sensor_readings, edge_sync_queue)
  ├── EdgeRiskEvaluator: Deterministic Himalayan Regolith Safety Thresholds
  │       |
  │       +---> [ SAFE / WATCH / WARNING / CRITICAL ]
  │                 |
  │                 +--> SirenController (Armed / Dry-Run Safe Audit Log)
  │                 +--> BLEAlertBridge (HMAC-Signed Point-to-Point Alert)
  │
  └── EdgeSync: Cloud Backhaul Connection Watchdog
          |
          +== [ CLOUD ONLINE ] ===> POST /api/sync/field-reports & /api/pahad/iot-telemetry
          |                                  |
          |                                  v
          |                         [ PAHAD AI MULTIMODAL FUSION ]
          |                         (CRI, FoS, Event Prob, CAP v1.2)
          |
          +== [ CLOUD OFFLINE ] ==> Buffer into SQLite (Zero Packet Loss)
```

---

## 3. Hardware vs. Software Boundary

| Domain | Physical Hardware Layer | Software Abstraction / Emulation Layer |
|---|---|---|
| **Sensors** | Geokon piezometers, MEMS biaxial tiltmeters, Decagon 10HS soil moisture, tipping-bucket rain gauges. | `MockSensorAdapter` in `backend/edge/adapters.py` generating calibrated analog/I2C sensor readouts. |
| **Radio** | Semtech SX1262 / SX1276 LoRa transceivers (865–867 MHz India ISM band). | `MockLoRaAdapter` & `backend/edge/packet.py` handling 34-byte binary serialization and CRC-16-CCITT. |
| **Gateway** | Industrial Linux single-board computer (Raspberry Pi Compute Module 4 / Advantech UNO). | `EdgeGateway` class managing local pipeline, memory state, and sync workers. |
| **Siren** | 12V / 120 dB electronic horn siren with dual-channel optocoupled relay. | `SirenController` in `backend/edge/siren_controller.py` enforcing `DRY_RUN=true` safety invariants. |
| **BLE** | Nordic Semi nRF52840 BLE 5.3 Long Range Bluetooth SoC. | `BLEAlertBridge` in `backend/edge/ble_bridge.py` with device allowlists and HMAC signatures. |
| **Local DB** | On-board eMMC / industrial microSD flash. | SQLite database (`edge_store.db`) via `EdgeStore`. |

---

## 4. Local Risk Evaluation vs. Cloud PAHAD AI

To guarantee absolute sub-second deterministic execution on low-power edge hardware, **local risk evaluation is strictly segregated from cloud PAHAD AI**:

| Attribute | EdgeRiskEvaluator (Local Edge) | PAHAD AI (Central Cloud) |
|---|---|---|
| **Scope** | Immediate in-situ sensor breach (single hillslope segment). | Basin-wide multimodal fusion (8 NER states). |
| **Inputs** | Real-time rainfall, soil moisture, pore pressure, tilt angle. | Satellite InSAR, Mohr-Coulomb FoS, historical GSI catalog, IMD forecasts, crowd reports. |
| **Algorithms** | Normalized multi-sensor anomaly score & threshold bounds. | Gradient Boosting event classifiers, physics FoS calculations, 2-of-3 signal agreement. |
| **Latency** | $< 50\,\text{ms}$ deterministic response time. | $500 - 1500\,\text{ms}$ asynchronous API response. |
| **Output State** | `SAFE`, `WATCH`, `WARNING`, `CRITICAL`. | CRI score (0–100), $P(\text{event})$ (6h–48h), CAP-XML alert. |
| **Connectivity** | Zero network dependencies (100% offline). | Requires HTTPS connection to central cloud. |

---

## 5. Offline Data Resiliency & Sync Protocol

1. **State Detection**: `EdgeSync` continuously monitors cloud reachability via HTTP heartbeat checks (`/api/health`).
2. **Buffering**: When offline, incoming packets are processed, saved into `edge_sensor_readings`, and queued in `edge_sync_queue`.
3. **Queue Prioritization**:
   - Priority 1: Triggered local alerts (`CRITICAL` or `WARNING`).
   - Priority 2: In-situ geotechnical sensor readings.
4. **Resynchronization**: Upon network restoration, `EdgeSync.flush_sync_queue()` batches queued items with exponential backoff and updates sync timestamps.

---

## 6. Real Hardware Deployment Guidelines

When deploying real edge hardware in Sikkim corridors:
1. **Radio Frequency**: Utilize 865–867 MHz band with Spreading Factor SF7/SF8 to maintain transmission airtime below $50\,\text{ms}$ per packet.
2. **Antenna Staging**: Mount omni-directional fiberglass collinear antennas at high elevation above regolith line of sight.
3. **Power Architecture**: 50W monocrystalline solar panel + 12V 24Ah LiFePO4 battery pack with MPPT solar charge controller.
4. **Siren Hardware Wiring**: Connect GPIO pin to optoisolated solid-state relay controlling 12V siren coil. Set `SIREN_HARDWARE_ENABLED=true` in `.env` only after verifying physical audible safety perimeter.
