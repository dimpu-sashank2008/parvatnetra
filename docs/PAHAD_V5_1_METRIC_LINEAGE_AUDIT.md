# PARVAT NETRA / PAHAD AI — PHASE V5.1 METRIC LINEAGE AUDIT

**Audit Date**: September 21, 2026  
**Phase**: V5.1 Cross-Phase Scientific Consistency Audit  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering  
**Scope**: Metric Lineage, Calibration Quality, and Demotion of Untraced Claims  

---

## 1. Executive Summary

This audit forensically traces every published quantitative evaluation metric in PARVAT NETRA back to its exact Python evaluation script, confusion matrix, and holdout test set. It separates reproducible empirical metrics from untraced placeholder numbers.

---

## 2. Reproducible Empirical Metrics on Disk

### 2.1 Event Classifier GBDT (`models/pahad_event_model.pkl`)
- **Evaluation Script**: `scripts/train_event_model.py` / `reports/pahad_validation_strategy.md`
- **Test Holdout Set**: `data/features/real_test.csv` ($N = 8$: 5 positive events, 3 negative controls)
- **Validation Holdout Set**: `data/features/real_val.csv` ($N = 12$: 4 positive events, 8 negative controls)
- **Train Set**: `data/features/real_train.csv` ($N = 16$: 8 positive events, 8 negative controls)
- **Measured Holdout Metrics**:
  - **ROC-AUC**: **1.000** (Perfect rank ordering on 8 test samples)
  - **PR-AUC**: **1.000**
  - **Probability of Detection (POD)**: **1.000** (Hits: 5, Misses: 0)
  - **False Alarm Ratio (FAR)**: **0.000** (False Alarms: 0, Hits: 5)
  - **Critical Success Index (CSI)**: **1.000**
  - **Brier Score**: **0.0824** (Reflecting well-calibrated Platt scaling)
  - **Expected Calibration Error (ECE)**: **0.083**
- **Disclosed Limitation**: The small holdout test partition ($N=8$) achieves 1.000 because extreme rainfall events in the test fold are cleanly separable from dry/moderate non-event controls. This 1.000 score reflects the small sample size rather than perfection in the real world. Status remains honestly designated as `TRAINED_LIMITED_DATA`.

### 2.2 Deep Learning Research Baseline V4.5 (`models/pahad_lstm_v4_5_research_weights.pt`)
- **Evaluation Script**: `scripts/evaluate_v4_5_temporal_cv.py`
- **Dataset**: `lstm_v4_4_real_temporal_sequences.csv` (105 continuous 168h sequences)
- **Temporal Lead Horizons & Performance**:
  - **6h Horizon**: POD: 1.000 | FAR: 0.000 | CSI: 1.000
  - **12h Horizon**: POD: 1.000 | FAR: 0.000 | CSI: 1.000
  - **24h Horizon**: POD: 1.000 | FAR: 0.000 | CSI: 1.000
  - **48h Horizon**: POD: 1.000 | FAR: 0.048 | CSI: 0.952
  - **72h Horizon**: POD: 1.000 | FAR: 0.048 | CSI: 0.952
  - **168h Horizon (7 Days)**: POD: 1.000 | FAR: 0.048 | CSI: 0.952
- **Key Scientific Finding**: BiLSTM + Temporal Attention maintains high infiltration capture skill across the 48h–168h window without performance collapse, unlike baseline shallow models.

---

## 3. Demotion of Untraced Claims to `UNSUPPORTED`

| Claimed Metric String | Claimed Value | Audit Finding | Authoritative Status |
|---|---|---|---|
| ROC-AUC | 0.81 | Does not match GBDT holdout (1.000) or V4.5 sequence metrics. No code generated 0.81. | **`UNSUPPORTED`** |
| PR-AUC | 0.74 | Untraced placeholder in late prompt response summary. | **`UNSUPPORTED`** |
| Probability of Detection (POD) | 0.78 | Untraced placeholder. Real GBDT POD is 1.000; V4.5 POD is 1.000. | **`UNSUPPORTED`** |
| False Alarm Ratio (FAR) | 0.22 | Untraced placeholder. Real GBDT FAR is 0.000; V4.5 FAR is 0.048. | **`UNSUPPORTED`** |
| Critical Success Index (CSI) | 0.64 | Untraced placeholder. Real GBDT CSI is 1.000; V4.5 CSI is 0.952. | **`UNSUPPORTED`** |
| Sample Split Count | 41 Train / 11 Val / 11 Test | Untraced sample counts ($N=63$). Real data is 16/12/8 ($N=36$). | **`UNSUPPORTED`** |

These untraced metrics are formally expunged from operational and research baselines.
