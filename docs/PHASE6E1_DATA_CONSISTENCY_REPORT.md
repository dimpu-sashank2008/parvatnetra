# PARVAT NETRA / PAHAD AI — PHASE 6E.1
## Data, Split & Metric Consistency Audit Report

**Project**: PARVAT NETRA — National Landslide Disaster Intelligence  
**AI Engine**: PAHAD AI  
**Audit Scope**: Phase 6E.1 Data/Metric Reconciliation  
**Date**: September 2026  
**Final Status**: `CORRECTED_AND_CONSISTENT`  

---

## 1. Canonical Event Count Reconciliation

- **Canonical Verified Historical Landslide Events**: **17**
  - Authenticated by Geological Survey of India (GSI), ISRO Disaster Management Support Group (DMSG), State Disaster Management Authorities (SDMAs), and Border Roads Organisation (BRO Swastik/Pushpak).
  - Geographic Coverage: All 8 North Eastern Region (NER) states (Sikkim, Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura).
  - Temporal Range: May 16, 2022 to October 4, 2024.
  - Source Artifacts: `data/raw/historical_landslides_ner.csv` and `data/manifests/canonical_event_inventory.json`.
  - Excluded Events: 0 (All 17 documented catastrophic slope failures are retained).

- **Root Cause of "36 Real Historical Events" Discrepancy**:
  The Phase 6E report summary box previously stated `REAL HISTORICAL EVENTS: 36`. This was an erroneous conflation of **Total Model Observation Samples** ($N=36$, consisting of 17 positive event rows + 19 negative control windows) with "Historical Events". The verified canonical historical event count is strictly **17**.

---

## 2. Model Observation Count & Split Reconciliation

### 2.1 Baseline Observation Dataset (`data/features/features_all.csv` & `pahad_event_observations.csv`)
- **Total Model Observations**: **36**
  - **Positive Event Observations**: **17** ($Y=1$, one per verified historical disaster)
  - **Negative Control Windows**: **19** ($Y=0$, verified non-event stability regimes)
  - Balance: 47.2% Positive / 52.8% Negative

| Split | Samples Total | Positive Events | Negative Controls | Temporal Window | Status |
|:---|:---:|:---:|:---:|:---|:---:|
| **Training Set** (`real_train.csv`) | **16** | 8 | 8 | 2022-05-16 to 2023-10-04 | `[HISTORICAL]` |
| **Validation Set** (`real_val.csv`) | **12** | 4 | 8 | 2024-02-14 to 2024-06-25 | `[HISTORICAL]` |
| **Test Set** (`real_test.csv`) | **8** | 5 | 3 | 2024-07-02 to 2024-10-04 | `[HISTORICAL]` |
| **Total** | **36** | **17** | **19** | **2022-05-16 to 2024-10-04** | **Reconciled** |

$$\text{Train (16)} + \text{Validation (12)} + \text{Test (8)} = \mathbf{36} \quad \text{(Verified: 100\% match)}$$

### 2.2 Antecedent Temporal Expansion Dataset (`data/processed/phase5b_temporal_full.csv`)
- **Total Antecedent Samples**: **105**
  - **Antecedent Event Windows**: **85** ($17 \text{ events} \times 5 \text{ non-overlapping windows: } T-48\text{h}, T-36\text{h}, T-24\text{h}, T-12\text{h}, T-6\text{h}$)
  - **Independent Control Windows**: **20** (4 distinct stability regimes without FoS circular bias)
- **Partitions**:
  - `Train`: **48** samples (40 event windows, 8 controls)
  - `Validation`: **33** samples (25 event windows, 8 controls)
  - `Test`: **24** samples (20 event windows, 4 controls)

$$\text{Train (48)} + \text{Validation (33)} + \text{Test (24)} = \mathbf{105} \quad \text{(Verified: 100\% match)}$$

- **Event-Group Separation**: Strict chronological holdout. Zero cross-partition event contamination or window overlap.

---

## 3. Model Metric Reconciliation

### 3.1 Single-Classifier Model Artifact (`models/pahad_event_model.pkl`)
- **Metadata**: `models/pahad_event_model.metadata.json` / `models/pahad_event_metrics.json`
- **Model Version**: `test-v1.0` (Status: `TRAINED_LIMITED_DATA`)
- **Evaluation Set**: Held-out test set `data/features/real_test.csv` ($N=8$ samples: 5 positive events, 3 negative controls)
- **Actual Verified Metrics**:
  - `ROC-AUC`: **1.000**
  - `PR-AUC`: **1.000**
  - `POD (Recall)`: **1.000** ($5/5$)
  - `FAR`: **0.000** ($0/5$)
  - `CSI (Threat Score)`: **1.000** ($5/5$)
  - `Brier Score`: **0.0824**
  - `ECE (Calibration Error)`: **0.2604**
  - `Warning Lead Time`: Median **24.0 hours** (Min: 24.0h, Max: 24.0h)
  - `Confusion Matrix`: $\text{TP}=5, \text{TN}=3, \text{FP}=0, \text{FN}=0$

