# PARVAT NETRA / PAHAD AI — PHASE V5.2
## SENSOR CALIBRATION CERTIFICATE EVIDENCE AUDIT REPORT

**Corridor**: CORR-NH10-SIKKIM-KM48 (NH-10 Rangpo–Singtam, Sikkim, KM 48.2)  
**Authority**: PARVAT NETRA Metrology & Quality Assurance Directorate  
**Date**: September 2026  
**Verdict**: `V5_2_PHYSICAL_DEPLOYMENT_PENDING`  
**Classification**: `OFFICIAL USE ONLY / LOCALHOST AUDIT`  

---

### 1. Executive Summary
Under the scientific integrity invariants of Phase V5.2, calibration references recorded as string metadata in software registries (`corridor_sensor_registry.json`) are rigorously prohibited from being recognized as accredited calibration evidence. Genuine calibration requires physical, signed, and stamped laboratory certificates from NABL/ISO-17025 accredited metrology laboratories.

### 2. Calibration Evidence Gate Evaluation

| Sensor ID | Declared Calibration Reference | Lab Accreditation Standard | Physical Certificate File On Disk | Cryptographic SHA-256 Hash | Calibration Status |
|---|---|---|---|---|---|
| `PIEZO-NH10-KM48-01` | `NABL-CAL-GK-2026-0812` | ISO/IEC 17025 (Pressure) | None (`field_evidence/certificates/*.pdf`) | UNVERIFIED | `CALIBRATION_EVIDENCE_MISSING` |
| `INCL-NH10-KM48-01` | `NABL-CAL-DGSI-2026-0441` | ISO/IEC 17025 (Angle/Displacement) | None (`field_evidence/certificates/*.pdf`) | UNVERIFIED | `CALIBRATION_EVIDENCE_MISSING` |
| `TILT-NH10-KM48-01` | `NABL-CAL-TILT-2026-0199` | ISO/IEC 17025 (Tilt Biaxial) | None (`field_evidence/certificates/*.pdf`) | UNVERIFIED | `CALIBRATION_EVIDENCE_MISSING` |
| `RAIN-NH10-KM48-01` | `NABL-CAL-RAIN-2026-1104` | WMO No. 8 / ISO 17025 | None (`field_evidence/certificates/*.pdf`) | UNVERIFIED | `CALIBRATION_EVIDENCE_MISSING` |
| `GW-NH10-KM48-01` | N/A (Edge Gateway) | TEC / WPC RF Compliance | None | UNVERIFIED | `NOT_APPLICABLE` |

### 3. Inspection of Storage Repositories
An automated scan of `field_evidence/certificates/` confirms:
- **Total Signed PDF Certificates Detected**: 0
- **Total Certified Calibration Reports**: 0
- **Integrity Rule**: No certificate reference string alone may satisfy the calibration evidence gate.

### 4. Operational Gating Action
Because zero physical certificates are deposited:
1. All sensor nodes remain locked in `CALIBRATION_EVIDENCE_MISSING`.
2. Calibration factors (multiplier $1.0$, offset $0.0$) operate as provisional defaults only.
3. No sensor node may be promoted to operational alarming without physical certificate deposition and hash validation.
