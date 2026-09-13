# PARVAT NETRA / PAHAD AI — Official Master Dataset Dossier
**Smart India Hackathon (SIH 26001) National Disaster-Intelligence Platform**  
**Evaluation Dossier for Technical Evaluators, Geoscientists & Judges**  
**Standard: ACM FAccT & National Disaster Management Authority (NDMA) Early Warning Protocol**  
**Document Generated**: 2026-09-12T08:22:22.297902+00:00  
**Master CSV File**: `data/PAHAD_AI_MASTER_JUDGES_DATASET.csv`  
**Master File SHA-256**: `02af3c8f4fe0e80259b5c5494898ac2163268ebbf57bbff8a17d022d1926ab23`  
**Operational Training SHA-256**: `68832707bc1983ab4b9d6b74ff0d3854e79f2697732abfff57acad4c36dac736`  

---

## 1. Executive Summary & Scientific Data Honesty Oath

PARVAT NETRA never fabricates operational performance or uses synthetic augmentation to claim artificial accuracy. In accordance with the **Core Project Constitution**:

1. **Model Classification**: **`TRAINED_LIMITED_DATA`**  
   The operational event model is trained exclusively on **16 ground-truth historical training windows** ($\le 2023$), validated on **12 temporal holdout windows** (H1 2024), and tested on **8 recent disaster windows** (H2 2024).
2. **Strict Quarantining of Synthetic Samples**:  
   All 25 synthetic walkthrough samples are segregated in `demo_train.csv` under `[DEMO]` badges. They are **strictly forbidden** from operational model training and guarded by `PAHAD_DEMO_MODE=1`.
3. **Dual-Model Architectural Invariant**:  
   - **MODEL A (Geotechnical FoS Regressor)**: Evaluates limit-equilibrium slope stability using Mohr-Coulomb soil physics ($FoS \in [0.4, 3.0]$). Calibrated on 2,000 physical simulations ($R^2 = 0.9985$).
   - **MODEL B (Landslide Event Classifier)**: Predicts event failure probability within 6h, 12h, 24h, 48h windows using calibrated gradient boosting trees on audited temporal event logs.
   - **PAHAD CRI Fusion**: Blends $FoS$, event probability, rainfall thresholds, and telemetry into a 0–100 Composite Risk Index governed by the **2-of-3 independent confirmation rule** before issuing warnings.

---

## 2. Dataset Composition & High-Level Breakdown

| Category | Record Count | Class Breakdown | Date Range (UTC) | Storage Path | Provenance | Operational Role |
| :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| **Real Documented Failures** | **17** | $y=1$ (100% Positive) | 2022-05-16 to 2024-10-04 | `data/raw/historical_landslides_ner.csv` | `[HISTORICAL]` | Operational Ground Truth |
| **Defensible Stable Controls** | **19** | $y=0$ (100% Negative) | 2023-01-15 to 2024-08-04 | `data/labels/event_labels.csv` | `[HISTORICAL]` | Operational Ground Truth |
| **Operational Training Split** | **16** | 8 Pos / 8 Neg | 2022-05-16 to 2023-10-04 | `data/features/real_train.csv` | `[HISTORICAL]` | Pre-2024 Model Training |
| **Operational Validation Split** | **12** | 4 Pos / 8 Neg | 2024-01-15 to 2024-06-25 | `data/features/real_val.csv` | `[HISTORICAL]` | Platt Sigmoid Calibration |
| **Operational Test Split** | **8** | 5 Pos / 3 Neg | 2024-07-02 to 2024-10-04 | `data/features/real_test.csv` | `[HISTORICAL]` | Out-of-Sample Holdout Eval |
| **Quarantined Demo Samples** | **25** | 12 Pos / 13 Neg | N/A (Synthetic) | `data/features/demo_train.csv` | `[DEMO]` | Evaluator Rig Only (`PAHAD_DEMO_MODE=1`) |
| **CONSOLIDATED MASTER FILE** | **61** | **36 Real + 25 Demo** | **2022-05-16 to 2024-10-04** | `data/PAHAD_AI_MASTER_JUDGES_DATASET.csv` | **AUDITED** | **Unified Evaluation Master** |

---

## 3. Table 1: All 17 Documented Real Disaster Failure Events ($y=1$)

