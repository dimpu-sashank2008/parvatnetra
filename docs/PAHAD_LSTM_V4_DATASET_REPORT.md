# PARVAT NETRA / PAHAD AI — LSTM V4 Real Temporal Dataset & Quality Audit Report

**Document ID**: `PAHAD-DOC-V4-DATASET-REPORT-001`  
**Generated At**: `2026-09-20T11:06:08.965087+00:00`  
**Author**: PAHAD AI Autonomous Engineering & Geotechnical Validation Sentinel  
**Problem Statement**: SIH 26001 (National Disaster Intelligence / NER Sentinel)  
**Final Verdict**: `V4_DATASET_REQUIRES_REWORK`

---

## 1. Executive Summary & Authoritative Verdict

This report documents the forensic extraction, temporal window audit, and quality assessment conducted on `data/observations/pahad_observations.db` and archival GSI/IMD disaster records to construct the **PAHAD LSTM V4 Real Temporal Dataset**.

```
============================================================
AUTHORITATIVE SCIENTIFIC VERDICT:
V4_DATASET_REQUIRES_REWORK
============================================================
```

### The Three Foundational Empirical Findings:
1. **The Temporal Dislocation Invariant**: All 17 documented GSI landslide disasters occurred between **May 16, 2022 and October 4, 2024**. The database `pahad_observations.db` contains records **exclusively from September 10 to September 20, 2026** (a 10.3-day span). There is zero overlap between recorded database telemetry and actual historical disaster events.
2. **The Continuity & Gap Bottleneck**: Within `pahad_observations.db` (`realtime_cri_evaluations`), the **maximum consecutive unbroken hourly telemetry period across any sector is exactly 6 hours**. There are 11 gaps $> 1.5$ hours and a major 35.07-hour gap. **Zero sectors possess an unbroken 72-hour continuous stream.**
3. **The Synthetic Origin of V3 Sequences**: In `train_lstm_v3.py`, sequences were constructed using `build_33f_sequence()`, which took single aggregate static summary rows from `phase5b_temporal_full.csv` and mathematically synthesized 72-hour antecedent curves backwards in time using polynomial linspace equations. Per instructions, `build_33f_sequence()` has been completely removed.

---

## 2. Source Database Inventory

The SQLite database `data/observations/pahad_observations.db` was fully audited:

| Table Name | Total Rows | Temporal Extent (UTC) | Sectors | Primary Contents | Provenance |
|---|---|---|---|---|---|
| `observations` | 151,543 | 2026-09-10 to 2026-09-20 | 33 | `fos` (50,687), `cri` (49,657), `event_prob` (50,687), sparse IoT | `MODELLED`, `DERIVED` |
| `realtime_cri_evaluations` | 6,017 | 2026-09-13 to 2026-09-20 | 20 | 24 columns (rainfall, pore pressure, FoS, displacement, CRI) | `[LIVE/HYBRID]` |
| `eoc_incidents` | 1,186 | 2026-09-11 to 2026-09-20 | 1 (`SK-NH10-KM48`) | Operational alert tickets (zero physical landslides) | `[SIMULATED]` |

---

## 3. Observation Counts & Temporal Sampling

- **Raw Evaluations Ingested**: 6,017 records.
- **Aggregated Hourly Telemetry Records Generated**: 643 records saved to `data/processed/lstm_v4_hourly_observations.csv`.
- **Sampling Cadence**: Nominal 1-hour resampling in UTC.
- **Cadence Realities**:
  - Telemetry was received in periodic batch runs (median inter-evaluation gap ~3 minutes during active runs).
  - Outages of 6 to 35 hours separate active monitoring bursts.

---

## 4. Continuity & Gaps Analysis

