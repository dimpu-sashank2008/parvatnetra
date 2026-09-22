# PARVAT NETRA / PAHAD AI — Phase V4.4 Data Source Audit

**Document ID**: `PAHAD-DOC-V4-4-SRC-001`  
**Timestamp**: `2026-09-20T13:32:12.261670+00:00`  

---

## 1. Authoritative Historical Data Sources

| Source Name | Dataset Version | Variables Extracted | Spatial Res | Temporal Res | Coverage Period | Retrieval Method | License / Notes |
|---|---|---|---|---|---|---|---|
| **ECMWF ERA5-Land** | ERA5-Land Reanalysis | `precipitation`, `soil_moisture_0_to_7cm`, `temperature_2m` | 9 km (0.1 deg) | Hourly | 1950–present | Open-Meteo Archive REST API (Deterministic Cache) | Copernicus Open Access / Open-Meteo Attribution |
| **USGS FDSN** | Catalog v1 | `magnitude`, `time`, `coordinates`, `depth` | Point coordinates | Continuous | 1900–present | USGS FDSN Web Service API | Public Domain USGS Earth Hazards |
| **Cartosat / SRTM** | CartoDEM 30m v3R1 | `slope`, `aspect`, `elevation`, `curvature` | 30 m | Static | 2014–present | ISRO Bhuvan / USGS EarthExplorer | Academic / Government Research Use |
| **GSI NLSM** | NLSM 2020 | `historical_susceptibility` | Regional Polygon | Static | 2014–2020 | GSI Bhukosh Open Geospatial Portal | Government of India Survey Authority |

## 2. Spatial Extraction Protocol
- **Methodology**: Nearest valid grid centroid within 4.5 km distance to the verified GSI disaster epicenter.
- **Elevation Adjustments**: Atmospheric lapse rate and hypsometric checks confirmed across mountain relief.
