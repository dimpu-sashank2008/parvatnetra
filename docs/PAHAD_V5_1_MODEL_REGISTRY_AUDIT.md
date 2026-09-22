# PARVAT NETRA / PAHAD AI — PHASE V5.1 MODEL REGISTRY AUDIT

**Audit Date**: September 21, 2026  
**Phase**: V5.1 Cross-Phase Scientific Consistency Audit  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering  
**Scope**: All Machine Learning & Statistical Surrogates across Phases 2A–V5.1  

---

## 1. Executive Summary

This document performs an exhaustive, byte-level forensic audit of every model weight artifact, pickle binary, feature schema, and inference contract in the repository. It codifies the permanent separation between physical geotechnical models, tabular event classifiers, sequence deep learning baselines, and uninstantiated kinematic networks.

---

## 2. Definitive Model Family Breakdown

### Model A: Geotechnical Factor of Safety (FoS) Regressor
- **System Designation**: `PAHAD-Geotechnical-FoS-Predictor`
- **Target Variable**: Factor of Safety ($FoS$) — continuous scalar $\in [0.4, 2.5]$.
- **Physical Grounding**: Infinite-slope Mohr-Coulomb shear strength formulation:
  $$FoS = \frac{c' + (\gamma z \cos^2\beta - u)\tan\phi'}{\gamma z \sin\beta\cos\beta}$$
- **Model Type**: Random Forest Regressor surrogate for finite-element / limit-equilibrium numerical solver.
- **Model Artifact**: `models/fos_predictor.pkl`
- **Status**: `PHYSICS_SURROGATE_ACTIVE`
- **Invariant**: FoS is NOT a landslide probability. FoS $< 1.0$ indicates limit-state failure mechanics; FoS $\ge 1.3$ denotes stable hillslope.

### Model B: Landslide Event Classifier
- **System Designation**: `PAHAD-Event-Classifier-GBDT`
- **Target Variable**: Landslide Event Probability $P(\text{Event} = 1 \mid X) \in [0.0, 1.0]$.
- **Model Type**: Scikit-Learn `GradientBoostingClassifier` with Platt Sigmoid Probability Calibration (`CalibratedClassifierCV`).
- **Model Artifact**: `models/pahad_event_model.pkl` (calibrator: `models/pahad_event_calibrator.pkl`)
- **Verified SHA-256**: `80eeeb3c261e4e3e3b3e23927d3b51d8b9d3ffbb9007f3d9d300ad8c44b931be`
- **Dataset**: `features_all.csv` (36 real samples: 16 train, 12 val, 8 test holdout).
- **Status**: `TRAINED_LIMITED_DATA`
- **Invariant**: The Event Classifier must NEVER be confused with the Geotechnical FoS model.

### Model C: Production BiLSTM Sequence Model (Phase V3)
- **System Designation**: `PAHAD-BiLSTM-v3-MultiModal-33Features`
- **Target Variable**: Multi-horizon cumulative hazard index / CRI alert vector.
- **Architecture**: 2-layer Bidirectional LSTM + Temporal Attention (hidden size = 160, 33 input channels).
- **Weights File**: `models/pahad_lstm_v3_weights.pt`
- **Immutable SHA-256**: `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`
- **Input Sequence Length**: 72 hours (hourly resolution).
- **Status**: `PRODUCTION_SERVING_FROZEN`
- **Invariant**: Frozen for operational serving stability.

### Model D: Research Deep Learning Baseline (Phase V4.5)
- **System Designation**: `Model_D_1Layer_BiLSTM_Att_V4_5`
- **Target Variable**: Extended-horizon failure likelihood (up to 168 hours).
- **Architecture**: 1-layer Bidirectional LSTM + Multi-Head Temporal Attention (hidden size = 128, 31 input channels).
- **Weights File**: `models/pahad_lstm_v4_5_research_weights.pt`
- **Immutable SHA-256**: `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f`
- **Input Sequence Length**: 168 hours (7 days continuous empirical reanalysis).
- **Feature Channel Hygiene**: CRI feature channel strictly removed to prevent circular target leakage.
- **Status**: `RESEARCH_BASELINE_OFFLINE`
- **Invariant**: Offline research benchmark demonstrating deep infiltration capture.

### Model E: Kinematic IoT In-Situ ML Network (Phases V4.8–V5.1)
- **System Designation**: `PAHAD-Kinematic-IoT-ML-Model`
- **Status**: Strictly `NOT_TRAINED_DATA_PENDING`
- **Weights File**: None (`None`, zero weights files exist on disk).
- **Rationale**: Physical downhole sensors and borehole casings are NOT yet installed in the mountain. Zero live field telemetry exists. Training or synthesizing weights is strictly prohibited.

---

## 3. Cryptographic Immutability Ledger

```
================================================================================
MODEL WEIGHTS SHA-256 INVARIANCE AUDIT
================================================================================
V3 Production Model:
  Path:     models/pahad_lstm_v3_weights.pt
  Expected: 7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183
  Actual:   7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183
  Status:   MATCH — BIT-FOR-BIT IMMUTABLE

V4.5 Research Baseline:
  Path:     models/pahad_lstm_v4_5_research_weights.pt
  Expected: 31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f
  Actual:   31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f
  Status:   MATCH — BIT-FOR-BIT IMMUTABLE
================================================================================
```
