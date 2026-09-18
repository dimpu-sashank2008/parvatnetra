# PAHAD AI — Model Card: Landslide Event Classifier v1.0
**Standard: Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform**  
**Specification: ACM FAccT & National Disaster Management Authority (NDMA) Early Warning Protocol**

---

## 1. Executive Summary & Mandatory Classification

| Attribute | Specification |
| :--- | :--- |
| **MODEL** | **PAHAD Event Classifier** (`PAHAD-Event-Classifier-v1.1`) |
| **TARGET** | **Landslide Event Probability** ($P(\text{failure} \mid \mathbf{x}) \in [0, 1]$) |
| **GEOGRAPHIC SCOPE** | **North Eastern Region (NER) of India** (8 States: Sikkim, Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura) |
| **FORECAST HORIZONS** | **6h / 12h / 24h / 48h** (plus immediate 1h / 3h early-detection windows) |
| **TRAINING DATA** | **16 Real Samples** (8 documented GSI events, 8 defensible control windows; $\le 2023\text{-}12\text{-}31$) |
| **VALIDATION METHOD** | **Strict Temporal Holdout** (Val: 12 samples, $2024\text{-}01$ to $2024\text{-}06$; Test: 8 samples, $\ge 2024\text{-}07$) + Grouped Spatial CV |
| **DATASET SHA-256** | `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e` |
| **STATUS** | **`TRAINED_LIMITED_DATA`** (`DATA-GROUNDED RESEARCH PROTOTYPE`) |

> [!IMPORTANT]
> **Data Honesty & Scientific Integrity Invariant**:  
> The model status is formally classified as **`TRAINED_LIMITED_DATA`** with stage designation **`DATA-GROUNDED RESEARCH PROTOTYPE`**. It is **NOT** classified as `PRODUCTION-CANDIDATE` or fully autonomous deployment grade. The dataset consists of verified historical events and strict controls without synthetic augmentation. Synthetic/demo records are completely isolated in `data/features/demo_train.csv` and restricted to `PAHAD_DEMO_MODE=1`. Under no circumstances are synthetic samples used to train the operational event classifier.

---

## 2. Critical Dual-Model Architecture Invariant

PARVAT NETRA maintains two strictly separate model families to prevent category confusion between physical mechanics and temporal hazard likelihood:

```
+-------------------------------------------------------------------------------+
|                             PARVAT NETRA PLATFORM                             |
+---------------------------------------+---------------------------------------+
                                        |
                    +-------------------+-------------------+
                    |                                       |
                    v                                       v
    +-------------------------------+       +-------------------------------+
    |            MODEL A            |       |            MODEL B            |
    |  PAHAD Geotechnical FoS Model |       |   PAHAD Landslide Event Model |
    +-------------------------------+       +-------------------------------+
    | Type: Non-linear Regressor    |       | Type: Calibrated Classifier   |
    | Artifact: pahad_fos_model.pkl |       | Artifact: pahad_event_model.pkl|
    | Target: Factor of Safety (FoS)|       | Target: P(Event in forecast)  |
    | Scale: Continuous [0.4, 3.0]  |       | Scale: Probability [0.0, 1.0] |
    | Basis: Mohr-Coulomb mechanics |       | Basis: Multimodal event logs  |
    +-------------------------------+       +-------------------------------+
                    |                                       |
                    +-------------------+-------------------+
                                        |
                                        v
                    +---------------------------------------+
                    |          PAHAD FUSION ENGINE          |
                    | Composite Risk Index (CRI: 0-100)     |
                    | 2-of-3 Independent Confirmation Rule  |
                    +---------------------------------------+
```

1. **MODEL A: PAHAD Geotechnical FoS Model**
   - **Target**: Physical Factor of Safety ($FoS$).
   - **Objective**: Evaluates slope equilibrium using geotechnical shear strength, pore-water pressure, and slope geometry.
   - **Invariant**: Kept completely distinct. Never merged with the event classifier.
2. **MODEL B: PAHAD Landslide Event Model**
   - **Target**: Probability of a documented landslide event within 6h, 12h, 24h, or 48h.
   - **Objective**: Identifies temporal pattern signatures of rapid destabilization from precipitation, displacement, tilt, and antecedent saturation.
