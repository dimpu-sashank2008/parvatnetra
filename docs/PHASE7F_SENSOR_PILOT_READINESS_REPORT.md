# PARVAT NETRA / PAHAD AI — PHASE 7F
## PHYSICAL SENSOR READINESS & ON-SLOPE TELEMETRY COMMISSIONING REPORT
*Evaluated: 2026-09-11T02:40:00Z • Corridor: CORR-NH10-SIKKIM-KM48 (Pakyong District, Sikkim)*

---

## 1. Executive Summary

Phase 7F systematically audits the technical readiness of the **PARVAT NETRA / PAHAD AI** data pipeline to ingest, validate, calibrate, and fuse real-time in-situ hillslope instrumentation along the Project Swastik NH-10 corridor (`CORR-NH10-SIKKIM-KM48`).

In accordance with the **Core Project Constitution & Data Honesty Protocol**:
- Software readiness to parse, validate, and store sensor packets **does NOT** equal physical field deployment.
- Zero physical geotechnical transducers (piezometers, inclinometers, tiltmeters, rain gauges) are currently installed or grouted on the hillside at KM48.
- The MQTT broker daemon is offline (`BROKER_UNAVAILABLE`) in the test environment; communication operates in software testbench standby.
- The overall pilot readiness status is honestly and unalterably determined as:

$$\mathbf{PHYSICAL\_DEPLOYMENT\_PENDING}$$

---

## 2. The 14-Gate Sensor Pilot Readiness Evaluation

| Gate | Domain | Status | Rationale & Forensic Evidence |
| :--- | :--- | :---: | :--- |
| **G1** | **Sensor Hardware** | **PARTIAL** | Transducer specifications bench-qualified (`VW_PIEZOMETER`, `IN_PLACE_INCLINOMETER`, `MEMS_TILTMETER`, `TIPPING_BUCKET_RAIN`). Zero physical units anchored in rock/soil at KM48. |
| **G2** | **Calibration Engine** | **PASS** | `GLOBAL_CALIBRATION_ENGINE` operational with 10 factory calibration profiles in SQLite store. Field zero-drift baseline pending installation. |
| **G3** | **Physical Installation** | **BLOCKED** | On-slope exploratory borehole drilling, guide casing grouting, and sensor head anchoring pending Project Swastik BRO clearance and site possession. |
| **G4** | **Power Subsystem** | **PARTIAL** | 40W Solar PV + 12V 24Ah LiFePO4 battery pack bench-verified (14-day autonomy). Physical mast mounting on highway retaining wall pending. |
| **G5** | **Edge Gateway** | **PASS** | `GTW-NH10-KM48-01` LoRaWAN/Cellular edge firmware configured with 72-hour non-volatile flash ring buffer for offline survivability. |
| **G6** | **MQTT / LoRaWAN Broker** | **PARTIAL** | Port 1883/8883 closed (`BROKER_UNAVAILABLE`). LoRaWAN IN865 packet decoders and MQTT topic routing verified in software testbench. |
| **G7** | **Telemetry Ingestion** | **PASS** | `services/device_gateway.py` and `services/mqtt_ingestion.py` active, handling JSON/binary decoding and queueing with zero packet loss. |
| **G8** | **Data Validation Contract** | **PASS** | `services/telemetry_contract.py` strictly validates 16-field schema, sequence monotonicity, rate-of-change limits, and physical boundaries. |
| **G9** | **Provenance Normalization** | **PASS** | Standardized vocabulary enforced: `LIVE`, `CACHED`, `DERIVED`, `MODELLED`, `SIMULATED`, `HIL`, `MISSING`, `AUTH_REQUIRED`, `UNAVAILABLE`. |
| **G10** | **Observation Store** | **PASS** | Persistent SQLite store (`data/observations/pahad_observations.db`) active with indexed sector, timestamp, and feature queries. |
| **G11** | **PAHAD Physics Fusion** | **PASS** | Mohr-Coulomb infinite slope FoS and ML classifier ingest telemetry directly; feature imputation dynamically deactivates when live sensors stream. |
| **G12** | **Failure Handling & OOD** | **PASS** | Out-of-distribution detector, stale-data TTL penalties, single-sensor spike isolation, and graceful fallback to training medians verified. |
| **G13** | **Safety Gate & Governance** | **PASS** | 2-of-3 corroboration strictly enforced for alert eligibility. `AI recommendation != public alert`. Public dispatch is `DISABLED`; sirens are `DRY_RUN`. |
| **G14** | **Field Acceptance** | **BLOCKED** | Joint technician inspection, telemetry commissioning sign-off, and site acceptance testing blocked pending physical drilling. |

**Summary**: 8 PASS, 4 PARTIAL, 2 BLOCKED, 0 FAIL.

---

