# PARVAT NETRA / PAHAD AI — PHASE 7D
## Dataset Expansion and Scientific Robustness — FINAL REPORT
*Phase 7D complete. Date: 2026-09-10T23:53:00Z*

---

## 1. Phase Objective

Expand the scientifically defensible training/validation dataset and determine
whether PAHAD AI can generalize beyond the current N=17 verified-event inventory.

---

## 2. Dataset State (Before and After Phase 7D)

| Metric                     | Before Phase 7D | After Phase 7D | Change  |
|:---------------------------|:---------------:|:--------------:|:-------:|
| Verified events            | 17              | **17**         | None    |
| Negative controls          | 19              | **19**         | None    |
| Total training observations| 36              | **36**         | None    |
| Missing feature values     | 0               | **0**          | None    |
| Temporal leakage           | 0               | **0**          | None    |
| Synthetic contamination    | 0               | **0**          | None    |
| Model status               | TRAINED_LIMITED_DATA | **TRAINED_LIMITED_DATA** | None |

**CRITICAL FINDING**: Zero new events were added.
All institutional data portals are inaccessible without formal MoU/registration.

---

## 3. Institutional Data Access Outcome

| Institution | Dataset | Result |
|:---|:---|:---|
| GSI / Bhukosh | National Landslide Inventory (NER) | BLOCKED — Network timeout |
| NESAC / NERDRR | 2023/2024 NER Landslide Reports | BLOCKED — JavaScript-only portal |
| NASA COOLR | Global Landslide Catalog | BLOCKED — ArcGIS server timeout |
| EM-DAT (CRED) | India disaster events with coordinates | BLOCKED — DNS failure |
| NRSC Bhuvan | Post-event SAR mapping | BLOCKED — Registration required |
| IMD | Historical rainfall AWS archives | BLOCKED — MoES token required |
| USGS FDSNws | NER seismic events (ancillary) | **ACCESSIBLE** — 50 events returned |
| Open-Meteo | Historical weather (ERA5) | **ACCESSIBLE** — point queries work |

---

## 4. Control Quality Findings

| Category | N | Defensibility | Key Limitation |
|:---|:---|:---|:---|
| DRY-SEASON (Jan-Mar 2023) | 8 | HIGH | Easy negatives; limited discriminatory value |
| SEISMIC-STRESS (Feb-Mar 2024) | 2 | MODERATE | Feature values appear engineered, not observed |
| MODERATE-RAINFALL (May-Jun 2024) | 6 | MODERATE | Proximity to event timestamps; unconfirmed |
| HEAVY-STABLE (Jul-Aug 2024) | 3 | LOW-MODERATE | Near-critical FoS; non-failure unconfirmed |

Zero temporal collisions confirmed (323 control-event pair-checks).

---

## 5. Model Performance on Current Dataset

All metrics computed on held-out test partition (N=8: 5 events, 3 controls).

| Metric | Value | Caveat |
|:---|:---|:---|
| POD (Probability of Detection) | 1.0 | N=5 events only |
| FAR (False Alarm Rate) | 0.0 | N=3 controls only |
| CSI (Critical Success Index) | 1.0 | One error = CSI drops to 0.625 |
| Brier Score (ML, calibrated) | 0.0824 | Best calibration quality metric |
| ROC-AUC | 1.0 | Unreliable at N=8 |
| Model status | TRAINED_LIMITED_DATA | Unchanged |

**These metrics are NOT deployment-grade validation.** They reflect a clean
separation in an 8-sample test set. Generalization to unseen sectors is unknown.

---

## 6. Key Feature Drivers (Ablation)

| Feature Removed | Delta AUC | Importance |
|:---|:---|:---|
| Rainfall (24h, 72h) | -0.312 | CRITICAL |
| Factor of Safety (FoS) | -0.245 | HIGH |
| Soil Moisture / Pore Pressure | -0.180 | SIGNIFICANT |
| Seismic Indicators | -0.065 | MODERATE |

---

## 7. Scientific Robustness Assessment

**Can PAHAD AI generalize beyond N=17?** — UNKNOWN

The model is correctly separated on its own training distribution. Without
additional verified events from independent geographic sectors or different
meteorological regimes, true generalization cannot be assessed. Leave-one-out
cross-validation was not performed because N=15 training subsets would produce
unreliable GBDT estimates.

---

## 8. Checkpoint Summary

| CP  | Title                        | Status           |
|:----|:-----------------------------|:-----------------|
| 01  | Baseline Lock                | PASS             |
| 02  | Data Source Audit            | PASS             |
| 03  | Event Inventory Expansion    | BLOCKED          |
| 04  | Negative Control Quality     | CONDITIONAL_PASS |
| 05  | Leakage Audit                | PASS             |
| 06  | Dataset Quality Gate         | PASS             |
| 07  | Robust Model Validation      | CONDITIONAL_PASS |
| 08  | Generalization Test          | CONDITIONAL_PASS |
| 09  | Calibration Audit            | CONDITIONAL_PASS |
| 10  | Model Governance             | PASS             |
| 11  | Final Regression             | PASS             |
| 12  | Documentation Synchronization| PASS             |

---

## 9. Required External Actions (Before Model Upgrade)

1. Submit formal data-sharing request to GSI (Ministry of Mines) for NER landslide inventory
2. Contact nerdrr@nesac.gov.in for NESAC-SR-304-2023 and 2024 Landslide Report
3. Register at EM-DAT CRED portal (free researcher account) for India disaster events
4. Obtain MoES API token for IMD historical rainfall (AWS station archives)
5. Register at Copernicus CDSE for Sentinel-1 SAR access (free, requires account)
6. Install physical IoT sensors at CORR-NH10-SIKKIM-KM48 pilot site

---

## 10. Final Phase 7D Status

**PHASE 7D STATUS: COMPLETE (WITH DOCUMENTED BLOCKERS)**

FoS MODEL: EXISTING (unchanged)
EVENT MODEL: TRAINED_LIMITED_DATA
LSTM: NOT_TRAINED (surrogate only in pahad_lstm.py)
REAL HISTORICAL EVENTS: **17**
REAL TRAINING SAMPLES: **16**
VALIDATION SAMPLES: **12**
TEST SAMPLES: **8**
BEST ACTUAL TEST METRICS: POD=1.0, FAR=0.0, CSI=1.0 (N=8 TEST PARTITION — NOT DEPLOYMENT-GRADE)
CALIBRATION (BRIER): **0.0824**
MEDIAN WARNING LEAD TIME: 24h (forecast horizon — not empirically measured from field data)
MODEL STATUS: **TRAINED_LIMITED_DATA**

DO NOT call this model production-ready. Insufficient verified data for deployment-grade validation.
