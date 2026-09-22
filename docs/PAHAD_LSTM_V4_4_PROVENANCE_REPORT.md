# PARVAT NETRA / PAHAD AI — Phase V4.4 Feature Provenance Report

**Document ID**: `PAHAD-DOC-V4-4-PROV-001`  
**Timestamp**: `2026-09-20T13:32:12.263672+00:00`  

---

## 1. 37-Channel Taxonomy & Provenance Ledger

| Category | Channel Count | Channels | Operational Meaning |
|---|---|---|---|
| **REANALYSIS** | 21 | `rain_1h`, `rain_3h`, `rain_6h`, `rain_12h`, `rain_24h`, `rain_48h`, `rain_72h`, `rain_96h`, `rain_120h`, `rain_168h`, `rain_intensity`, `rain_acceleration`, `antecedent_rain_3d`, `antecedent_rain_7d`, `api_30d`, `temperature_2m`, `soil_moisture`, `soil_moisture_change_24h`, `seismic_count_24h`, `max_magnitude_24h`, `nearest_seismic_distance` | Genuine reanalysis observations from ECMWF ERA5-Land (9km) and USGS FDSN |
| **PHYSICS_DERIVED** | 4 | `fos`, `pore_pressure`, `effective_stress`, `hydraulic_saturation` | Infinite slope Mohr-Coulomb mechanics and transient seepage |
| **STATIC** | 6 | `slope`, `aspect`, `elevation`, `curvature`, `soil_porosity`, `historical_susceptibility` | Cartosat 30m DEM terrain and GSI baseline susceptibility |
| **MISSING** | 9 | `piezometer_pressure`, `inclinometer_tilt`, `tilt_rate_24h`, `ground_displacement`, `displacement_velocity_24h`, `acoustic_emission`, `insar_velocity`, `ndvi`, `ndvi_anomaly` | Unmonitored historically on natural slopes; marked NaN |
| **SIMULATED** | 0 | None | **STRICT ZERO SYNTHETIC CURVES** |
