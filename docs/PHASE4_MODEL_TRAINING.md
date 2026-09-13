# PARVATNETRA / PAHAD AI — Scientific Model Training & Benchmarking Report

**Document ID**: `PAHAD-REP-04-TRAINING`  
**Classification**: Research & Engineering Benchmark  
**Phase**: Phase 4 — Data-Grounded Research Prototype  
**Dataset SHA-256**: `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`  
**Status**: `DATA-GROUNDED RESEARCH PROTOTYPE`  

---

## 1. Executive Summary

This report documents the architectural benchmarking, temporal holdout validation, and Platt sigmoid probability calibration for the **PAHAD AI Landslide Event Prediction Model**.

Three distinct classification architectures were evaluated on identical, leakage-free temporal partitions:
1. **L2-Regularized Logistic Regression** (standardized linear baseline)
2. **Random Forest Classifier** (bagged non-linear decision trees)
3. **Gradient Boosting Classifier** (sequentially boosted decision trees)

---

## 2. Partition & Dataset Setup

The training pipeline strictly adhered to the chronological holdout split without random shuffling:

- **Training Partition** (`data/features/real_train.csv`): 16 samples (8 events, 8 controls) up to October 2023.
- **Validation Partition** (`data/features/real_val.csv`): 12 samples (4 events, 8 controls) from February 2024 to June 2024.
- **Held-Out Test Partition** (`data/features/real_test.csv`): 8 samples (5 events, 3 controls) from July 2024 to October 2024.

---

## 3. Model Architecture Comparison

| Model Architecture | Hyperparameters / Structure | Strengths | Limitations |
| :--- | :--- | :--- | :--- |
| **Logistic Regression** | L2 Penalty, $C=1.0$, `StandardScaler` | Highly interpretable weights, stable on small sample sizes | Cannot capture non-linear hydro-mechanical interaction thresholds |
| **Random Forest** | 50 estimators, max depth 4, balanced class weights | Resilient to individual outlier features, handles high dimensionality | Can exhibit discrete probability steps on small leaf nodes |
| **Gradient Boosting (GBDT)** | 45 estimators, learning rate 0.08, max depth 3, subsample 0.85 | Accurately models compound non-linear triggers ($FoS \times \text{rainfall}$) | Requires calibration to avoid overconfident boundary probabilities |

---

## 4. Benchmark Performance Matrix (Held-Out Test Set, $N=8$)

### Uncalibrated vs Platt-Calibrated Comparison

| Architecture | Variant | ROC-AUC | PR-AUC | POD (Recall) | FAR | CSI | Brier Score | ECE | Lead Time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | Raw | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0021 | 0.0345 | 24.0h |
| **Logistic Regression** | Calibrated | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0354 | 0.1849 | 24.0h |
| **Random Forest** | Raw | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0684 | 0.1600 | 24.0h |
| **Random Forest** | Calibrated | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0656 | 0.2385 | 24.0h |
| **Gradient Boosting** | Raw | 1.0000 | 1.0000 | 1.0000 | 0.2857 | 0.7143 | 0.0942 | 0.1959 | 24.0h |
| **Gradient Boosting** | **Calibrated (Selected)** | **1.0000** | **1.0000** | **1.0000** | **0.0000** | **1.0000** | **0.0824** | **0.2604** | **24.0h** |

> [!IMPORTANT]
> **Why Calibration Mattered**:  
> In the raw uncalibrated Gradient Boosting model, heavy monsoon rainfall on stable slopes (`CTRL-ML-HEAVY-01` and `CTRL-AR-HEAVY-01`) caused two false alarms ($FAR = 0.2857$, $CSI = 0.7143$). Platt sigmoid scaling properly rescaled the probability outputs against validation controls, eliminating false alarms ($FAR = 0.0000$, $CSI = 1.0000$).

---

## 5. Sample Size Caveat & Scientific Honesty

The evaluation was conducted on a held-out test partition of **$N = 8$ samples (5 disaster events, 3 negative controls)**.
While nominal ROC-AUC and CSI scores are 1.0, the small sample size means that confidence intervals are broad. The model status is formally designated as:

$$\text{STATUS} = \text{DATA-GROUNDED RESEARCH PROTOTYPE}$$

It must NOT be claimed as an unconstrained "production-certified" model until validated across multi-season deployments.
