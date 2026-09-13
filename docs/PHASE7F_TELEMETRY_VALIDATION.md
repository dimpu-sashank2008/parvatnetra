# PARVAT NETRA / PAHAD AI — PHASE 7F
## IN-SITU TELEMETRY VALIDATION & TRANSDUCER QUALITY SPECIFICATION
*Document Version: 1.0.0 • Verified: 2026-09-11 • Corridor: CORR-NH10-SIKKIM-KM48*

---

## 1. Executive Summary & Telemetry Invariant

This document establishes the canonical telemetry schema, physical boundary limits, quality classification rules, and ingestion safeguards for all in-situ geotechnical instrumentation connected to the **PARVAT NETRA** disaster-intelligence platform.

> [!IMPORTANT]
> **Data Honesty Invariant**: Software capability to parse and validate sensor packets does NOT constitute on-slope transducer deployment. As of Phase 7F, zero physical transducers are installed on the slope at `CORR-NH10-SIKKIM-KM48`. All bench-tested or emulated streams MUST bear `provenance = SIMULATED` or `provenance = HIL`. Never `LIVE`.

---

## 2. Canonical Telemetry Packet Contract

Every telemetry packet arriving at the edge gateway or cloud ingestion endpoint MUST conform to the 16-field schema specified in [`services/telemetry_contract.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/services/telemetry_contract.py):

| Field | Type | Description | Mandatory | Validation Constraint |
| :--- | :--- | :--- | :---: | :--- |
| `device_id` | `str` | Unique hardware identifier (e.g., `GTW-01-PZ-01`) | **YES** | Alphanumeric, registered in `SensorRegistry` |
| `sensor_id` | `str` | Sensor transducer channel identifier | **YES** | Matches calibrated transducer channel |
| `timestamp_utc` | `str` (ISO-8601) | Device sample timestamp with UTC offset | **YES** | Cannot exceed server time by $>30\text{s}$ |
| `received_at` | `str` (ISO-8601) | Ingestion server arrival timestamp | **YES** | Server-generated upon arrival |
| `sequence_number` | `int` | Monotonically increasing packet counter | **YES** | Rejects duplicates and replays |
| `latitude` | `float` | WGS84 latitude coordinate | **YES** | $20.0^\circ\text{N} \le \text{lat} \le 30.0^\circ\text{N}$ (NER Bounding Box) |
| `longitude` | `float` | WGS84 longitude coordinate | **YES** | $87.0^\circ\text{E} \le \text{lon} \le 98.0^\circ\text{E}$ (NER Bounding Box) |
| `sensor_type` | `str` | Physical instrumentation modality | **YES** | One of `VALID_SENSOR_TYPES` |
| `measurement` | `dict` / `float` | Metric reading(s) with engineering unit | **YES** | Within physical boundary limits |
| `unit` | `str` | SI / engineering unit (`kPa`, `mm`, `deg`, `mm/h`) | **YES** | Standardized unit string |
| `battery_voltage` | `float` | Node battery level in volts or percentage | **YES** | Battery $<15\%$ triggers `DEGRADED` quality |
| `signal_quality` | `float` | RSSI in dBm / SNR | **YES** | RSSI $<-95\text{ dBm}$ triggers `DEGRADED` |
| `calibration_status`| `str` | Transducer calibration state | **YES** | `CALIBRATED`, `CALIBRATION_DUE`, `INVALID` |
| `firmware_version` | `str` | Node edge firmware version string | **YES** | SemVer format (e.g., `v1.2.4`) |
| `source` | `str` | Originating transport or hardware node | **YES** | Explicit hardware or transport origin |
| `provenance` | `str` | Data truth badge (`[LIVE]`, `[SIMULATED]`) | **YES** | Normalized provenance badge |
| `quality_flag` | `str` | Quality tier (`GOOD`, `DEGRADED`, `INVALID`) | **YES** | Evaluated by `TelemetryValidator` |

---

## 3. Physical Transducer Boundary & Rate Limits

Readings exceeding physical bounds are rejected outright. Readings with sudden rate-of-change acceleration are flagged as suspicious and quarantined.

| Sensor Type | Target Metric | Min Value | Max Value | Unit | Max Hourly Delta | Failure / Malfunction Indicator |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Vibrating-Wire Piezometer** | Pore-water pressure | $-10.0$ | $250.0$ | $\text{kPa}$ | $40.0\text{ kPa/h}$ | Negative suction $>10\text{ kPa}$ or casing rupture |
| **Borehole Inclinometer** | Shear displacement | $-500.0$ | $500.0$ | $\text{mm}$ | $60.0\text{ mm/h}$ | Guide tube shearing or sensor detachment |
| **MEMS Tiltmeter** | Surface slope deflection | $-45.0$ | $45.0$ | $\text{deg}$ | $10.0\text{ deg/h}$ | Anchor pole tilt or animal interference |
| **Tipping-Bucket Rain Gauge** | Rainfall accumulation | $0.0$ | $300.0$ | $\text{mm}$ | $150.0\text{ mm/h}$ | Funnel clogging or reed switch chatter |
| **Soil Moisture (TDR/FDR)** | Volumetric water content | $0.0$ | $1.0$ | $\text{m}^3/\text{m}^3$ | $0.50\text{ m}^3/\text{m}^3/\text{h}$ | Probe corrosion or air gap separation |
| **Laser / LVDT Crack Meter** | Joint aperture dilation | $0.0$ | $200.0$ | $\text{mm}$ | $30.0\text{ mm/h}$ | Optical beam occlusion or anchor pullout |
| **River Hydrometric Gauge** | Water stage level | $0.0$ | $50.0$ | $\text{m}$ | $15.0\text{ m/h}$ | Ultrasonic echo bounce or riverbed siltation |
| **Ground Temperature** | Subsurface temperature | $-30.0$ | $60.0$ | $^\circ\text{C}$ | $25.0\text{ }^\circ\text{C/h}$ | Thermistor short or wiring damage |

---

## 4. Quality Classification Rules

Incoming observations are systematically partitioned into 6 operational categories:

```
                          ┌──────────────────────────┐
                          │ Incoming Telemetry Packet│
                          └─────────────┬────────────┘
                                        │
                         [Schema / BBox / Time Valid?]
                                 ├─── NO ───► REJECTED (Dropped + Audit Log)
                                 │
                         [Within Physical Bounds?]
                                 ├─── NO ───► REJECTED_IMPOSSIBLE_VALUE
                                 │
                         [Rate-of-Change Feasible?]
                                 ├─── NO ───► QUARANTINED (High Variance / Noise)
                                 │
                         [Packet Age > TTL?]
                                 ├─── YES ──► STALE (Age Penalty Applied)
                                 │
                         [Hardware Environment?]
                                 ├─── BENCH / HIL ──► SIMULATED / HIL
                                 │
                                 └─── PHYSICAL ON-SLOPE ──► LIVE
```

1. **`LIVE`**: Authentic telemetry streamed from physically verified and anchored transducers at the corridor pilot site. Stored in observation store with full model weight ($1.00$).
2. **`SIMULATED`**: Telemetry generated by mathematical models, historical replay, or testbench harnesses. Clearly isolated and never used for operational dispatch. Weight: $0.40$.
3. **`HIL`**: Hardware-In-The-Loop electronic emulator transmitting through physical LoRaWAN/MQTT gateways. Proves hardware protocol compatibility without physical rock drilling.
4. **`STALE`**: Telemetry whose age exceeds the modality TTL (Piezometer: $120\text{s}$, Tiltmeter: $120\text{s}$, Rain Gauge: $900\text{s}$). Carries proportional confidence penalty.
5. **`QUARANTINED`**: Suspicious telemetry (abnormal rate of change $>3\times$ physical threshold, calibration expired, or sensor noise spike). Isolated from infinite-slope FoS calculations.
6. **`REJECTED`**: Dropped immediately with security audit entry:
   - `REJECTED_MISSING_DEVICE_ID`
   - `REJECTED_UNKNOWN_DEVICE`
   - `REJECTED_DUPLICATE` (replay attack protection)
   - `REJECTED_CORRUPT_SEQUENCE`
   - `REJECTED_FUTURE_TIMESTAMP` ($>30\text{s}$ drift)
   - `REJECTED_OUT_OF_BOUNDS` (outside NER bounding box)
   - `REJECTED_IMPOSSIBLE_VALUE` (outside physical range)

---

## 5. Transport Protocol Specifications

### A. MQTT Broker Route
- **Topic Hierarchy**: `pahad/{state}/{sector_id}/{device_id}/telemetry`
- **Example**: `pahad/Sikkim/SK-NH10-KM48/PZ-01/telemetry`
- **Payload**: JSON matching `TelemetryPacket` schema.
- **Port**: 1883 (TCP plain) or 8883 (MQTTS TLS v1.3).
- **QoS Level**: QoS 1 (At least once delivery) with local client-side flash queueing.

### B. LoRaWAN Ingress
- **Frequency Band**: IN865 (865–867 MHz) for India / North-Eastern Region.
- **Payload Decoders**: Native Cayenne LPP or custom binary packing decoded in `services/edge_gateway.py`.
- **Failsafe**: 72-hour on-node SD card buffer with automatic backhaul replay upon gateway reconnection.

### C. HTTP REST Endpoint
- **URL**: `POST /api/iot/telemetry`
- **Headers**: `Content-Type: application/json`, `X-Gateway-Auth: <token>`
- **Response**: `200 OK` with JSON `{ "status": "ACCEPTED", "packet_id": "...", "quality": "GOOD" }`