## 3. Telemetry Contract & Physical Boundary Specifications

### Canonical 16-Field Telemetry Schema
Every telemetry packet conforms to `TelemetryPacket`:
1. `device_id`: Hardware identifier (e.g., `GTW-01-PZ-01`)
2. `sensor_id`: Transducer channel (e.g., `SITE-NH10-PIEZ-01`)
3. `timestamp_utc`: Device sample time (ISO-8601 UTC)
4. `received_at`: Server arrival time (ISO-8601 UTC)
5. `sequence_number`: Monotonic counter (rejects duplicates & replays)
6. `latitude`: WGS84 coordinate ($20.0^\circ\text{N}$ to $30.0^\circ\text{N}$)
7. `longitude`: WGS84 coordinate ($87.0^\circ\text{E}$ to $98.0^\circ\text{E}$)
8. `sensor_type`: Modality identifier (`piezometer`, `inclinometer`, `tilt`, `rain_gauge`)
9. `measurement`: Dictionary of calibrated engineering metrics
10. `unit`: Standard SI / geotechnical unit (`kPa`, `mm`, `deg`, `mm/h`)
11. `battery_voltage`: Voltage or percentage (low battery triggers `DEGRADED`)
12. `signal_quality`: RSSI in dBm / SNR (weak signal triggers `DEGRADED`)
13. `calibration_status`: `CALIBRATED`, `CALIBRATION_DUE`, or `INVALID`
14. `firmware_version`: SemVer string (e.g., `v1.2.0`)
15. `source`: Hardware transport origin (e.g., `MQTT (GTW-PZ-01)`)
16. `provenance`: `[LIVE]` or `[SIMULATED]`

### Physical Boundary & Anomaly Safeguards
- **Vibrating-Wire Piezometer**: $-10.0$ to $250.0\text{ kPa}$ (Max rate: $40.0\text{ kPa/h}$). Values $>250\text{ kPa}$ are rejected as `REJECTED_IMPOSSIBLE_VALUE`.
- **Borehole Inclinometer**: $-500.0$ to $500.0\text{ mm}$ (Max rate: $60.0\text{ mm/h}$).
- **MEMS Tiltmeter**: $-45.0$ to $45.0^\circ$ (Max rate: $10.0^\circ\text{/h}$).
- **Tipping-Bucket Rain Gauge**: $0.0$ to $300.0\text{ mm}$ (Max rate: $150.0\text{ mm/h}$).
- **Abnormal Velocity Isolation**: Rate of change $>3\times$ max hourly delta quarantines the observation as `DEGRADED`, preventing spurious sensor spikes from altering infinite slope FoS calculations.

---

## 4. Hardware-In-The-Loop (HIL) Scenario Evaluation

Ten operational failure and stress scenarios were evaluated through the software testbench:
1. **Stable Slope Baseline**: Nominal piezometric pressure ($12\text{ kPa}$), zero displacement. $FoS = 1.35$, $P(\text{event}) = 0.04$, Alert: `NONE`.
2. **Slowly Rising Pore Pressure**: Gradual increase ($15 \to 35\text{ kPa}$) over 48h. FoS degrades from $1.35 \to 1.15$. CRI increases from $25 \to 45$.
3. **Rapid Pore Pressure Surge**: Sudden increase ($15 \to 65\text{ kPa}$) simulating storm infiltration. FoS drops below critical threshold ($1.04$). Triggers Signal 1.
4. **Gradual Tilt Acceleration**: Biaxial deflection from $0.5^\circ \to 3.8^\circ$. Anomaly detector flags kinematic creep.
5. **Sudden Shear Displacement**: Shear jump of $18\text{ mm}$ along slip plane. Classified as immediate structural deformation.
6. **Sensor Dropout**: Transducer communication drops. System flags `MISSING`, applies training median ($26.0\text{ kPa}$), penalizes confidence.
7. **Sensor Electrical Noise / Spike**: $180\text{ kPa}$ single-cycle transient spike. Rate-of-change filter flags `DEGRADED`; 2-of-3 corroboration rejects false alarm.
8. **Battery Decline**: Voltage drops below $15\%$. Telemetry validator flags packet `DEGRADED`; operator dashboard alerted.
9. **Gateway Backhaul Outage**: Cellular link fails for 12 hours. Edge buffer logs 144 packets locally.
10. **Network Reconnection & Replay**: Link restored. 144 packets backfilled with `EDGE_BUFFER_REPLAY` tag; continuous time-series reconstructed.

---

## 5. Provenance & Terrain Discrepancy Resolution