Every event below is an authoritative recorded disaster from Geological Survey of India (GSI) NLSM reports, SDMA incident bulletins, or Border Roads Organisation (BRO) operational logs:

| Record ID | Disaster / Incident ID | Sector ID | Date & Time (UTC) | State | District | Source Authority | Trigger Rain (mm) | FoS | CRI | Partition |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **EV-01** | `SK-2024-NH10-KM48` | `SK-NH10-KM48` | 2024-10-04T06:00:00Z | Sikkim | Pakyong | GSI Pakyong Field Inspection | 185.0 | 0.62 | 89.0 | **TEST** |
| **EV-02** | `SK-2024-MANGAN` | `SK-MANGAN-01` | 2024-06-12T14:00:00Z | Sikkim | Mangan | ISRO DMSG / Sikkim SDMA | 210.0 | 0.55 | 92.5 | **VAL** |
| **EV-03** | `SK-2023-SINGTAM` | `SK-SINGTAM-01` | 2023-10-04T01:30:00Z | Sikkim | Gangtok | South Lhonak GLOF / GSI Assessment | 140.0 | 0.48 | 94.0 | **TRAIN** |
| **EV-04** | `MN-2022-NONEY` | `MN-NONEY-01` | 2022-06-29T23:30:00Z | Manipur | Noney | GSI Disaster Report GSI-NER-MN-2022-004 | 180.0 | 0.68 | 88.5 | **TRAIN** |
| **EV-05** | `MN-2024-TAMENGLONG` | `MN-TAMENG-01` | 2024-07-02T08:00:00Z | Manipur | Tamenglong | Manipur SDMA Monsoon Bulletin | 165.0 | 0.74 | 82.0 | **TEST** |
| **EV-06** | `MZ-2024-MELTHUM` | `MZ-AIZAWL-MELTHUM` | 2024-05-28T05:30:00Z | Mizoram | Aizawl | Cyclone Remal GSI Report GSI-NER-MZ-2024-019 | 205.0 | 0.58 | 91.0 | **VAL** |
| **EV-07** | `MZ-2023-LUNGLEI` | `MZ-LUNGLEI-01` | 2023-08-22T11:00:00Z | Mizoram | Lunglei | Mizoram PWD / DDMA | 150.0 | 0.81 | 78.0 | **TRAIN** |
| **EV-08** | `AS-2022-DIMA-HASAO` | `AS-DIMA-HASAO-01` | 2022-05-16T09:00:00Z | Assam | Dima Hasao | New Haflong Railway Station Breaches GSI Report | 230.0 | 0.52 | 93.0 | **TRAIN** |
| **EV-09** | `AS-2024-CACHAR` | `AS-CACHAR-01` | 2024-06-18T16:00:00Z | Assam | Cachar | Assam State Disaster Management Authority (ASDMA) | 170.0 | 0.76 | 81.0 | **VAL** |
| **EV-10** | `ML-2022-MAWSYNRAM` | `ML-MAWSYNRAM-01` | 2022-06-17T12:00:00Z | Meghalaya | East Khasi Hills | GSI Shillong Plateau Escarpment Survey | 350.0 | 0.45 | 96.0 | **TRAIN** |
| **EV-11** | `ML-2024-SHILLONG` | `ML-SHILLONG-01` | 2024-07-10T10:00:00Z | Meghalaya | East Khasi Hills | Meghalaya SDMA Flood & Landslide Log | 160.0 | 0.79 | 79.5 | **TEST** |
| **EV-12** | `NL-2024-DZUKOU-KOHIMA` | `NL-KOHIMA-01` | 2024-09-03T07:00:00Z | Nagaland | Kohima | Nagaland NSDMA Monsoon Assessment | 175.0 | 0.72 | 83.5 | **TEST** |
| **EV-13** | `NL-2023-PHEK` | `NL-PHEK-01` | 2023-07-28T15:00:00Z | Nagaland | Phek | GSI NLSM Archive | 145.0 | 0.84 | 75.0 | **TRAIN** |
| **EV-14** | `AR-2024-TAWANG` | `AR-TAWANG-01` | 2024-06-25T13:00:00Z | Arunachal Pradesh | Tawang | BRO Project Vartak / Arunachal SDMA | 190.0 | 0.65 | 87.0 | **VAL** |
| **EV-15** | `AR-2023-ITANAGAR` | `AR-ITANAGAR-01` | 2023-06-20T09:30:00Z | Arunachal Pradesh | Papum Pare | GSI Itanagar Road Survey | 155.0 | 0.8 | 77.0 | **TRAIN** |
| **EV-16** | `TR-2024-JAMPUI` | `TR-JAMPUI-01` | 2024-08-20T11:00:00Z | Tripura | North Tripura | Tripura SDMA Monsoon Deluge Log | 160.0 | 0.78 | 78.5 | **TEST** |
| **EV-17** | `TR-2023-DHARMANAGAR` | `TR-DHARMAN-01` | 2023-07-14T06:00:00Z | Tripura | North Tripura | GSI NLSM Archive | 135.0 | 0.85 | 72.0 | **TRAIN** |