### 3.2 Multi-Horizon Models (`models/pahad_event_model_{6h,12h,24h,48h}.pkl`)
- **Metadata**: `models/phase5b_multi_horizon_metrics.json`
- **Model Version**: `5.2.0-phase5b` (Status: `TRAINED_LIMITED_DATA`)
- **Evaluation Set**: Held-out antecedent test set `data/processed/phase5b_temporal_test.csv` ($N=24$ samples: 4 unseen events $\times$ 5 windows = 20 event windows, 4 controls)
- **Actual Verified Metrics**:
  - **6h Horizon**: POD = 1.000, FAR = 0.000, CSI = 1.000, ROC-AUC = 1.000, Brier = 0.0043, ECE = 0.0516, Lead Time = 6.0h
  - **12h Horizon**: POD = 1.000, FAR = 0.000, CSI = 1.000, ROC-AUC = 1.000, Brier = 0.0034, ECE = 0.0547, Lead Time = 12.0h
  - **24h Horizon**: POD = 1.000, FAR = 0.000, CSI = 1.000, ROC-AUC = 1.000, Brier = 0.0045, ECE = 0.0638, Lead Time = 24.0h
  - **48h Horizon**: POD = 1.000, FAR = 0.000, CSI = 1.000, ROC-AUC = 1.000, Brier = 0.0084, ECE = 0.0751, Lead Time = 48.0h

- **Correction of Copied Metrics**:
  The previous summary box in `PHASE6E_SUPERVISED_OPERATIONS_REPORT.md` reported `ROC-AUC: 0.850 | PR-AUC: 0.812 | POD: 0.800 | FAR: 0.200 | CSI: 0.667 | Lead Time: 4.5h`. These numbers were placeholders from early design documents and did not reflect actual model evaluation artifacts. The report has been updated to reflect the true metrics.

---

## 4. Model Registry & API Consistency Audit

All sources have been verified and confirmed in agreement:

| Parameter | `models/*.metadata.json` | `engine/model_registry.py` | `/api/pahad/model-status` | Reconciled Status |
|:---|:---:|:---:|:---:|:---:|
| **Model Name** | `PAHAD-Event-Classifier` | `PAHAD-Event-Classifier` | `PAHAD-Event-Classifier` | **MATCH** |
| **Model Version** | `test-v1.0` | `test-v1.0` | `test-v1.0` | **MATCH** |
| **Model Status** | `TRAINED_LIMITED_DATA` | `TRAINED_LIMITED_DATA` | `TRAINED_LIMITED_DATA` | **MATCH** |
| **Training Samples** | 16 | 16 | 16 | **MATCH** |
| **Validation Samples**| 12 | 12 | 12 | **MATCH** |
| **Test Samples** | 8 | 8 | 8 | **MATCH** |
| **Historical Events** | 17 | 17 | 17 | **MATCH** |
| **Dataset SHA-256** | `79ece554...` | `79ece554...` | `79ece554...` | **MATCH** |
| **Forecast Horizons** | `[1, 3, 6, 12, 24, 48]` | `[1, 3, 6, 12, 24, 48]` | `[1, 3, 6, 12, 24, 48]` | **MATCH** |
| **Calibration** | Platt Sigmoid | Platt Sigmoid | Platt Sigmoid | **MATCH** |

---

## 5. Temporal Model Architecture Verification

| Model Component | Artifact File | Classification | Status | Rationale |
|:---|:---|:---:|:---:|:---|
| **6h Horizon Event Model** | `models/pahad_event_model_6h.pkl` | GBDT Classifier | `TRAINED` | Trained on 48 antecedent samples, calibrated via validation fold. |
| **12h Horizon Event Model**| `models/pahad_event_model_12h.pkl`| GBDT Classifier | `TRAINED` | Trained on 48 antecedent samples, calibrated via validation fold. |
| **24h Horizon Event Model**| `models/pahad_event_model_24h.pkl`| GBDT Classifier | `TRAINED` | Trained on 48 antecedent samples, calibrated via validation fold. |
| **48h Horizon Event Model**| `models/pahad_event_model_48h.pkl`| GBDT Classifier | `TRAINED` | Trained on 48 antecedent samples, calibrated via validation fold. |
| **Physics-Informed LSTM** | `engine/pahad_lstm.py` | Physics Surrogate | `SURROGATE` (`NOT_TRAINED`) | Explicitly documented as a physics-informed mathematical surrogate; zero deep learning weights claimed. |
| **Physical FoS Model** | `models/pahad_fos_model.pkl` | Mohr-Coulomb Engine | `EXISTING` | Model A (Infinite slope factor of safety), strictly decoupled from event classifier. |

---

## 6. Files Corrected

1. `docs/PHASE6E_SUPERVISED_OPERATIONS_REPORT.md`:
   - Reconciled historical event count from 36 down to canonical **17**.
   - Reconciled observations to 36 total (17 positive, 19 negative control).
   - Reconciled partition counts: Train = 16, Validation = 12, Test = 8 (sum = 36).
   - Documented Phase 5B antecedent expansion: 105 samples (Train = 48, Val = 33, Test = 24).
   - Replaced placeholder metrics (`0.850`, etc.) with authentic test metrics from `pahad_event_metrics.json` and `phase5b_multi_horizon_metrics.json`.

2. `app.py`:
   - Updated `/api/pahad/model-metrics` to load `models/pahad_event_metrics.json` and return `statistical_metrics` and `operational_metrics` dictionaries alongside `multi_horizon_metrics`.
   - Cleaned duplicate return statement.

---

## 7. Verification Test Battery

The entire test battery of event, registry, API, inference, and Phase 6E suites was executed:
- Event and Model Consistency Suites (12 test modules): **39 / 39 PASSED**
- Phase 6E Operational Suites (9 test modules): **38 / 38 PASSED**
- Live Inference Suite (`test_live_inference.py`): **40 / 40 PASSED**
- **Total Verified**: **117 / 117 PASSED (100% Pass Rate)**