| Sector ID | Total Span (h) | Present Hours | Missing Hours | Max Consecutive (h) | Unbroken 72h Capable? |
|---|---|---|---|---|---|
| `AR-BHALUK-01` | 168 | 32 | 136 | 6 | **False** |
| `AR-PASIGHAT-01` | 168 | 32 | 136 | 6 | **False** |
| `AR-SELA-01` | 168 | 32 | 136 | 6 | **False** |
| `AS-DIMA-01` | 168 | 33 | 135 | 6 | **False** |
| `AS-GUWAHATI-01` | 168 | 33 | 135 | 6 | **False** |
| `ML-CHERRA-01` | 168 | 32 | 136 | 6 | **False** |
| `ML-SONAPUR-01` | 168 | 32 | 136 | 6 | **False** |
| `MN-JIRIBAM-01` | 168 | 32 | 136 | 6 | **False** |
| `MN-TUPUL-01` | 168 | 32 | 136 | 6 | **False** |
| `MZ-HUNTHAR-01` | 168 | 32 | 136 | 6 | **False** |

*(All 20 sectors exhibit identical gap structures with a maximum unbroken continuous period of 6 hours).*

---

## 5. Feature Missingness Analysis

When strictly rejecting synthetic imputation:
- **Available in DB Telemetry**: 6 variables (`rainfall_24h_mm`, `rainfall_intensity_mmh`, `seismic_magnitude`, `pore_pressure_kpa`, `displacement_rate_mm_day`, `physical_fos`).
- **Completely Missing in DB Telemetry**: 26 variables (`rain_1h`, `rain_3h`, `rain_6h`, `rain_12h`, `rain_48h`, `rain_72h`, `antecedent_rain_3d`, `antecedent_rain_7d`, `api_30d`, `soil_moisture`, `soil_porosity`, `effective_stress`, `hydraulic_saturation`, `tilt`, `tilt_rate_24h`, `ground_displacement`, `slope`, `aspect`, `elevation`, `curvature`, `ndvi`, `ndvi_anomaly`, `insar_velocity`, `seismic_count_24h`, `nearest_seismic_distance`, `historical_susceptibility`).
- **Missingness Preservation**: All missing variables are strictly encoded as `NaN` / `None`. **Zero artificial values were invented.**

---

## 6. Event Construction & Historical Disaster Catalog

Documented real-world landslide disasters cataloged in the dataset:

| Event ID | Date (UTC) | State | District | Corridor / Sector | Trigger Rainfall (mm) | Physical FoS | Source |
|---|---|---|---|---|---|---|---|
| `EV-01` | 2024-10-04 | Sikkim | Pakyong | `SK-NH10-KM48` | 185.0 | 0.62 | GSI Pakyong Field Inspection |
| `EV-02` | 2024-06-12 | Sikkim | Mangan | `SK-MANGAN-01` | 210.0 | 0.55 | ISRO DMSG / Sikkim SDMA |
| `EV-03` | 2023-10-04 | Sikkim | Gangtok | `SK-SINGTAM-01` | 140.0 | 0.48 | South Lhonak GLOF / GSI |
| `EV-04` | 2022-06-29 | Manipur | Noney | `MN-NONEY-01` | 180.0 | 0.68 | GSI Tupul Railway Breaches |
| `EV-05` | 2024-07-02 | Manipur | Tamenglong | `MN-TAMENG-01` | 165.0 | 0.74 | Manipur SDMA Monsoon Bulletin |
| `EV-06` | 2024-05-28 | Mizoram | Aizawl | `MZ-AIZAWL-MELTHUM` | 205.0 | 0.58 | Cyclone Remal GSI Report |
| `EV-07` | 2023-08-22 | Mizoram | Lunglei | `MZ-LUNGLEI-01` | 150.0 | 0.81 | Mizoram PWD / DDMA |
| `EV-08` | 2022-05-16 | Assam | Dima Hasao | `AS-DIMA-HASAO-01` | 230.0 | 0.52 | New Haflong Station Breaches |
| `EV-09` | 2024-06-18 | Assam | Cachar | `AS-CACHAR-01` | 170.0 | 0.76 | ASDMA Flood & Landslide Log |
| `EV-10` | 2022-06-17 | Meghalaya | East Khasi Hills | `ML-MAWSYNRAM-01` | 350.0 | 0.45 | GSI Shillong Plateau Survey |
| `EV-11` | 2024-07-10 | Meghalaya | East Khasi Hills | `ML-SHILLONG-01` | 160.0 | 0.79 | Meghalaya SDMA Log |
| `EV-12` | 2024-09-03 | Nagaland | Kohima | `NL-KOHIMA-01` | 175.0 | 0.72 | Nagaland NSDMA Assessment |
| `EV-13` | 2023-07-28 | Nagaland | Phek | `NL-PHEK-01` | 145.0 | 0.84 | GSI NLSM Archive |
| `EV-14` | 2024-06-25 | Arunachal | Tawang | `AR-TAWANG-01` | 190.0 | 0.65 | BRO Project Vartak |
| `EV-15` | 2023-06-20 | Arunachal | Papum Pare | `AR-ITANAGAR-01` | 155.0 | 0.80 | GSI Itanagar Road Survey |
| `EV-16` | 2024-08-20 | Tripura | North Tripura | `TR-JAMPUI-01` | 160.0 | 0.78 | Tripura SDMA Monsoon Log |
| `EV-17` | 2023-07-14 | Tripura | North Tripura | `TR-DHARMAN-01` | 135.0 | 0.85 | GSI NLSM Archive |

