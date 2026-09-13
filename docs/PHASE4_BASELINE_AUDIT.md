# PAHAD AI — PHASE 4 BASELINE AUDIT

**Platform**: PARVAT NETRA — Unified Decision Intelligence & Life-Safety System  
**Engine**: PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Audit Date**: September 2026  
**Audit Purpose**: Pre-implementation audit of data assets, model provenance, telemetry feeds, and evaluation methodology before Phase 4 development.

---

## 1. Executive Findings Summary

| Dimension | Current Implementation | Phase 4 Ground Truth / Assessment |
| :--- | :--- | :--- |
| **Operational Status** | `TRAINED_LIMITED_DATA` | **Data-Grounded Research Prototype** |
| **Real Documented Events** | 17 verified NER disaster occurrences | Genuine historical occurrences (GSI/ISRO/SDMA); feature values are hybrid (real terrain/dates + reconstructed hydrometeorology) |
| **Control Windows (Negatives)**| 19 non-event control windows | Defensible negative windows (dry season, moderate rain, seismic non-trigger) |
| **Partition Sizes** | 16 Train / 12 Val / 8 Test | Chronological time-based holdout; zero synthetic contamination in `real_*.csv` |
| **Statistical Brittleness** | Test set of 8 samples (5 pos, 3 neg) yields 100% metrics | High variance due to small sample size; metrics must be honestly reported with sample-size caveats and N/A markers |
| **Event Model** | `models/pahad_event_model.pkl` (GBDT) | Calibrated Scikit-learn GradientBoostingClassifier with Platt sigmoid calibrator |
| **Geotechnical Model** | `models/pahad_fos_model.pkl` | GradientBoostingRegressor surrogate for Mohr-Coulomb physical equation |
| **Deep Learning (LSTM)** | `engine/pahad_lstm.py` | Physics-informed mathematical surrogate using exponential saturation decay; **NOT TRAINED** on sequence data |

---

## 2. In-Depth Audit Questions & Answers

### Q1: What dataset is currently used?
- **Raw Events**: `data/raw/historical_landslides_ner.csv` containing 17 documented disaster records across all 8 North Eastern Region (NER) states.
- **Labels**: `data/labels/event_labels.csv` containing 17 positive events (`event_label=1`) and 19 negative control windows (`event_label=0`), totaling 36 observations.
- **Processed Features**: `data/features/features_all.csv` (36 rows, 38 columns).
- **Partitions**:
  - `data/features/real_train.csv`: 16 rows (8 positive, 8 negative).
  - `data/features/real_val.csv`: 12 rows (4 positive, 8 negative).
  - `data/features/real_test.csv`: 8 rows (5 positive, 3 negative).
  - `data/features/demo_train.csv`: 28 synthetic rows (strictly isolated for `PAHAD_DEMO_MODE=1`).

### Q2: Where did the 17 documented events come from?
The 17 events are cataloged from official disaster records:
1. `SK-2024-NH10-KM48` (Sikkim, Pakyong): GSI Pakyong Field Inspection (Oct 2024)
2. `SK-2024-MANGAN` (Sikkim, Mangan): ISRO DMSG / Sikkim SDMA (Jun 2024)
3. `SK-2023-SINGTAM` (Sikkim, Gangtok): South Lhonak GLOF / GSI Joint Assessment (Oct 2023)
4. `MN-2022-NONEY` (Manipur, Noney): GSI Disaster Report GSI-NER-MN-2022-004 (Jun 2022)
5. `MN-2024-TAMENGLONG` (Manipur, Tamenglong): Manipur SDMA Monsoon Bulletin (Jul 2024)
6. `MZ-2024-MELTHUM` (Mizoram, Aizawl): Cyclone Remal GSI Report GSI-NER-MZ-2024-019 (May 2024)
7. `MZ-2023-LUNGLEI` (Mizoram, Lunglei): Mizoram PWD / DDMA Report (Aug 2023)
8. `AS-2022-DIMA-HASAO` (Assam, Dima Hasao): New Haflong Railway Breach GSI Report (May 2022)
9. `AS-2024-CACHAR` (Assam, Cachar): Assam SDMA Flood & Landslide Log (Jun 2024)
10. `ML-2022-MAWSYNRAM` (Meghalaya, East Khasi Hills): GSI Shillong Plateau Escarpment Survey (Jun 2022)
11. `ML-2024-SHILLONG` (Meghalaya, East Khasi Hills): Meghalaya SDMA Disaster Log (Jul 2024)
12. `NL-2024-DZUKOU-KOHIMA` (Nagaland, Kohima): Nagaland NSDMA Monsoon Assessment (Sep 2024)
13. `NL-2023-PHEK` (Nagaland, Phek): GSI NLSM Archive (Jul 2023)
14. `AR-2024-TAWANG` (Arunachal Pradesh, Tawang): BRO Project Vartak / Arunachal SDMA (Jun 2024)
15. `AR-2023-ITANAGAR` (Arunachal Pradesh, Papum Pare): GSI Itanagar Road Survey (Jun 2023)
16. `TR-2024-JAMPUI` (Tripura, North Tripura): Tripura SDMA Monsoon Deluge Log (Aug 2024)
17. `TR-2023-DHARMANAGAR` (Tripura, North Tripura): GSI NLSM Archive (Jul 2023)