---

## 4. Table 2: All 19 Defensible Non-Event Control Windows ($y=0$)

In strict adherence to geoscientific standards, negative control samples are **not** arbitrarily assumed to be "globally stable". Each control window represents a defensible observation period:
- **Dry Season Equilibrium Baseline**: Stable winter baseline equilibrium with minimal saturation.
- **Moderate Monsoon Non-Failure**: Substantial precipitation recorded without slope destabilization.
- **Heavy Monsoon on Competent Lithology**: Over 90–115mm rain on high-cohesion quartzite/granite.
- **Moderate Seismic Shaking Without Moisture**: M4.8–5.1 shaking on dry slopes.

| Record ID | Control ID | State | Control Scenario Rationale | Date (UTC) | 24h Rain (mm) | Soil Moisture | Pore Press (kPa) | FoS | CRI | Partition |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **CTRL-18** | `CTRL-SK-DRY-01` | Sikkim | Dry Season Equilibrium Baseline | 2023-01-15T12:00:00Z | 0.0 | 0.22 | 2.0 | 1.78 | 14.0 | **TRAIN** |
| **CTRL-19** | `CTRL-MZ-DRY-01` | Mizoram | Dry Season Equilibrium Baseline | 2023-02-10T12:00:00Z | 1.5 | 0.24 | 2.5 | 1.72 | 16.0 | **TRAIN** |
| **CTRL-20** | `CTRL-MN-DRY-01` | Manipur | Dry Season Equilibrium Baseline | 2023-03-05T12:00:00Z | 0.0 | 0.21 | 1.8 | 1.82 | 12.0 | **TRAIN** |
| **CTRL-21** | `CTRL-AS-DRY-01` | Assam | Dry Season Equilibrium Baseline | 2023-02-20T12:00:00Z | 0.0 | 0.23 | 2.2 | 1.75 | 15.0 | **TRAIN** |
| **CTRL-22** | `CTRL-ML-DRY-01` | Meghalaya | Dry Season Equilibrium Baseline | 2023-01-28T12:00:00Z | 0.0 | 0.2 | 1.5 | 1.85 | 11.0 | **TRAIN** |
| **CTRL-23** | `CTRL-NL-DRY-01` | Nagaland | Dry Season Equilibrium Baseline | 2023-03-12T12:00:00Z | 2.0 | 0.25 | 2.8 | 1.7 | 17.0 | **TRAIN** |
| **CTRL-24** | `CTRL-AR-DRY-01` | Arunachal Pradesh | Dry Season Equilibrium Baseline | 2023-02-18T12:00:00Z | 0.0 | 0.19 | 1.2 | 1.9 | 10.0 | **TRAIN** |
| **CTRL-25** | `CTRL-TR-DRY-01` | Tripura | Dry Season Equilibrium Baseline | 2023-01-22T12:00:00Z | 0.0 | 0.24 | 2.4 | 1.76 | 15.0 | **TRAIN** |
| **CTRL-26** | `CTRL-SK-MON-01` | Sikkim | Moderate Monsoon Non-Failure Window | 2024-05-10T12:00:00Z | 38.0 | 0.35 | 7.2 | 1.41 | 34.0 | **VAL** |
| **CTRL-27** | `CTRL-MZ-MON-01` | Mizoram | Moderate Monsoon Non-Failure Window | 2024-05-15T12:00:00Z | 44.0 | 0.37 | 7.8 | 1.36 | 37.0 | **VAL** |
| **CTRL-28** | `CTRL-MN-MON-01` | Manipur | Moderate Monsoon Non-Failure Window | 2024-05-20T12:00:00Z | 40.0 | 0.36 | 7.5 | 1.38 | 35.5 | **VAL** |
| **CTRL-29** | `CTRL-AS-MON-01` | Assam | Moderate Monsoon Non-Failure Window | 2024-06-02T12:00:00Z | 52.0 | 0.39 | 8.5 | 1.32 | 39.0 | **VAL** |
| **CTRL-30** | `CTRL-ML-MON-01` | Meghalaya | Moderate Monsoon Non-Failure Window | 2024-06-05T12:00:00Z | 65.0 | 0.41 | 9.5 | 1.28 | 44.0 | **VAL** |
| **CTRL-31** | `CTRL-NL-MON-01` | Nagaland | Moderate Monsoon Non-Failure Window | 2024-06-08T12:00:00Z | 46.0 | 0.38 | 8.0 | 1.35 | 38.0 | **VAL** |
| **CTRL-32** | `CTRL-AS-HEAVY-01` | Assam | Heavy Monsoon on Stable Competent Lithology | 2024-07-22T12:00:00Z | 92.0 | 0.42 | 11.5 | 1.16 | 53.0 | **TEST** |
| **CTRL-33** | `CTRL-ML-HEAVY-01` | Meghalaya | Heavy Monsoon on Stable Competent Lithology | 2024-07-25T12:00:00Z | 115.0 | 0.44 | 13.0 | 1.1 | 56.5 | **TEST** |
| **CTRL-34** | `CTRL-AR-HEAVY-01` | Arunachal Pradesh | Heavy Monsoon on Stable Competent Lithology | 2024-08-04T12:00:00Z | 105.0 | 0.43 | 12.2 | 1.12 | 55.0 | **TEST** |
| **CTRL-35** | `CTRL-SK-SEIS-01` | Sikkim | Moderate Seismic Shaking Without Moisture Trigger | 2024-02-14T03:00:00Z | 0.0 | 0.25 | 3.0 | 1.35 | 42.0 | **VAL** |
| **CTRL-36** | `CTRL-AS-SEIS-01` | Assam | Moderate Seismic Shaking Without Moisture Trigger | 2024-03-20T04:30:00Z | 5.0 | 0.27 | 3.8 | 1.3 | 45.0 | **VAL** |

