# PARVAT NETRA / PAHAD AI — PHASE 6C
## Field & Bench Sensor Commissioning Operating Procedure

**Document**: `docs/PHASE6C_COMMISSIONING_PROCEDURE.md`  
**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**AI Engine**: PAHAD AI  
**Standard**: SIH 26001 / NDMA Himalayan Instrumentation Protocol  
**Target Audience**: SDRF / BRO Electronics Technicians & Geotechnical Instrumentation Engineers  
**Date**: 2026-09-10  

---

## 1. Safety Prerequisites & Environmental Checks

Prior to initiating sensor commissioning on a Himalayan roadway or test bench:
1. **Safety Clearance**: Confirm zero active RED regional alert from Central EOC.
2. **Electrical Safety**: Ensure proper earth ground bonding ($<5\ \Omega$ resistance to earth) and surge suppression modules installed.
3. **Environmental Verification**: Check ambient temperature ($-20^\circ\text{C}$ to $+60^\circ\text{C}$) and casing seal integrity (IP67/IP68).

---

## 2. Canonical 8-Stage Commissioning Pipeline

Every sensor transducer must execute and pass the authoritative 8-stage state machine before its telemetry is accepted into the operational PAHAD predictive AI model:

```
[ STAGE 1: REGISTER ]
  Scan device QR/MAC -> Allocate device_id & sensor_type -> Assign sector_id
         │
         ▼
[ STAGE 2: INSTALL ]
  Physical anchor / borehole placement -> Cable conduit routing -> Earth bonding
         │
         ▼
[ STAGE 3: CALIBRATE ]
  Verify factory certificate -> Measure zero offset -> Upload scale factor
         │
         ▼
[ STAGE 4: CONNECT ]
  Join LoRaWAN / RS-485 network -> Verify RSSI > -110 dBm, SNR > -5 dB
         │
         ▼
[ STAGE 5: HEARTBEAT ]
  Verify battery > 80% -> Clock drift < 30s -> Solar charging verified
         │
         ▼
[ STAGE 6: TELEMETRY ]
  Ingest consecutive test packets -> Monotonic sequence verification -> Duplicate rejection
         │
         ▼
[ STAGE 7: VALIDATE ]
  Physical bounds verification -> Noise & drift analysis -> Quality score = GOOD
         │
         ▼
[ STAGE 8: ACCEPT ]
  Geotechnical authority sign-off -> State = ACTIVE -> Digital Certificate issued
```

---

## 3. Procedure Breakdown

### STAGE 1: REGISTER
- **Requirement**: Device identifier formatted according to corridor standards (e.g. `PZ-NH10-KM48-01`), valid sensor type in `{"piezometer", "inclinometer", "tilt", "rain_gauge", "soil_moisture", "crack_sensor", "water_level", "temperature"}`.
- **Geographic Bounding**: Coordinates must lie within the North-Eastern Region (Lat: $20.0^\circ\text{N}$ to $30.0^\circ\text{N}$, Lon: $87.0^\circ\text{E}$ to $98.0^\circ\text{E}$).

### STAGE 2: INSTALL
- **Requirement**: Physical anchoring into sound bedrock or grouted standpipe casing. Confirmation of surge suppression bonding.
- **Verification**: Visual inspection checklist recorded with installation technician signature.

### STAGE 3: CALIBRATE
- **Requirement**: Laboratory or factory calibration reference recorded.
- **Parameters Required**:
  - `zero_offset`: Measured baseline offset in engineering units.
  - `scale_factor`: Linear slope multiplier ($>0.0$).
  - `calibration_date`: ISO-8601 acquisition date.
  - `calibration_expiry`: Validity window (typically 365 days).
  - `certificate_ref`: Laboratory certificate reference code.
  - `technician`: Accredited metrology engineer name.

### STAGE 4: CONNECT
- **Requirement**: LoRaWAN OTAA join request or RS-485 handshake with corridor edge concentrator gateway.
- **RF Bounds**: $\text{RSSI} \ge -110.0\text{ dBm}$ and $\text{SNR} \ge -5.0\text{ dB}$.

### STAGE 5: HEARTBEAT
- **Requirement**: Node diagnostic packet received.
- **Metrics**: Battery level $>80.0\%$, clock offset magnitude $<30.0\text{ seconds}$.

### STAGE 6: TELEMETRY
- **Requirement**: Transmission of at least two consecutive sequential telemetry packets.
- **Check**: Sequence number increments monotonically ($seq_2 > seq_1$), and identical packet re-transmissions are rejected cleanly with `REJECTED_DUPLICATE`.

### STAGE 7: VALIDATE
- **Requirement**: Ingested readings pass physical limits and yield data quality score `GOOD`.
- **Examples**:
  - Piezometer: $-10.0\text{ kPa} \le u \le 250.0\text{ kPa}$
  - Tiltmeter: $-45.0^\circ \le \theta \le +45.0^\circ$
  - Rain Gauge: $0.0\text{ mm} \le R \le 300.0\text{ mm}$

### STAGE 8: ACCEPT
- **Requirement**: Final acceptance transition.
- **Outcome**: Device transitions from `COMMISSIONING` to `ACTIVE`.
- **Certificate**: Immutable SHA-256 digital certificate generated and stored in sensor registry.

---

## 4. CLI Execution Guide

The commissioning process can be executed interactively or automatically via CLI:

```bash
# Automated bench or field acceptance for a piezometer:
python scripts/commission_sensor.py \
  --device-id PZ-NH10-KM48-01 \
  --sensor-type piezometer \
  --gateway-id GW-NH10-KM48-01 \
  --sector-id SK-NH10-KM48 \
  --lat 27.3302 \
  --lon 88.6104 \
  --technician "A. Sharma, Geotechnical Metrologist" \
  --cert-ref "NABL-CAL-2026-PZ09" \
  --auto
```

### Exit Codes:
- `0`: **ACCEPTED** — All 8 stages passed; sensor marked ACTIVE with SHA-256 digital certificate.
- `1`: **REJECTED** — Failed physical limits, calibration validity, or RF thresholds.
- `2`: **COMMISSIONING_FAILED** — Prerequisite step missing or fatal configuration exception.
