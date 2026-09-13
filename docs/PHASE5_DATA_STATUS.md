# PAHAD AI — Phase 5 Data Status & Provenance Audit

**Document**: `PHASE5_DATA_STATUS.md`  
**Classification**: Data Quality & Provenance Audit  
**Phase**: Phase 5 — Real Data Expansion & Live Predictive Inference  
**Status**: AUDITED & BENCHMARKED  

---

## 1. Verified Historical Event Catalog Summary

The core training dataset is strictly grounded in 17 catastrophic landslide events authenticated by national geological and disaster response bodies:

| State | Documented Events | Key High-Impact Disaster Sites | Primary Authoritative Source |
| :--- | :--- | :--- | :--- |
| **Sikkim** | 3 | NH-10 Km 48 (Pakyong), Mangan (North Sikkim), Singtam (GLOF surge) | GSI Sikkim Field Inspections, ISRO DMSG, SDMA |
| **Manipur** | 2 | Tupul Railway Construction Site (Noney), Tamenglong | GSI NER Disaster Report GSI-NER-MN-2022-004, SDMA |
| **Mizoram** | 2 | Melthum Stone Quarry (Cyclone Remal, Aizawl), Lunglei | Cyclone Remal GSI Report GSI-NER-MZ-2024-019, PWD |
| **Assam** | 2 | New Haflong Railway Breaches (Dima Hasao), Cachar (Silchar) | GSI Field Survey, Assam SDMA (ASDMA) |
| **Meghalaya** | 2 | Mawsynram Escarpment, Shillong-Barapani Corridor | GSI Shillong Plateau Survey, Meghalaya SDMA |
| **Nagaland** | 2 | Dzukou Valley / Kohima Bypass, Phek Hill Highway | Nagaland NSDMA Monsoon Bulletins, GSI NLSM |
| **Arunachal** | 2 | Tawang Sela Approach, Itanagar Capital Complex | BRO Project Vartak, GSI Arunachal Survey |
| **Tripura** | 2 | Jampui Hills Escarpment, Dharmanagar Link Road | Tripura SDMA Monsoon Log, GSI NLSM |

- **Total Documented Real Events**: **17**
- **Date Range**: May 16, 2022 to October 4, 2024
- **State Coverage**: 8 / 8 North Eastern Region (NER) States (100% regional representation)
- **Coordinate Integrity**: 100% valid WGS-84 coordinates within NER bounding box ($21.5^\circ - 29.5^\circ\text{N}$, $88.0^\circ - 97.5^\circ\text{E}$).
- **Timing Uncertainty**: All timestamps confirmed to $< 24\text{ hours}$ error margin.

---

## 2. Negative Control Strategy & Exclusion Buffers

Negative controls are essential for training a discriminative binary classifier that does not raise false alarms during non-hazardous rainfall.

### 2.1 Buffer Invariants
- **Temporal Exclusion Buffer**: $\pm 7\text{ days}$ around any documented positive event.
- **Spatial Exclusion Buffer**: $5.0\text{ km}$ radius around any known failure scarp.
- **Non-Trivial Terrain**: Controls require slope $> 15.0^\circ$ (flat plains are excluded as trivial negatives).

### 2.2 Control Inventory
- **Verified Negative Controls**: **19** (Phase 4 baseline) / **4** (strict dry-season non-event windows in Phase 5 temporal dataset).
- **Physical Verification**: Controls possess verified $FoS \ge 1.10$, indicating mechanical equilibrium.

---

## 3. Provenance & Imputation Protocol

| Feature Name | Primary Source | Production Provenance | Historical Training Source | Imputation Strategy (if missing) |
| :--- | :--- | :--- | :--- | :--- |
| `rainfall_24h` | IMD AWS / Open-Meteo | `[LIVE]` / `[CACHED]` | IMD daily rain logs / reanalysis | Training median ($165.0\text{ mm}$) |
| `soil_moisture` | In-situ probe / Satellite | `[LIVE]` / `[CACHED]` | Hydro-mechanical saturation | Training median ($0.52$) |
| `pore_pressure_kpa` | LoRaWAN Piezometer | `[LIVE]` | FoS limit-equilibrium reconstruction | Training median ($26.0\text{ kPa}$) |
| `tilt_deg` | MEMS Inclinometer | `[LIVE]` | Post-failure survey reconstruction | Training median ($3.5^\circ$) |
| `ground_displacement_mm` | InSAR / Total Station | `[HISTORICAL]` | GSI scarp survey logs | Training median ($38.0\text{ mm}$) |
| `slope_deg` | Copernicus GLO-30 DEM | `[MODELLED]` | GLO-30 30m DEM grid | Sector average ($39.0^\circ$) |
| `elevation_m` | Copernicus GLO-30 DEM | `[MODELLED]` | GLO-30 30m DEM grid | Sector average ($890.0\text{ m}$) |
| `fos` | Infinite Slope Engine | `[MODELLED]` | Mohr-Coulomb equation | Recomputed deterministically |
| `seismic_magnitude` | USGS / NCS | `[LIVE]` / `[CACHED]` | `[MISSING]` (historical events) | Default to $0.0$ |
| `ndvi_anomaly` | MODIS / Sentinel-2 | `[CACHED]` | `[MISSING]` (historical events) | Default to $0.0$ |

---

## 4. Remaining External Data Ingestion Roadblocks

To transition from `DATA-GROUNDED RESEARCH PROTOTYPE` to `PRODUCTION-CANDIDATE`, the following institutional integrations must be secured:
1. **GSI Bhukosh Enterprise Database API**: Real-time push integration with the National Landslide Susceptibility Mapping (NLSM) inventory to continuously ingest post-monsoon incident polygon reports.
2. **IMD Dedicated Disaster Weather Gateway**: High-speed authenticated access to Doppler Weather Radar (DWR) quantitative precipitation estimates (QPE) for the Agartala, Mohanbari, and Sohra radars.
3. **Broadband In-Situ Telemetry Deployment**: Expanding piezometric instrumentation from 2 pilot corridors to all 32 critical GSI sectors identified across the NER.
