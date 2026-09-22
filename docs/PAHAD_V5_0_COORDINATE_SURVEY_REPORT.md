# PARVAT NETRA / PAHAD AI — PHASE V5.0
## GNSS COORDINATE SURVEY & SPATIAL PROVENANCE REPORT

**Authoritative Status**: `PENDING_FIELD_SURVEY`  
**Verdict**: `V5_0_HARDWARE_EVIDENCE_PENDING`  
**Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 KM48 Rangpo–Singtam, Sikkim)  

---

### 1. Geodetic Framework & Benchmark
Accurate deformation kinematic modeling requires sub-centimeter geodetic survey coordinates tied to national reference datum standards.

```
+-----------------------------------------------------------------------------------------+
|                              GEODETIC SURVEY SPECIFICATION                              |
+-----------------------------------+-----------------------------------------------------+
| Geodetic Datum                    | WGS-84 / UTM Zone 45N                               |
| Reference Benchmark Station       | SOI-GTS-RANGPO-BM14 (Survey of India Great Trig Stn)|
| Benchmark Elevation               | 612.45 meters Above Mean Sea Level (MSL)            |
| Mandatory Survey Method           | Dual-Frequency RTK-GNSS (Base Station + Rover)      |
| Horizontal Accuracy Tolerance     | ± 0.015 meters (15 mm)                              |
| Vertical Accuracy Tolerance       | ± 0.030 meters (30 mm)                              |
| Maximum Allowable Drift           | 0.050 meters (50 mm)                                |
| Current Survey Evidence           | PENDING_FIELD_SURVEY                                |
+-----------------------------------+-----------------------------------------------------+
```

---

### 2. Planned Sensor Coordinate Roster

| Node ID | Physical Asset | Planned Latitude | Planned Longitude | Planned Elevation (MSL) | Spatial Source | Verification Status |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `BH-NH10-KM48-01` | Borehole Collar & Casing | 27.2023° N | 88.5147° E | 620.0 m | GIS Corridor Plan | `PENDING_FIELD_SURVEY` |
| `TILT-NH10-KM48-01` | Biaxial Tiltmeter Plinth | 27.2025° N | 88.5149° E | 624.5 m | GIS Corridor Plan | `PENDING_FIELD_SURVEY` |
| `RAIN-NH10-KM48-01` | Optical Rain Gauge Mast  | 27.2030° N | 88.5152° E | 631.0 m | GIS Corridor Plan | `PENDING_FIELD_SURVEY` |
| `GW-NH10-KM48-01`   | Solar LoRa Gateway Mast  | 27.2028° N | 88.5150° E | 628.0 m | Line-of-Sight RF Study | `PENDING_FIELD_SURVEY` |

---

### 3. Spatial Evidence Audit Findings
- Planned coordinates derive from high-resolution DEM / GIS route planning models.
- No physical surveyor field book, raw RINEX observation files, or post-processed kinematic (PPK) baseline solutions exist on disk.
- In accordance with Phase V5.0 integrity rules, spatial coordinates are flagged as **`PENDING_FIELD_SURVEY`** and must not be declared as surveyed ground truth until field execution with BRO survey parties.
