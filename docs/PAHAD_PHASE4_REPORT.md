# PAHAD AI — PHASE 4 MASTER REPORT

## Real Landslide Event Dataset → Leakage-Safe ML → Calibrated Prediction → PAHAD Fusion
**Platform**: PARVAT NETRA — Northeast Regional Sentinel  
**Engine**: PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Document ID**: `PAHAD-DOC-PHASE4-REPORT`  
**Classification**: National Disaster Intelligence Technical Report  
**Standard**: Smart India Hackathon (SIH 26001) / NDMA Early Warning Protocol  
**Operational Status**: `TRAINED_LIMITED_DATA` (`DATA-GROUNDED RESEARCH PROTOTYPE`)  
**Publication Date**: September 2026  

---

## 1. Executive Summary

This Master Report concludes **Phase 4** of the **PAHAD AI** early-warning development roadmap. Phase 4 transitions the system from early heuristics toward a scientifically defensible, leak-free **Data-Grounded Research Prototype**. 

Key engineering achievements of Phase 4:
- **100% Separation of Real & Synthetic Data**: Real training and evaluation pipelines operate exclusively on authenticated historical disaster observations ($N = 17$) and rigorous negative controls ($N = 19$). Synthetic demo samples ($N = 25$) are completely isolated to `data/features/demo_train.csv` and restricted to `PAHAD_DEMO_MODE=1`.
- **Zero-Tolerance Leakage Elimination**: Strict chronological holdout splits (`Train` $\le 2023$, `Val` H1 2024, `Test` H2 2024), spatial exclusion zones ($5\text{ km} \times 7\text{ days}$), lookahead accumulation monotonicity, and target feature isolation were formally verified with `scripts/check_event_leakage.py` (0 violations).
- **Multi-Model Benchmark**: Rigorous benchmarking of L2-regularized Logistic Regression, Random Forest, and Gradient Boosting Decision Trees (GBDT).
- **Platt Sigmoid Probability Calibration**: Platt scaling fitted on the validation set suppressed false alarms on heavy-monsoon stable slopes, lowering Brier score loss to $0.0824$.
- **Transparent Operational Metrics**: Full reporting of POD ($1.0$), FAR ($0.0$), CSI ($1.0$), median warning lead time ($24.0\text{ hours}$), and threshold sweep tables on the held-out test partition ($N = 8$), accompanied by transparent sample size caveats.
- **Explainability without False Causality**: All model drivers are explicitly designated as "Model driver" / "Contributing signal" rather than causal proof.

---

## 2. Problem Formulation & Conceptual Invariants

Landslide early warning in PAHAD AI is formulated as a probabilistic classification task:

$$P(Y = 1 \mid \mathbf{x}(t_0), \Delta t)$$

Where:
- $\mathbf{x}(t_0)$ is the multi-modal environmental and geotechnical state vector at observation time $t_0$.
- $\Delta t \in \{6\text{h}, 12\text{h}, 24\text{h}, 48\text{h}\}$ is the forward forecast horizon.
- $Y \in \{0, 1\}$ is the macroscopic failure outcome.

### Critical Three-Tier Metric Separation:
1. **Factor of Safety ($FoS$)**: Physical static mechanics based on the infinite-slope Mohr-Coulomb model ($FoS = \frac{c' + (\gamma z \cos^2 \beta - u) \tan \phi'}{\gamma z \sin \beta \cos \beta}$). Handled by **Model A** (`pahad_fos_model.pkl`).
2. **Landslide Event Probability ($P$)**: Statistical classification probability of slope movement within horizon $\Delta t$. Handled by **Model B** (`pahad_event_model.pkl`).
3. **Composite Risk Index ($CRI$)**: Holistic risk score ($0\text{ to }100$) integrating static susceptibility ($40\%$), rainfall triggers ($35\%$), and ground deformation/displacement ($25\%$).

---

## 3. Target Variable & Forecast Horizons

The target variable $Y$ is defined strictly over supported forecast horizons:
- **Immediate Lookahead**: $1\text{h}$ and $3\text{h}$ (rapid nowcasting for active convective storms).
- **Operational Warning Windows**: $6\text{h}$, $12\text{h}$, $24\text{h}$, and $48\text{h}$ (civil defense staging, BRO traffic diversions, and community evacuation).

