# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Field Commissioning Lifecycle & Acceptance Checklist Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.7 — Sensor Hardware Acceptance & Calibration Traceability  
**Commissioning Status**: `FIELD_COMMISSIONING_PENDING` (0 Commissioned, 5 Bench-Accepted)  
**Authoritative Ledger**: `data/processed/sensor_acceptance_ledger.json`  

---

## 1. 10-Stage Sensor Acceptance Lifecycle

PARVAT NETRA enforces a non-negotiable 10-stage lifecycle for all physical geotechnical sensors:

$$\text{PLANNED} \longrightarrow \text{RECEIVED} \longrightarrow \text{IDENTIFIED} \longrightarrow \text{CALIBRATED} \longrightarrow \text{BENCH\_ACCEPTED} \longrightarrow \text{INSTALLED} \longrightarrow \text{CONNECTED} \longrightarrow \text{TELEMETRY\_VALIDATED} \longrightarrow \text{FIELD\_COMMISSIONED} \longrightarrow \text{MONITORING}$$

### Transition Rules & Guarantees:
- **No Stage Skipping**: A sensor in `PLANNED` cannot jump directly to `FIELD_COMMISSIONED` or `INSTALLED`.
- **Immutable Evidence Records**: Every state transition requires operator identity, timestamp, cryptographic evidence reference, and technical justification.
- **Prohibition of Software-Only Commissioning**: Software simulators or synthetic HIL drivers can advance sensors only to `BENCH_ACCEPTED`. Advancement to `FIELD_COMMISSIONED` strictly requires human authority cryptographic authorization tokens.

---

## 2. Sensor Fleet Commissioning Status

| Sensor ID | Type | Manufacturer & Model | Serial Number | Current Stage | NABL Cert Ref | Field Commissioning Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `PIEZO-NH10-KM48-01` | Piezometer | Geokon 4500AL | `GK-4500AL-9988` | `BENCH_ACCEPTED` | `NABL-GEO-2026-P8821` | `PENDING_BOREHOLE` |
| `INCL-NH10-KM48-01` | Inclinometer | RST MEMS-IPI-01 | `RST-MEMS-5521` | `BENCH_ACCEPTED` | `NABL-GEO-2026-I4409` | `PENDING_BOREHOLE` |
| `TILT-NH10-KM48-01` | Tiltmeter | Encardio-Rite EAN-92M | `ENC-92M-3312` | `BENCH_ACCEPTED` | `NABL-GEO-2026-T1134` | `PENDING_WALL_MOUNT` |
| `RAIN-NH10-KM48-01` | Rain Gauge | Davis Aerocone 0.2mm | `DAV-AERO-7740` | `BENCH_ACCEPTED` | `IMD-MET-2026-R0921` | `PENDING_MAST_MOUNT` |
| `GW-NH10-KM48-01` | Gateway | RAKwireless RAK7289 | `RAK-7289-4411` | `BENCH_ACCEPTED` | `FACTORY-TEST-2026-G109` | `PENDING_SOLAR_MAST` |

**Fleet Totals**:
- **Registered**: 5
- **Installed**: 0
- **Commissioned**: 0
- **Bench Accepted**: 5
- **Live In-Situ Telemetry**: 0

---

## 3. Commissioning Checklist Evaluation

| Checklist Item | Description | Gate Result | Verification Artifact |
| :--- | :--- | :--- | :--- |
| **1. Identity Verification** | Physical barcode / QR match to manufacturer datasheet | `PASS` | `BARCODE_SCAN_VERIFIED` |
| **2. Physical Condition** | Housing integrity, O-ring seal, cable gland inspection | `PASS` | `INSPECTION_BENCH_PASS` |
| **3. Calibration Certificate** | Traceable NABL calibration within active validity interval | `PASS` | `NABL-GEO-2026-*` |
| **4. OTA Packet Codec** | 18-byte binary frame packing, scaling, and CRC16-CCITT | `PASS` | `BENCH_HIL_LOG_RUN48` |
| **5. Store-and-Forward** | Offline SQLite ring-buffer FIFO queueing & replay | `PASS` | `EDGE_BUFFER_REPLAY_TEST` |
| **6. Civil Borehole Drilling** | Rotary core drilling to target depth (12m/15m) | `PENDING` | `NOT_AVAILABLE` |
| **7. Azimuth Orientation** | Gyroscopic casing alignment within $\pm 1^\circ$ | `PENDING` | `NOT_AVAILABLE` |
| **8. Solar Power Stability** | 72h continuous power telemetry under monsoon sky | `PENDING` | `NOT_AVAILABLE` |
| **9. RF Path Margin** | LoRaWAN RSSI $> -115\text{ dBm}$, SNR $> -10\text{ dB}$ | `PENDING` | `NOT_AVAILABLE` |
| **10. 72h Burn-in Telemetry** | Monotonic timestamps, zero CRC corruption, drift $< 30\text{s}$ | `PENDING` | `NOT_AVAILABLE` |
| **11. Human Authority Sign-off**| BRO Executive Engineer cryptographic approval token | `PENDING` | `NOT_AVAILABLE` |

---

## 4. Commissioning Governance Verdict

Because items 6 through 11 are unresolved in the field, no sensor can or will be transitioned to `FIELD_COMMISSIONED`. The system status is definitively:

$$\mathbf{V4\_7\_BENCH\_VALIDATED\_FIELD\_PENDING}$$
