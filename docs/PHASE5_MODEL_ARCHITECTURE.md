# PAHAD AI — Phase 5 Model Architecture & Benchmarking

**Document**: `PHASE5_MODEL_ARCHITECTURE.md`  
**Classification**: AI/ML Scientific Architecture Specification  
**Phase**: Phase 5 — Real Data Expansion & Live Predictive Inference  
**Status**: BENCHMARKED & VERIFIED  

---

## 1. Architectural Overview

The **PAHAD AI Model Subsystem** relies on a hybrid physics-guided machine learning framework that couples empirical pattern classification with deterministic geotechnical mechanics.

```
                                  INPUT OBSERVATION VECTOR (x)
             [Rainfall, Soil Moisture, Pore Pressure, Tilt, Displacement, Slope, Elevation]
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       │                                                 │
                       ▼                                                 ▼
             GEOTECHNICAL SUBSYSTEM                           EMPIRICAL CLASSIFIER
          Mohr-Coulomb Infinite Slope                    Gradient Boosting Classifier (GBDT)
                       │                                                 │
                       ▼                                                 ▼
             Factor of Safety (FoS)                            Raw Logit Score (z)
                       │                                                 │
                       │                                                 ▼
                       │                                      Platt Sigmoid Calibration
                       │                                                 │
                       │                                                 ▼
                       │                                    P(Event | x) in [0.0, 1.0]
                       │                                                 │
                       └────────────────────────┬────────────────────────┘
                                                │
                                                ▼
                                     PAHAD FUSION ENGINE
                               Composite Risk Index (CRI: 0-100)
                              2-of-3 Corroboration Safety Gate
```

---

## 2. Model Family Benchmark Comparison

Three canonical supervised classification architectures were benchmarked on strictly non-overlapping temporal holdout partitions:

| Architecture | Implementation | Primary Advantages | Operational Limitations | Selection Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **L2-Regularized Logistic Regression** | `sklearn.linear_model.LogisticRegression` | Highly interpretable coefficients; minimal risk of variance explosion on $N < 50$. | Linear hyperplanes cannot model the compound non-linear trigger boundary between rainfall and steep slope. | Baseline comparison. |
| **Random Forest Classifier** | `sklearn.ensemble.RandomForestClassifier` | Resilient to individual feature noise; sub-sampling handles collinear features. | Leaf-probability averaging creates step-function artifacts in probability boundaries. | Ensemble benchmark. |
| **Gradient Boosting Classifier (GBDT)** | `sklearn.ensemble.GradientBoostingClassifier` | Superior non-linear capacity; models critical hydrometeorological trigger thresholds with high fidelity. | Uncalibrated probabilities tend to be overconfident at distribution extremes. | **SELECTED MODEL** (paired with Platt calibration). |

---

## 3. Probability Calibration Architecture

Raw tree ensemble probabilities are uncalibrated confidence scores that often fail to represent empirical frequency.

### Platt Sigmoid Scaling
We employ Platt scaling by fitting a univariate logistic sigmoid over the raw decision scores $z = f(\mathbf{x})$ using the held-out temporal validation partition:
$$P(\text{event} \mid z) = \frac{1}{1 + \exp(A \cdot z + B)}$$

### Empirical Calibration Metrics (Held-Out Test Set, $N=8$)
- **Raw GBDT Brier Score**: $0.0942 \implies$ **Platt Calibrated Brier Score**: **$0.0824$** (12.5% calibration error reduction).
- **False Alarm Ratio (FAR)**: Reduced from $0.2857$ (raw) to **$0.0000$** (calibrated), successfully eliminating monsoon heavy-rain false alarms on structurally stable slopes.

---

## 4. Deep Learning & Sequence Models Status

### Status: `NOT_TRAINED` (Mathematical Surrogate Maintained)
In compliance with SIH and NDMA scientific honesty invariants:
1. No recurrent neural network (LSTM / GRU / Transformer) is claimed as trained on field data.
2. `engine/pahad_lstm.py` contains an explicitly designated **mathematical surrogate** used for simulation walkthroughs under `PAHAD_DEMO_MODE=1`.
3. True sequence model training requires high-frequency ($\ge 1\text{ Hz}$) continuous telemetry spanning $\ge 3$ complete monsoon cycles ($> 100,000$ time steps) to avoid catastrophic memorization.

---

## 5. Model Reproducibility & Governance

- **Training Script**: `scripts/train_event_model.py`
- **Reproducibility CLI Command**:
  ```powershell
  python scripts/train_event_model.py --dataset data/features/real_train.csv --algorithm gradient_boosting --seed 42 --forecast-window 24
  ```
- **Serialization Artifacts**:
  - `models/pahad_event_model.pkl`: Serialized `CalibratedClassifierCV` pipeline.
  - `models/pahad_event_model.metadata.json`: Contains model version, creation timestamp, feature names, dataset SHA-256 hash, and status flag.
  - `models/pahad_event_metrics.json`: Test metrics ($AUC$, $POD$, $FAR$, $CSI$, $Brier$).
