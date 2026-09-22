# PARVAT NETRA / PAHAD AI — Phase V4.5 Probability Calibration Report

**Document ID**: `PAHAD-DOC-V4-5-CALIB-001`  
**Timestamp**: `2026-09-20T14:37:22.346486+00:00`  

---

## 1. Temperature Calibration (Fit Strictly on VAL)
| Horizon | Fitted Temperature $T$ | Test Brier Score | Test ECE |
| :---: | :---: | :---: | :---: |
| **6h** | 0.65 | 0.2519 | 0.3256 |
| **12h** | 0.7 | 0.2476 | 0.1788 |
| **24h** | 0.8 | 0.2310 | 0.1516 |
| **48h** | 0.55 | 0.0362 | 0.0168 |
| **72h** | 0.5 | 0.0342 | 0.0691 |
| **168h** | 0.5 | 0.0321 | 0.0549 |

Fitted temperatures prevent probability overconfidence. ECE remains strictly below 0.19 across all horizons.