### A. Rainfall Inconsistency Resolution (Phase 7E Fix)
- **Previous Discrepancy**: Weather was reported `LIVE`, but `rainfall_24h` appeared in `imputed_features` because of key nesting (`obs["rainfall"]["rain_24h_mm"]`).
- **Resolution**: `engine/pahad_live_inference.py` now flattens nested rainfall keys into `features_used["rainfall_24h"]` and registers explicit `FeatureProvenance(feature="rainfall_24h", provenance="LIVE", source="Open-Meteo")`.
- **Result**: `rainfall_24h` is correctly classified as observed and removed from `imputed_features`.

### B. Simulated Seismic Event Provenance (Phase 7E Fix)
- **Previous Discrepancy**: Cached simulation `SIM-EQ-NER-01` was stamped `CACHED`, implying historical ground truth.
- **Resolution**: `services/seismic_service.py` preserves `SIMULATED` provenance whenever `event_id` begins with `SIM-`, even when fetched from local cache.

### C. Terrain Slope Resolution (DEM $0.0^\circ$ vs Corridor $39.0^\circ$)
- **Investigation**: Point DEM finite-difference calculation at KM48 returned $0.0^\circ$ because the GLO-30 elevation raster clamped to a flat baseline ($180.0\text{ m}$) across the 3x3 window.
- **Authoritative Source**: GSI Project Swastik geological engineering survey established the slope at KM48 as $39.0^\circ$ to $42.5^\circ$.
- **Resolution**: When raw DEM slope equals $0.0^\circ$ placeholder, the pipeline resolves the authoritative corridor baseline ($39.0^\circ$) from `engine/corridor_registry.py`, explicitly tagging its provenance as `MODELLED`, source `Corridor Registry (GSI Swastik Geological Baseline)`. It is **never** misrepresented as live measured terrain truth.

---

## 6. Sector Snapshot Accounting (CORR-NH10-SIKKIM-KM48)

Live inference snapshot executed on 2026-09-11:

```json
{
  "sector_id": "CORR-NH10-SIKKIM-KM48",
  "event_probability": 0.0497,
  "fos_physical": 1.028,
  "cri": 23.6,
  "observed_feature_count": 2,
  "imputed_feature_count": 4,
  "missing_feature_count": 0,
  "data_quality_score": 0.442,
  "features_used": {
    "rainfall_24h": 8.3,
    "soil_moisture": 0.52,
    "pore_pressure_kpa": 26.0,
    "tilt_deg": 3.5,
    "ground_displacement_mm": 38.0,
    "slope_deg": 39.0,
    "elevation_m": 890.0,
    "seismic_magnitude": 4.6,
    "fos": 1.0282
  },
  "imputed_features": [
    "soil_moisture",
    "pore_pressure_kpa",
    "tilt_deg",
    "ground_displacement_mm"
  ],
  "feature_provenance": [
    {"feature": "weather", "provenance": "LIVE", "source": "Open-Meteo"},
    {"feature": "seismic", "provenance": "SIMULATED", "source": "PAHAD Himalayan Fault Simulator (SIM-EQ-NER-01)"},
    {"feature": "terrain", "provenance": "MODELLED", "source": "Corridor Registry (GSI Swastik Geological Baseline)"},
    {"feature": "iot", "provenance": "MISSING", "source": "No deployed in-situ sensors in sector"},
    {"feature": "rainfall_24h", "provenance": "LIVE", "source": "Open-Meteo"}
  ],
  "model_status": "TRAINED_LIMITED_DATA",
  "confidence": "LOW_CONFIDENCE",
  "safety_policy": {
    "public_dispatch_enabled": false,
    "siren_hardware_enabled": false,
    "operational_mode": "SHADOW"
  }
}
```

---

## 7. Safety Interlocks & Public Dispatch Invariants

1. **2-of-3 Corroboration Rule**:
   - Modality 1: $FoS < 1.10$ (Limit-equilibrium physical instability)
   - Modality 2: $Rainfall_{24h} > 150.0\text{ mm}$ (Mandal-Sarkar empirical threshold)
   - Modality 3: $P(\text{event}) > 0.70$ (Calibrated gradient boosted classifier)
   - **Enforcement**: Alert eligibility requires at least 2 modalities converging. No single modality (e.g. single sensor noise spike) can trigger an alert.
2. **AI Recommendation $\ne$ Public Alert**: All alerts require verified human authorization by certified officers (SDMA / DDMA / BRO Commander).
3. **Hardware Lockout**: Public emergency dispatch is locked to `DISABLED`; acoustic warning sirens are locked to `DRY_RUN`.

---

## 8. Final Gate Determination

$$\mathbf{PHYSICAL\_DEPLOYMENT\_PENDING}$$

**Determination Rationale**:  
The complete software, edge protocol, telemetry validation, and physics-AI fusion stack is operational and verified across all test scenarios. However, because on-slope transducers have not yet been drilled and anchored at `CORR-NH10-SIKKIM-KM48`, the system cannot be designated `PHYSICAL_SENSOR_READY`.
