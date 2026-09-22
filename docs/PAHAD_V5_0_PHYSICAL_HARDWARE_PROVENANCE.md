# PARVAT NETRA / PAHAD AI — PHASE V5.0
## PHYSICAL HARDWARE PROVENANCE ACQUISITION & DEVICE IDENTITY AUDIT

**Authoritative Verdict**: `V5_0_EVIDENCE_PENDING`  
**Evaluation Scope**: NH-10 KM48 Geological Corridor, Sikkim (`CORR-NH10-SIKKIM-KM48`)  
**Standard**: Smart India Hackathon (SIH) 2026 / National Disaster Management Authority (NDMA) OASIS CAP  

---

### 1. Executive Summary

Phase V5.0 establishes an unsparing, forensic audit of physical hardware provenance for all planned sensor nodes in the NH-10 KM48 pilot instrumentation corridor. In accordance with the non-negotiable data honesty protocols of PARVAT NETRA, software declarations and bench simulator records are strictly segregated from physical reality.

```
+-----------------------------------------------------------------------------------------+
|                                HARDWARE PROVENANCE MATRIX                               |
+------------------------+-------------------+-----------------+--------------------------+
| Dimension              | Registry Declared | Physical On-Disk| Forensic Status          |
+------------------------+-------------------+-----------------+--------------------------+
| Physical Sensor Nodes  | 5 Nodes           | 0 Devices       | PHYSICAL_EVIDENCE_MISSING|
| Nameplate Photographs  | Declared Serials  | 0 Images (JPG)  | UNVERIFIED_IDENTITY      |
| Delivery Challans      | Declared Orders   | 0 Documents     | DELIVERY_EVIDENCE_MISSING|
| Chain of Custody Logs  | Declared Partners | 0 Signed Logs   | CUSTODY_PENDING          |
| Borehole Drilling Logs | 25m Planned Depth | 0 Physical Logs | BOREHOLE_EVIDENCE_MISSING|
| Calibration Certs      | Declared NABL IDs | 0 External PDFs | CALIBRATION_EVID_MISSING |
| Field Mounting Records | Planned Anchors   | 0 Signed Records| NOT_INSTALLED            |
| Live Telemetry Packets | 8,640 Bench Frames| 0 Live Packets  | PHYSICAL_TELEMETRY_PEND_ |
+------------------------+-------------------+-----------------+--------------------------+
```

---

### 2. Node-by-Node Forensic Audit

#### 2.1 Node PIEZO-NH10-KM48-01 (Vibrating Wire Piezometer)
- **Declared Specification**: Geokon 4500AL Vibrating Wire Piezometer, S/N: `GK-4500AL-2026-0812`.
- **Target Location**: NH-10 KM48, Downhole Borehole `BH-NH10-KM48-01`, Depth: 12.0m.
- **Nameplate Photograph**: `MISSING` (No authenticated optical photograph on disk).
- **Delivery Challan**: `MISSING` (No vendor delivery note / purchase invoice).
- **Laboratory Calibration**: `CALIBRATION_EVIDENCE_MISSING` (String `NABL-CAL-GK-2026-0812` declared in registry, but no ISO 17025 / NABL signed PDF present).
- **Physical Installation**: `NOT_INSTALLED` (Borehole drilling pending field execution).
- **Device Status**: `BENCH_ACCEPTED` (Firmware and HIL loopback validated; physical device unverified).

#### 2.2 Node INCL-NH10-KM48-01 (In-Place Inclinometer)
- **Declared Specification**: DGSI In-Place Inclinometer (IPI), S/N: `DGSI-IPI-2026-0441`.
- **Target Location**: NH-10 KM48, Downhole ABS Casing `BH-NH10-KM48-01`, Depth: 15.0m.
- **Nameplate Photograph**: `MISSING`.
- **Delivery Challan**: `MISSING`.
- **Laboratory Calibration**: `CALIBRATION_EVIDENCE_MISSING` (Declared `NABL-CAL-DGSI-2026-0441`).
- **Physical Installation**: `NOT_INSTALLED`.
- **Device Status**: `BENCH_ACCEPTED` (Digital twin and tilt displacement algorithms verified).

#### 2.3 Node TILT-NH10-KM48-01 (Surface MEMS Tiltmeter)
- **Declared Specification**: PARVAT-NETRA Metrology Biaxial Surface Tiltmeter, S/N: `PN-TILT-2026-0199`.
- **Target Location**: NH-10 KM48, Crown Scarp Bedrock Anchor, Depth: 0.0m.
- **Nameplate Photograph**: `MISSING`.
- **Delivery Challan**: `MISSING`.
- **Laboratory Calibration**: `CALIBRATION_EVIDENCE_MISSING`.
- **Physical Installation**: `NOT_INSTALLED`.
- **Device Status**: `BENCH_ACCEPTED`.

#### 2.4 Node RAIN-NH10-KM48-01 (Tipping Bucket Rain Gauge)
- **Declared Specification**: PARVAT-NETRA Metrology 0.2mm Tipping Bucket Rain Gauge, S/N: `PN-RAIN-2026-0082`.
- **Target Location**: NH-10 KM48, Solar Mast Weather Station, Depth: 0.0m.
- **Nameplate Photograph**: `MISSING`.
- **Delivery Challan**: `MISSING`.
- **Laboratory Calibration**: `CALIBRATION_EVIDENCE_MISSING`.
- **Physical Installation**: `NOT_INSTALLED`.
- **Device Status**: `BENCH_ACCEPTED`.

#### 2.5 Node GW-NH10-KM48-01 (Solar LoRaWAN Concentrator Node)
- **Declared Specification**: IP67 Outdoor LoRaWAN Concentrator Gateway, S/N: `PN-GW-2026-0038`.
- **Target Location**: NH-10 KM48, Highway Ridge Mast (Line-of-Sight to Slope).
- **Nameplate Photograph**: `MISSING`.
- **Delivery Challan**: `MISSING`.
- **Firmware Status**: `v3.0.1-gateway-hil` (Verified in bench simulation).
- **Physical Installation**: `NOT_INSTALLED`.
- **Device Status**: `CONFIGURED_ONLY`.

---

### 3. Verification Conclusion

PARVAT NETRA maintains absolute scientific transparency: while the digital architecture, codecs, and bench simulators are 100% operational, physical hardware custody remains pending field acquisition. The status of all 5 nodes is authoritatively designated as `UNVERIFIED_IDENTITY` / `BENCH_ACCEPTED`.