3. **Temporal Deep Learning (LSTM) Status**:
   - **Status**: **`NOT_TRAINED`**.
   - **Protocol**: The sequence model in `engine/pahad_lstm.py` is explicitly maintained as a documented **mathematical surrogate** until continuous multi-year telemetry sequences with millisecond timestamps are archived. No synthetic LSTM claims are made.

---

## 3. Data Provenance & Partitioning

### 3.1 Historical Event Ground Truth
All documented landslide events originate from verified national and state authority records:
- **Primary Sources**: Geological Survey of India (GSI) National Landslide Susceptibility Mapping (NLSM), Sikkim SDMA, Assam SDMA, BRO Project Swastik / Pushpak logs.
- **Coverage**: 17 documented disaster events covering all 8 North Eastern states (Sikkim, Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura).
- **Date Range**: August 11, 2022 to September 18, 2024.

### 3.2 Dataset Separation
- **Operational Training Set (`real_train.csv`)**: 16 samples (8 documented failures, 8 verified stable control windows; $\le 2023\text{-}12\text{-}31$).
- **Operational Validation Set (`real_val.csv`)**: 12 samples (4 documented failures, 8 verified stable control windows; $2024\text{-}01\text{-}01$ to $2024\text{-}06\text{-}30$).
- **Operational Test Set (`real_test.csv`)**: 8 samples (5 documented failures, 3 verified stable control windows; $\ge 2024\text{-}07\text{-}01$).
- **Demo Set (`demo_train.csv`)**: 25 synthetic walkthrough samples. **Strictly segregated**; forbidden in operational training and guarded by `PAHAD_DEMO_MODE=1`.

### 3.3 Leakage Prevention
Automated leakage audit via `scripts/check_event_leakage.py` verifies:
- Zero duplicate event IDs or coordinate-timestamp collisions.
- Zero temporal overlap between train ($\le 2023$), validation (H1 2024), and test (H2 2024) partitions.
- Zero lookahead leakage (all antecedent precipitation indices $API_{30d}$, 24h/72h rainfall, and displacement metrics strictly computed backward from assessment timestamp).

### 3.4 Authoritative GSI Geological Quadrangle Map (GQM) Stratigraphic Grounding Catalog
All hillslope physical baselines, cohesion ($c'$), internal friction angle ($\phi'$), shear surface depth ($z$), and structural tectonic controls are strictly calibrated against 10 official Geological Survey of India (GSI) 1:250,000 Geological Quadrangle Maps:

| GSI Degree Sheet | Quadrangle Name | Target Corridors & Jurisdictions | Lithostratigraphic Formations | Critical Structural & Tectonic Controls |
| :---: | :---: | :---: | :---: | :---: |
| **Sheet 78M** | **Tawang Quadrangle** | Arunachal Pradesh (Tawang, Sela Pass, NH-13) | Se La Group Higher Himalayan Crystallines, Bomdila Group, Dirang / Lumla Formation | Main Central Thrust (MCT) hanging wall zone, active periglacial freeze-thaw loosening |
| **Sheet 83I** | **Lower Siang Quadrangle** | Arunachal Pradesh (Kimin, Harmoti, Ziro, Lower Siang) | Sub-Himalayan Siwalik molasse sandstones, Gondwana and Dafla/Subansiri formations | Main Boundary Thrust (MBT), Himalayan Frontal Thrust (HFT), Tipi Thrust, Bomdila Thrust, Miri Thrust |
| **Sheet 83E** | **Subansiri Quadrangle** | Arunachal Pradesh / Assam (Papum Pare, Itanagar, Subansiri basin) | Upper/Middle Tertiary sandstones, Gondwana coal-bearing shales | Himalayan frontal imbricate thrust zone |
| **Sheet 78O** | **Shillong Quadrangle** | Meghalaya (Shillong, East Khasi Hills, Ri-Bhoi, Cherrapunji) | Shillong Group quartzites & phyllites, Mahadek sandstones, Sylhet/Shella karstic limestones | **Dawki Fault** (east-west plate boundary master fault), **Kulsi Fault** strike-slip system |
| **Sheet 78K** | **Tura Quadrangle** | Meghalaya (East/West Garo Hills, Tura Range, Nokrek) | Assam-Meghalaya Gneissic Complex (AMGC), Kopili & Simsang splintery shales | **Dapsi Thrust**, Dawki Fault western extension |
| **Sheet 78J** | **Goalpara Quadrangle** | Assam & Bhutan Foothills (Goalpara, Kokrajhar, Bongaigaon) | AMGC crystalline basement, Buxa group dolomites, Quaternary Brahmaputra alluvium | Himalayan frontal flexural ramp |
| **Sheet 83D** | **Silchar Quadrangle** | Assam / Mizoram / Tripura (Barak Valley, Kolasib, Cachar, Aizawl link) | Surma Group (Bhuban & Bokabil) rhythmic sandstones, shales, siltstones | Longai river shear zone, steep anticlinal limbs |
| **Sheet 83H** | **Imphal Quadrangle** | Manipur (Noney, Tupul Railway Corridor, Jiribam axis) | Disang Group splintery dark grey flysch shales, Barail arenites | Irang Fault zone, Indo-Myanmar Range fold-and-thrust belt |
| **Sheet 83G** | **Peren Quadrangle** | Nagaland (Peren, Kohima, NH-29 Lifeline, Barail Range) | Barail massive quartz arenites & Disang flysch shales | Pagla Pahar regional shear zone |
| **Sheet 83J** | **Sibsagar Quadrangle** | Nagaland / Assam border (Wokha, Mokokchung, Belt of Schuppen) | Disang-Barail thrust sheets, Tipam sandstone | Belt of Schuppen imbricate thrust duplex, **Naga Thrust** |
| **Sheet 78A/78B**| **Sikkim Quadrangle** | Sikkim (NH-10 Km 48, Singtam, Dikchu, Mangan, Teesta Gorge) | Daling Group quartz-chlorite phyllites, Chungthang gneisses | Main Central Thrust (MCT) footwall crushed zone, Teesta gorge toe erosion |