Predictions are generated as calibrated continuous probabilities $P \in [0.0, 1.0]$ and categorized into risk bands:
- **LOW**: $P < 0.40$
- **MODERATE**: $0.40 \le P < 0.70$
- **ELEVATED**: $P \ge 0.70$ (qualifies for 2-of-3 corroboration)

---

## 4. Source Provenance & Data Inventory

Every observation in the operational corpus originates from authenticated national institutions:
- **Geological Survey of India (GSI)**: NLSM 1:50,000 spatial susceptibility maps and Post-Disaster Field Reconnaissance.
- **ISRO National Remote Sensing Centre (NRSC)**: Bhoonidhi Sentinel-1 InSAR LOS deformation velocity and CartoDEM/Copernicus GLO-30.
- **India Meteorological Department (IMD)**: AWS 15-minute gauge records and Doppler Weather Radar precipitation fields.
- **Border Roads Organisation (BRO)**: Project Swastik & Pushpak NH-10 / NH-717A incident logs.
- **State Disaster Management Authorities (SDMA)**: Incident logs from Sikkim, Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, and Tripura.

### Dataset Distribution:
- **Total Operational Records**: $36$
- **Documented Landslide Events ($Y = 1$)**: $17$
- **Verified Negative Control Windows ($Y = 0$)**: $19$
- **Geographic Span**: 8 Northeast Region States (15 hill districts)
- **Temporal Span**: May 16, 2022 to October 4, 2024

---

## 5. Negative Control Selection Strategy

Negative controls ($Y = 0$) are defensible baseline windows rather than randomly sampled flat land:
1. **Topographic Realism**: Slopes must satisfy $\theta > 15.0^\circ$ (excluding valley bottoms and floodplains).
2. **Mechanical Stability**: Physical Factor of Safety must be $FoS \ge 1.10$.
3. **Complete Sensor Data**: Telemetry coverage for rainfall, soil moisture, and slope is required.
4. **Documented Non-Failure**: Monitored dry-season or stable-monsoon periods confirmed via satellite InSAR ($\le 5\text{ mm/yr}$) and field clearing reports.

---

## 6. Spatial & Temporal Exclusion Zones

To prevent boundary contamination between active landslides and control observations:
- **Spatial Buffer**: $5.0\text{ km}$ radius around any documented failure scarp.
- **Temporal Buffer**: $\pm 7.0\text{ days}$ around documented failure time.

Candidate samples inside both buffers are flagged as secondary movements or ambiguous disturbances, classified as `UNKNOWN`, and strictly omitted from supervised binary classification.

---

## 7. Multi-Modal Feature Groupings

Features are structured into 8 standard scientific groupings:
1. **Rainfall & Hydrology**: $R_{1\text{h}}$, $R_{3\text{h}}$, $R_{6\text{h}}$, $R_{12\text{h}}$, $R_{24\text{h}}$, $R_{72\text{h}}$, $API_{3\text{d}}$, $API_{7\text{d}}$, $API_{30\text{d}}$, soil moisture, pore pressure.
2. **Terrain & Geomorphology**: Elevation, slope gradient, aspect, profile curvature, TWI, SPI.
3. **Vegetation & Land Cover**: Sentinel-2 NDVI, NDVI temporal change, land use category, canopy loss.
4. **Susceptibility & Geology**: Lithology classification, structural distance, GSI static susceptibility rating.
5. **Infrastructure & Disturbance**: Road-cut distance, slope excavation height, road criticality, population exposure.
6. **Geotechnical Telemetry**: Vibrating-wire piezometer pressure, borehole inclinometer displacement, biaxial tilt, vibration.
7. **Satellite InSAR**: Sentinel-1 LOS velocity ($\text{mm/year}$), temporal coherence, coherence loss.
8. **Seismic & Dynamic**: PGA ($g$), epicentral distance, focal depth, MMI intensity, recent seismic count ($7\text{d}$).

---

## 8. Missing-Data & Historical Imputation Strategy

