# PAHAD AI — IoT & Sensor Gateway Architecture

**Document**: `PAHAD_IOT_ARCHITECTURE.md`  
**Classification**: Geotechnical Telemetry & Edge Systems Architecture  
**Phase**: Phase 5 — Real Data Expansion & Live Predictive Inference  
**Status**: ACTIVE  

---

## 1. Executive Summary

The **PAHAD AI IoT Telemetry Subsystem** bridges physical hillslope instrumentation across hazardous North Eastern Region (NER) mountain transportation corridors to the digital predictive core of **PARVAT NETRA**.

Hillslope failure in the Himalayas is primarily governed by pore-water pressure elevation, creep strain, and toe erosion. Real-time in-situ telemetry provides the earliest physical warning indicators before catastrophic shear surface mobilization occurs.

---

## 2. In-Situ Instrumentation & Supported Sensor Types

The system ingests observations from 4 primary classes of geotechnical and hydrometeorological instruments deployed along critical pilot corridors (e.g., NH-10 Km 48 / 29th Mile, Pakyong, Singtam):

| Sensor Class | Transducer Mechanism | Measured Physical Parameter | Nominal Range | Critical Threshold | Engineering Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vibrating-Wire Piezometer** | Frequency resonance of tensioned wire under diaphragm deflection | Pore-water pressure ($u$) in $\text{kPa}$ | $0.0 - 150.0\text{ kPa}$ | $> 30.0\text{ kPa}$ (warning)<br>$> 45.0\text{ kPa}$ (critical) | Directly reduces effective stress: $\sigma' = \sigma - u$. Primary driver of FoS reduction. |
| **Borehole Inclinometer** | MEMS dual-axis accelerometer package | Subsurface shear displacement ($\delta$) in $\text{mm}$ | $0.0 - 200.0\text{ mm}$ | $> 15.0\text{ mm/day}$ (velocity)<br>$> 50.0\text{ mm}$ (cumulative) | Detects developing slip plane shear band before visible surface rupture. |
| **Surface Tiltmeter** | High-precision electrolytic / MEMS tilt | Angular slope deflection ($\theta$) in degrees ($^\circ$) | $0.0 - 15.0^\circ$ | $> 2.5^\circ$ deviation | Measures surficial rotation, retaining wall leaning, or tension crack aperture tilt. |
| **Tipping-Bucket Rain Gauge** | Dual-bucket magnetic reed switch | Real-time precipitation intensity ($R$) in $\text{mm/hr}$ | $0.0 - 250.0\text{ mm/hr}$ | $> 50.0\text{ mm/hr}$ or $> 150.0\text{ mm/24h}$ | Drives antecedent infiltration model and pore pressure recharge curves. |

---

## 3. Telemetry Gateway Architecture (`services/device_gateway.py`)

The `DeviceGateway` acts as the single ingress point for edge field telemetry, accepting transmissions over HTTP REST, MQTT, and LoRaWAN JSON payloads.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FIELD SENSOR CLUSTER                            │
│  [Piezometer VW-01]  [Inclinometer IN-02]  [Tiltmeter TL-01]  [AWS-01] │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  LoRaWAN (865-867 MHz) / BLE Mesh
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     SOLAR-POWERED EDGE CONCENTRATOR                    │
│   - Raspberry Pi CM4 / ESP32-S3 Edge Gateway                          │
│   - Local SQLite buffer for offline forward-logging                    │
│   - Satellite / 4G-LTE / VSAT dual uplink                              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS POST / MQTT
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               PAHAD DEVICE GATEWAY (services/device_gateway.py)         │
│   - Schema Validation & Range Sanitization                             │
│   - Data Quality Scoring (GOOD, DEGRADED, SUSPECT, INVALID)            │
│   - Provenance Tagging ([LIVE], [SIMULATED], [CACHED])                 │
│   - In-Memory Device State Registry & Persistent Telemetry Journal     │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
       PAHAD Live Inference Pipeline        Database / Event Journal
     (engine/pahad_live_inference.py)       (PostGIS telemetry table)
