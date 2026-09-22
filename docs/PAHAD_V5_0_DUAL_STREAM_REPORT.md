# PARVAT NETRA / PAHAD AI — PHASE V5.0
## DUAL-STREAM DATA ARCHITECTURE REPORT

**Authoritative Status**: `DUAL_STREAM_ISOLATION_ACTIVE`  
**Regional Macro-Stream**: `AVAILABLE`  
**Kinematic In-Situ Stream**: `UNAVAILABLE (PENDING_PHYSICAL_TELEMETRY)`  
**Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 KM48 Rangpo–Singtam, Sikkim)  
**Verdict**: `V5_0_HARDWARE_EVIDENCE_PENDING`  

---

### 1. Dual-Stream Architecture Design
PARVAT NETRA maintains a strict separation between broad regional observation feeds and hyper-local geotechnical telemetry:

```
               PARVAT NETRA DUAL-STREAM PIPELINE
               
+─────────────────────────────────────────────────────────────+
| STREAM 1: REGIONAL MACRO-STREAM [STATUS: AVAILABLE]        |
|  - IMD Gridded Rainfall & Real-Time API Feeds               |
|  - CWC Teesta River Hydrometric Gauges (Melli / Singtam)    |
|  - Sentinel-1 InSAR LOS Displacement Velocities (Offline)   |
|  - USGS / NCS Regional Earthquake Seismic Hypocenters       |
|  --> Powers Regional Slope Susceptibility & Corridor CRI    |
+─────────────────────────────────────────────────────────────+
                               │
                               ▼
               MULTIMODAL FUSION ENGINE (PAHAD AI)
                               ▲
                               │
+─────────────────────────────────────────────────────────────+
| STREAM 2: KINEMATIC IN-SITU PILOT [STATUS: UNAVAILABLE]     |
|  - Deep Borehole Inclinometer BH-1 (Displacement mm)        |
|  - Vibrating-Wire Piezometer BH-1 (Pore Water Pressure kPa) |
|  - Surface Biaxial Tiltmeter (Angular Deflection deg)       |
|  - Optical Corridor Rain Gauge (Intensity mm/h)             |
|  --> Awaiting Physical Installation at NH-10 KM48           |
+─────────────────────────────────────────────────────────────+
```

---

### 2. Contamination Safeguards
1. **Zero Fabrication**: In-situ sensors report `NaN` / `UNAVAILABLE`. The system never fills missing telemetry with synthetic values.
2. **Autonomous Regional Operation**: Regional corridor risk calculations (CRI, IMD Antecedent Precipitation Index) function reliably using Stream 1 alone.
3. **No Blended Claims**: UI badges explicitly distinguish regional macro data (`[LIVE / SATELLITE]` or `[LIVE / METEOROLOGICAL]`) from hillslope sensor telemetry (`[PENDING / IN-SITU]`).
