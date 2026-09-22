# PARVAT NETRA / PAHAD AI — PHASE V5.0
## METROLOGICAL TRACEABILITY & CALIBRATION FORENSICS REPORT

**Authoritative Status**: `CALIBRATION_EVIDENCE_MISSING`  
**Verdict**: `V5_0_HARDWARE_EVIDENCE_PENDING`  
**Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 KM48 Rangpo–Singtam, Sikkim)  

---

### 1. Executive Summary
A forensic inspection was conducted across all configuration registries, data directories, and field evidence folders to verify physical calibration certificates and ISO/IEC 17025 / NABL metrological traceability claims for hillslope instrumentation at NH-10 KM48.

The inspection determined that while reference tokens such as `NABL-CAL-GK-2026-0812` exist within registry schemas, zero authenticated external calibration laboratory certificate PDFs or cryptographic signatures exist within the repository.

Per Section 8 and Section 14 of Phase V5.0 rules:
- Declared calibration strings **do not constitute evidence** of calibration.
- All 5 sensor nodes are assigned calibration status **`CALIBRATION_EVIDENCE_MISSING`**.
- Institutional claims referencing NABL accreditation are classified as **`UNSUPPORTED`**.

---

### 2. Sensor Node Calibration Audit

| Sensor ID | Sensor Type | Declared Calibration String | Certificate on Disk | Laboratory Traceability | Forensic Status |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `PIEZO-NH10-KM48-01` | Piezometer | `NABL-CAL-GK-2026-0812` | None | Unverified | `CALIBRATION_EVIDENCE_MISSING` |
| `INCL-NH10-KM48-01` | Inclinometer | `NABL-CAL-DGSI-2026-0441` | None | Unverified | `CALIBRATION_EVIDENCE_MISSING` |
| `TILT-NH10-KM48-01` | Tiltmeter | `CAL-JWL-EM-2026-1092` | None | Unverified | `CALIBRATION_EVIDENCE_MISSING` |
| `RAIN-NH10-KM48-01` | Rain Gauge | `CAL-TX-TR525-2026-0319` | None | Unverified | `CALIBRATION_EVIDENCE_MISSING` |
| `GW-NH10-KM48-01` | LoRa Gateway | `CAL-RF-IN865-2026-0038` | None | Unverified | `CALIBRATION_EVIDENCE_MISSING` |

---

### 3. Metrological Requirements for Field Commissioning
Before any physical sensor observation can be used for operational safety decisions, the following must be provided and cryptographically logged:
1. **Manufacturer Calibration Sheet**: Showing zero-drift polynomial coefficients, gauge factors, and thermal coefficients.
2. **NABL / ISO-17025 Accredited Laboratory Certificate**: Documenting test rig identification, traceability to national standards (NPL India / NIST), uncertainty budgets, and valid calibration dates.
3. **Pre-Installation Zero Verification**: On-site atmospheric zero-pressure and plumb-line baseline readings recorded before downhole lowering.
