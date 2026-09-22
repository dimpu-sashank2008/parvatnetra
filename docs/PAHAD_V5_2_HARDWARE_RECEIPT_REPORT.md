# PARVAT NETRA / PAHAD AI — PHASE V5.2
## PHYSICAL HARDWARE RECEIPT & PROVENANCE AUDIT REPORT

**Corridor**: CORR-NH10-SIKKIM-KM48 (NH-10 Rangpo–Singtam, Sikkim, KM 48.2)  
**Authority**: PARVAT NETRA Metrology & Quality Assurance Directorate  
**Date**: September 2026  
**Verdict**: `V5_2_PHYSICAL_DEPLOYMENT_PENDING`  
**Classification**: `OFFICIAL USE ONLY / LOCALHOST AUDIT`  

---

### 1. Executive Summary
This report documents the rigorous physical hardware receipt and forensic chain-of-custody audit conducted for the 5 planned sensor nodes and gateway allocated to the **CORR-NH10-SIKKIM-KM48** pilot slope monitoring site. Under the strict anti-fabrication mandate of Phase V5.2, software declarations and configuration files are legally and operationally distinguished from verifiable physical possession.

### 2. Node-by-Node Receipt Audit Matrix

| Sensor ID | Sensor Type | Declared Make & Model | Declared Serial Number | Delivery Challan | Physical Nameplate Photo | Ground Truth Physical Status |
|---|---|---|---|---|---|---|
| `PIEZO-NH10-KM48-01` | Piezometer | Geokon 4500AL Vibrating Wire | `GK-4500AL-2026-0812` | UNVERIFIED (Missing) | UNVERIFIED (Missing) | `BENCH_ACCEPTED / FIELD_PENDING` |
| `INCL-NH10-KM48-01` | Inclinometer | DGSI Slope Indicator IPI | `DGSI-IPI-2026-0441` | UNVERIFIED (Missing) | UNVERIFIED (Missing) | `BENCH_ACCEPTED / FIELD_PENDING` |
| `TILT-NH10-KM48-01` | Tiltmeter | PN Biaxial MEMS Tiltmeter | `PN-TILT-2026-0199` | UNVERIFIED (Missing) | UNVERIFIED (Missing) | `BENCH_ACCEPTED / FIELD_PENDING` |
| `RAIN-NH10-KM48-01` | Rain Gauge | Texas Electronics TR-525M | `TE-TR525M-2026-1104` | UNVERIFIED (Missing) | UNVERIFIED (Missing) | `BENCH_ACCEPTED / FIELD_PENDING` |
| `GW-NH10-KM48-01` | LoRa Gateway | PN Edge Concentrator (SX1302) | `PN-GW-2026-0001` | UNVERIFIED (Bench Proto) | UNVERIFIED (Missing) | `BENCH_ACCEPTED / FIELD_PENDING` |

### 3. Verification Criteria & Forensic Evidence Rules
1. **Physical Nameplate Photograph**: High-resolution image showing manufacturer serial number matching registry, with cryptographic SHA-256 hash verified on disk. Currently, 0 matching photos exist in `field_evidence/photos/`.
2. **Delivery Challan / Consignment Note**: Verified physical dispatch/delivery document from OEM to field staging depot. Currently, 0 verified documents exist in `field_evidence/delivery/`.
3. **Custody Record**: Verified transfer from Border Roads Organisation (Project Swastik) / SSDMA logistics. Currently, 0 verified transfer receipts exist.

### 4. Findings & Operational Directive
- **Total Registered Nodes**: 5
- **Physically Verified on Mountain Slope**: 0
- **Delivery Challans Verified**: 0
- **Nameplate Photos Verified**: 0
- **Status Assignment**: All nodes retain stage `BENCH_ACCEPTED` with physical presence marked `NOT_INSTALLED`. Transition to `PHYSICAL_VERIFIED` is strictly gated until physical inspection and photographic custody logs are deposited.
