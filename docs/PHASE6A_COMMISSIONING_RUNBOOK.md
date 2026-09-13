# PARVAT NETRA / PAHAD AI — PHASE 6A
## In-Situ Sensor Field Commissioning Runbook & Verification Protocol

**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**Document**: `docs/PHASE6A_COMMISSIONING_RUNBOOK.md`  
**Standard**: SIH 26001 / Phase 6A Field Engineering Protocol  
**Target Audience**: SDRF / BRO / NDRF Field Electronics Technicians & Geotechnical Engineers  
**Status**: APPROVED RUNBOOK  

---

## 1. Safety Prerequisites & PPE Requirements

Prior to entering active Himalayan landslide corridors (e.g. NH-10 Pakyong, Tupul Railway Cut, Melthum Quarry):
1. **Safety Clearance**: Confirm zero active RED regional alert from Central EOC.
2. **Personal Protective Equipment (PPE)**:
   - High-visibility reflective vest (EN ISO 20471).
   - Industrial safety helmet (EN 397) with chin strap.
   - Steel-toe puncture-resistant boots.
   - Portable VHF tactical radio tuned to BRO Corridor Command Frequency ($156.800\text{ MHz}$).
3. **Emergency Egress**: Identify immediate uphill and downhill designated refuge points before commencing borehole works.

---

## 2. The 8-Stage Field Commissioning Workflow

Every in-situ transducer must strictly execute and pass the 8-stage state machine before its telemetry is accepted into the operational PAHAD predictive AI model:

```
[ STAGE 1: REGISTER ]
  Scan device QR code -> Allocate device_id & sensor_type -> Assign corridor sector_id
         │
         ▼
[ STAGE 2: INSTALL ]
  Downhole lowering / rock anchor mounting -> Cable conduit routing -> Surge protection earth bonding
         │
         ▼
[ STAGE 3: CALIBRATE ]
  Verify factory certificate -> Measure barometric zero offset -> Upload scale factor
         │
         ▼
[ STAGE 4: CONNECT ]
  Join LoRaWAN network -> Verify RSSI > -110 dBm and SNR > -5 dB at corridor concentrator
         │
         ▼
[ STAGE 5: HEARTBEAT ]
  Verify battery > 85% -> Verify solar charger charging current -> Clock drift < 10s
         │
         ▼
[ STAGE 6: TELEMETRY ]
  Acquire 5 consecutive raw sample packets -> Confirm plausible physical range
         │
         ▼
[ STAGE 7: VALIDATE ]
  Automatic contract validation: bounding box, CRC, non-zero values, noise check
         │
         ▼
[ STAGE 8: ACCEPT ]
  Geotechnical authority sign-off -> Device status transitions to ACTIVE -> Telemetry marked [LIVE]
```

---

## 3. Step-by-Step Commissioning Procedures

### STAGE 1: REGISTER
- **Action**: Field technician uses ParvatNetra Mobile App or CLI tool.
- **REST API Call**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{
      "device_id": "SN-PZ-NH10-KM48-01",
      "stage": "REGISTER",
      "sensor_type": "piezometer",
      "sector_id": "SK-NH10-KM48",
      "latitude": 27.3302,
      "longitude": 88.6104,
      "gateway_id": "GW-NH10-01"
    }'
  ```
- **Verification**: Ensure API returns `{"status": "SUCCESS", "current_status": "COMMISSIONING"}`.

---

### STAGE 2: INSTALL
- **Borehole Transducers (Piezometers / Inclinometers)**:
  1. Inspect standpipe borehole depth using a water level sounder tape.
  2. Lower piezometer tip to design elevation ($1\text{--}2\text{ m}$ below predicted shear surface).
  3. Pour clean silica sand filter pack ($0.5\text{--}1.0\text{ mm}$) to $0.5\text{ m}$ above the porous filter stone.
  4. Pour bentonite pellet seal ($1.0\text{ m}$ thickness) and allow hydration for 60 minutes.
  5. Backfill borehole with non-shrink cement-bentonite grout ($1:1$ ratio).
- **Surface Transducers (Tiltmeters / Crackmeters)**:
  1. Drill 3 holes with rotary hammer drill into sound, non-weathered bedrock.
  2. Insert stainless steel mechanical expansion wedge anchors ($M8 \times 75\text{ mm}$).
  3. Bolt mounting plate with high-strength threadlocker and align $X$-axis with downslope fall line.
- **REST API Call**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{"device_id": "SN-PZ-NH10-KM48-01", "stage": "INSTALL"}'
  ```

---

