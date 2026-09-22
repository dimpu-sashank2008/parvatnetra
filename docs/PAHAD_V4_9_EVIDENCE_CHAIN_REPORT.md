# PARVAT NETRA / PAHAD AI — PHASE V4.9 EVIDENCE CHAIN REPORT
## 12-Point First Live Telemetry Evidence Package & Forensic Audit Trail

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Phase**: V4.9 — Joint Field Installation, LoRa Gateway Alignment & First Live Telemetry Commissioning  
**Evidence Package Status**: `PENDING_FIELD_INSTALLATION`  
**Cryptographic Immutability**: Production V3 SHA-256 Verified  

---

### 1. The 12 Mandatory Evidence Requirements (Section 30)
Section 30 establishes that before any sensor telemetry is recognized as operational, a complete 12-point First Live Telemetry Evidence Package must be assembled and cryptographically sealed.

| Item # | Evidence Requirement | Verification Standard | Current Repository Status |
| :--- | :--- | :--- | :--- |
| **1** | Sensor Installation Evidence | GPS, casing depth, lithology log, mount photo | `PENDING_FIELD_DEPLOYMENT` |
| **2** | Calibration Evidence | ISO/IEC 17025 accredited laboratory certificate PDF | `CALIBRATION_EVIDENCE_MISSING` |
| **3** | Gateway Association | Gateway ID `GW-NH10-KM48-01` verified | `CONFIGURED_ONLY` |
| **4** | Packet Capture | Raw RF hex payload captured by LoRa concentrator | `BENCH_HIL_CAPTURED` |
| **5** | Packet Hash | SHA-256 checksum of raw over-the-air packet | `BENCH_VALIDATED` |
| **6** | Decoded Observation | Engineering units (kPa, mm, deg, mm/h) | `BENCH_VALIDATED` |
| **7** | Timestamp Comparison | Device RTC vs Ingest UTC ($\Delta t \le 60\text{ s}$) | `BENCH_VALIDATED` |
| **8** | CRC Verification | Hardware CRC-16 CCITT polynomial check | `CRC16_VALIDATED` |
| **9** | Backend Persistence ID | Unique UUID / monotonic row ID in DB | `BENCH_PERSISTED` |
| **10** | Sensor Health Result | Battery voltage, RSSI, SNR, temperature bounds | `BENCH_VALIDATED` |
| **11** | Provenance Badge | `[LIVE]` badge strictly restricted to field hardware | `PHYSICAL_TELEMETRY_PENDING` |
| **12** | Operator Record | Certified field technician signoff | `PENDING_JOINT_SIGN_OFF` |

---

### 2. Institutional Authorization Forensics (Section 27)
A critical finding of the Phase V4.9 forensic audit was the demotion of the placeholder token:
- **Investigated Token**: `"BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026"`
- **Forensic Assessment**: The token was identified as a software placeholder string created during prototype testing. No signed administrative MOU, operational signoff, or PKI digital signature is attached in the repository.
- **Remediation**: The token has been formally classified as `AUTHORIZATION_UNVERIFIED`. The system forbids advancing any sensor to `COMMISSIONED` using this token.
- **Binding Rule**: Public alerting, siren dispatch, and automated SACHET broadcasts require human administrative signoff and remain disabled (`ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`).

---

### 3. Conclusion
The 12-point evidence verification machinery is fully operational in code. Items 1, 2, and 12 await on-site execution during the upcoming joint field deployment.