---

## 7. Target Construction

For every observation window, 4 independent multi-horizon binary targets are constructed based strictly on future event occurrence:
- `target_6h`: Event occurred within `(T, T+6h]` $ightarrow 1$, else $0$.
- `target_12h`: Event occurred within `(T, T+12h]` $ightarrow 1$, else $0$.
- `target_24h`: Event occurred within `(T, T+24h]` $ightarrow 1$, else $0$.
- `target_48h`: Event occurred within `(T, T+48h]` $ightarrow 1$, else $0$.

All targets are derived strictly from downstream ground-truth event timestamps. No target information was used to construct input features.

---

## 8. Leakage Audit

The automated leakage audit verified the following invariants:
- **Event Label $ightarrow$ Input Feature**: Zero instances. Target columns are isolated.
- **Future Rainfall $ightarrow$ Input**: Rainfall values at forecast origin represent only historical accumulations up to $T$.
- **Post-Event Measurements $ightarrow$ Input**: Antecedent windows terminate at or before $T$.
- **Model Inferences $ightarrow$ Input**: Previous model event probabilities (`event_probability_24h`, etc.) are stripped.
- **Cross-Partition Contamination**: Zero physical events appear in more than one partition.

---

## 9. Composite Risk Index (CRI) Audit

- **Input Variables to CRI**: Static slope susceptibility ($S$), 24h rainfall + intensity ($P$), ground anomaly from pore pressure + displacement + InSAR + seismic ($A$), road criticality ($V$), and previous event probability.
- **Downstream Dependency**: CRI is an alerting decision score produced *after* physical and statistical modeling.
- **Decision**: **EXCLUDED** from V4 features. Including CRI creates circular model-in-the-loop dependencies.

---

## 10. Factor of Safety (FoS) Audit

- **Physical FoS Calculation**: Infinite-slope Mohr-Coulomb equation:
  $$FoS = \frac{c' + (\gamma \cdot z - u) \tan\phi'}{\gamma \cdot z \cdot \sin\beta \cos\beta}$$
- **Audited Timing**: Computed strictly from slope geometry ($eta$), soil cohesion ($c'$), friction ($\phi'$), depth ($z$), and in-situ pore water pressure ($u$) at the prediction timestamp.
- **Decision**: **PERMISSIBLE** under Option A as an independent physics feature available at prediction origin.

---

## 11. Feature Provenance Matrix

