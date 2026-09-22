# PARVAT NETRA / PAHAD AI — PHASE V4.8
# In-Situ Sensor Quality Control, Physical Boundaries & Hazard Discrimination Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.8 — Real Physical Corridor Telemetry Ingestion & Ground-Truth Dataset Pipeline  
**Modules**: `services/telemetry_contract.py`, `engine/telemetry_trust_engine.py`  
**Test Suites**: `tests/test_v4_8_real_telemetry_ingestion.py`, `tests/test_v4_8_live_boundary.py`  

---

## 1. Quality Control (QC) State Machine

Every sensor observation processed by PARVAT NETRA is classified into one of five deterministic QC states:

| QC State | Operational Meaning | Safety System Treatment |
| :--- | :--- | :--- |
| **`VALID`** | Conforms to physical range, rate of change, timestamp sync, and valid calibration. | Admitted at full weight into kinematic feature derivation. |
| **`DEGRADED`** | Minor anomaly detected (clock drift $> 120\text{s}$, low battery $< 15\%$, calibration overdue). | Admitted with down-weighted confidence penalty ($\le 25\%$). |
| **`SUSPECT`** | Abnormal rate of change or sudden step change pending cross-sensor corroboration. | Quarantined from automatic alarm escalation pending 2-of-3 vote. |
| **`INVALID`** | Impossible physical value, CRC failure, corrupted sequence, or negative rain accumulation. | Dropped immediately; logged in forensic rejection registry. |
| **`STALE`** | Observation age exceeds freshness window ($> 900\text{s}$ for sensors, $> 300\text{s}$ for gateway). | Excluded from current nowcast; flagged as offline if $> 3600\text{s}$. |

---

## 2. Transducer-Specific QC Invariants

```
                ┌───────────────────────────────┐
                │ Incoming Sensor Observation   │
                └──────────────┬────────────────┘
                               │
               [Physical Range Checked?]
                    ├── NO  ──► REJECTED_IMPOSSIBLE_VALUE (INVALID)
                    └── YES
                         │
               [Calibration Status Valid?]
                    ├── NO  ──► CALIBRATION_DUE / INVALID (DEGRADED)
                    └── YES
                         │
               [Rate of Change <= 3x Max?]
                    ├── NO  ──► SENSOR_NOISE_OR_BURST (SUSPECT)
                    └── YES
                         │
               [Clock Drift <= 30s?]
                    ├── NO  ──► REJECTED_FUTURE_TIMESTAMP (INVALID)
                    └── YES
                         │
                         ▼
                   QC State: VALID
```

### Transducer Parameter Thresholds:
- **Piezometer (Geokon 4500AL)**:
  - Range: $[-10.0, 250.0]\text{ kPa}$
  - Maximum Rate: $40.0\text{ kPa/h}$
  - Flatline Threshold: Variance $\sigma^2 = 0$ across 24 consecutive 15-min cycles ($6\text{ hours}$).
- **Inclinometer (RST MEMS-IPI-01)**:
  - Range: $[-500.0, 500.0]\text{ mm}$
  - Maximum Shear Rate: $60.0\text{ mm/h}$
- **Biaxial Tiltmeter (Encardio-Rite EAN-92M)**:
  - Range: $[-45.0, 45.0]^\circ$
  - Maximum Deflection Rate: $10.0^\circ/\text{h}$
- **Tipping Bucket Rain Gauge (Davis Aerocone)**:
  - Range: $[0.0, 300.0]\text{ mm}$
  - Negative Accumulation: Strictly forbidden (triggers immediate `INVALID`).

---

## 3. Discriminating Real Hazards from Sensor Errors

A critical challenge in Himalayan geotechnical monitoring is ensuring that extreme observations indicative of rapid landslide acceleration are not mistakenly discarded as sensor glitches:

1. **The Multi-Modal Corroboration Principle**:
   - A single pore pressure jump of $80\text{ kPa/h}$ is flagged as `SUSPECT` if unaccompanied by rainfall or tilt.
   - If IMD radar concurrently indicates $> 50\text{ mm/h}$ rainfall and tiltmeter resultant registers deflection $> 1.5^\circ$, the observation is classified as **`POSSIBLE_HAZARD`** and immediately routed to the authority triage queue.
2. **Fail-Closed Governance**:
   - Extreme readings never trigger unverified public alerts autonomously.
   - They trigger DDMA/BRO warning escalation with a mandatory human authorization gate.
