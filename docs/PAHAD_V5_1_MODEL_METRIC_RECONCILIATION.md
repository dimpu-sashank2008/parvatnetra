# PARVAT NETRA / PAHAD AI — PHASE V5.1 MODEL METRIC RECONCILIATION

**Document ID**: `DOC-V5-1-METRIC-RECON`  
**Phase**: V5.1 — Scientific Truth Ledger & Metric Lineage Reconciliation  
**Primary Corridor**: `CORR-NH10-SIKKIM-KM48`  
**System Designation**: Smart India Hackathon (SIH) 2026 AI-Assisted Research and Decision-Support Prototype  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering Swarm  
**Date**: September 21, 2026  

---

## 1. Executive Summary

This report reconciles all reported machine learning model metrics across PARVAT NETRA, distinguishing verified reproducible metrics from untraced narrative claims. 

Specifically, it audits:
1. **PAHAD Event Classifier (GBDT)**: Holdout evaluation on $N=8$ test samples.
2. **Production BiLSTM V3**: 33-feature multimodal model evaluated on $N=24$ test holdout.
3. **Research BiLSTM V4.5**: 31-feature model evaluated on 24 frozen sequences across 6h, 12h, 24h, 48h, 72h, 168h horizons.
4. **Untraced Claims**: ROC-AUC 0.81 / PR-AUC 0.74 / POD 0.78 / FAR 0.22 / CSI 0.64.

---

## 2. Authoritative Reproducible Metrics

### 2.1 PAHAD Event Classifier (GBDT)
- **Model File**: `models/pahad_event_model.pkl`
- **Calibrator**: `models/pahad_event_calibrator.pkl`
- **Source Artifact**: `models/pahad_event_metrics.json`
- **Evaluation Partition**: Test Holdout ($N=8$: 5 positive events, 3 negative controls)
- **ROC-AUC**: **1.000**
- **PR-AUC**: **1.000**
- **POD (Probability of Detection)**: **1.000**
- **FAR (False Alarm Ratio)**: **0.000**
- **CSI (Critical Success Index)**: **1.000**
- **Brier Score**: **0.0824**
- **Expected Calibration Error (ECE)**: **0.2604**
- **Qualification**: Statistically constrained by the small test sample ($N=8$). Officially cataloged as `TRAINED_LIMITED_DATA`.

### 2.2 Research BiLSTM V4.5 (Model D)
- **Model File**: `models/pahad_lstm_v4_5_research_weights.pt`
- **Source Artifact**: `reports/pahad_lstm_v4_5_result.json`
- **Evaluation Partition**: Frozen single-pass test holdout ($N=24$ sequences)
- **48-Hour Horizon Performance**:
  - **CSI**: **0.9524**
  - **POD**: **1.0000**
  - **FAR**: **0.0476**
  - **Brier Score**: **0.0362**
  - **Precision**: **0.9524**
  - **F1 Score**: **0.9756**
- **24-Hour Horizon Performance**: CSI = 0.5000, POD = 0.7500, FAR = 0.4000
- **12-Hour Horizon Performance**: CSI = 0.3333, POD = 0.7500, FAR = 0.6250
- **6-Hour Horizon Performance**: CSI = 0.1667, POD = 0.5000, FAR = 0.8000
- **Status**: `REPRODUCIBLE` (Offline Research Baseline Only).

---

## 3. Demotion of Untraced Metric Claims

| Claimed Metric | Claimed Value | Source Artifact Found? | Status | Resolution |
|---|---|---|---|---|
| ROC-AUC | 0.81 | None | `UNSUPPORTED` | Formally demoted; figures do not correspond to any artifact on disk. |
| PR-AUC | 0.74 | None | `UNSUPPORTED` | Demoted. |
| POD | 0.78 | None | `UNSUPPORTED` | Demoted. |
| FAR | 0.22 | None | `UNSUPPORTED` | Demoted. |
| CSI | 0.64 | None | `UNSUPPORTED` | Demoted. |

These claims appeared only in narrative text in Phase V5.0 and cannot be reproduced by any training script or model evaluation in the codebase. In accordance with Section 32 ("No Synthetic Performance Claims"), they are strictly demoted to `UNSUPPORTED`.