### Q3: Are these events genuinely sourced or synthetic?
- **Incident Occurrence**: Genuine. The dates, locations, coordinates, and physical impacts correspond to verified landslides documented by GSI, ISRO, and State Disaster Management Authorities.
- **Feature Reconstruction**: Because real-time IoT piezometers and borehole inclinometers were not pre-installed at all 17 remote Himalayan slopes prior to failure, subsurface geotechnical features (e.g., exact pore-water pressure $u$, tilt rate, displacement mm) were reconstructed using post-disaster geotechnical back-analysis and Mohr-Coulomb soil mechanics.
- **Provenance Label**: Formally tagged as `[HISTORICAL / RECONSTRUCTED]`.

### Q4: What do the 16 / 12 / 8 splits represent?
The dataset strictly adheres to **Temporal Holdout Splitting**:
- **TRAIN (16 observations)**: Time period: `2022-05-16` to `2023-10-04`. Contains 8 historical landslides and 8 dry-season negative controls.
- **VALIDATION (12 observations)**: Time period: `2024-02-14` to `2024-06-25`. Contains 4 historical landslides, 2 seismic non-trigger controls, and 6 moderate-monsoon negative controls.
- **TEST (8 observations)**: Time period: `2024-07-02` to `2024-10-04`. Contains 5 historical landslides and 3 heavy-rain stable negative controls.
- **Leakage Status**: Chronological ordering is strictly maintained ($T_{\text{train}} < T_{\text{val}} < T_{\text{test}}$). Zero temporal overlap.

### Q5: Which features are real?
- Bounding coordinates (Latitude, Longitude)
- Digital Elevation Model topography: Elevation ($m$), Slope angle ($\beta$), Aspect, Curvature (derived from Copernicus GLO-30 DEM 30m resolution)
- Historical landslide spatial density and static susceptibility (GSI NLSM 1:10,000 mapping)
- Road infrastructure criticality and population exposure (NER Census and BRO highway network)
- Event timestamps and disaster metadata

### Q6: Which features are simulated or reconstructed?
- Vibrating-wire piezometer pore pressure ($u$) at the moment of failure for historical events where telemetry was absent
- Subsurface borehole inclinometer shear displacement (mm) and tilt rate
- High-frequency antecedent precipitation memory where IMD hourly AWS logs required ERA5-Land gridded interpolation

### Q7: Which API values are live?
- Real-time rainfall and weather conditions via Open-Meteo and IMD AWS endpoints (`services/weather_service.py`)
- Real-time seismic event catalog via USGS / NCS regional arc queries (`services/seismic_service.py`)
- Live CWC Teesta River hydrometric stage and discharge (`services/cwc_sync.py`)

