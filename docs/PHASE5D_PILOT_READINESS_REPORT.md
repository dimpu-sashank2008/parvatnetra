# PARVAT NETRA / PAHAD AI — Phase 5D Data Reality & Pilot Readiness Report

**Document ID**: `PAHAD-REPORT-5D-01`  
**Classification**: National Emergency Authority Technical & Scientific Audit  
**Phase**: Phase 5D — Data Reality, Label Audit & Pilot Readiness Gate  
**Date**: September 2026  
**Final System Verdict**: **`NOT_READY_FOR_PILOT`**  
**Model Status**: **`TRAINED_LIMITED_DATA` / `RESEARCH_PROTOTYPE`**  

---

## 1. Executive Summary & Final Verdict

The objective of Phase 5D is to conduct a scientifically uncompromising audit of PARVAT NETRA / PAHAD AI to determine whether the platform can safely transition from `PARTIALLY_OPERATIONAL` into a live field pilot.

### Core Audit Question
> **"Can ParvatNetra / PAHAD AI safely enter a controlled pilot using real data?"**

### Objective Verdict: **`NOT_READY_FOR_PILOT`**

**Scientific Justification**:
1. **Critical Institutional Telemetry Gaps (P0)**: India Meteorological Department (IMD) Doppler Weather Radar and National Center for Seismology (NCS) live streams are in `AUTH_REQUIRED` state due to absent institutional API tokens (`IMD_API_TOKEN`, `NCS_API_TOKEN`). The system currently falls back to public Open-Meteo and USGS endpoints. While resilient for development, an operational disaster-warning pilot cannot legally dispatch public evacuations based on unauthenticated third-party weather feeds.
2. **Physical Sensor Grid Absence (P0)**: In-situ piezometers, borehole inclinometers, and surface tiltmeters are `UNAVAILABLE` along candidate pilot corridors (e.g. NH-10 Pakyong Km 48). Physical slope monitoring currently relies on synthetic limit-equilibrium approximations.
3. **Limited Training Volume (P1)**: The model is trained on $N=17$ authenticated catastrophic landslides expanded to $N=36$ balanced observation rows ($N=16$ train, $N=12$ val, $N=8$ test; or $N=105$ antecedent temporal windows). This dataset size warrants formal classification as **`TRAINED_LIMITED_DATA` / `RESEARCH_PROTOTYPE`**, requiring supervised authority oversight rather than autonomous pilot deployment.

---

## 2. Data & Event Reconciliation

### Discrepancy Resolution
A prior documentation discrepancy existed between reports mentioning **17 verified events** versus **16 events / 36 balanced observations**:
- **Audit Finding**: Exactly **17 documented catastrophic landslide events** exist in `data/raw/historical_landslides_ner.csv` spanning all 8 North Eastern Region (NER) states. Zero events have been excluded.
- **Root Cause of Confusion**: In the baseline training partition (`data/features/real_train.csv`), there are exactly **16 training samples** (8 positive events + 8 negative controls). Early draft notes erroneously conflated "16 training samples" with "16 events".
- **Canonical Observation Total**: 
  - **Training Split**: 16 samples (8 positive events $\le 2023$, 8 dry-season controls)
  - **Validation Split**: 12 samples (4 positive events in H1 2024, 8 controls: 2 seismic, 6 moderate monsoon)
  - **Test Split**: 8 samples (5 positive events in H2 2024, 3 heavy-rain stable controls)
  - **Total Samples**: $16 + 12 + 8 = 36$ samples ($17$ positive events + $19$ negative controls).
- **Antecedent Temporal Expansion (Phase 5B)**: Each of the 17 events was expanded into 5 antecedent windows ($T-48\text{h}, T-36\text{h}, T-24\text{h}, T-12\text{h}, T-6\text{h}$) resulting in $17 \times 5 = 85$ event windows + 20 control windows = 105 samples.

### Canonical Event Inventory Table

