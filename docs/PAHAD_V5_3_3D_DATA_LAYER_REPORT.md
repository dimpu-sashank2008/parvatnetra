# PARVAT NETRA • PAHAD AI — PHASE V5.3
# SYNCHRONIZED 3D DATA LAYERS & GEOTECHNICAL REPRESENTATION REPORT

**Document ID**: `PN-DOC-V5_3-004`  
**Classification**: Geotechnical Data Layer Specification  
**Version**: `5.3.0`  
**Date**: `2026-09-21`  

---

## 1. Overview of 3D Data Layers

Phase V5.3 visualizes seven authoritative data modalities directly within the 3D scene without altering the underlying physical or machine-learning models:

### 1. Composite Risk Index (CRI) Risk Zones
- **Visual Encoding**: 3D terrain surface overlays with 5 standard color bands:
  - Low (0–20): `#10B981` (Emerald)
  - Moderate (20–40): `#EAB308` (Amber)
  - High (40–60): `#F97316` (Orange)
  - Very High (60–80): `#EA580C` (Red-Orange)
  - Extreme (80–100): `#DC2626` (Red)
- **KM48 Current Value**: `78.4 / 100` (`VERY HIGH`).

### 2. Physical Factor of Safety (FoS) Slip Surface
- **Location**: Pakyong Escarpment (`27.3300°N, 88.6100°E`, elevation $680\text{ m}$).
- **Formula**: Infinite-slope Mohr-Coulomb limit equilibrium:
  $$FoS = \frac{c' + (\gamma z \cos^2\beta - u)\tan\phi'}{\gamma z \sin\beta\cos\beta}$$
- **Current Metric**: $FoS = 1.04$ ($< 1.10$, Critical Hazard threshold).

### 3. Live Weather Telemetry
- Sourced from Open-Meteo High-Resolution NWP grid.
- Pakyong station: $14.2\text{ mm/h}$ intensity, $68.5\text{ mm}$ 24h accumulation.
- Badge: `[LIVE / OPEN-METEO]`.

### 4. Regional Seismic Hypocenters
- Sourced from USGS FDSNws regional feed.
- Recent event: M4.1 at depth $10.0\text{ km}$, $38\text{ km}$ SE of Pakyong.
- Badge: `[LIVE / USGS-FDSNWS]`.

### 5. InSAR Ground Deformation
- Sentinel-1 Descending Track 121 interferometry.
- LOS velocity: $-8.4\text{ mm/year}$ steady subsidence.
- Badge: `[HISTORICAL / INSAR-LOS]`.

### 6. Planned In-Situ Geotechnical Sensors
- Piezometer Borehole (`SITE-NH10-PIEZ-01`), depth $18.5\text{ m}$.
- Biaxial Tiltmeter (`SITE-NH10-TILT-01`), retaining wall crest.
- Inclinometer Casing (`SITE-NH10-INCL-01`), depth $25.0\text{ m}$.
- Truthful Status: `0 Physical Sensors Installed`, `0 Live Records`.
- Badge: `[PLANNED / BENCH TESTED / PHYSICAL TELEMETRY PENDING]`.

### 7. Lifeline Transportation Corridor (NH-10)
- BRO Project Swastik corridor line between Km 42 and Km 52.
- Current Status: `HAZARD WATCH — SINGLE LANE CONTROLLED PASSAGE`.
- Badge: `[HISTORICAL / BRO RECORDS]`.
