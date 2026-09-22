# PARVAT NETRA / PAHAD AI — Phase V4.5 Multi-Horizon Forecast Report

**Document ID**: `PAHAD-DOC-V4-5-HORIZON-001`  
**Timestamp**: `2026-09-20T14:37:22.346486+00:00`  

---

## 1. Multi-Horizon Test Partition Performance (24 Sequences)

| Horizon | Category | POD (Recall) | FAR | CSI (Threat Score) | Precision | F1-Score | Brier Score | ECE |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6h** | Diagnostic | 0.500 | 0.800 | 0.167 | 0.200 | 0.286 | 0.2519 | 0.3256 |
| **12h** | Diagnostic | 0.750 | 0.625 | 0.333 | 0.375 | 0.500 | 0.2476 | 0.1788 |
| **24h** | Primary | 0.750 | 0.400 | 0.500 | 0.600 | 0.667 | 0.2310 | 0.1516 |
| **48h** | Primary | 1.000 | 0.048 | 0.952 | 0.952 | 0.976 | 0.0362 | 0.0168 |
| **72h** | Primary | 1.000 | 0.048 | 0.952 | 0.952 | 0.976 | 0.0342 | 0.0691 |
| **168h** | Primary | 1.000 | 0.048 | 0.952 | 0.952 | 0.976 | 0.0321 | 0.0549 |

## 2. Horizon Invariants & Operational Findings
- **Synoptic Horizons (24h to 168h)**: Strong predictive skill driven by multi-day moisture saturation front. 48h achieves CSI=0.952, POD=1.000; 72h and 168h maintain CSI=0.952.
- **Diagnostic Horizons (6h, 12h)**: Reanalysis precipitation at 9km spatial resolution lacks sub-daily localized divergence to predict imminent failure without in-situ IoT telemetry.
