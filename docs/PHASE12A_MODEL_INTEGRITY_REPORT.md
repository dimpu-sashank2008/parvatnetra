# PARVAT NETRA / PAHAD AI — PHASE 12A MODEL INTEGRITY REPORT
**Machine Learning Model Verification, Dataset Provenance & Honest Performance Metrics**
*SIH 2026 Problem Statement: SIH 26001*

---

## 1. Executive Summary & Scientific Limitation Acknowledgment

The PAHAD Landslide Event Classifier is a supervised machine learning model trained to estimate the calibrated probability of a landslide event within a forecast horizon ($P(\text{event} \mid \mathbf{x})$):

- **Current Status:** `TRAINED_LIMITED_DATA / DATA-GROUNDED RESEARCH PROTOTYPE`
- **Model Family:** Gradient Boosting Classifier (`scikit-learn`) + Platt Probability Scaling
- **Artifact File:** `models/pahad_event_model.pkl`
- **Model SHA-256:** `0041fcaf0010fff4c45c3f7bb5a3ca36348b0672677f2a4d0c7cca3ef180a23e`
- **Training Dataset SHA-256:** `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`

### CRITICAL SCIENTIFIC LIMITATION:
The model was evaluated on a held-out temporal test set containing **$N = 8$ windows (5 positive events, 3 negative controls)**. While the model achieves a test score of $1.0$ (ROC-AUC, Precision, Recall, CSI), **THIS METRIC IS STATISTICALLY QUALIFIED BY THE SMALL SAMPLE SIZE ($N=8$)**. 

PARVAT NETRA **strictly prohibits** claiming "100% production accuracy" or "field deployment readiness" based on an $N=8$ test set. The model is presented honestly as a data-grounded prototype demonstrating full architectural integration.

---

## 2. Dataset Partitioning & Provenance Audit

All training, validation, and testing partitions were constructed using **Temporal and Spatial Grouped Holdout** (older historical events for training, subsequent events for validation, most recent events for testing).

| Partition | CSV File Path | Row Count | Positives ($y=1$) | Controls ($y=0$) | SHA-256 Dataset Hash |
|---|---|---|---|---|---|
| **Train** | `data/features/real_train.csv` | **16** | 8 | 8 | `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e` |
| **Validation**| `data/features/real_val.csv` | **12** | 4 | 8 | `ed732e2054f1b028cab9380a35ad31affbbb5e93a3cb207fda1582665aa0bd81` |
| **Test** | `data/features/real_test.csv` | **8** | 5 | 3 | `29f84cf974241844a16086736e1cab833484a9587519946dd24ee09ae09d28da` |
| **Total** | `data/labels/event_labels.csv` | **36** | 17 | 19 | `edcdb95b13a87208deb3aa20cf29f381bad8c9312c8879131bce38ad00455a4c` |

### Integrity Invariants Verified:
1. **Zero Synthetic Contamination:** No synthetic or simulated demo samples exist in `real_train.csv`, `real_val.csv`, or `real_test.csv`.
2. **Zero Temporal Leakage:** Test windows strictly post-date training windows.
3. **Zero Label Circularity:** Labels ($y=1$) are derived exclusively from documented physical disaster occurrences (GSI/BRO/ISRO reports), NOT from model outputs, FoS calculations, or rainfall thresholds.

---

## 3. Feature Vector Schema & Preprocessing Pipeline

The model utilizes an 11-feature input vector with strict index ordering:

| Index | Feature Name | Description | Units | Source | Imputation Fallback |
|---|---|---|---|---|---|
| 0 | `slope_deg` | Topographic slope angle | degrees | SRTM / CartoDEM | $39.0^\circ$ |
| 1 | `elevation_m` | Elevation above MSL | meters | SRTM DEM | $890.0\text{ m}$ |
| 2 | `rainfall_24h` | 24-hour cumulative rainfall | mm | IMD / Open-Meteo | $165.0\text{ mm}$ |
| 3 | `rain_48h` | 48-hour cumulative rainfall | mm | IMD / Open-Meteo | $210.0\text{ mm}$ |
| 4 | `rain_72h` | 72-hour cumulative rainfall | mm | IMD / Open-Meteo | $260.0\text{ mm}$ |
| 5 | `rain_intensity` | Peak hourly rainfall intensity | mm/hr | Rain gauge / Nowcast | $6.5\text{ mm/h}$ |
| 6 | `pore_pressure_kpa` | Basal pore-water pressure | kPa | In-situ piezometer | $26.0\text{ kPa}$ |
| 7 | `ground_displacement_mm`| Cumulative ground displacement | mm | In-situ inclinometer | $38.0\text{ mm}$ |
| 8 | `fos` | Infinite-slope Factor of Safety | dimensionless | Physical model | $0.72$ |
| 9 | `ndvi_anomaly` | Satellite vegetation loss index | dimensionless | Sentinel-2 NDVI | $0.0$ |
| 10 | `insar_los_mm` | Satellite line-of-sight velocity | mm/yr | Sentinel-1 InSAR | $0.0$ |

---

## 4. Empirical Test Set Metrics ($N = 8$)

The metrics below were computed directly on `data/features/real_test.csv`:

| Evaluation Metric | Measured Value | Standard Formulation | Interpretation with Sample Limitation |
|---|---|---|---|
| **ROC-AUC** | **$1.000$** | Area under Receiver Operating Characteristic | Perfect ranking on $N=8$ test set ($5$ positive, $3$ negative). |
| **PR-AUC** | **$1.000$** | Area under Precision-Recall Curve | Complete separation between positive and negative test windows. |
| **Precision** | **$1.000$** | $TP / (TP + FP)$ | $5 / (5 + 0) = 1.0$ (Zero false alarms on test set). |
| **Recall / POD** | **$1.000$** | $TP / (TP + FN)$ | $5 / (5 + 0) = 1.0$ (Zero misses on test set). |
| **FAR** | **$0.000$** | $FP / (TP + FP)$ | False Alarm Ratio = $0\%$. |
| **CSI** | **$1.000$** | $TP / (TP + FN + FP)$ | Critical Success Index = $1.0$. |
| **F1 Score** | **$1.000$** | $2 \cdot (P \cdot R) / (P + R)$ | Harmonic mean of precision and recall. |
| **Brier Score** | **$0.0824$** | Mean squared probability error | Reflects well-calibrated probabilistic confidence. |
| **Expected Calibration Error (ECE)** | **$0.2604$** | Average calibration deviation | Indicates moderate miscalibration due to small sample size. |
| **Median Warning Lead Time** | **$24.0\text{ hours}$** | Time from first prediction to event | Forecasts delivered at least 24h prior to recorded slide. |

### Confusion Matrix Breakdown:
$$\begin{pmatrix} TN = 3 & FP = 0 \\ FN = 0 & TP = 5 \end{pmatrix}$$