```

---

## 4. Ingestion Wire Protocol & Packet Format

### 4.1 Ingress API Endpoints
- `POST /api/iot/telemetry`: Telemetry ingestion from gateways.
- `GET /api/iot/telemetry`: Retrieval of recent telemetry packets.
- `GET /api/iot/devices`: Registry listing of active sensor devices and their health status.

### 4.2 Standard Telemetry Packet Schema
```json
{
  "device_id": "SK-NH10-KM48-PIEZOMETER-01",
  "sensor_type": "piezometer",
  "value": 28.4,
  "unit": "kPa",
  "timestamp": "2026-09-09T18:15:00Z",
  "latitude": 27.3300,
  "longitude": 88.6100,
  "battery_v": 3.65,
  "rssi_dbm": -82,
  "metadata": {
    "borehole_depth_m": 12.5,
    "installation_sector": "SK-NH10-KM48",
    "calibration_factor": 0.0421
  }
}
```

---

## 5. Telemetry Quality Assessment Engine

Every packet ingested undergoes immediate physical sanity checks. Packets are tagged with authoritative quality flags:

1. **`GOOD`**:
   - `device_id` registered and authenticated.
   - Value strictly within physically plausible limits ($0 \le u \le 150\text{ kPa}$, $0 \le \delta \le 300\text{ mm}$).
   - Timestamp fresh ($\le 120\text{ seconds}$ latency).
   - Battery voltage $> 3.2\text{V}$.

2. **`DEGRADED`**:
   - Telemetry age exceeds nominal freshness threshold ($> 120\text{s}$ but $< 24\text{ hours}$).
   - Low battery warning ($3.0\text{V} \le V < 3.2\text{V}$).
   - Weak signal strength ($\text{RSSI} < -110\text{ dBm}$).

3. **`SUSPECT`**:
   - Delta jump exceeds maximum physical rate of change ($> 15\text{ kPa/min}$ without corresponding rainfall).
   - Value outside plausible limits ($u > 150\text{ kPa}$, tilt $> 45^\circ$).
   - Flagged for automated maintenance inspection.

4. **`INVALID` / `REJECTED`**:
   - Malformed schema, non-numeric values, or missing `device_id`.
   - Returns structured error code without interrupting system runtime.

---

## 6. Offline Resilient Edge Sync Protocol (BLE Mesh / LoRaWAN)

During monsoon deluges, road breaches frequently sever fiber-optic lines and cellular towers along Himalayan valley corridors. PARVAT NETRA implements a multi-hop store-and-forward edge protocol:

1. **Local Ring Buffer**: Edge sensor nodes maintain an on-flash ring buffer capable of storing 72 hours of 30-second telemetry.
2. **BLE Mesh Burst Synchronization**: In the event of complete backhaul failure, passing emergency convoys (BRO / NDRF patrol vehicles equipped with mobile collector units) automatically harvest stored sensor logs via 2.4 GHz Bluetooth Low Energy mesh beacons.
3. **Reconciliation & Deduplication**: When connectivity is re-established, the gateway transmits batches tagged with original device timestamps. `services/device_gateway.py` performs SHA-256 fingerprint deduplication to prevent duplicate ingress.

---

## 7. Integration with PAHAD Live Inference (`engine/pahad_live_inference.py`)

In live prediction cycles:
1. `_collect_iot(sector_id)` queries `DeviceGateway` for the nearest active device within the targeted geofenced sector.
2. If fresh telemetry ($\le 120\text{s}$) exists, live pore-water pressure and tilt are directly fed into the Infinite Slope Mohr-Coulomb equation:
   $$FoS = \frac{c' + (\gamma \cdot z \cdot \cos^2\beta - u) \cdot \tan\phi'}{\gamma \cdot z \cdot \sin\beta \cdot \cos\beta}$$
3. If no telemetry is available, the pipeline explicitly flags the feature as `[MISSING]` and falls back to training-split medians, preserving transparent provenance without fabrication.
