# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Sensor Hardware Identity & Serial Number Forensic Audit Report

**Document Version**: 1.0.0  
**Phase**: V4.8 Real Telemetry Evidence Audit & First-Data Foundation  
**System Status**: `V4_8_DATA_FOUNDATION_READY`  
**Target Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 Rangpo–Singtam Geological Corridor, Sikkim)  
**Date**: September 2026  

---

## 1. Physical Device Verification Standard

To prevent fraudulent claims of sensor deployments in disaster monitoring, PARVAT NETRA distinguishes between two distinct levels of hardware identification:

1. **Syntactically Valid Hardware Declaration**: A non-empty, non-placeholder serial number adhering to manufacturer naming conventions recorded in a JSON registry.
2. **Physically Verified Sensor Identity**: A hardware device supported by external evidence (e.g. factory delivery receipt, photographed serial nameplate, MAC/DevEUI cryptographic attestation, or NABL laboratory chain-of-custody document).

---

## 2. Sensor Identity Audit Matrix

| Sensor Node ID | Claimed Manufacturer & Model | Declared Serial Number | Nameplate Photo in Repo | Delivery Receipt in Repo | Classification | Operational Trust |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `PIEZO-NH10-KM48-01` | Geokon 4500AL Vibrating Wire | `GK-4500AL-9988` | ABSENT | ABSENT | `SOFTWARE_DECLARATION` | `UNVERIFIED_IDENTITY` |
| `INCL-NH10-KM48-01` | RST Instruments MEMS-IPI | `RST-MEMS-5521` | ABSENT | ABSENT | `SOFTWARE_DECLARATION` | `UNVERIFIED_IDENTITY` |
| `TILT-NH10-KM48-01` | Encardio-Rite EAN-92M | `ENC-92M-3312` | ABSENT | ABSENT | `SOFTWARE_DECLARATION` | `UNVERIFIED_IDENTITY` |
| `RAIN-NH10-KM48-01` | Davis Aerocone 0.2mm Bucket | `DAV-AERO-7740` | ABSENT | ABSENT | `SOFTWARE_DECLARATION` | `UNVERIFIED_IDENTITY` |
| `GW-NH10-KM48-01` | RAKwireless RAK7289 LoRaWAN | `RAK-7289-4411` | ABSENT | ABSENT | `SOFTWARE_DECLARATION` | `UNVERIFIED_IDENTITY` |

**Audit Finding**: None of the five instruments possesses external documentary proof of physical custody in the repository. Therefore, under Section 4 of the V4.8 Master Engineering Prompt:
$$\textbf{Status} = \textbf{UNVERIFIED\_IDENTITY}$$
The platform strictly refuses to claim `PHYSICAL_SENSOR_VERIFIED`.

---

## 3. Automated Anti-Placeholder Quarantine Engine

The `SensorAcceptanceEngine` (`engine/sensor_acceptance_engine.py`) and `TelemetryEvidenceAuditEngine` (`engine/telemetry_evidence_audit_engine.py`) actively guard against placeholder entries.

### Quarantine Test Results:
- Serial numbers matching placeholder patterns (`""`, `"none"`, `"null"`, `"tbd"`, `"unknown"`, `"0000"`, `"pending"`) are immediately rejected.
- When an operator or automated test submits a placeholder serial, the engine transitions the node directly to `STATE_UNVERIFIED_IDENTITY` and records an immutable audit violation.
- Verified in `tests/test_v4_8_evidence_audit.py::test_audit_placeholder_serial_rejection`.

---

## 4. Path to Physical Identity Verification (Phase V4.9)

To promote an instrument from `SOFTWARE_DECLARATION_ONLY` to `PHYSICAL_SENSOR_VERIFIED`:
1. **Physical Delivery Receipt**: Upload digital PDF of shipping manifest or warehouse inspection sheet.
2. **Serial Nameplate Photograph**: High-resolution photograph of physical engraved/printed serial plate on the transducer body.
3. **DevEUI Cryptographic Matching**: LoRaWAN Over-The-Air Activation (OTAA) join verification matching the hardware factory DevEUI.
4. **Append-Only Evidence Manifest**: Automatic SHA-256 hash generation and ledger recording via `POST /api/telemetry/evidence`.