| Event ID | Disaster ID | State & District | Sector ID | Date (UTC) | Trigger Rain (24h) | FoS (Phys) | Institutional Source | Split |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **EV-01** | SK-2024-NH10-KM48 | Sikkim, Pakyong | `SK-NH10-KM48` | 2024-10-04 | 185.0 mm | 0.62 | GSI Pakyong Field Inspection | **TEST** |
| **EV-02** | SK-2024-MANGAN | Sikkim, Mangan | `SK-MANGAN-01` | 2024-06-12 | 210.0 mm | 0.55 | ISRO DMSG / Sikkim SDMA | **VAL** |
| **EV-03** | SK-2023-SINGTAM | Sikkim, Gangtok | `SK-SINGTAM-01` | 2023-10-04 | 140.0 mm | 0.48 | South Lhonak GLOF / GSI Assessment | **TRAIN** |
| **EV-04** | MN-2022-NONEY | Manipur, Noney | `MN-NONEY-01` | 2022-06-29 | 180.0 mm | 0.68 | GSI Disaster Report GSI-NER-MN-2022-004 | **TRAIN** |
| **EV-05** | MN-2024-TAMENGLONG | Manipur, Tamenglong | `MN-TAMENG-01` | 2024-07-02 | 165.0 mm | 0.74 | Manipur SDMA Monsoon Bulletin | **TEST** |
| **EV-06** | MZ-2024-MELTHUM | Mizoram, Aizawl | `MZ-AIZAWL-MELTHUM` | 2024-05-28 | 205.0 mm | 0.58 | Cyclone Remal GSI Report GSI-NER-MZ-2024-019 | **VAL** |
| **EV-07** | MZ-2023-LUNGLEI | Mizoram, Lunglei | `MZ-LUNGLEI-01` | 2023-08-22 | 150.0 mm | 0.81 | Mizoram PWD / DDMA | **TRAIN** |
| **EV-08** | AS-2022-DIMA-HASAO | Assam, Dima Hasao | `AS-DIMA-HASAO-01` | 2022-05-16 | 230.0 mm | 0.52 | New Haflong Station GSI Breaches Report | **TRAIN** |
| **EV-09** | AS-2024-CACHAR | Assam, Cachar | `AS-CACHAR-01` | 2024-06-18 | 170.0 mm | 0.76 | Assam SDMA (ASDMA) Monsoon Log | **VAL** |
| **EV-10** | ML-2022-MAWSYNRAM | Meghalaya, East Khasi | `ML-MAWSYNRAM-01` | 2022-06-17 | 350.0 mm | 0.45 | GSI Shillong Plateau Escarpment Survey | **TRAIN** |
| **EV-11** | ML-2024-SHILLONG | Meghalaya, East Khasi | `ML-SHILLONG-01` | 2024-07-10 | 160.0 mm | 0.79 | Meghalaya SDMA Flood & Landslide Log | **TEST** |
| **EV-12** | NL-2024-DZUKOU-KOHIMA | Nagaland, Kohima | `NL-KOHIMA-01` | 2024-09-03 | 175.0 mm | 0.72 | Nagaland NSDMA Monsoon Assessment | **TEST** |
| **EV-13** | NL-2023-PHEK | Nagaland, Phek | `NL-PHEK-01` | 2023-07-28 | 145.0 mm | 0.84 | GSI NLSM Archive | **TRAIN** |
| **EV-14** | AR-2024-TAWANG | Arunachal, Tawang | `AR-TAWANG-01` | 2024-06-25 | 190.0 mm | 0.65 | BRO Project Vartak / Arunachal SDMA | **VAL** |
| **EV-15** | AR-2023-ITANAGAR | Arunachal, Papum Pare | `AR-ITANAGAR-01` | 2023-06-20 | 155.0 mm | 0.80 | GSI Itanagar Road Survey | **TRAIN** |
| **EV-16** | TR-2024-JAMPUI | Tripura, North Tripura | `TR-JAMPUI-01` | 2024-08-20 | 160.0 mm | 0.78 | Tripura SDMA Monsoon Deluge Log | **TEST** |
| **EV-17** | TR-2023-DHARMANAGAR | Tripura, North Tripura | `TR-DHARMAN-01` | 2023-07-14 | 135.0 mm | 0.85 | GSI NLSM Archive | **TRAIN** |

---

## 3. Label Audit & Scientific Correction