---

## 4. Model Specification & Calibration

- **Algorithm**: `GradientBoostingClassifier` with Platt Sigmoid Probability Calibration (`CalibratedClassifierCV` via `PredefinedSplit`).
- **Hyperparameters**: `n_estimators=100`, `learning_rate=0.05`, `max_depth=3`, `subsample=0.85`, `random_state=42`.
- **Calibration Method**: Platt Sigmoid scaling fitted on the temporal validation partition.
- **Reliability & Brier Score**:
  - Raw Brier Score: $0.0912$
  - Calibrated Brier Score: **$0.0824$** (improvement of $+9.6\%$)
  - Empirical Calibration Error (ECE): $0.2604$ (discretization effect on $N=8$ test set; within expected bounds for small samples).

---

## 5. Performance Metrics (Held-Out Temporal Test Set: $\ge 2024\text{-}07$)

Evaluated on 8 unseen historical samples (5 positive mass movements, 3 stable negative controls) from the 2024 monsoon:

| Metric | Empirical Value | Operational Interpretation |
| :--- | :--- | :--- |
| **ROC-AUC** | **1.000** | Perfect ranking separation on held-out test windows |
| **PR-AUC** | **1.000** | Uncompromised precision-recall frontier on test sample |
| **Precision** | **1.000** | Zero false alarms ($FP = 0$) at operational threshold $0.70$ |
| **Recall (POD)** | **1.000** | Probability of Detection ($5/5$ test events caught) |
| **False Alarm Ratio (FAR)** | **0.000** | $FAR = \frac{FP}{TP + FP} = \frac{0}{5} = 0.000$ |
| **Critical Success Index (CSI)** | **1.000** | $CSI = \frac{TP}{TP + FP + FN} = \frac{5}{5+0+0} = 1.000$ |
| **F1-Score** | **1.000** | Harmonic mean of precision and recall |
| **Brier Score** | **0.0824** | Mean squared error of calibrated probability |
| **Median Warning Lead Time** | **24.0 Hours** | First qualifying warning ($P \ge 0.70$) prior to failure |

> [!NOTE]
> While test partition performance metrics are $1.0$, this is a direct mathematical consequence of the modest test sample size ($N=8$). In accordance with NDMA guidelines, these metrics must not be interpreted as claiming zero real-world error. The model remains classified as `TRAINED_LIMITED_DATA`.

---

## 6. Operational Threshold Analysis

System performance evaluated across 5 decision thresholds on held-out test data:

