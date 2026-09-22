# PARVAT NETRA / PAHAD AI — PHASE V4.6
# In-Situ Telemetry Architecture & Dual-Stream Inference Specification

**Document Version**: 1.0.0  
**Phase**: V4.6 Master Engineering  
**System Status**: BENCH_VALIDATED_FIELD_PENDING  
**Target Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 Rangpo–Singtam Geological Corridor, Sikkim)  
**Safety Classification**: LIFE-CRITICAL GEOTECHNICAL EARLY WARNING  

---

## 1. Executive Overview

Phase V4.6 establishes the end-to-end engineering architecture for integrating real-time site-specific geotechnical instrumentation into the PARVAT NETRA / PAHAD AI landslide intelligence platform. The primary innovation of Phase V4.6 is the **Decoupled Dual-Stream Hazard Inference Architecture**, which strictly separates macro-scale synoptic meteorological hazard modeling from localized, high-frequency physical hillslope kinematic monitoring.

```
+-----------------------------------------------------------------------------------+
|                           PARVAT NETRA PLATFORM                                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [STREAM A: REGIONAL / SYNOPTIC HAZARD]       [STREAM B: SITE-SPECIFIC KINEMATIC]  |
|  - Horizons: 24h, 48h, 72h, 168h              - Horizons: 0h, 1h, 3h, 6h          |
|  - Sources: IMD, ERA5-Land, USGS, SRTM DEM    - Sources: In-situ Piezometers,     |
|  - Mechanics: Mohr-Coulomb Infinite Slope      Inclinometers, Tiltmeters, Gauges  |
|  - Baseline: FoS Predictor & V4.5 Sentinel    - Feature Layer: Velocities & Accel |
|  - Status: AVAILABLE                          - Status: PHYSICAL_TELEMETRY_PENDING|
|                                                                                   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                       DECOUPLED DUAL-STREAM FUSION SENTINEL                       |
|  - Parallel, Non-Blended Evidence Presentation (Zero False Masking)               |
|  - Fail-Closed Confidence Rating (Degraded when Kinematic is Unavailable)         |
|  - Geotechnical Advisory Synthesis for Emergency Operations (BRO / SDRF / NDMA)   |
|  - Non-Negotiable Safety Safeguard: Autonomous Public Dispatch Strictly Disabled  |
+-----------------------------------------------------------------------------------+
```

---

## 2. In-Situ Physical Instrumentation Stack

For the pilot corridor `CORR-NH10-SIKKIM-KM48` (Chainage KM 48.2, Pakyong District, Sikkim), the instrumentation layout comprises five physical sensing nodes:

1. **Vibrating Wire Piezometer (`PIEZO-NH10-KM48-01`)**:
   - **Model**: Geokon 4500AL High-Sensitivity Vibrating Wire Piezometer.
   - **Deployment Depth**: 12.0 meters below ground level (in bore casing).
   - **Physical Parameter**: Hydrostatic & transient pore water pressure ($u_w$).
   - **Units**: $\text{kPa}$ (Range: $-50.0$ to $500.0\text{ kPa}$).
   - **Sampling Rate**: 1-minute sampling, 5-minute transmission cadence.

2. **In-Place Inclinometer (`INCL-NH10-KM48-01`)**:
   - **Model**: Slope Indicator Digital In-Place Inclinometer (IPI) Biaxial String.
   - **Deployment Depth**: 15.0 meters below ground level across potential shear plane.
   - **Physical Parameter**: Lateral shear displacement ($\delta$).
   - **Units**: $\text{mm}$ (Range: $-100.0$ to $100.0\text{ mm}$).
   - **Sampling Rate**: Continuous tilt sampling, transmitted at 5-minute intervals.

3. **Surface Biaxial Tiltmeter (`TILT-NH10-KM48-01`)**:
   - **Model**: MEMS Digital Surface Tiltmeter with ceramic housing.
   - **Mount**: Bedrock-anchored structural plate at slope crown.
   - **Physical Parameter**: Angular slope deflection ($\theta_x, \theta_y$) and resultant magnitude.
   - **Units**: $\text{degrees}$ (Range: $-45.0^\circ$ to $45.0^\circ$).

4. **Tipping Bucket Rain Gauge (`RAIN-NH10-KM48-01`)**:
   - **Model**: Aerodynamic tipping bucket rain gauge ($0.2\text{ mm}$ bucket resolution).
   - **Mount**: Surface mast $1.5\text{ m}$ elevation above ground, clear clearing.
   - **Physical Parameter**: Instantaneous intensity and accumulation windows (5m, 15m, 1h, 3h, 6h).
   - **Units**: $\text{mm/h}$ (Range: $0.0$ to $250.0\text{ mm/h}$).

5. **Edge LoRaWAN Gateway (`GW-NH10-KM48-01`)**:
   - **Model**: PARVAT-NETRA Solar-Powered Ruggedized Edge Concentrator (IP67).
   - **RF Link**: LoRaWAN IN865 band ($865.0 - 867.0\text{ MHz}$) with 18-byte packed binary frames.
   - **Backhaul**: Dual-SIM 4G LTE with satellite fallback (IRIDIUM SBD queue).

---

## 3. Telemetry Processing Pipeline

The ingestion pipeline executes six deterministic validation and derivation steps:

1. **Physical & Hex Ingestion**: Accepts either raw 18-byte LoRa frames or canonical REST JSON payloads.
2. **CRC-16-CCITT Verification**: For binary packets, enforces standard polynomial `0x1021` checksum with zero bit tolerance.
3. **Canonical Contract Validation**: Enforces mandatory fields, WGS84 coordinate bounds within the North-Eastern Region (NER: $20^\circ\text{N}-30^\circ\text{N}$, $87^\circ\text{E}-98^\circ\text{E}$), and clock drift limits ($\le 30\text{ seconds}$ future drift).
4. **Physical Bounds & Plausibility**: Validates values against physical instrument thresholds; rejects physically impossible outliers.
5. **Deduplication & Sequence Tracking**: Monotonic sequence numbering per sensor ID prevents packet replay attacks.
6. **Freshness Monitoring**: Real-time evaluation against instrument timeouts ($15\text{ minutes}$ for sensors, $5\text{ minutes}$ for gateway).
7. **High-Frequency Kinematic Feature Layer**: Derives rolling rate of change, velocity, and acceleration vectors over sliding temporal windows ($5\text{m}$, $15\text{m}$, $1\text{h}$, $3\text{h}$, $6\text{h}$).

---

## 4. Production Immutability & Safety Standards

- **Primary Production Model**: `models/pahad_lstm_v3_weights.pt` remains the sole active production inference model with locked SHA-256 hash `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`.
- **Offline Research Model**: `models/pahad_lstm_v4_5_research_weights.pt` remains offline research only with verified SHA-256 hash `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f`.
- **Zero Counterfeit Rule**: Bench simulator and synthetic test packets can NEVER be tagged as `[LIVE]`. Field deployment status is transparently reported as `PHYSICAL_TELEMETRY_PENDING`.
- **Fail-Closed Principle**: Dropped or unmonitored sensors degrade platform confidence; the system NEVER interprets missing telemetry as evidence of slope stability.