| Feature | Provenance Class | Unit | Source | Prediction Availability |
|---|---|---|---|---|
| `rain_1h`, `rain_24h`, `rain_intensity` | `MEASURED` | mm, mm/h | IMD AWS / Open-Meteo | Realtime API |
| `rain_3h`, `rain_6h`, `rain_12h`, `rain_48h`, `rain_72h`, `api_3d`, `api_7d`, `api_30d` | `DERIVED_FROM_MEASUREMENTS` | mm | Temporal window integrations | Computed at origin |
| `pore_pressure`, `displacement_rate`, `tilt` | `MEASURED` | kPa, mm/day, deg | In-situ IoT Edge Gateways | Realtime LoRa/4G |
| `fos` (physical) | `MODEL_DERIVED` | dimensionless | Infinite Slope Mohr-Coulomb | Computed at origin |
| `slope`, `aspect`, `elevation`, `curvature` | `STATIC` | deg, m, 1/m | ISRO CartoDEM 30m | Cached PostGIS GIS Store |
| `soil_porosity` | `STATIC` | dimensionless | GSI Quadrangle Geotechnical Baseline | Cached PostGIS GIS Store |
| `ndvi`, `ndvi_anomaly`, `insar_velocity` | `EXTERNAL` | index, mm/yr | Sentinel-2 MSI / Sentinel-1 InSAR | Cached EO Store |
| `seismic_magnitude`, `seismic_count`, `seismic_distance` | `EXTERNAL` | Mw, count, km | NCS / USGS Realtime Feed | Realtime API |

---

## 12. Split Methodology & Dataset Sizes

Dataset partitions were constructed strictly via **Chronological Holdout + Grouped Event Isolation**:

| Split | Criteria | Unique Disasters | Total Rows | Historical Disasters | Negative DB Controls | SHA-256 Hash |
|---|---|---|---|---|---|---|
| **TRAIN** | Historical $\le 2023$ + Sept 13–15 DB | 8 (`EV-03, 04, 07, 08, 10, 13, 15, 17`) | **168** | 48 | 120 | `f7e194556840094a...` |
| **VAL** | Historical H1 2024 + Sept 16–17 DB | 5 (`EV-02, 05, 06, 09, 14`) | **336** | 33 | 303 | `ab682ed2ce288e0e...` |
| **TEST** | Historical H2 2024 + Sept 18–20 DB | 4 (`EV-01, 11, 12, 16`) | **244** | 24 | 220 | `f110d303463b1f82...` |

---

## 13. Data Limitations & Honest Scientific Disclosure

1. **Database Operational Isolation**: The live telemetry database only recorded from September 10 to September 20, 2026. It contains zero historical failure events.
2. **Short Continuous Spans**: The maximum uninterrupted hourly stream in any sector is 6 hours, precluding the formation of authentic unbroken 72-hour continuous sequences from the database alone.
3. **Discrete Historical Time-Steps**: Historical GSI/IMD disaster records only possess 5 to 6 discrete antecedent snapshot observations (T-48h, T-36h, T-24h, T-12h, T-6h, T-0h).
4. **Synthetic Interpolation Ceased**: The previous practice of synthetically manufacturing 72 hours via polynomial linspaces has been terminated.

---

## 14. Actionable Next Steps to Resolve Rework

To elevate the dataset from `V4_DATASET_REQUIRES_REWORK` to `V4_DATASET_READY_FOR_TRAINING`:
1. **Backfill Historical Hourly ERA5-Land Reanalysis**: Ingest authentic 1-hour precipitation, soil moisture, and temperature grids for the 17 GSI disaster sites for 72 hours prior to each failure (May 2022 to October 2024).
2. **Backfill IMD AWS Hourly Station Data**: Ingest recorded hourly rain gauge data from nearest AWS stations (e.g. Pakyong, Gangtok, Mangan, Haflong, Imphal, Shillong, Aizawl, Kohima).
3. **Continuous DB Logging**: Maintain continuous operational telemetry ingestion without 35-hour outages to accumulate genuine 72-hour continuous multi-feature streams.

```
============================================================
EXECUTION STATUS: STOPPED AS MANDATED.
NO NEURAL NETWORK TRAINING EXECUTED.
NO MODEL WEIGHTS CREATED OR MODIFIED.
v3 ARTIFACTS FULLY PRESERVED.
============================================================
```
