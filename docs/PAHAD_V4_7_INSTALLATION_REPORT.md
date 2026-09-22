# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Physical Sensor Installation Specification & Baseline Status Report

**Corridor**: `CORR-NH10-SIKKIM-KM48` (Rangpo–Singtam Geological Corridor, NH-10, Sikkim)  
**Document Version**: 1.0.0  
**Phase**: V4.7 — Physical Field Evidence & Sensor Acceptance  
**Installation Status**: `NOT_INSTALLED` (Physical Borehole & Mast Deployment Pending)  
**Authoritative Ledger**: `data/processed/field_evidence_registry.json`  

---

## 1. Executive Summary & Site Context

CORR-NH10-SIKKIM-KM48 spans Kilometer 48 of National Highway 10 along the Teesta River gorge in Pakyong/Gangtok districts, Sikkim. The slope is characterized by heavily fractured Daling Group phyllites and schists subject to rapid pore-pressure escalation during monsoonal cloudbursts and flash floods (e.g., October 2023 South Lhonak GLOF).

In strict accordance with the **Zero-Fabrication Data Integrity Invariant**, this report establishes that **0 out of 5 planned in-situ sensors are currently physically installed in the field**. All five instruments are bench-tested, calibrated, and held in warehouse staging under `BENCH_ACCEPTED` status awaiting civil borehole drilling by Border Roads Organisation (BRO) Project Swastik.

---

## 2. Canonical Installation Records

| Installation ID | Sensor ID | Sensor Type | Target Depth / Location | Mounting Specification | Planned Orientation | Installation Status | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `INST-PIEZO-KM48-01` | `PIEZO-NH10-KM48-01` | Vibrating-Wire Piezometer | 12.0 m (BH-1) | Sand filter pack with bentonite pellet seal | Vertical downhole | `NOT_INSTALLED` | `PENDING` |
| `INST-INCL-KM48-01` | `INCL-NH10-KM48-01` | MEMS Inclinometer String | 15.0 m (BH-2) | Grooved ABS casing with cement-bentonite grout | A-axis aligned to $240^\circ$ azimuth | `NOT_INSTALLED` | `PENDING` |
| `INST-TILT-KM48-01` | `TILT-NH10-KM48-01` | Biaxial Surface Tiltmeter | Retaining Wall Face (RW-1) | Anodized aluminum bracket anchored to pier | X-horiz, Y-plumb vertical | `NOT_INSTALLED` | `PENDING` |
| `INST-RAIN-KM48-01` | `RAIN-NH10-KM48-01` | Tipping Bucket Rain Gauge | Crest Weather Station (MET-1) | 1.5m rigid stainless steel mast with bird spikes | Horizontal level ($0.0^\circ$) | `NOT_INSTALLED` | `PENDING` |
| `INST-GW-KM48-01` | `GW-NH10-KM48-01` | LoRa Concentrator Gateway | Solar Mast Node (GW-1) | IP67 weatherproof enclosure, 60W solar array | Omnidirectional antenna vertical | `NOT_INSTALLED` | `PENDING` |

---

## 3. Physical Installation Requirements & Gating Protocol

To advance any sensor from `BENCH_ACCEPTED` to `INSTALLED`, the following physical criteria must be verified by a human field supervisor:
1. **Core Hole Logging & Borehole Calipering**: Rotary core drilling to target depth with standard RQD and lithology logging.
2. **Backfill & Sealing Integrity**: Verification of washed silica sand filter pack and impermeable bentonite grout plug to prevent surface water channeling.
3. **Casing Azimuth Alignment**: Inclinometer casing grooves surveyed using gyro-orientation tool with deviation $< 1.0^\circ$.
4. **Geodetic Differential GNSS Survey**: High-precision dual-frequency RTK GNSS survey recording real-world latitude, longitude, and ellipsoidal height. **No approximate or interpolated coordinates may be entered.**
5. **Photographic & Video Dossier**: Geo-tagged, timestamped high-resolution photographs of borehole head, grouting manifold, bracket mounting, and serial number plates.

---

## 4. Current Operational Boundary

Because installation status remains `NOT_INSTALLED`:
- Stream B Kinematic pipeline remains `UNAVAILABLE` (`PHYSICAL_TELEMETRY_PENDING`).
- Regional synoptic Stream A (FoS, satellite InSAR, IMD rainfall) serves as the sole operational hazard monitoring stream.
- Zero synthetic sensor feeds are permitted into operational decision pipelines.