### STAGE 3: CALIBRATE
- **Procedure**:
  1. Record atmospheric barometric pressure at ground level using a calibrated digital barometer.
  2. Take zero-depth baseline frequency reading of piezometer prior to submersion ($f_0$).
  3. Enter zero offset and factory thermal/gauge factors into calibration registry.
- **REST API Call**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/calibration \
    -H "Content-Type: application/json" \
    -d '{
      "sensor_id": "SN-PZ-NH10-KM48-01",
      "calibration_id": "CAL-2026-PZ-01",
      "calibration_date": "2026-09-10T00:00:00Z",
      "calibration_due": "2027-09-10T00:00:00Z",
      "zero_offset": 0.42,
      "scale_factor": 1.0024,
      "calibration_source": "FIELD_FACTORY_VERIFIED"
    }'
  ```
- **Advance Stage**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{"device_id": "SN-PZ-NH10-KM48-01", "stage": "CALIBRATE"}'
  ```

---

### STAGE 4: CONNECT
- **Procedure**:
  1. Power on the LoRaWAN transceiver node.
  2. Observe the green diagnostic LED for Join Accept sequence (3 rapid flashes).
  3. Confirm RF signal quality at edge concentrator:
     - RSSI must be $\ge -115\text{ dBm}$ (Target: $\ge -95\text{ dBm}$).
     - SNR must be $\ge -7\text{ dB}$ (Target: $\ge +5\text{ dB}$).
- **Advance Stage**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{"device_id": "SN-PZ-NH10-KM48-01", "stage": "CONNECT"}'
  ```

---

### STAGE 5: HEARTBEAT
- **Procedure**:
  1. Check terminal battery voltage under load ($>3.45\text{V}$ for $3.6\text{V}$ lithium cells).
  2. Measure solar panel open-circuit voltage ($V_{oc} > 18\text{V}$ under indirect sunlight).
  3. Verify internal RTC drift against concentrator NTP clock ($|\Delta t| < 10\text{ seconds}$).
- **Advance Stage**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{"device_id": "SN-PZ-NH10-KM48-01", "stage": "HEARTBEAT"}'
  ```

---

### STAGE 6: TELEMETRY
- **Procedure**:
  1. Trigger 5 manual test transmissions at 1-minute intervals.
  2. Verify that values are non-zero and within expected physical ranges (e.g., $15.0\text{--}35.0\text{ kPa}$ water pressure for standard hillside water table).
- **Advance Stage**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{"device_id": "SN-PZ-NH10-KM48-01", "stage": "TELEMETRY"}'
  ```

---

### STAGE 7: VALIDATE
- **Automated Validation**:
  - The central validation engine confirms:
    - Sequence numbers increment monotonically ($1, 2, 3, \dots$).
    - Zero dropped packets across the 5 test frames.
    - Coordinates fall strictly within the North-Eastern Himalayan bounding box.
    - Zero future timestamps.
- **Advance Stage**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{"device_id": "SN-PZ-NH10-KM48-01", "stage": "VALIDATE"}'
  ```

---

### STAGE 8: ACCEPT
- **Procedure**:
  - Geotechnical Authority (EOC Chief or Senior Geologist) verifies the deployment dossier and executes acceptance.
- **REST API Call**:
  ```bash
  curl -X POST http://<gateway-ip>:8080/api/iot/commission \
    -H "Content-Type: application/json" \
    -d '{"device_id": "SN-PZ-NH10-KM48-01", "stage": "ACCEPT"}'
  ```
- **Result**:
  - Device status transitions from `COMMISSIONING` to `ACTIVE`.
  - `commissioned_at` timestamp is permanently recorded.
  - Live readings from this node are immediately ingested by PAHAD AI with `[LIVE]` provenance.

---

## 4. Troubleshooting & Remediation Matrix

| Symptom | Probable Root Cause | Field Action |
| :--- | :--- | :--- |
| **LoRa Join Request Denied** | Misconfigured DevEUI or AppKey | Re-verify AppKey in node firmware against Central Registry credentials. |
| **Piezometer reading out of range ($>250\text{ kPa}$)** | Grout overpressure during setting | Wait 24h for cement hydration heat to dissipate; bleed standpipe if artesian. |
| **Erratic tilt spikes ($\Delta \theta > 5^\circ/\text{hr}$)** | Loose mounting anchor / rock spall | Inspect physical bracket; re-torque anchor bolts to $25\text{ N}\cdot\text{m}$. |
| **Rapid battery drain ($<50\%$ in 1 month)** | Excessive TX power / retry storms | Lower SF from SF12 to SF8; reposition gateway antenna to improve direct line-of-sight. |
| **Clock offset rejection ($>30\text{s}$)** | Node RTC drift | Force node time resynchronization via downlink MAC command `DeviceTimeReq`. |