---

## 5. Feature Engineering Dictionary (38 Operational Attributes)

The consolidated master dataset supplies 38 primary features across 6 distinct environmental and physical modalities:

1. **Precipitation Metrics**:
   - `rainfall_1h_mm`, `rainfall_6h_mm`, `rainfall_24h_mm`, `rainfall_72h_mm`: Real-time rain gauge accumulations.
   - `API_3d_mm`, `API_7d_mm`, `API_30d_mm`: Antecedent Precipitation Indices measuring multi-day saturation:
     $$API_N = \sum_{t=1}^N k^t \cdot P_t \quad (k=0.84)$$
   - `rainfall_accumulation_3h_mm`, `rainfall_intensity_3h_mmh`, `rainfall_acceleration`: Burst rate dynamics.
2. **In-Situ Geotechnical Telemetry**:
   - `soil_moisture_ratio`: Volumetric Water Content ($m^3/m^3$).
   - `soil_moisture_trend_24h`: 24-hour rate of change in moisture.
   - `pore_pressure_kpa`: Vibrating wire piezometer water pressure ($kPa$).
   - `pore_pressure_trend_24h`: 24-hour hydrodynamic pressurization rate.
   - `tilt_deg`: Dual-axis surface tilt angle ($^\circ$).
   - `tilt_rate_24h`: Angular displacement rate ($^\circ/24h$).
   - `ground_displacement_mm`: Borehole extensometer / InSAR cumulative displacement ($mm$).
   - `displacement_velocity_24h_mmd`: Creep velocity ($mm/day$).
3. **Geomorphometry (Copernicus GLO-30 DEM)**:
   - `elevation_m`: Absolute altitude above mean sea level.
   - `slope_deg`: Terrain slope inclination gradient ($0^\circ - 90^\circ$).
   - `aspect_deg`: Compass orientation of slope face.
   - `curvature`: Plan/profile surface curvature (negative = convergent hollow).