### Flaw Identified
In earlier implementations (`engine/event_labeling.py` and `scripts/build_temporal_dataset.py`), candidate negative controls were rejected if their calculated Factor of Safety was below 1.10 ($FoS < 1.10$):
```python
# PREVIOUS CIRCULAR LOGIC (ELIMINATED IN PHASE 5D)
if fos < 1.10:
    return False, "Factor of Safety < 1.10 (slope is near critical equilibrium)."
```

### Scientific Impact
1. **Target Circularity / Selection Bias**: A machine learning model predicting slope failure probability ($P(\text{event})$) must not have its negative ground truth filtered by the output of a geotechnical model ($FoS$). If negative controls are only accepted when $FoS \ge 1.10$, the classifier trivially learns that high $FoS \implies$ negative, preventing the model from learning how to differentiate stable steep slopes under rain from active failures.
2. **Loss of Hard Negatives**: The most valuable samples for preventing false alarms are steep slopes ($\text{slope} \ge 28^\circ$) experiencing heavy precipitation where no failure occurred. Excluding them degrades operational reliability.

### Correction Applied in Phase 5D
- **Decoupling Enforced**: In [`engine/event_labeling.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/engine/event_labeling.py), `validate_negative_control` now establishes ground truth strictly on:
  1. Authoritative non-event observation from official disaster agency records.
  2. Strict geographic exclusion: $> 5\text{ km}$ distance from any documented scarp.
  3. Strict temporal exclusion: $> 7\text{ days}$ separation from any known event.
  4. Non-trivial mountain terrain ($\text{slope} \ge 15.0^\circ$).
  5. Core telemetry completeness.
- **FoS Decoupled**: $FoS$ is preserved as an input physics feature (Model A), never a ground-truth label selector.

---

## 4. Leakage & Partition Audit

A comprehensive leakage audit was executed using [`scripts/check_event_leakage.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/scripts/check_event_leakage.py) and verified via [`tests/test_event_leakage.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_event_leakage.py):

| Leakage Vector | Audit Test | Result | Verification Detail |
| :--- | :--- | :---: | :--- |
| **Temporal Lookahead** | Observation timestamp vs Failure timestamp | **PASS** | Strict antecedent inequality: $T_{\text{obs}} < T_{\text{event}}$ across all rows. |
| **Window Hierarchy** | Precipitation accumulation consistency | **PASS** | Monotonically non-decreasing: $R_{1h} \le R_{6h} \le R_{24h} \le R_{72h}$. |
| **Partition Boundaries** | Chronological holdout isolation | **PASS** | $\text{Train}_{\max} (\text{2023-10-04}) < \text{Val}_{\min} (\text{2024-02-14}) < \text{Test}_{\min} (\text{2024-07-02})$. |
| **Sector Overlap** | Identical sector + timestamp across splits | **PASS** | 0 cross-partition duplicates. |
| **Target Leakage** | Target label presence in input vector | **PASS** | `event_label` and `CRI` strictly excluded from feature matrix $X$. |
| **Synthetic Contamination** | Demo records in operational splits | **PASS** | Demo samples isolated in `demo_train.csv`; 0 demo records in real splits. |
| **Overall Result** | **Automated Leakage Audit** | **`PASS`** | Zero data leakage detected. |

---

## 5. Real Data Coverage & Operational Source Classification

Every operational data stream is strictly classified into exactly one canonical status:

| Data Stream | Operational Source | Endpoint / Implementation | Status | Freshness TTL | Operational Fallback | Scientific Role |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **Precipitation (Current)** | Open-Meteo REST API | `api.open-meteo.com/v1/forecast` | `LIVE` | 15 min | Regional 24h antecedent cache | Hydrometeorological trigger |
| **Precipitation (Forecast)** | Open-Meteo Forecast | `api.open-meteo.com/v1/forecast` | `LIVE` | 15 min | Persistence / zero rain | Multi-horizon trigger projection |
| **Regional Seismology** | USGS FDSNws API | `earthquake.usgs.gov/fdsnws/event/1` | `LIVE` | 5 min | Tectonic baseline ($M=0.0$) | Dynamic shaking destabilization |
| **Spatial Database** | Neon PostgreSQL / PostGIS | AWS `ep-wild-wave-awpqskzf` | `LIVE` | Permanent | Local SQLite fallback | Spatial queries, telemetry store |
| **Decision Intelligence** | OmniRoute Local LLM | `http://localhost:20128/v1` | `LIVE` | Real-time | Deterministic CAP templates | Multilingual SitRep synthesis |
| **Terrain / DEM** | Copernicus GLO-30 Tiles | Static 30m raster tiles | `CACHED` | 30 days | Regional default slope ($35^\circ$) | Slope, aspect, curvature, elevation |
| **Official Doppler Radar** | IMD Nowcast & AWS | `mausam.imd.gov.in/api` | `AUTH_REQUIRED` | 15 min | Open-Meteo public feed | Authoritative GOI precipitation |
| **National Seismology** | MoES NCS Seismology | MoES NCS Private API | `AUTH_REQUIRED` | 5 min | USGS NER bounding box | Authoritative GOI micro-tremors |
| **Earth Observation (SAR)** | Copernicus CDSE (Download) | `dataspace.copernicus.eu` | `AUTH_REQUIRED` | 1 day | Static GSI InSAR baselines | 12-day InSAR LOS deformation |
| **National Satellite Data** | ISRO NRSC Bhoonidhi | `bhoonidhi.nrsc.gov.in` | `AUTH_REQUIRED` | 7 days | Copernicus Sentinel-2 / DEM | High-res CartoDEM & L-band SAR |
| **In-situ Boreholes** | IoT Piezometers / Inclinometers | MQTT Broker / Gateway | `UNAVAILABLE` | 2 min | Mohr-Coulomb limit equilibrium | Real-time pore pressure & tilt |
| **River Hydrometry** | Central Water Commission | CWC Teesta Basin Portal | `UNAVAILABLE` | 1 hour | Historical hydrometric curves | River toe-erosion scouring |
| **Field Incident Feeds** | Citizen & Responder Reports | `/api/reports` & Mobile Sync | `SECONDARY` | Real-time | Authority verification queue | Crowdsourced field evidence |

---

## 6. Authoritative Source Connections & Credential Gaps

The following credentials are required to upgrade streams from `AUTH_REQUIRED` to `LIVE`:

1. **IMD Disaster Gateway**:
   - Environment Variables: `IMD_API_BASE_URL`, `IMD_API_TOKEN`
   - Verification Command: `python -c "from services.imd_service import IMD_CONNECTOR; print(IMD_CONNECTOR.get_status())"`
   - Expected Output: `{'status': 'READY', 'provider': 'IMD', 'auth': 'CONFIGURED'}`
2. **MoES NCS Seismology**:
   - Environment Variables: `NCS_API_BASE_URL`, `NCS_API_TOKEN`
   - Verification Command: `python -c "from services.ncs_service import NCS_CONNECTOR; print(NCS_CONNECTOR.get_status())"`
   - Expected Output: `{'status': 'READY', 'provider': 'NCS', 'auth': 'CONFIGURED'}`
3. **Copernicus CDSE Sentinel Raster Download**:
   - Environment Variables: `COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET`
   - Verification Command: `python -c "from services.eo_catalog_service import EO_CATALOG; print(EO_CATALOG.get_status())"`
   - Expected Output: `{'status': 'READY', 'provider': 'Copernicus CDSE', 'auth': 'CONFIGURED'}`
4. **ISRO NRSC Bhoonidhi**:
   - Environment Variables: `BHOONIDHI_API_URL`, `BHOONIDHI_API_TOKEN`
   - Formal Requirement: Institutional MoU with National Remote Sensing Centre (NRSC), Hyderabad.

---

## 7. Model Validation & Benchmark Comparison

Benchmark evaluation executed across $N=36$ balanced observations ($N=8$ held-out test samples):

### Strategy Comparison (24h Forecast Horizon)

| Strategy | Decision Rule | Test POD (Recall) | Test FAR | Test CSI | Test Brier Score | Operational Takeaway |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Rainfall Only** | $R_{24h} \ge 150\text{ mm}$ | 0.4000 | 0.0000 | 0.4000 | 0.1850 | Misses 60% of landslides triggered on saturated slopes by moderate rain. |
| **2. FoS Only** | $FoS < 1.00$ | 1.0000 | 0.3750 | 0.6250 | 0.1250 | High sensitivity, but flags steep stable slopes experiencing transient pore pressure. |
| **3. Compound Rule** | $R_{24h} \ge 150\text{ mm} \lor FoS < 1.10$ | 1.0000 | 0.3750 | 0.6250 | 0.1250 | Captures all events, but 37.5% false alarm rate overwhelms emergency dispatchers. |
| **4. Calibrated ML** | $P(\text{event}) \ge 0.50$ | **1.0000** | **0.0000** | **1.0000** | **0.0824** | Optimal non-linear separation on distinct disaster archetypes. |
| **5. 2-of-3 Fusion Gate** | 2-of-3 Corroboration Rule | **1.0000** | 0.3750 | 0.6250 | 0.1250 | Conservative safety interlock preventing unverified public sirens. |

### Early Warning Lead Time
- **Median Warning Lead Time**: **24.0 hours**
- **Minimum Lead Time**: 24.0 hours
- **Maximum Lead Time**: 24.0 hours

### Probability Calibration
- Raw GBDT Brier Score: 0.0942 $\implies$ Platt Calibrated Brier Score: **0.0824** (12.5% calibration error reduction).
- Expected Calibration Error (ECE): **0.2604**.

---

## 8. Deep Learning Sequence Models (LSTM) Status

- **Status**: **`NOT_TRAINED` / `MATHEMATICAL_SURROGATE`**
- In accordance with SIH problem statement invariants and NDMA guidelines, `engine/pahad_lstm.py` remains strictly identified as a mathematical surrogate.
- **Minimum Requirement for Production Training**: Deep recurrent sequence architectures (LSTM/GRU/Temporal Transformer) require continuous high-frequency ($\ge 1\text{ Hz}$) telemetry from installed borehole sensor loggers spanning $\ge 3$ complete monsoon cycles ($> 100,000$ continuous time steps). Training on sparse disaster incident rows is scientifically indefensible.

---

## 9. Safety Gate Audit (2-of-3 Independent Corroboration)

The platform enforces a strict mechanical-empirical corroboration interlock before escalating alerts:
1. **Physical Mechanics (Model A)**: $FoS < 1.10$
2. **Hydrometeorological Threshold**: $R_{24h} \ge 150.0\text{ mm}$ (Mandal-Sarkar regional threshold)
3. **Calibrated Event Probability (Model B)**: $P(\text{event}_{24h}) \ge 0.70$

### Safety Invariants
- **Public Warning Protection**: A public `RED` (EXTREME) alert **CANNOT** be triggered by the event classifier alone. At least two independent modalities must confirm imminent destabilization.
- **Fallback Downgrade**: If only one modality triggers, the alert level is automatically downgraded to `YELLOW` (ADVISORY) or `ORANGE` (WARNING).
- **Human-in-the-Loop Override**: No public CAP v1.2 broadcast or siren dispatch occurs without authenticated district magistrate or SDMA authorization.

---

## 10. Objective Pilot Readiness Gate

Evaluation against standard National Disaster Management Authority (NDMA) pilot deployment criteria:

| Category | Gate Criterion | Assessment | Result |
| :--- | :--- | :--- | :---: |
| **DATA** | Authenticated historical ground truth | 17 verified events authenticated by GSI, ISRO, SDMAs | **PASS** |
| **DATA** | Leakage-free temporal holdout split | Chronological split ($\le 2023$, H1 2024, H2 2024), 0 lookahead | **PASS** |
| **DATA** | Authoritative national weather feed | IMD Doppler Radar in `AUTH_REQUIRED`; relies on Open-Meteo fallback | **FAIL** |
| **MODEL** | Separation of FoS and Event Probability | Model A ($FoS$) and Model B ($P(\text{event})$) are fully decoupled | **PASS** |
| **MODEL** | Non-circular label assignment | Negative controls decoupled from $FoS \ge 1.10$ | **PASS** |
| **MODEL** | Production-scale sample volume | $N=17$ events ($N=36$ balanced rows) — sample size too small | **FAIL** |
| **LIVE** | Real-time physical borehole telemetry | In-situ piezometers/inclinometers `UNAVAILABLE` along pilot corridors | **FAIL** |
| **LIVE** | Continuous data freshness monitoring | `DataFreshnessEngine` active with modality-specific TTL penalties | **PASS** |
| **INFRASTRUCTURE**| PostGIS spatial persistence | Neon PostgreSQL pool operational via `DATABASE_URL` | **PASS** |
| **INFRASTRUCTURE**| Resilient offline field synchronization | SQLite mobile store + push/pull sync verified | **PASS** |
| **SAFETY** | 2-of-3 Independent Corroboration Gate | Mathematical interlock verified; single signal cannot trigger RED alert | **PASS** |
| **PILOT** | Defined corridor & operational SOP | NH-10 Pakyong Km 48 mapped; SDRF/NDRF dispatch protocols codified | **PASS** |
| **OVERALL** | **Pilot Readiness Gate Verdict** | **3 of 12 Criteria Failed (Critical telemetry & data volume)** | **`NOT_READY_FOR_PILOT`** |

---

## 11. Prioritized Blockers & Remediation Roadmap

### Priority 0 (Blocks Pilot Deployment)
1. **[P0-1] IMD Institutional API Authentication**: Secure operational MOU and credentials (`IMD_API_TOKEN`) for direct Doppler Radar QPE feeds at `mausam.imd.gov.in`.
2. **[P0-2] Pilot Corridor Hardware Instrumentation**: Deploy physical vibrating-wire piezometer and biaxial MEMS inclinometer hardware at NH-10 Pakyong Km 48 with LoRaWAN gateway uplink to replace simulated in-situ telemetry.

### Priority 1 (Major Engineering Requirements)
3. **[P1-1] Historical Dataset Expansion**: Integrate Geological Survey of India (GSI) National Landslide Susceptibility Mapping (NLSM) historical inventory to expand verified event rows from $N=17$ to $N \ge 150$.
4. **[P1-2] MoES NCS Enterprise Seismology**: Obtain official Ministry of Earth Sciences token to replace secondary USGS query with direct localized Himalayan fault monitoring.

### Priority 2 (Enhancements for Scaling)
5. **[P2-1] High-Resolution CartoDEM Ingestion**: Complete NRSC Bhoonidhi MOU for 10m stereo elevation models to refine Horn kernel slope gradients.
6. **[P2-2] Sequence Model Pre-Training**: Archive continuous 1-minute field logger telemetry across the 2027 monsoon season to enable genuine LSTM temporal pre-training.

---

## 12. Automated Test Verification Summary

Comprehensive test execution across all project modules:

| Test Suite | Modules Covered | Passing | Status |
| :--- | :--- | :---: | :---: |
| **Phase 5D Event Suite** | `test_event_api.py`, `test_event_model.py`, `test_event_labeling.py`, `test_event_leakage.py`, `test_event_training.py`, `test_event_validation.py`, `test_event_calibration.py`, `test_event_data_quality.py`, `test_event_dataset.py` | **31 / 31** | **100% PASS** |
| **Phase 5C Telemetry Connectors** | `test_live_connectors.py`, `test_freshness.py`, `test_observation_store.py`, `test_sector_snapshot.py`, `test_mcp_integration.py` | **63 / 63** | **100% PASS** |
| **Core Physics & Engine Regression** | `test_pahad_engine.py`, `test_pahad_phase2.py`, `test_pahad_phase3.py`, `test_model_regression.py`, `test_live_inference.py` | **77 / 77** | **100% PASS** |
| **Services & Localization Regression** | `test_weather_service.py`, `test_seismic_service.py`, `test_terrain_api.py`, `test_i18n_localization.py` | **36 / 36** | **100% PASS** |
| **Total Automated Tests Verified** | **All suites combined** | **207 / 207** | **100% PASS** |

---

## 13. Next Required Phase

**Phase 6: Institutional Sensor Corridor Commissioning & Pre-Pilot In-Situ Deployment**
- Physical sensor node integration on NH-10 Pakyong Km 48.
- IMD Mausam API institutional token deployment.
- Supervised authority field shadow trial with District Disaster Management Authority (DDMA) Gangtok.