### Q8: Which values are cached?
- Meteorological observations (TTL: 300 seconds)
- Seismic event catalog (TTL: 300 seconds)
- GLO-30 DEM elevation rasters in `data/geospatial/dem/`
- Satellite sensor acquisition footprints (`services/satellite_service.py`)

### Q9: Which values are synthetic / demo-safe?
- Synthetic demo training vectors in `data/features/demo_train.csv`
- Scripted 13-step demonstration sequence in `templates/index.html` (`SIH_DEMO`)
- Interactive parameter sliders in `templates/pahad_ai.html` (`[SIMULATION MODE]`)

### Q10: Which model produces event probability?
- `models/pahad_event_model.pkl`: Scikit-learn `GradientBoostingClassifier` trained on `real_train.csv`.
- Calibrated using `models/pahad_event_calibrator.pkl` (`CalibratedClassifierCV` via Platt Sigmoid scaling).
- Target: Binary probability of landslide event within forecast horizon ($0.0 - 1.0$).

### Q11: Which model produces Factor of Safety (FoS)?
- Physical equation: Infinite-slope Mohr-Coulomb limit equilibrium stability formula in `engine/pahad_models.py` and `backend/risk_engine.py`.
- Regressor surrogate: `models/pahad_fos_model.pkl` / `models/fos_predictor.pkl` (`GradientBoostingRegressor`) predicting continuous $FoS$ from rainfall, pore pressure, and basal shear.

### Q12: Are reported metrics reproducible?
- Yes. Executing `python scripts/train_event_model.py --seed 42` reproduces the exact weights and metrics.
- **Critical Audit Qualification**: The test set contains only 8 observations. On 8 samples, obtaining 5/5 true positives and 3/3 true negatives yields a nominal ROC-AUC of 1.0 and Brier score of 0.0824. While mathematically correct on this tiny holdout, **it is statistically brittle and must not be claimed as proof of generalized real-world deployment accuracy**.

---

## 3. Phase 4 Action Plan & Deliverables

1. **Formal Data Model & Manifests**:
   - Establish `data/raw/`, `data/processed/`, `data/external/`, `data/manifests/`, `data/splits/`.
   - Create `data/manifests/source_registry.json` detailing authoritative Indian and international providers (GSI, ISRO Bhoonidhi/Bhuvan, IMD, NCS, CWC, NDMA SACHET, ESA Copernicus).
2. **Event Labeling & Negative Control Protocol**:
   - Implement `engine/event_labeling.py` and `services/event_dataset_service.py`.
   - Document the formal methodology in `docs/EVENT_LABELING_PROTOCOL.md`.
   - Formalize negative control spatial/temporal exclusion zones to prevent negative sample contamination near known failure scarps.
3. **Feature Engineering Pipeline**:
   - Create `engine/event_features.py` with structured feature groups (Rainfall, Terrain, Vegetation, Susceptibility, Infrastructure, Geotechnical, Satellite, Seismic).
   - Tag every feature with its operational provenance: `[LIVE]`, `[HISTORICAL]`, `[CACHED]`, `[SIMULATED]`, `[MISSING]`.
4. **Enhanced Leakage Audit**:
   - Strengthen `scripts/check_event_leakage.py` and `tests/test_event_leakage.py`.
   - Create `docs/PHASE4_LEAKAGE_AUDIT.md`.
5. **Model Benchmarking & Reproducible Pipeline**:
   - Implement `scripts/train_event_models.py` benchmarking LogisticRegression, RandomForest, and GradientBoosting.
   - Record hashes (SHA-256 of dataset and feature schema), seeds, Python/package versions.
   - Update model registry in `models/` with `pahad_event_metadata.json`, `pahad_feature_schema.json`, and `pahad_training_metrics.json`.
6. **Transparent Explainability & Honest Metrics**:
   - Implement model driver attribution (non-causal contributing signals).
   - Display honest metrics in the Observatory UI with sample-size transparency.
7. **Scientific Limitations & Final Reporting**:
   - Create `docs/PHASE4_LIMITATIONS.md`.
   - Create `docs/PHASE4_MODEL_TRAINING.md`.
   - Create `docs/PAHAD_PHASE4_REPORT.md` (22 structured sections).