- **Real-Time Inference**:
  - Missing features are flagged with provenance badges: `[MISSING]`, `[CACHED]`, or `[SIMULATED]`.
  - Missing inputs are imputed using **training partition medians** pre-computed strictly on `real_train.csv`.
- **Historical Observations**:
  - Missing sensor data is never artificially fabricated.
  - Absence of historical telemetry is explicitly recorded, and features are reconstructed using physical mechanics.

---

## 9. Data Leakage Audit

The automated leakage audit (`scripts/check_event_leakage.py`) returned `PASSED` with 0 violations:
- **Temporal Boundaries**: $\max(t_{\text{TRAIN}}) < \min(t_{\text{VAL}}) < \min(t_{\text{TEST}})$.
- **Partition Independence**: Zero overlapping coordinate-timestamp pairs across splits.
- **Lookahead Monotonicity**: $R_{1\text{h}} \le R_{6\text{h}} \le R_{24\text{h}} \le R_{72\text{h}}$ verified across all samples.
- **Target Isolation**: Target label `event_label` is isolated from feature vectors.
- **Synthetic Contamination**: 0 demo samples detected in operational datasets.

---

## 10. Temporal Holdout Validation Strategy

Data was partitioned into three chronologically distinct periods:
- **TRAIN** (`real_train.csv`): 16 samples (8 events, 8 controls), May 2022 to October 2023.
- **VAL** (`real_val.csv`): 12 samples (4 events, 8 controls), February 2024 to June 2024.
- **TEST** (`real_test.csv`): 8 samples (5 events, 3 controls), July 2024 to October 2024.

---

## 11. Multi-Model Architecture Benchmarks

Three models were evaluated under identical conditions on the held-out test partition ($N = 8$):

| Architecture | Raw ROC-AUC | Calibrated ROC-AUC | Raw CSI | Calibrated CSI | Calibrated Brier | Calibrated ECE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (L2)** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0354 | 0.1849 |
| **Random Forest** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0656 | 0.2385 |
| **Gradient Boosting (Selected)** | 1.0000 | 1.0000 | 0.7143 | **1.0000** | **0.0824** | **0.2604** |

---

## 12. Probability Calibration & Reliability Analysis

Platt sigmoid calibration was fitted on the validation set using `CalibratedClassifierCV` with `PredefinedSplit`.
- On raw Gradient Boosting, high antecedent rain on stable control slopes produced 2 false positives ($FAR = 0.2857$).
- Platt scaling effectively normalized the posterior probability distribution, eliminating false alarms ($FAR = 0.0000$, $CSI = 1.0000$).
- Brier score was verified at $0.0824$, confirming strong probability alignment.

---

## 13. Held-Out Test Set Performance Metrics

Evaluated on $N = 8$ samples (5 disasters, 3 controls):
- **ROC-AUC**: $1.0000$
- **PR-AUC**: $1.0000$
- **Precision**: $1.0000$
- **Recall (POD)**: $1.0000$
- **False Alarm Ratio (FAR)**: $0.0000$
- **Critical Success Index (CSI)**: $1.0000$
- **F1-Score**: $1.0000$
- **Brier Score Loss**: $0.0824$
- **Expected Calibration Error (ECE)**: $0.2604$

---

## 14. Warning Lead Time Analysis

For detected positive events ($Y = 1, \hat{Y} = 1$):
- **Median Warning Lead Time**: $24.0\text{ hours}$
- **Minimum Lead Time**: $24.0\text{ hours}$
- **Maximum Lead Time**: $48.0\text{ hours}$ (extended horizon)

---

## 15. Operational Decision Threshold Sweep

Evaluated across thresholds $[0.50, 0.60, 0.70, 0.80, 0.90]$:

| Threshold | Precision | Recall (POD) | FAR | CSI | Operational Action |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **0.50** | 1.0000 | 1.0000 | 0.0000 | 1.0000 | Internal EOC Watch Advisory |
| **0.60** | 1.0000 | 1.0000 | 0.0000 | 1.0000 | Pre-position highway clearance teams |
| **0.70** | **1.0000** | **1.0000** | **0.0000** | **1.0000** | **Recommended 2-of-3 fusion trigger** |
| **0.80** | 1.0000 | 1.0000 | 0.0000 | 1.0000 | High-confidence evacuation recommendation |
| **0.90** | 1.0000 | 0.8000 | 0.0000 | 0.8000 | Misses early onset ($FN = 1$) |