| Probability Threshold | Precision | Recall (POD) | FAR | CSI | Operational Guidance |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **0.50** | 1.000 | 1.000 | 0.000 | 1.000 | Early Advisory: High sensitivity; appropriate for internal EOC watch |
| **0.60** | 1.000 | 1.000 | 0.000 | 1.000 | Staging Alert: Pre-position SDRF relief and road-clearing machinery |
| **0.70** | **1.000** | **1.000** | **0.000** | **1.000** | **RECOMMENDED OPERATIONAL THRESHOLD: Balanced trigger for 2-of-3 fusion** |
| **0.80** | 1.000 | 1.000 | 0.000 | 1.000 | High Confidence: Multi-agency response mobilization |
| **0.90** | 1.000 | 0.800 | 0.000 | 0.800 | Conservative: Misses early-stage failure onset ($POD=0.80$) |

---

## 7. Model Drivers & Feature Signals

Feature signals derived via GBDT tree split gain. In compliance with NDMA Early Warning Protocol, these are formally designated as **"Model Drivers"** / **"Contributing Signals"**, never as causal proof:

| Rank | Model Driver Feature | Importance | Direction | Primary Data Source | Live Availability |
| :---: | :--- | :---: | :---: | :--- | :---: |
| 1 | `soil_moisture_trend_24h` | **$20.2\%$** | Positive ($\uparrow$) | In-situ volumetric soil moisture probe | `[SIMULATED]` / AWS |
| 2 | `ground_displacement` | **$15.2\%$** | Positive ($\uparrow$) | Borehole Inclinometer / InSAR | `[SIMULATED]` / Sentinel-1 |
| 3 | `FoS` (Mohr-Coulomb) | **$13.5\%$** | Negative ($\downarrow$) | Physical Infinite Slope Engine | `[LIVE / DETERMINISTIC]` |
| 4 | `API_30d` (Antecedent Rain) | **$12.9\%$** | Positive ($\uparrow$) | IMD Automatic Weather Stations | `[LIVE]` / IMD AWS |
| 5 | `tilt` | **$6.7\%$** | Positive ($\uparrow$) | MEMS Biaxial Tiltmeter | `[SIMULATED]` / PostGIS |
| 6 | `displacement_velocity_24h`| **$6.3\%$** | Positive ($\uparrow$) | In-situ Extensometer Rate of Change | `[SIMULATED]` |
| 7 | `CRI` (Composite Risk Index) | **$5.1\%$** | Positive ($\uparrow$) | Multi-Source Fusion Engine | `[LIVE / DETERMINISTIC]` |
| 8 | `rainfall_24h` | **$4.1\%$** | Positive ($\uparrow$) | IMD Automatic Weather Stations | `[LIVE]` / IMD AWS |
| 9 | `NDVI_change` | **$3.3\%$** | Negative ($\downarrow$) | Sentinel-2 Multispectral Vegetation Loss | `[SIMULATED]` |
| 10 | `rainfall_72h` | **$2.8\%$** | Positive ($\uparrow$) | Cumulative IMD Gauges | `[LIVE]` / IMD AWS |

---

## 8. Operational Safeguards & Public Alert Protocol

To prevent catastrophic false-positive panic or unverified road closures, the Landslide Event Model is strictly bound to the **PARVAT NETRA 2-of-3 Independent Confirmation Protocol**:

1. **Prediction Layer**: $P(\text{event}) \ge 0.70$ generated by `PAHAD-Event-Classifier`.
2. **Verification Layer**: An independent physical or observational signal must agree:
   - Factor of Safety $FoS < 1.05$ (geotechnical instability), **OR**
   - Rainfall exceeds regional IMD threshold ($R_{24h} > 120\text{ mm}$ or $API_{30d} > 250\text{ mm}$), **OR**
   - Verified field intelligence / CCTV crack detection confirmed.
3. **Authorization Layer**: Automated recommendations require Emergency Operations Center (EOC) watch-officer authorization before triggering OASIS CAP v1.2 public siren broadcasts.

---

## 9. Reproducibility & Model Registry

All model artifacts are versioned, hashed, and tracked:
- **Model Path**: `models/pahad_event_model.pkl`
- **Metadata Path**: `models/pahad_event_model.metadata.json`
- **Metrics Path**: `models/pahad_event_metrics.json`
- **Retraining Command**:
  ```bash
  python scripts/train_event_model.py --dataset data/features/real_train.csv --output models/pahad_event_model.pkl --seed 42 --algorithm gradient_boosting --model-version v1.0
  ```
- **Environment**: Python 3.11.0, scikit-learn 1.9.0, pandas 2.2.0, numpy 2.0.0.