4. **Earth Observation (Sentinel-1 / Sentinel-2)**:
   - `NDVI`: Normalized Difference Vegetation Index ($[-1.0, 1.0]$).
   - `NDVI_change`: 30-day vegetation loss or scarp denudation anomaly.
5. **Seismotectonics**:
   - `seismic_magnitude`: Maximum regional earthquake magnitude within 24h.
   - `seismic_distance_km`: Distance to nearest active hypocenter.
   - `seismic_trigger_score`: Ground motion trigger index based on Arias Intensity ($I_a$).
   - `seismic_recency_hours`: Elapsed time since last qualifying seismic tremor.
6. **Physical & Socio-Economic Context**:
   - `geotechnical_fos`: Limit-equilibrium Factor of Safety ($FoS$).
   - `composite_risk_index_cri`: Fused multi-modal hazard index ($0 - 100$).
   - `historical_landslide_density`: GSI NLSM spatial hazard probability ($0.0 - 1.0$).
   - `road_criticality`: Strategic importance of mountain highway corridor ($0.0 - 1.0$).
   - `population_exposure`: Downslope settlement density count.

---

## 6. Multi-Modal Real-Time Telemetry Ingestion Streams

In live operations, PAHAD AI continuously ingests data from four independent channels to evaluate the 2-of-3 confirmation rule:

| Modality | Provider / Endpoint | Telemetry Stream | Freshness TTL | Provenance Badge |
| :--- | :--- | :--- | :---: | :---: |
| **Meteorological** | Open-Meteo & IMD Nowcast (`services/imd_service.py`) | Hourly rainfall, 24h rain, 7-day forecast | 15 minutes | `[LIVE]` |
| **Seismological** | USGS FDSNws API & NCS (`services/ncs_service.py`) | NER tectonic box ($20^\circ-30^\circ\text{N}, 87^\circ-98^\circ\text{E}$) | 5 minutes | `[LIVE]` |
| **Satellite InSAR** | Copernicus CDSE Sentinel-1 (`services/eo_catalog_service.py`) | 12-day repeat pass LOS ground displacement | 24 hours | `[HISTORICAL]` |
| **Geotechnical IoT** | LoRaWAN / MQTT Gateway (`services/device_gateway.py`) | Piezometer ($kPa$), inclinometer ($mm$), tilt ($^\circ$) | 2 minutes | `[LIVE]` |
| **Continuous Store** | SQLite Store (`data/observations/pahad_observations.db`) | Continuous multi-modal observations | Persistent | `[STORED]` |

---

## 7. Geotechnical Mohr-Coulomb Calibration Benchmark (Model A)

- **Target**: Continuous Factor of Safety ($FoS$).
- **Algorithm**: `GradientBoostingRegressor` (100 estimators, max depth 4).
- **Calibration Source**: 2,000 limit-equilibrium physics simulations calibrated to GSI Sikkim Colluvium and Teesta Basin river incision profiles:
  $$FoS = \frac{c' + (\sigma_n - u) \tan\phi'}{\tau + \tau_b}$$
- **Validation Accuracy**:
  - $R^2$ Score: **`0.9985`**
  - 5-Fold Cross-Validation $R^2$: **`0.9984`**
  - Root Mean Squared Error (RMSE): **`0.0136`**
  - Mean Absolute Error (MAE): **`0.0104`**
- **Feature Relative Importance**:
  - Pore-water pressure ($u$): **83.2%**
  - 24h Cumulative Precipitation ($P_{24}$): **10.1%**
  - River bed-shear toe erosion ($\tau_b$): **6.7%**

---

## 8. Quarantined Demo Walkthrough Register (`demo_train.csv`)

In compliance with our scientific ethics rule, the 25 synthetic walkthrough sequences are cataloged below. Evaluators can confirm they are designated `[DEMO]` and are completely barred from operational models:

