# PARVAT NETRA / PAHAD AI — Phase V4.3 Data Audit Report

**Document ID**: `PAHAD-DOC-V4-3-DATA-001`  
**Timestamp**: `2026-09-20T12:13:23.115450+00:00`  
**Phase**: `Phase V4.3 — Research Training & Scientific Diagnostics`  
**Operational Status**: **RESEARCH / OFFLINE ONLY (PRODUCTION DISABLED)**

---

## 1. Feature Provenance Matrix & Classification
All 32 feature channels audited across the 105 continuous 72-hour historical sequences:

| Category | Channel Count | Features | Source Provenance | Within-Seq Dynamics |
|---|---|---|---|---|
| **Reanalysis (Measured)** | 5 | `rain_1h`, `soil_moisture`, `seismic_count_24h`, `max_magnitude_24h`, `nearest_seismic_distance` | ECMWF ERA5-Land (9km grid) & USGS FDSN | Fully dynamic temporal series |
| **Derived Temporal** | 10 | `rain_3h`, `rain_6h`, `rain_12h`, `rain_24h`, `rain_48h`, `rain_72h`, `antecedent_rain_3d`, `antecedent_rain_7d`, `api_30d`, `rain_intensity` | Cumulative rolling calculations from hourly ERA5 | Fully dynamic rolling evolution |
| **Derived Physics** | 4 | `fos`, `pore_pressure`, `effective_stress`, `hydraulic_saturation` | Infinite Slope Mohr-Coulomb & transient seepage formulas | Dynamic response driven by moisture & rain |
| **Static DEM / Geoscience** | 6 | `slope`, `aspect`, `elevation`, `curvature`, `soil_porosity`, `historical_susceptibility` | Cartosat/SRTM 30m DEM & GSI National Landslide Map | Constant across all 72 hours (Zero Within-Seq Variance) |
| **Unmonitored Historical** | 7 | `tilt`, `tilt_rate_24h`, `ground_displacement`, `displacement_velocity_24h`, `ndvi`, `ndvi_anomaly`, `insar_velocity` | Absent historically on unmonitored slopes in 2022-2024 | Zero-masked (100% constant 0.0) |

## 2. Quantitative Provenance Breakdown
- **Genuinely Dynamic Channels**: 19 / 32 (59.4%)
- **Static DEM & Geological Channels**: 6 / 32 (18.8%)
- **Unmonitored Historically (Zero-Masked)**: 7 / 32 (21.9%)
- **`composite_risk_index_cri`**: **100% STRICTLY EXCLUDED** (Zero target leakage)
