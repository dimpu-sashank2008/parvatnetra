# PAHAD AI Landslide Event Model — Calibration & Reliability Report

**Model Version**: `v1.0.0-phase3.1`  
**Dataset SHA-256**: `79ece554fd0d2fc6...`  
**Status**: `TRAINED_LIMITED_DATA`  
**Calibration Method**: Platt Sigmoid Scaling (`CalibratedClassifierCV`)  

---

## 1. Probabilistic Reliability & Calibration Metrics

- **Brier Score Loss**: `0.0824` (lower is better; 0 = perfect probability accuracy)
- **Expected Calibration Error (ECE)**: `0.2604` (average gap between forecast confidence and empirical event frequency)
- **Total Training Samples**: 16 (8 positive, 8 negative)
- **Validation Tuning Samples**: 12
- **Held-Out Test Samples**: 8

## 2. Early Warning Lead Time

- **Median Lead Time**: `24.0 hours`
- **Minimum Lead Time**: `24.0 hours`
- **Maximum Lead Time**: `24.0 hours`

## 3. Operational Threshold Analysis

| Threshold | Precision | Recall | POD | FAR | CSI | TP | FP | FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0.50** | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 5 | 0 | 0 |
| **0.60** | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 5 | 0 | 0 |
| **0.70** | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 5 | 0 | 0 |
| **0.80** | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 5 | 0 | 0 |
| **0.90** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 5 |

---

## 4. Scientific Honesty & Limitations

> [!NOTE]
> Given the sample size of 36 real ground-truth events across the Northeast Region, probability calibration is stabilized through Platt sigmoid scaling. Predictions represent calibrated event likelihoods and are formally cross-verified with physical Factor of Safety ($FoS$) and regional I-D rainfall thresholds under the 2-of-3 signal rule.