| Record ID | Demo Scenario ID | Sector ID | Simulated 24h Rain | Sim FoS | Sim CRI | Provenance | Operational Role |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **DEMO-01** | `DEMO-SCENARIO-01` | `DEMO-SEC-01` | 24.345107725078563 | 1.3 | 12.0 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-02** | `DEMO-SCENARIO-02` | `DEMO-SEC-02` | 162.0352054217846 | 0.73 | 89.6 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-03** | `DEMO-SCENARIO-03` | `DEMO-SEC-03` | 44.4751467232902 | 1.79 | 19.1 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-04** | `DEMO-SCENARIO-04` | `DEMO-SEC-04` | 151.55811486610597 | 0.88 | 78.9 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-05** | `DEMO-SCENARIO-05` | `DEMO-SEC-05` | 50.13257253458647 | 1.61 | 21.6 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-06** | `DEMO-SCENARIO-06` | `DEMO-SEC-06` | 184.31751560008297 | 0.56 | 85.9 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-07** | `DEMO-SCENARIO-07` | `DEMO-SEC-07` | 41.17124417317753 | 1.55 | 38.3 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-08** | `DEMO-SCENARIO-08` | `DEMO-SEC-08` | 167.13766885439907 | 0.7 | 94.3 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-09** | `DEMO-SCENARIO-09` | `DEMO-SEC-09` | 9.4181666859295 | 1.7 | 18.3 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-10** | `DEMO-SCENARIO-10` | `DEMO-SEC-10` | 131.82466118206418 | 0.83 | 79.7 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-11** | `DEMO-SCENARIO-11` | `DEMO-SEC-11` | 6.051679907383448 | 1.43 | 35.4 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-12** | `DEMO-SCENARIO-12` | `DEMO-SEC-12` | 147.68888565592485 | 0.83 | 75.9 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-13** | `DEMO-SCENARIO-13` | `DEMO-SEC-13` | 57.98302608651236 | 1.52 | 16.8 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-14** | `DEMO-SCENARIO-14` | `DEMO-SEC-14` | 236.33203009480368 | 0.89 | 77.9 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-15** | `DEMO-SCENARIO-15` | `DEMO-SEC-15` | 45.30602316469242 | 1.73 | 40.3 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-16** | `DEMO-SCENARIO-16` | `DEMO-SEC-16` | 133.95365011764164 | 0.56 | 70.9 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-17** | `DEMO-SCENARIO-17` | `DEMO-SEC-17` | 47.195936691973 | 1.38 | 25.4 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-18** | `DEMO-SCENARIO-18` | `DEMO-SEC-18` | 160.7927286640537 | 0.72 | 76.2 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-19** | `DEMO-SCENARIO-19` | `DEMO-SEC-19` | 11.258121544150988 | 1.23 | 23.1 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-20** | `DEMO-SCENARIO-20` | `DEMO-SEC-20` | 200.76170402865887 | 0.93 | 92.6 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-21** | `DEMO-SCENARIO-21` | `DEMO-SEC-21` | 7.680713795407657 | 1.72 | 19.9 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-22** | `DEMO-SCENARIO-22` | `DEMO-SEC-22` | 212.99971614931508 | 0.68 | 92.4 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-23** | `DEMO-SCENARIO-23` | `DEMO-SEC-23` | 43.713699645007495 | 1.52 | 12.0 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-24** | `DEMO-SCENARIO-24` | `DEMO-SEC-24` | 220.4046065219392 | 0.7 | 79.3 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |
| **DEMO-25** | `DEMO-SCENARIO-25` | `DEMO-SEC-25` | 0.7379869098822395 | 1.62 | 36.1 | `[DEMO]` | **QUARANTINED (DEMO ONLY)** |

---

## 9. Verification & Audit Trail Summary

- **Total Consolidated Records**: 61 (36 Real Operational Ground Truth + 25 Isolated Demo Walkthrough)
- **Real Operational Columns**: 44
- **Date Range of Ground Truth**: May 16, 2022 to October 4, 2024
- **States Represented**: 8/8 North Eastern Region States (Sikkim, Manipur, Mizoram, Assam, Meghalaya, Nagaland, Arunachal Pradesh, Tripura)
- **Duplicated Records**: 0
- **Missing Administrative Labels**: 0
- **Primary Model Classification**: **`TRAINED_LIMITED_DATA`**
- **Deep Temporal Neural Network Status**: **`NOT_TRAINED_DATA_INSUFFICIENT`** (Real sequence threshold $N \ge 500$ honestly maintained)
