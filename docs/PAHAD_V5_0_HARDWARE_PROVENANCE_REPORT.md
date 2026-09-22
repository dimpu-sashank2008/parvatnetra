# PARVAT NETRA / PAHAD AI — PHASE V5.0
## PHYSICAL HARDWARE PROVENANCE ACQUISITION REPORT

**Authoritative Status**: `PHYSICAL_EVIDENCE_PENDING`  
**Verdict**: `V5_0_HARDWARE_EVIDENCE_PENDING`  
**Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 KM48 Rangpo–Singtam, Sikkim)  
**System Designation**: Smart India Hackathon (SIH) 2026 AI-Assisted Research & Decision-Support Prototype  

---

### 1. Executive Summary
In compliance with Phase V5.0 Master Engineering Mandates, PARVAT NETRA enforces rigorous physical hardware provenance auditing across 9 distinct evidentiary dimensions. Declared serial numbers and hardware metadata in configuration registries are strictly distinguished from physical field hardware evidence.

Zero physical delivery challans or nameplate inspection photographs currently exist on disk for the 5 planned corridor sensor nodes. Consequently, all 5 nodes remain classified as `BENCH_ACCEPTED` with hardware identity audited as `UNVERIFIED_IDENTITY`.

---

### 2. Forensic Audit Matrix Across 9 Dimensions

| Sensor ID | Sensor Type | Declared Mfr & Model | Declared S/N | Nameplate Photo | Delivery Challan | Custody Record | Borehole Log | Calibration Cert | Installation Record | Commissioning Checklist | Gateway Route | Live Telemetry |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `PIEZO-NH10-KM48-01` | Piezometer | Geokon 4500AL-1.0-MPa | GK-4500-2026-0812 | MISSING | MISSING | MISSING | MISSING | MISSING | NOT_INSTALLED | PENDING | CONFIGURED | PENDING |
| `INCL-NH10-KM48-01` | Inclinometer | DGSI Digitilt-AT-Biaxial | DGSI-DAT-2026-0441 | MISSING | MISSING | MISSING | MISSING | MISSING | NOT_INSTALLED | PENDING | CONFIGURED | PENDING |
| `TILT-NH10-KM48-01` | Tiltmeter | Jewell Emerald Biaxial | JWL-EM-2026-1092 | MISSING | MISSING | MISSING | N/A (Surface) | MISSING | NOT_INSTALLED | PENDING | CONFIGURED | PENDING |
| `RAIN-NH10-KM48-01` | Rain Gauge | Texas Electronics TR-525USW | TX-TR525-2026-0319 | MISSING | MISSING | MISSING | N/A (Surface) | MISSING | NOT_INSTALLED | PENDING | CONFIGURED | PENDING |
| `GW-NH10-KM48-01` | Edge Gateway | Dragino/RAK Solar LoRaWAN | PN-GW-2026-0038 | MISSING | MISSING | MISSING | N/A (Mast) | MISSING | NOT_INSTALLED | PENDING | CONFIGURED | PENDING |

---

### 3. Hardware Provenance Verification Requirements
To transition any node from `BENCH_ACCEPTED` to `PHYSICAL_VERIFIED`:
1. **Nameplate Inspection Photograph**: High-resolution image showing manufacturer nameplate, legible serial number matching the registry, and tamper-evident seal, cryptographically hashed via SHA-256.
2. **Delivery Challan / Procurement Receipt**: Signed goods receipt note from authorized manufacturer/distributor with verified consignment tracking number.
3. **Chain of Custody Form**: Signed transfer documentation showing physical possession by BRO Project Swastik or SSDMA field engineering team.

Until these physical artifacts are acquired and ingested into `field_evidence/<sensor_id>/`, no node can be promoted.