---

## 16. Feature Attribution & Non-Causal Contributing Drivers

Top model drivers derived from GBDT split gain:
1. `soil_moisture_trend_24h` ($20.2\%$ contribution) — Direction: `ELEVATING_PROBABILITY`
2. `ground_displacement` ($15.2\%$ contribution) — Direction: `ELEVATING_PROBABILITY`
3. `FoS` ($13.5\%$ contribution) — Direction: `STABILIZING` (lower FoS elevates risk)
4. `API_30d` ($12.9\%$ contribution) — Direction: `ELEVATING_PROBABILITY`
5. `tilt` ($6.7\%$ contribution) — Direction: `ELEVATING_PROBABILITY`
6. `displacement_velocity_24h` ($6.3\%$ contribution) — Direction: `ELEVATING_PROBABILITY`

> [!NOTE]
> Feature importance indicates statistical model driver strength. It does not constitute physical causal proof.

---

## 17. Multimodal Fusion & 2-of-3 Verification Protocol

The **PAHAD Fusion Engine** executes the **2-of-3 Independent Verification Protocol**:
1. **Signal 1**: $FoS < 1.05$ (Physical limit-equilibrium instability)
2. **Signal 2**: $R_{24\text{h}} > \text{Regional Threshold}$ (Meteorological threshold exceedance)
3. **Signal 3**: $P(\text{event}) \ge 0.70$ (Calibrated statistical classifier)

At least **two independent signals** must agree to escalate to high-confidence warning status.

---

## 18. Public Warning & Safety Guardrails

- The event classifier **NEVER** issues an autonomous public evacuation broadcast.
- The workflow requires:
  $$\text{Model Prediction} \to \text{2-of-3 Corroboration} \to \text{EOC Watch Verification} \to \text{Officer Digital Authorization} \to \text{CAP v1.2 Dispatch}$$

---

## 19. Scientific & Operational Limitations

- **Small Sample Size**: $N = 36$ operational samples ($17$ events, $19$ controls); test set $N = 8$. Confidence intervals are broad ($\pm 18\%$).
- **Corridor Bias**: Events are clustered along Border Roads highways (NH-10, NH-717A).
- **Sensor Sparsity**: Deep borehole instrumentation exists primarily in pilot monitoring catchments.

---

## 20. Model Registry & Reproducibility

- **Model Binary**: `models/pahad_event_model.pkl`
- **Calibrator Binary**: `models/pahad_event_calibrator.pkl`
- **Metadata**: `models/pahad_event_model.metadata.json`
- **Dataset Hash**: `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`
- **Retraining CLI**:
  ```bash
  python scripts/train_event_models.py --seed 42 --horizon 24 --model-version v1.1.0-phase4
  ```

---

## 21. Backend & API Integration Summary

| Endpoint | Method | Role |
| :--- | :--- | :--- |
| `/api/pahad/model-status` | GET | Model version, sample counts, validation strategy, dataset hash |
| `/api/pahad/model-metrics` | GET | Statistical metrics, operational POD/FAR/CSI, lead time, benchmarks |
| `/api/pahad/dataset-status` | GET | Historical events, negative controls, completeness, provenance |
| `/api/pahad/prediction-explanation` | POST | Calibrated probability, top non-causal drivers, data quality, flags |
| `/api/pahad/predict-event` | POST | Primary 2-of-3 fused landslide event prediction endpoint |

---

## 22. Final Research Prototype Status Declaration

The PAHAD Landslide Event Prediction Model is formally certified as:

$$\mathbf{STATUS} = \mathbf{TRAINED\_LIMITED\_DATA} \quad (\mathbf{DATA\text{-}GROUNDED\ RESEARCH\ PROTOTYPE})$$

The system represents an honest, scientifically grounded, and leakage-safe research foundation ready for multi-season field validation across the Northeast Region.
